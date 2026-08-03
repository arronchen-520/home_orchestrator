create table public.ai_usage_daily (
    user_id uuid not null references auth.users(id) on delete cascade,
    usage_date date not null,
    request_count integer not null default 0 check (request_count >= 0),
    updated_at timestamptz not null default now(),
    primary key (user_id, usage_date)
);

create table public.ai_user_limits (
    user_id uuid primary key references auth.users(id) on delete cascade,
    daily_limit integer check (daily_limit is null or daily_limit >= 0),
    updated_at timestamptz not null default now()
);

alter table public.ai_usage_daily enable row level security;
alter table public.ai_user_limits enable row level security;
revoke all on table public.ai_usage_daily, public.ai_user_limits from public, anon, authenticated;

create or replace function public.consume_ai_quota(target_household_id text)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
    current_user_id uuid := auth.uid();
    quota_date date := (now() at time zone 'UTC')::date;
    limit_value integer;
    used_count integer;
begin
    if current_user_id is null then raise exception 'Authentication required'; end if;
    if not exists (
        select 1 from public.household_memberships
        where user_id = current_user_id and household_id = target_household_id
    ) then
        raise exception 'Household not found';
    end if;
    if not exists (
        select 1 from public.members
        where user_id = current_user_id
          and household_id = target_household_id
          and deleted_at is null
    ) then
        raise exception 'Member profile setup required';
    end if;

    select daily_limit into limit_value
    from public.ai_user_limits
    where user_id = current_user_id;
    if not found then limit_value := 5; end if;

    insert into public.ai_usage_daily(user_id, usage_date)
    values (current_user_id, quota_date)
    on conflict do nothing;

    select request_count into used_count
    from public.ai_usage_daily
    where user_id = current_user_id and usage_date = quota_date
    for update;

    if limit_value is not null and used_count >= limit_value then
        return jsonb_build_object('allowed', false);
    end if;

    update public.ai_usage_daily
    set request_count = used_count + 1, updated_at = now()
    where user_id = current_user_id and usage_date = quota_date;
    return jsonb_build_object('allowed', true);
end;
$$;

revoke all on function public.consume_ai_quota(text) from public, anon, authenticated;
grant execute on function public.consume_ai_quota(text) to authenticated;
