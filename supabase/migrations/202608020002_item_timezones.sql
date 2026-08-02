alter table public.items add column schedule_timezone text;

update public.items as item
set schedule_timezone = household.timezone
from public.households as household
where household.id = item.household_id
  and item.kind <> 'note';

update public.items set schedule_timezone = null where kind = 'note';

alter table public.items add constraint items_schedule_timezone_check check (
    (kind = 'note' and schedule_timezone is null)
    or (kind <> 'note' and schedule_timezone is not null)
);

drop function public.create_board_items(text, text, text, jsonb);

alter table public.households drop column timezone;

create function public.create_board_items(
    target_household_id text,
    target_conversation_id text,
    item_data jsonb
)
returns text[] language plpgsql set search_path = '' as $$
declare item_ids text[];
begin
    insert into public.items
    select * from jsonb_populate_recordset(null::public.items, item_data)
    on conflict (conversation_id, conversation_index) where conversation_id is not null
    do nothing;
    select array_agg(id order by conversation_index)
    into item_ids
    from public.items
    where conversation_id = target_conversation_id;
    return coalesce(item_ids, array[]::text[]);
end;
$$;

revoke all on function public.create_board_items(text, text, jsonb) from public;
grant execute on function public.create_board_items(text, text, jsonb) to authenticated;
