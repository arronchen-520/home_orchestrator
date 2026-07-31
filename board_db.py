from __future__ import annotations

import json
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from supabase import Client

from models import ItemDraft
from recurrence import base_occurrences, item_date, occurrence_item, validate_month_end

HOUSEHOLD_MEMORY_MAX_CHARS = 2000


def now_text() -> str:
    return datetime.now(timezone.utc).isoformat()


class BoardDatabase:
    def __init__(self, client: Client):
        self.client = client

    def close(self) -> None:
        pass

    @staticmethod
    def _one(response) -> dict | None:
        rows = response.data or []
        return rows[0] if rows else None

    def ensure_household(self, household_id: str) -> None:
        row = self._one(
            self.client.table("households").select("id").eq("id", household_id).limit(1).execute()
        )
        if row is None:
            raise ValueError("Household setup required")

    def require_member(self, household_id: str, member_id: str | None) -> str:
        row = (
            self._one(
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

    def get_household_memory(self, household_id: str) -> str:
        row = self._one(
            self.client.table("households").select("memory").eq("id", household_id).limit(1).execute()
        )
        return row["memory"] if row else ""

    def set_household_memory(self, household_id: str, memory: str) -> None:
        memory = memory.strip()[:HOUSEHOLD_MEMORY_MAX_CHARS]
        self.ensure_household(household_id)
        self.client.table("households").update({"memory": memory}).eq("id", household_id).execute()

    def create_conversation(
        self, household_id: str, actor_id: str, timezone_name: str, text: str
    ) -> dict:
        self.ensure_household(household_id)
        self.require_member(household_id, actor_id)
        session_id = str(uuid4())
        now = now_text()
        self.client.rpc(
            "create_conversation",
            {
                "session_data": {
                    "id": session_id,
                    "household_id": household_id,
                    "actor_id": actor_id,
                    "status": "active",
                    "intent": None,
                    "timezone": timezone_name,
                    "payload_json": "{}",
                    "created_at": now,
                    "updated_at": now,
                },
                "first_message": text,
            },
        ).execute()
        return self.get_conversation(household_id, session_id, actor_id)

    def get_conversation(self, household_id: str, session_id: str, actor_id: str) -> dict:
        row = self._one(
            self.client.table("conversation_sessions")
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
        session["payload"] = json.loads(session.pop("payload_json"))
        session["messages"] = (
            self.client.table("conversation_messages")
            .select("role,content")
            .eq("session_id", session_id)
            .order("id")
            .execute()
            .data
            or []
        )
        return session

    def add_conversation_message(
        self, household_id: str, session_id: str, actor_id: str, role: str, content: str
    ) -> dict:
        self.get_conversation(household_id, session_id, actor_id)
        self.client.rpc(
            "append_conversation_message",
            {
                "target_session_id": session_id,
                "message_role": role,
                "message_content": content,
                "now_text": now_text(),
            },
        ).execute()
        return self.get_conversation(household_id, session_id, actor_id)

    def update_conversation(
        self,
        household_id: str,
        session_id: str,
        actor_id: str,
        *,
        status: str,
        intent: str,
        payload: dict,
    ) -> dict:
        self.get_conversation(household_id, session_id, actor_id)
        self.client.table("conversation_sessions").update(
            {
                "status": status,
                "intent": intent,
                "payload_json": json.dumps(payload, ensure_ascii=False),
                "updated_at": now_text(),
            }
        ).eq("id", session_id).execute()
        return self.get_conversation(household_id, session_id, actor_id)

    def confirm_conversation(
        self,
        household_id: str,
        session_id: str,
        actor_id: str,
        remind_member_ids: list[str | None],
        accepted_preparations: list[bool],
    ) -> dict:
        session = self.get_conversation(household_id, session_id, actor_id)
        if session["status"] != "review" or session["intent"] != "capture":
            raise ValueError("This conversation is not ready to confirm")
        drafts = session["payload"].get("drafts") or []
        if len(remind_member_ids) != len(drafts) or len(accepted_preparations) != len(drafts):
            raise ValueError("Review every draft before confirming")
        for draft, member_id, accepted in zip(drafts, remind_member_ids, accepted_preparations):
            if member_id is not None:
                self.require_member(household_id, member_id)
            draft["remind_member_id"] = member_id if draft["kind"] != "note" else None
            if not accepted or draft["kind"] == "note":
                draft["preparation"] = None
        original_text = "\n".join(
            message["content"] for message in session["messages"] if message["role"] == "user"
        )
        item_ids = self.create_items(
            household_id, session_id, original_text, "conversation", session["timezone"], actor_id, drafts
        )
        self.client.table("conversation_sessions").update(
            {"status": "confirmed", "payload_json": "{}", "updated_at": now_text()}
        ).eq("id", session_id).execute()
        return {"action": "created", "item_ids": item_ids}

    def get_household(self, household_id: str) -> dict:
        row = self._one(
            self.client.table("households")
            .select("id,name,invite_code,timezone,city,country_code")
            .eq("id", household_id)
            .limit(1)
            .execute()
        )
        return dict(row) if row else {"id": household_id, "timezone": "UTC"}

    def get_weather_location(self, household_id: str) -> dict | None:
        row = self._one(
            self.client.table("households")
            .select("city,country_code,latitude,longitude")
            .eq("id", household_id)
            .limit(1)
            .execute()
        )
        return dict(row) if row and row.get("latitude") is not None else None

    def set_household_location(self, household_id: str, location: dict) -> None:
        latitude, longitude = float(location["latitude"]), float(location["longitude"])
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError("Invalid city coordinates")
        self.client.table("households").update(
            {
                "city": location["city"],
                "country_code": location["country_code"],
                "latitude": latitude,
                "longitude": longitude,
            }
        ).eq("id", household_id).execute()

    def add_member(self, household_id: str, name: str, role: str = "") -> str:
        name, role = name.strip(), role.strip()
        if not 1 <= len(name) <= 40 or len(role) > 40:
            raise ValueError("Invalid family member")
        existing = (
            self.client.table("members")
            .select("name")
            .eq("household_id", household_id)
            .is_("deleted_at", "null")
            .execute()
            .data
            or []
        )
        if any(row["name"].casefold() == name.casefold() for row in existing):
            raise ValueError("That family member already exists")
        member_id = str(uuid4())
        self.client.table("members").insert(
            {"id": member_id, "household_id": household_id, "name": name, "role": role, "created_at": now_text()}
        ).execute()
        return member_id

    def delete_member(self, household_id: str, member_id: str) -> None:
        self.require_member(household_id, member_id)
        self.client.table("members").update({"deleted_at": now_text()}).eq("id", member_id).eq(
            "household_id", household_id
        ).execute()

    def create_items(
        self,
        household_id: str,
        submission_id: str,
        text: str,
        source: str,
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
                    "submission_id": submission_id,
                    "source_index": index,
                    **draft,
                    "all_day": int(draft["all_day"]),
                    "monthly_on_last_day": int(draft["monthly_on_last_day"]),
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
                "submission_data": {
                    "id": submission_id,
                    "household_id": household_id,
                    "created_by": actor_id,
                    "source": source,
                    "original_text": text,
                    "timezone": timezone_name,
                    "created_at": now,
                },
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
                "id,submission_id,kind,title,details,preparation,remind_member_id,completed_at,"
                "start_at,end_at,start_date,due_at,due_date,reminder_at,all_day,recurrence,"
                "monthly_on_last_day,recurrence_until,created_by,created_at,updated_at,"
                "submissions(original_text)"
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
            submission = item.pop("submissions", None)
            item["original_text"] = submission.get("original_text") if submission else None
            item["all_day"] = bool(item["all_day"])
            item["monthly_on_last_day"] = bool(item["monthly_on_last_day"])
            item["notes"] = notes_by_item.get(item["id"], [])
            items.append(item)
        return {"household": self.get_household(household_id), "members": members, "items": items}

    def get_calendar(self, household_id: str, start_date: date, end_date: date) -> dict:
        if end_date < start_date or (end_date - start_date).days > 370:
            raise ValueError("Invalid calendar range")
        board = self.get_board(household_id)
        timezone_name = board["household"]["timezone"]
        series_ids = [item["id"] for item in board["items"] if item.get("recurrence")]
        exceptions = (
            self.client.table("recurrence_exceptions").select("*").in_("series_id", series_ids).execute().data
            or []
            if series_ids
            else []
        )
        by_series: dict[str, dict[str, dict]] = {}
        for exception in exceptions:
            exception["cancelled"] = bool(exception["cancelled"])
            by_series.setdefault(exception["series_id"], {})[exception["occurrence_date"]] = exception
        result = []
        for item in board["items"]:
            if item["kind"] == "note":
                continue
            if not item.get("recurrence"):
                target = item_date(item, timezone_name)
                if target and start_date <= target <= end_date:
                    result.append({**item, "series_id": None, "occurrence_date": target.isoformat(), "is_occurrence": False})
                continue
            exceptions_for_series = by_series.get(item["id"], {})
            seen = set()
            for occurrence in base_occurrences(item, start_date, end_date, timezone_name):
                key = occurrence.date().isoformat()
                seen.add(key)
                expanded = occurrence_item(item, occurrence, exceptions_for_series.get(key))
                target = item_date(expanded, timezone_name) if expanded else None
                if target and start_date <= target <= end_date:
                    result.append(expanded)
            for key, exception in exceptions_for_series.items():
                if key in seen or exception["cancelled"]:
                    continue
                original = date.fromisoformat(key)
                occurrences = base_occurrences(item, original, original, timezone_name)
                if occurrences:
                    expanded = occurrence_item(item, occurrences[0], exception)
                    target = item_date(expanded, timezone_name) if expanded else None
                    if target and start_date <= target <= end_date:
                        result.append(expanded)
        result.sort(key=lambda item: (item_date(item, timezone_name) or date.max, item.get("start_at") or "", item["title"]))
        return {"items": result}

    def get_today(self, household_id: str, target_date: date, timezone_name: str) -> dict:
        zone = ZoneInfo(timezone_name)
        calendar = self.get_calendar(household_id, target_date, target_date)["items"]
        board = self.get_board(household_id)
        chosen: dict[str, dict] = {}

        def add(item: dict, reason: str) -> None:
            key = (
                f'{item["series_id"]}:{item.get("occurrence_date") or ""}'
                if item.get("series_id")
                else item["id"]
            )
            entry = chosen.setdefault(key, {**item, "today_reasons": []})
            if reason not in entry["today_reasons"]:
                entry["today_reasons"].append(reason)

        for item in calendar:
            add(item, "happens_today" if item["kind"] == "event" else "due_today")
        # ponytail: expand one year; family boards are small and calendar already owns recurrence correctness.
        for item in self.get_calendar(household_id, target_date, target_date + timedelta(days=370))["items"]:
            if item.get("reminder_at") and datetime.fromisoformat(item["reminder_at"]).astimezone(zone).date() == target_date:
                add(item, "reminder_today")
        for item in board["items"]:
            if item["kind"] == "note" or item.get("completed_at"):
                continue
            if item.get("reminder_at") and datetime.fromisoformat(item["reminder_at"]).astimezone(zone).date() == target_date:
                add(item, "reminder_today")
            if item["kind"] == "task":
                due = item_date(item, timezone_name)
                if due and due < target_date:
                    add(item, "overdue")
        priority = {"overdue": 0, "reminder_today": 1, "happens_today": 2, "due_today": 2}
        items = list(chosen.values())
        items.sort(key=lambda item: (min(priority[r] for r in item["today_reasons"]), item.get("start_at") or item.get("due_at") or "", item["title"]))
        return {"date": target_date.isoformat(), "items": items}

    def find_draft_conflicts(self, household_id: str, drafts: list[dict], timezone_name: str) -> list[dict]:
        board = self.get_board(household_id)
        conflicts = []
        for index, draft in enumerate(drafts):
            target = item_date(draft, timezone_name)
            for item in board["items"]:
                if item["kind"] == draft["kind"] and item["title"].casefold() == draft["title"].casefold() and item_date(item, timezone_name) == target:
                    conflicts.append({"kind": "duplicate", "draft_index": index, "existing_title": item["title"], "date": target.isoformat() if target else None})
        return conflicts

    def add_item_note(self, household_id: str, item_id: str, member_id: str, content: str) -> str:
        self.require_member(household_id, member_id)
        content = content.strip()
        if not 1 <= len(content) <= 1000:
            raise ValueError("Follow-up note must be 1 to 1000 characters")
        item = self._one(self.client.table("items").select("id,kind").eq("id", item_id).eq("household_id", household_id).limit(1).execute())
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
            "all_day", "recurrence_until",
        }
        if not fields or set(fields) - allowed:
            raise ValueError("Invalid item fields")
        self.require_member(household_id, actor_id)
        row = self._one(self.client.table("items").select("*").eq("id", item_id).eq("household_id", household_id).limit(1).execute())
        if row is None:
            raise ValueError("Item not found")
        item = dict(row)
        original_start = (item.get("start_at"), item.get("start_date"))
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
            if set(fields) & {"due_at", "due_date"}:
                raise ValueError("Events do not have task deadlines")
            item["all_day"] = bool(item["all_day"])
            if item["all_day"]:
                if not item.get("start_date"):
                    raise ValueError("An all-day event requires a date")
                item["start_at"] = item["end_at"] = None
            elif not item.get("start_at"):
                raise ValueError("A timed event requires a start")
            validate_month_end(item, self.get_household(household_id)["timezone"])
        elif item["kind"] == "task":
            if set(fields) & {"start_at", "end_at", "start_date", "all_day", "recurrence_until"}:
                raise ValueError("Tasks do not have event schedule fields")
            if item.get("due_at") and item.get("due_date"):
                raise ValueError("A task cannot have both a due date and due time")
        update = {key: item.get(key) for key in allowed - {"completed"}}
        update.update(completed_at=item.get("completed_at"), all_day=int(bool(item.get("all_day"))), updated_at=now_text())
        self.client.table("items").update(update).eq("id", item_id).eq("household_id", household_id).execute()
        if item.get("recurrence") and original_start != (item.get("start_at"), item.get("start_date")):
            self.client.table("recurrence_exceptions").delete().eq("series_id", item_id).execute()

    def delete_item(self, household_id: str, item_id: str, actor_id: str) -> None:
        self.require_member(household_id, actor_id)
        self.client.table("items").delete().eq("id", item_id).eq("household_id", household_id).execute()

    def _require_occurrence(self, household_id: str, series_id: str, occurrence_date: str) -> dict:
        row = self._one(self.client.table("items").select("*").eq("id", series_id).eq("household_id", household_id).limit(1).execute())
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
        self.client.table("recurrence_exceptions").upsert(
            {
                "series_id": series_id,
                "occurrence_date": occurrence_date,
                "cancelled": 0,
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
                "cancelled": 1,
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

    def query_assistant(self, household_id: str, timezone_name: str, sql: str) -> list[dict]:
        statement = sql.strip().removesuffix(";").strip()
        if not re.match(r"^(SELECT|WITH)\b", statement, re.IGNORECASE) or ";" in statement:
            raise ValueError("Assistant queries must be one read-only SELECT")
        board = self.get_board(household_id)
        names = {member["id"]: member["name"] for member in board["members"]}
        columns = [
            "id", "kind", "title", "details", "preparation", "remind_member_id",
            "remind_member_name", "completed_at", "start_at", "end_at", "start_date",
            "due_at", "due_date", "reminder_at", "recurrence", "recurrence_until",
            "created_at", "updated_at", "original_text",
        ]

        def values(item: dict) -> list:
            projected = {**item, "remind_member_name": names.get(item.get("remind_member_id"))}
            return [projected.get(column) for column in columns]

        today = datetime.now(ZoneInfo(timezone_name)).date()
        occurrences = self.get_calendar(household_id, today - timedelta(days=365), today)["items"]
        occurrences += self.get_calendar(household_id, today + timedelta(days=1), today + timedelta(days=370))["items"]
        database = sqlite3.connect(":memory:")
        database.row_factory = sqlite3.Row
        schema = ", ".join(f"{column} TEXT" for column in columns)
        placeholders = ", ".join("?" for _ in columns)
        database.execute("CREATE TABLE members (id TEXT, name TEXT, role TEXT)")
        database.execute(f"CREATE TABLE items ({schema})")
        database.execute(f"CREATE TABLE occurrences ({schema}, series_id TEXT, occurrence_date TEXT, is_occurrence INTEGER)")
        database.execute("CREATE TABLE item_notes (id TEXT, item_id TEXT, member_id TEXT, member_name TEXT, content TEXT, created_at TEXT)")
        database.executemany("INSERT INTO members VALUES (?, ?, ?)", [(m["id"], m["name"], m["role"]) for m in board["members"]])
        database.executemany(f"INSERT INTO items VALUES ({placeholders})", [values(item) for item in board["items"]])
        database.executemany(
            f"INSERT INTO occurrences VALUES ({placeholders}, ?, ?, ?)",
            [values(item) + [item.get("series_id"), item.get("occurrence_date"), int(item.get("is_occurrence", False))] for item in occurrences],
        )
        database.executemany(
            "INSERT INTO item_notes VALUES (?, ?, ?, ?, ?, ?)",
            [
                (note["id"], item["id"], note["member_id"], names.get(note["member_id"]), note["content"], note["created_at"])
                for item in board["items"] for note in item["notes"]
            ],
        )
        allowed_tables = {"items", "members", "occurrences", "item_notes"}
        allowed_functions = {"abs", "avg", "coalesce", "count", "date", "datetime", "group_concat", "julianday", "length", "lower", "max", "min", "round", "strftime", "sum", "total", "trim", "upper"}

        def authorize(action, first, second, _db, _trigger):
            if action in {sqlite3.SQLITE_SELECT, getattr(sqlite3, "SQLITE_RECURSIVE", -1)}:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and first in allowed_tables:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_FUNCTION and (second or first or "").lower() in allowed_functions:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        database.set_authorizer(authorize)
        try:
            rows = database.execute(f"SELECT * FROM ({statement}) LIMIT 100").fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            raise ValueError(f"Assistant query failed: {exc}") from exc
        finally:
            database.close()
