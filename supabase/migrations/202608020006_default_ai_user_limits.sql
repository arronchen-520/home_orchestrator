alter table public.ai_user_limits
alter column daily_limit set default 5;

insert into public.ai_user_limits (user_id, daily_limit)
select id, 5 from auth.users
on conflict (user_id) do nothing;

create or replace function public.create_ai_user_limit()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
    insert into public.ai_user_limits (user_id, daily_limit)
    values (new.id, 5)
    on conflict (user_id) do nothing;
    return new;
end;
$$;

drop trigger if exists create_ai_user_limit on auth.users;
create trigger create_ai_user_limit
after insert on auth.users
for each row execute function public.create_ai_user_limit();
