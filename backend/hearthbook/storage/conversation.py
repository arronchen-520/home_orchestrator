from __future__ import annotations

from uuid import uuid4

from .board import BoardDatabase, now_text


def get_conversation(
    database: BoardDatabase, household_id: str, session_id: str, actor_id: str
) -> dict:
    row = database.one(
        database.client.table("conversation_sessions")
        .select("*")
        .eq("id", session_id)
        .eq("household_id", household_id)
        .eq("actor_id", actor_id)
        .limit(1)
        .execute()
    )
    if row is None:
        raise ValueError("Conversation not found")
    session = dict(row)
    session["messages"] = (
        database.client.table("conversation_messages")
        .select("role,content")
        .eq("session_id", session_id)
        .order("id")
        .execute()
        .data
        or []
    )
    return session


def create_conversation(
    database: BoardDatabase,
    household_id: str,
    actor_id: str,
    timezone_name: str,
    text: str,
) -> dict:
    database.ensure_household(household_id)
    database.require_member(household_id, actor_id)
    session_id = str(uuid4())
    now = now_text()
    database.client.rpc(
        "create_conversation",
        {
            "session_data": {
                "id": session_id,
                "household_id": household_id,
                "actor_id": actor_id,
                "status": "active",
                "intent": None,
                "timezone": timezone_name,
                "payload": {},
                "created_at": now,
                "updated_at": now,
            },
            "first_message": text,
        },
    ).execute()
    return get_conversation(database, household_id, session_id, actor_id)


def add_message(
    database: BoardDatabase,
    household_id: str,
    session_id: str,
    actor_id: str,
    role: str,
    content: str,
) -> dict:
    get_conversation(database, household_id, session_id, actor_id)
    database.client.rpc(
        "append_conversation_message",
        {
            "target_session_id": session_id,
            "message_role": role,
            "message_content": content,
            "now_at": now_text(),
        },
    ).execute()
    return get_conversation(database, household_id, session_id, actor_id)


def update_conversation(
    database: BoardDatabase,
    household_id: str,
    session_id: str,
    actor_id: str,
    *,
    status: str,
    intent: str,
    payload: dict,
) -> dict:
    get_conversation(database, household_id, session_id, actor_id)
    database.client.table("conversation_sessions").update(
        {"status": status, "intent": intent, "payload": payload, "updated_at": now_text()}
    ).eq("id", session_id).execute()
    return get_conversation(database, household_id, session_id, actor_id)


def confirm_conversation(
    database: BoardDatabase,
    household_id: str,
    session_id: str,
    actor_id: str,
    remind_member_ids: list[str | None],
    accepted_preparations: list[bool],
) -> dict:
    session = get_conversation(database, household_id, session_id, actor_id)
    if session["status"] != "review" or session["intent"] != "capture":
        raise ValueError("This conversation is not ready to confirm")
    drafts = session["payload"].get("drafts") or []
    if len(remind_member_ids) != len(drafts) or len(accepted_preparations) != len(drafts):
        raise ValueError("Review every draft before confirming")
    for draft, member_id, accepted in zip(
        drafts, remind_member_ids, accepted_preparations, strict=True
    ):
        if member_id is not None:
            database.require_member(household_id, member_id)
        draft["remind_member_id"] = member_id if draft["kind"] != "note" else None
        if not accepted or draft["kind"] == "note":
            draft["preparation"] = None
    original_text = "\n".join(
        message["content"] for message in session["messages"] if message["role"] == "user"
    )
    item_ids = database.create_items(
        household_id, session_id, original_text, session["timezone"], actor_id, drafts
    )
    database.client.table("conversation_sessions").update(
        {"status": "confirmed", "payload": {}, "updated_at": now_text()}
    ).eq("id", session_id).execute()
    return {"action": "created", "item_ids": item_ids}
