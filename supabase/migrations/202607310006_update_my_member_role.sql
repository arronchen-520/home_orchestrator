create or replace function public.update_my_member_role(
    target_household_id text,
    member_role text
)
returns void language plpgsql security definer set search_path = '' as $$
declare
    normalized_role text;
begin
    if auth.uid() is null then raise exception 'Authentication required'; end if;
    normalized_role := trim(coalesce(member_role, ''));
    if length(normalized_role) > 40 then raise exception 'Invalid member role'; end if;

    update public.members
    set role = normalized_role
    where household_id = target_household_id
      and user_id = auth.uid()
      and deleted_at is null;
    if not found then raise exception 'Member profile setup required'; end if;
end;
$$;

revoke all on function public.update_my_member_role(text, text) from public;
grant execute on function public.update_my_member_role(text, text) to authenticated;
