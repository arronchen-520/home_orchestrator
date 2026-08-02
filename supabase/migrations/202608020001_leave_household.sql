create or replace function public.leave_household(target_household_id text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
    account_count integer;
begin
    if auth.uid() is null then raise exception 'Authentication required'; end if;

    perform 1
    from public.household_memberships
    where household_id = target_household_id
    for update;

    if not exists (
        select 1 from public.household_memberships
        where household_id = target_household_id and user_id = auth.uid()
    ) then
        raise exception 'Household not found';
    end if;

    select count(*) into account_count
    from public.household_memberships
    where household_id = target_household_id;

    if account_count <= 1 then
        raise exception 'Cannot leave the last account in a household';
    end if;

    update public.members
    set deleted_at = now()
    where household_id = target_household_id
      and user_id = auth.uid()
      and deleted_at is null;

    delete from public.household_memberships
    where household_id = target_household_id and user_id = auth.uid();
end;
$$;

revoke all on function public.leave_household(text) from public;
grant execute on function public.leave_household(text) to authenticated;
