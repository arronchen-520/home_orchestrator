drop function if exists public.create_board_items(text, text, jsonb, jsonb);
drop function if exists public.append_conversation_message(text, text, text, text);

alter table public.conversation_sessions
    add column payload jsonb not null default '{}'::jsonb;
update public.conversation_sessions
set payload = payload_json::jsonb;
alter table public.conversation_sessions drop column payload_json;

alter table public.items
    add column conversation_id text references public.conversation_sessions(id) on delete set null,
    add column conversation_index integer,
    add column original_text text not null default '';
update public.items as item
set conversation_id = case
        when exists (
            select 1 from public.conversation_sessions as session
            where session.id = item.submission_id
        ) then item.submission_id
    end,
    conversation_index = item.source_index,
    original_text = coalesce(submission.original_text, '')
from public.submissions as submission
where submission.id = item.submission_id;
alter table public.items
    drop column submission_id,
    drop column source_index;
create unique index items_conversation_index_unique
    on public.items(conversation_id, conversation_index)
    where conversation_id is not null;
drop table public.submissions;

alter table public.households
    drop column city,
    drop column country_code,
    drop column latitude,
    drop column longitude;

alter table public.households
    alter column created_at type timestamptz using created_at::timestamptz;
alter table public.household_memberships
    alter column created_at type timestamptz using created_at::timestamptz;
alter table public.members
    alter column deleted_at type timestamptz using deleted_at::timestamptz,
    alter column created_at type timestamptz using created_at::timestamptz;
alter table public.items
    drop constraint items_all_day_check,
    drop constraint items_monthly_on_last_day_check;
alter table public.items
    alter column completed_at type timestamptz using completed_at::timestamptz,
    alter column start_at type timestamptz using start_at::timestamptz,
    alter column end_at type timestamptz using end_at::timestamptz,
    alter column start_date type date using start_date::date,
    alter column due_at type timestamptz using due_at::timestamptz,
    alter column due_date type date using due_date::date,
    alter column reminder_at type timestamptz using reminder_at::timestamptz,
    alter column recurrence_until type date using recurrence_until::date,
    alter column all_day drop default,
    alter column all_day type boolean using all_day = 1,
    alter column all_day set default false,
    alter column monthly_on_last_day drop default,
    alter column monthly_on_last_day type boolean using monthly_on_last_day = 1,
    alter column monthly_on_last_day set default false,
    alter column created_at type timestamptz using created_at::timestamptz,
    alter column updated_at type timestamptz using updated_at::timestamptz;
alter table public.recurrence_exceptions
    drop constraint recurrence_exceptions_cancelled_check;
alter table public.recurrence_exceptions
    alter column occurrence_date type date using occurrence_date::date,
    alter column cancelled drop default,
    alter column cancelled type boolean using cancelled = 1,
    alter column cancelled set default false,
    alter column start_at type timestamptz using start_at::timestamptz,
    alter column end_at type timestamptz using end_at::timestamptz,
    alter column start_date type date using start_date::date,
    alter column updated_at type timestamptz using updated_at::timestamptz;
alter table public.item_notes
    alter column created_at type timestamptz using created_at::timestamptz;
alter table public.conversation_sessions
    alter column created_at type timestamptz using created_at::timestamptz,
    alter column updated_at type timestamptz using updated_at::timestamptz;
alter table public.conversation_messages
    alter column created_at type timestamptz using created_at::timestamptz;

drop policy items_household_access on public.items;
create policy items_household_access on public.items for all to authenticated
using ((select private.is_household_member(household_id)))
with check (
    (select private.is_household_member(household_id))
    and exists (
        select 1 from public.members
        where id = created_by and members.household_id = items.household_id
    )
    and (
        remind_member_id is null
        or exists (
            select 1 from public.members
            where id = remind_member_id and members.household_id = items.household_id
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

create or replace function public.append_conversation_message(
    target_session_id text,
    message_role text,
    message_content text,
    now_at timestamptz
)
returns void language plpgsql set search_path = '' as $$
begin
    insert into public.conversation_messages(session_id, role, content, created_at)
    values (target_session_id, message_role, message_content, now_at);
    update public.conversation_sessions
    set updated_at = now_at
    where id = target_session_id;
end;
$$;

create or replace function public.create_board_items(
    target_household_id text,
    target_timezone text,
    target_conversation_id text,
    item_data jsonb
)
returns text[] language plpgsql set search_path = '' as $$
declare item_ids text[];
begin
    update public.households
    set timezone = target_timezone
    where id = target_household_id;
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

revoke all on function public.append_conversation_message(text, text, text, timestamptz) from public;
revoke all on function public.create_board_items(text, text, text, jsonb) from public;
grant execute on function public.append_conversation_message(text, text, text, timestamptz) to authenticated;
grant execute on function public.create_board_items(text, text, text, jsonb) to authenticated;
