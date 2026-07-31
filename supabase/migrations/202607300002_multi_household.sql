alter table public.household_memberships
    drop constraint if exists household_memberships_pkey;
alter table public.household_memberships
    add primary key (user_id, household_id);

alter table public.members
    drop constraint if exists members_user_id_key;
create unique index if not exists members_household_user_unique
    on public.members(household_id, user_id)
    where user_id is not null;

create or replace function public.create_household(
    household_name text,
    member_name text
)
returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
    new_household_id text := gen_random_uuid()::text;
    new_invite_code text := upper(
        substr(encode(extensions.gen_random_bytes(8), 'hex'), 1, 12)
    );
    now_text text := now()::text;
begin
    if auth.uid() is null then
        raise exception 'Authentication required';
    end if;
    household_name := trim(household_name);
    member_name := trim(member_name);
    if length(household_name) not between 1 and 80
       or length(member_name) not between 1 and 40 then
        raise exception 'Invalid household or member name';
    end if;

    insert into public.households (
        id, name, invite_code, created_at
    ) values (
        new_household_id, household_name, new_invite_code, now_text
    );
    insert into public.household_memberships (
        user_id, household_id, role, created_at
    ) values (
        auth.uid(), new_household_id, 'owner', now_text
    );
    insert into public.members (
        id, household_id, user_id, name, role, created_at
    ) values (
        gen_random_uuid()::text, new_household_id, auth.uid(),
        member_name, 'Owner', now_text
    );
    return new_household_id;
end;
$$;

create or replace function public.join_household(
    household_invite_code text,
    member_name text
)
returns text
language plpgsql
security definer
set search_path = ''
as $$
declare
    target_household_id text;
    now_text text := now()::text;
begin
    if auth.uid() is null then
        raise exception 'Authentication required';
    end if;
    member_name := trim(member_name);
    if length(member_name) not between 1 and 40 then
        raise exception 'Invalid member name';
    end if;

    select id into target_household_id
    from public.households
    where invite_code = upper(trim(household_invite_code));
    if target_household_id is null then
        raise exception 'Invalid household invite';
    end if;
    if exists (
        select 1
        from public.household_memberships
        where user_id = auth.uid()
          and household_id = target_household_id
    ) then
        raise exception 'This account already belongs to this household';
    end if;

    insert into public.household_memberships (
        user_id, household_id, role, created_at
    ) values (
        auth.uid(), target_household_id, 'member', now_text
    );
    insert into public.members (
        id, household_id, user_id, name, role, created_at
    ) values (
        gen_random_uuid()::text, target_household_id, auth.uid(),
        member_name, '', now_text
    );
    return target_household_id;
end;
$$;
