create or replace function public.update_my_member_profile(
    target_household_id text,
    member_name text,
    member_role text
)
returns void language plpgsql security definer set search_path = '' as $$
declare
    normalized_name text := trim(member_name);
    normalized_role text := trim(coalesce(member_role, ''));
begin
    if auth.uid() is null then raise exception 'Authentication required'; end if;
    if length(normalized_name) not between 1 and 40 or length(normalized_role) > 40 then
        raise exception 'Invalid member name or role';
    end if;

    update public.members
    set name = normalized_name, role = normalized_role
    where household_id = target_household_id
      and user_id = auth.uid()
      and deleted_at is null;
    if not found then raise exception 'Member profile setup required'; end if;
end;
$$;

revoke all on function public.update_my_member_profile(text, text, text) from public;
grant execute on function public.update_my_member_profile(text, text, text) to authenticated;
