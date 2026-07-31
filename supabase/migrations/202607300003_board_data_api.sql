create or replace function public.create_chat_session(
    session_data jsonb,
    first_message text
)
returns void
language plpgsql
set search_path = ''
as $$
declare
    session_row public.chat_sessions;
begin
    session_row := jsonb_populate_record(null::public.chat_sessions, session_data);
    insert into public.chat_sessions select (session_row).*;
    insert into public.chat_messages (session_id, role, content, created_at)
    values (session_row.id, 'user', first_message, session_row.created_at);
end;
$$;

create or replace function public.append_chat_message(
    target_session_id text,
    message_role text,
    message_content text,
    now_text text
)
returns void
language plpgsql
set search_path = ''
as $$
begin
    insert into public.chat_messages (session_id, role, content, created_at)
    values (target_session_id, message_role, message_content, now_text);
    update public.chat_sessions
    set updated_at = now_text
    where id = target_session_id;
end;
$$;

create or replace function public.create_board_items(
    target_household_id text,
    target_timezone text,
    submission_data jsonb,
    item_data jsonb
)
returns text[]
language plpgsql
set search_path = ''
as $$
declare
    submission_row public.submissions;
    item_ids text[];
begin
    update public.households
    set timezone = target_timezone
    where id = target_household_id;

    submission_row := jsonb_populate_record(
        null::public.submissions, submission_data
    );
    insert into public.submissions select (submission_row).*
    on conflict (id) do nothing;

    insert into public.items
    select *
    from jsonb_populate_recordset(null::public.items, item_data)
    on conflict (submission_id, source_index) do nothing;

    select array_agg(id order by source_index)
    into item_ids
    from public.items
    where submission_id = submission_row.id;
    return coalesce(item_ids, array[]::text[]);
end;
$$;

revoke all on function public.create_chat_session(jsonb, text) from public;
revoke all on function public.append_chat_message(text, text, text, text) from public;
revoke all on function public.create_board_items(text, text, jsonb, jsonb) from public;
grant execute on function public.create_chat_session(jsonb, text) to authenticated;
grant execute on function public.append_chat_message(text, text, text, text) to authenticated;
grant execute on function public.create_board_items(text, text, jsonb, jsonb) to authenticated;
