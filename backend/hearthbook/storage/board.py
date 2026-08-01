from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4
from supabase import Client

from ..domain.models import ItemDraft
from ..domain.recurrence import base_occurrences, item_date, validate_month_end

HOUSEHOLD_MEMORY_MAX_CHARS = 2000


def now_text() -> str:
    return datetime.now(timezone.utc).isoformat()


class BoardDatabase:
    def __init__(self, client: Client):
        self.client = client

    @staticmethod
    def one(response) -> dict | None:
        rows = response.data or []
        return rows[0] if rows else None

    def ensure_household(self, household_id: str) -> None:
        row = self.one(
            self.client.table("households").select("id").eq("id", household_id).limit(1).execute()
        )
        if row is None:
            raise ValueError("Household setup required")

    def require_member(self, household_id: str, member_id: str | None) -> str:
        row = (
            self.one(
                self.client.table("members")
                .select("id")
                .eq("id", member_id)
                .eq("household_id", household_id)
                .is_("deleted_at", "null")
                .limit(1)
                .execute()
            )
            if member_id
            else None
        )
        if row is None:
            raise ValueError("Choose a valid family member first")
        return member_id

    def require_user_member(self, household_id: str, user_id: str) -> str:
        row = self.one(
            self.client.table("members")
            .select("id")
            .eq("household_id", household_id)
            .eq("user_id", user_id)
            .is_("deleted_at", "null")
            .limit(1)
            .execute()
        )
        if row is None:
            raise ValueError("Member profile setup required")
        return row["id"]

    def get_household_memory(self, household_id: str) -> str:
        row = self.one(
            self.client.table("households").select("memory").eq("id", household_id).limit(1).execute()
        )
        return row["memory"] if row else ""

    def set_household_memory(self, household_id: str, memory: str) -> None:
        memory = memory.strip()[:HOUSEHOLD_MEMORY_MAX_CHARS]
        self.ensure_household(household_id)
        self.client.table("households").update({"memory": memory}).eq("id", household_id).execute()

    def get_household(self, household_id: str) -> dict:
        row = self.one(
            self.client.table("households")
            .select("id,name,invite_code,timezone")
            .eq("id", household_id)
            .limit(1)
            .execute()
        )
        return dict(row) if row else {"id": household_id, "timezone": "UTC"}

    def create_items(
        self,
        household_id: str,
        conversation_id: str,
        text: str,
        timezone_name: str,
        actor_id: str,
        drafts: list[dict],
    ) -> list[str]:
        self.require_member(household_id, actor_id)
        now = now_text()
        rows = []
        for index, raw in enumerate(drafts):
            draft = ItemDraft.model_validate(raw).model_dump(mode="json")
            if draft["remind_member_id"] is not None:
                self.require_member(household_id, draft["remind_member_id"])
            rows.append(
                {
                    "id": str(uuid4()),
                    "household_id": household_id,
                    "conversation_id": conversation_id,
                    "conversation_index": index,
                    "original_text": text,
                    **draft,
                    "all_day": draft["all_day"],
                    "monthly_on_last_day": draft["monthly_on_last_day"],
                    "completed_at": None,
                    "created_by": actor_id,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        response = self.client.rpc(
            "create_board_items",
            {
                "target_household_id": household_id,
                "target_timezone": timezone_name,
                "target_conversation_id": conversation_id,
                "item_data": rows,
            },
        ).execute()
        return response.data or []

    def get_board(self, household_id: str) -> dict:
        members = (
            self.client.table("members")
            .select("id,name,role")
            .eq("household_id", household_id)
            .is_("deleted_at", "null")
            .order("created_at")
            .execute()
            .data
            or []
        )
        rows = (
            self.client.table("items")
            .select(
                "id,conversation_id,kind,title,details,preparation,remind_member_id,completed_at,"
                "start_at,end_at,start_date,due_at,due_date,reminder_at,all_day,recurrence,"
                "monthly_on_last_day,recurrence_until,created_by,created_at,updated_at,original_text"
            )
            .eq("household_id", household_id)
            .order("created_at")
            .execute()
            .data
            or []
        )
        item_ids = [row["id"] for row in rows]
        notes = (
            self.client.table("item_notes")
            .select("id,item_id,member_id,content,created_at")
            .in_("item_id", item_ids)
            .order("created_at")
            .execute()
            .data
            or []
            if item_ids
            else []
        )
        notes_by_item: dict[str, list[dict]] = {}
        for note in notes:
            notes_by_item.setdefault(note["item_id"], []).append(note)
        items = []
        for row in rows:
            item = dict(row)
            item["all_day"] = bool(item["all_day"])
            item["monthly_on_last_day"] = bool(item["monthly_on_last_day"])
            item["notes"] = notes_by_item.get(item["id"], [])
            items.append(item)
        return {"household": self.get_household(household_id), "members": members, "items": items}

    def add_item_note(self, household_id: str, item_id: str, member_id: str, content: str) -> str:
        self.require_member(household_id, member_id)
        content = content.strip()
        if not 1 <= len(content) <= 1000:
            raise ValueError("Follow-up note must be 1 to 1000 characters")
        item = self.one(self.client.table("items").select("id,kind").eq("id", item_id).eq("household_id", household_id).limit(1).execute())
        if item is None or item["kind"] == "note":
            raise ValueError("Follow-up notes belong to events or tasks")
        note_id = str(uuid4())
        self.client.table("item_notes").insert(
            {"id": note_id, "item_id": item_id, "member_id": member_id, "content": content, "created_at": now_text()}
        ).execute()
        return note_id

    def update_item(self, household_id: str, item_id: str, actor_id: str, fields: dict) -> None:
        allowed = {
            "title", "details", "preparation", "remind_member_id", "completed",
            "start_at", "end_at", "start_date", "due_at", "due_date", "reminder_at",
            "all_day", "recurrence", "monthly_on_last_day", "recurrence_until",
        }
        if not fields or set(fields) - allowed:
            raise ValueError("Invalid item fields")
        self.require_member(household_id, actor_id)
        row = self.one(self.client.table("items").select("*").eq("id", item_id).eq("household_id", household_id).limit(1).execute())
        if row is None:
            raise ValueError("Item not found")
        item = dict(row)
        original_pattern = tuple(
            item.get(key)
            for key in ("start_at", "start_date", "recurrence", "monthly_on_last_day")
        )
        completed = fields.pop("completed", None)
        item.update(fields)
        if item["kind"] == "note" and set(fields) - {"title", "details"}:
            raise ValueError("Notes only have a title and details")
        if item.get("remind_member_id") is not None:
            self.require_member(household_id, item["remind_member_id"])
        if completed is not None:
            if item["kind"] != "task":
                raise ValueError("Only tasks can be completed")
            item["completed_at"] = now_text() if completed else None
        if not isinstance(item.get("title"), str) or not 1 <= len(item["title"].strip()) <= 120:
            raise ValueError("Title must be 1 to 120 characters")
        if item["kind"] == "event":
            timezone_name = self.get_household(household_id)["timezone"]
            if set(fields) & {"due_at", "due_date"}:
                raise ValueError("Events do not have task deadlines")
            item["all_day"] = bool(item["all_day"])
            if item["all_day"]:
                if not item.get("start_date"):
                    raise ValueError("An all-day event requires a date")
                item["start_at"] = item["end_at"] = None
            elif not item.get("start_at"):
                raise ValueError("A timed event requires a start")
            elif item.get("end_at") and datetime.fromisoformat(
                item["end_at"]
            ) < datetime.fromisoformat(item["start_at"]):
                raise ValueError("Event end must be after its start")
            if not item.get("recurrence"):
                item["monthly_on_last_day"] = False
                item["recurrence_until"] = None
            elif item.get("recurrence_until") and date.fromisoformat(
                item["recurrence_until"]
            ) < item_date(item, timezone_name):
                raise ValueError("Recurrence end date cannot precede its start")
            if item.get("monthly_on_last_day") and item.get("recurrence") != "monthly":
                raise ValueError("Last-day recurrence must be monthly")
            validate_month_end(item, timezone_name)
        elif item["kind"] == "task":
            if set(fields) & {
                "start_at", "end_at", "start_date", "all_day", "recurrence",
                "monthly_on_last_day", "recurrence_until",
            }:
                raise ValueError("Tasks do not have event schedule fields")
            if item.get("due_at") and item.get("due_date"):
                raise ValueError("A task cannot have both a due date and due time")
        update = {key: item.get(key) for key in allowed - {"completed"}}
        update.update(completed_at=item.get("completed_at"), all_day=bool(item.get("all_day")), updated_at=now_text())
        self.client.table("items").update(update).eq("id", item_id).eq("household_id", household_id).execute()
        current_pattern = tuple(
            item.get(key)
            for key in ("start_at", "start_date", "recurrence", "monthly_on_last_day")
        )
        if original_pattern != current_pattern and (original_pattern[2] or item.get("recurrence")):
            self.client.table("recurrence_exceptions").delete().eq("series_id", item_id).execute()

    def delete_item(self, household_id: str, item_id: str, actor_id: str) -> None:
        self.require_member(household_id, actor_id)
        self.client.table("items").delete().eq("id", item_id).eq("household_id", household_id).execute()

    def _require_occurrence(self, household_id: str, series_id: str, occurrence_date: str) -> dict:
        row = self.one(self.client.table("items").select("*").eq("id", series_id).eq("household_id", household_id).limit(1).execute())
        if row is None or row["kind"] != "event" or not row["recurrence"]:
            raise ValueError("Item is not a recurring event")
        item = dict(row)
        item["all_day"] = bool(item["all_day"])
        item["monthly_on_last_day"] = bool(item["monthly_on_last_day"])
        target = date.fromisoformat(occurrence_date)
        if not base_occurrences(item, target, target, self.get_household(household_id)["timezone"]):
            raise ValueError("Occurrence not found")
        return item

    def update_occurrence(self, household_id: str, series_id: str, occurrence_date: str, actor_id: str, fields: dict) -> None:
        self.require_member(household_id, actor_id)
        allowed = {"title", "details", "preparation", "start_at", "end_at", "start_date"}
        if not fields or set(fields) - allowed:
            raise ValueError("Invalid occurrence fields")
        self._require_occurrence(household_id, series_id, occurrence_date)
        if fields.get("start_at") and fields.get("end_at") and datetime.fromisoformat(
            fields["end_at"]
        ) < datetime.fromisoformat(fields["start_at"]):
            raise ValueError("Event end must be after its start")
        self.client.table("recurrence_exceptions").upsert(
            {
                "series_id": series_id,
                "occurrence_date": occurrence_date,
                "cancelled": False,
                "start_at": fields.get("start_at"),
                "end_at": fields.get("end_at"),
                "start_date": fields.get("start_date"),
                "title": fields.get("title"),
                "details": fields.get("details"),
                "preparation": fields.get("preparation"),
                "updated_at": now_text(),
            },
            on_conflict="series_id,occurrence_date",
        ).execute()

    def cancel_occurrence(self, household_id: str, series_id: str, occurrence_date: str, actor_id: str) -> None:
        self.require_member(household_id, actor_id)
        self._require_occurrence(household_id, series_id, occurrence_date)
        self.client.table("recurrence_exceptions").upsert(
            {
                "series_id": series_id,
                "occurrence_date": occurrence_date,
                "cancelled": True,
                "start_at": None,
                "end_at": None,
                "start_date": None,
                "title": None,
                "details": None,
                "preparation": None,
                "updated_at": now_text(),
            },
            on_conflict="series_id,occurrence_date",
        ).execute()
