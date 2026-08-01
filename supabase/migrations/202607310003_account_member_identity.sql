-- Each account has one member identity per household. The API resolves it from auth.uid().
create unique index if not exists members_household_user_unique
    on public.members(household_id, user_id)
    where user_id is not null;

-- Member profiles are readable by the household, but their account binding is not
-- client-editable. The create/join security-definer functions remain the write path.
drop policy if exists members_household_access on public.members;
create policy members_household_read on public.members
for select to authenticated
using ((select private.is_household_member(household_id)));
