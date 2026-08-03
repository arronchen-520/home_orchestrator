drop function if exists public.leave_household(text);

create or replace function public.leave_household(
    target_household_id text,
    new_owner_member_id text default null
)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
    account_count integer;
    current_role text;
    new_owner_user_id uuid;
begin
    if auth.uid() is null then raise exception 'Authentication required'; end if;

    perform 1
    from public.household_memberships
    where household_id = target_household_id
    for update;

    select role into current_role
    from public.household_memberships
    where household_id = target_household_id and user_id = auth.uid();

    if current_role is null then
        raise exception 'Household not found';
    end if;

    select count(*) into account_count
    from public.household_memberships
    where household_id = target_household_id;

    if account_count <= 1 then
        raise exception 'Cannot leave the last account in a household';
    end if;

    if current_role = 'owner' then
        if new_owner_member_id is null then
            raise exception 'Household owner must choose a new owner before leaving';
        end if;

        select member.user_id into new_owner_user_id
        from public.members as member
        join public.household_memberships as membership
          on membership.household_id = member.household_id
         and membership.user_id = member.user_id
        where member.id = new_owner_member_id
          and member.household_id = target_household_id
          and member.deleted_at is null
          and member.user_id is not null;

        if new_owner_user_id is null or new_owner_user_id = auth.uid() then
            raise exception 'Choose a valid new household owner';
        end if;

        update public.household_memberships
        set role = 'member'
        where household_id = target_household_id and user_id = auth.uid();
        update public.household_memberships
        set role = 'owner'
        where household_id = target_household_id and user_id = new_owner_user_id;
    elsif new_owner_member_id is not null then
        raise exception 'Only the household owner can transfer ownership';
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

revoke all on function public.leave_household(text, text) from public;
grant execute on function public.leave_household(text, text) to authenticated;

create or replace function public.delete_household(target_household_id text)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
    current_role text;
begin
    if auth.uid() is null then raise exception 'Authentication required'; end if;

    select role into current_role
    from public.household_memberships
    where household_id = target_household_id and user_id = auth.uid();

    if current_role is null then
        raise exception 'Household not found';
    end if;
    if current_role <> 'owner' then
        raise exception 'Only the household owner can delete this household';
    end if;

    delete from public.item_notes
    where item_id in (
        select id from public.items where household_id = target_household_id
    );
    delete from public.recurrence_exceptions
    where series_id in (
        select id from public.items where household_id = target_household_id
    );
    delete from public.conversation_messages
    where session_id in (
        select id from public.conversation_sessions where household_id = target_household_id
    );
    delete from public.items where household_id = target_household_id;
    delete from public.conversation_sessions where household_id = target_household_id;
    delete from public.members where household_id = target_household_id;
    delete from public.household_memberships where household_id = target_household_id;
    delete from public.households where id = target_household_id;
end;
$$;

revoke all on function public.delete_household(text) from public;
grant execute on function public.delete_household(text) to authenticated;
