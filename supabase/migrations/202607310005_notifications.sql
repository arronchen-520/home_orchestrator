create extension if not exists supabase_vault with schema vault;
create extension if not exists pg_net with schema extensions;
create extension if not exists pg_cron;

create table public.push_subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users(id) on delete cascade,
    endpoint text not null unique,
    p256dh text not null,
    auth text not null,
    timezone text not null,
    language text not null check (language in ('zh', 'en')),
    disabled_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.notification_deliveries (
    subscription_id uuid not null references public.push_subscriptions(id) on delete cascade,
    notification_key text not null,
    created_at timestamptz not null default now(),
    sent_at timestamptz,
    primary key (subscription_id, notification_key)
);

create index push_subscriptions_user on public.push_subscriptions(user_id);

alter table public.push_subscriptions enable row level security;
alter table public.notification_deliveries enable row level security;
revoke all on public.push_subscriptions from anon, authenticated;
revoke all on public.notification_deliveries from anon, authenticated;
grant all on public.push_subscriptions to service_role;
grant all on public.notification_deliveries to service_role;

create or replace function public.claim_notification_delivery(
    target_subscription_id uuid,
    target_notification_key text
)
returns boolean language plpgsql set search_path = '' as $$
begin
    insert into public.notification_deliveries(subscription_id, notification_key)
    values (target_subscription_id, target_notification_key)
    on conflict (subscription_id, notification_key) do update
    set created_at = now()
    where notification_deliveries.sent_at is null
      and notification_deliveries.created_at < now() - interval '5 minutes';
    return found;
end;
$$;

revoke all on function public.claim_notification_delivery(uuid, text) from public, anon, authenticated;
grant execute on function public.claim_notification_delivery(uuid, text) to service_role;

select cron.unschedule(jobid)
from cron.job
where jobname = 'hearthbook-notifications';

select cron.schedule(
    'hearthbook-notifications',
    '* * * * *',
    $$
    select net.http_post(
        url := edge_url_secret.decrypted_secret,
        headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'X-Notification-Cron-Secret', cron_secret.decrypted_secret
        ),
        body := '{}'::jsonb,
        timeout_milliseconds := 30000
    )
    from vault.decrypted_secrets as edge_url_secret
    cross join vault.decrypted_secrets as cron_secret
    where edge_url_secret.name = 'hearthbook_notification_edge_url'
      and cron_secret.name = 'hearthbook_notification_cron_secret'
    limit 1;
    $$
);

select cron.unschedule(jobid)
from cron.job
where jobname = 'hearthbook-cron-log-cleanup';

select cron.schedule(
    'hearthbook-cron-log-cleanup',
    '17 3 * * *',
    $$
    delete from cron.job_run_details
    where end_time < now() - interval '7 days';
    $$
);
