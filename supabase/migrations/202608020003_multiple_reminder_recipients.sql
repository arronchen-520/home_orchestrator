alter table public.items
    add column remind_member_ids text[] not null default '{}'::text[];

update public.items
set remind_member_ids = case
    when remind_member_id is null then '{}'::text[]
    else array[remind_member_id]
end;

alter table public.items
    add constraint items_remind_member_ids_count_check
        check (cardinality(remind_member_ids) <= 20),
    add constraint items_remind_member_ids_no_nulls_check
        check (array_position(remind_member_ids, null) is null);

drop policy items_household_access on public.items;
create policy items_household_access on public.items for all to authenticated
using ((select private.is_household_member(household_id)))
with check (
    (select private.is_household_member(household_id))
    and exists (
        select 1 from public.members
        where id = created_by and members.household_id = items.household_id
    )
    and not exists (
        select 1
        from unnest(items.remind_member_ids) as recipient(member_id)
        where not exists (
            select 1 from public.members
            where members.id = recipient.member_id
              and members.household_id = items.household_id
        )
    )
    and (
        conversation_id is null
        or exists (
            select 1 from public.conversation_sessions
            where id = conversation_id
              and conversation_sessions.household_id = items.household_id
        )
    )
);

alter table public.items drop column remind_member_id;
