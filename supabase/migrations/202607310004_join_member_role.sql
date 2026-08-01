drop function if exists public.join_household(text, text);

create or replace function public.join_household(
    household_invite_code text,
    member_name text,
    member_role text default ''
)
returns text language plpgsql security definer set search_path = '' as $$
declare
    target_household_id text;
    now_text text := now()::text;
begin
    if auth.uid() is null then raise exception 'Authentication required'; end if;
    member_name := trim(member_name);
    member_role := trim(coalesce(member_role, ''));
    if length(member_name) not between 1 and 40 or length(member_role) > 40 then
        raise exception 'Invalid member name or role';
    end if;
    select id into target_household_id
    from public.households
    where invite_code = upper(trim(household_invite_code));
    if target_household_id is null then raise exception 'Invalid household invite'; end if;
    if exists (
        select 1 from public.household_memberships
        where user_id = auth.uid() and household_id = target_household_id
    ) then
        raise exception 'This account already belongs to this household';
    end if;
    insert into public.household_memberships(user_id, household_id, role, created_at)
    values (auth.uid(), target_household_id, 'member', now_text);
    insert into public.members(id, household_id, user_id, name, role, created_at)
    values (gen_random_uuid()::text, target_household_id, auth.uid(), member_name, member_role, now_text);
    return target_household_id;
end;
$$;

revoke all on function public.join_household(text, text, text) from public;
grant execute on function public.join_household(text, text, text) to authenticated;
