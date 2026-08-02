alter table public.items
    drop constraint if exists items_remind_member_ids_count_check;

alter table public.items
    add constraint items_remind_member_ids_count_check
    check (cardinality(remind_member_ids) <= 5) not valid;
