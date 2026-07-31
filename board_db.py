from __future__ import annotations

import json
import re
import sqlite3
from calendar import monthrange
from datetime import date, datetime, time, timedelta, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from dateutil.rrule import DAILY, MONTHLY, WEEKLY, rrule
from supabase import Client

HOUSEHOLD_MEMORY_MAX_CHARS = 2000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _item_date(item: dict, timezone_name: str) -> date | None:
    value = item.get("start_date") if item["kind"] == "event" else item.get("due_date")
    if value:
        return date.fromisoformat(value)
    value = item.get("start_at") if item["kind"] == "event" else item.get("due_at")
    return (
        datetime.fromisoformat(value).astimezone(ZoneInfo(timezone_name)).date()
        if value
        else None
    )


def _base_occurrences(
    item: dict, start_date: date, end_date: date, timezone_name: str
) -> list[datetime]:
    first_date = _item_date(item, timezone_name)
    if first_date is None or item["kind"] != "event":
        return []
    zone = ZoneInfo(timezone_name)
    if item["all_day"]:
        first = datetime.combine(first_date, time.min, zone)
    else:
        first = datetime.fromisoformat(item["start_at"]).astimezone(zone)
    until = min(
        end_date,
        date.fromisoformat(item["recurrence_until"])
        if item.get("recurrence_until")
        else end_date,
    )
    if until < start_date:
        return []
    kwargs = {
        "freq": {
            "daily": DAILY,
            "weekly": WEEKLY,
            "monthly": MONTHLY,
        }[item["recurrence"]],
        "dtstart": first,
        "until": datetime.combine(until, time.max, zone),
    }
    if item["recurrence"] == "monthly":
        kwargs["bymonthday"] = -1 if item["monthly_on_last_day"] else first.day
    rule = rrule(**kwargs)
    return rule.between(
        datetime.combine(start_date, time.min, zone),
        datetime.combine(until, time.max, zone),
        inc=True,
    )


def _occurrence_item(
    item: dict, occurrence: datetime, exception: dict | None = None
) -> dict | None:
    occurrence_date = occurrence.date().isoformat()
    if exception and exception["cancelled"]:
        return None
    result = {
        **item,
        "series_id": item["id"],
        "occurrence_date": occurrence_date,
        "is_occurrence": bool(item.get("recurrence")),
    }
    if item["all_day"]:
        result["start_date"] = occurrence_date
    else:
        duration = (
            datetime.fromisoformat(item["end_at"]) - datetime.fromisoformat(item["start_at"])
            if item.get("end_at")
            else None
        )
        result["start_at"] = occurrence.isoformat()
        result["end_at"] = (occurrence + duration).isoformat() if duration else None
    if exception:
        for field in ("title", "details", "preparation"):
            if exception[field] is not None:
                result[field] = exception[field]
        if exception["start_date"] is not None:
            result.update(
                all_day=True,
                start_date=exception["start_date"],
                start_at=None,
                end_at=None,
            )
        elif exception["start_at"] is not None:
            result.update(
                all_day=False,
                start_date=None,
                start_at=exception["start_at"],
                end_at=exception["end_at"],
            )
    if item.get("reminder_at"):
        base_start = (
            datetime.combine(date.fromisoformat(item["start_date"]), time.min, occurrence.tzinfo)
            if item["all_day"]
            else datetime.fromisoformat(item["start_at"]).astimezone(occurrence.tzinfo)
        )
        effective_start = (
            datetime.combine(date.fromisoformat(result["start_date"]), time.min, occurrence.tzinfo)
            if result["all_day"]
            else datetime.fromisoformat(result["start_at"]).astimezone(occurrence.tzinfo)
        )
        reminder_offset = (
            datetime.fromisoformat(item["reminder_at"]).astimezone(occurrence.tzinfo)
            - base_start
        )
        result["reminder_at"] = (effective_start + reminder_offset).isoformat()
    return result


class BoardDatabase:
    def __init__(self, client: Client):
        self.client = client

    def close(self) -> None:
        pass

    @staticmethod
    def _one(response) -> dict | None:
        rows = response.data or []
        return rows[0] if rows else None

    def ensure_household(self, household_id: str, timezone_name: str = "UTC") -> None:
        row = self._one(
            self.client.table("households")
            .select("id")
            .eq("id", household_id)
            .limit(1)
            .execute()
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
            self.client.table("households")
            .select("memory")
            .eq("id", household_id)
            .limit(1)
            .execute()
        )
        return row["memory"] if row else ""

    def set_household_memory(self, household_id: str, memory: str) -> None:
        memory = memory.strip()
        if len(memory) > HOUSEHOLD_MEMORY_MAX_CHARS:
            shortened = memory[:HOUSEHOLD_MEMORY_MAX_CHARS]
            memory = shortened.rsplit("\n", 1)[0].strip() or shortened.rstrip()
        self.ensure_household(household_id)
        self.client.table("households").update({"memory": memory}).eq(
            "id", household_id
        ).execute()

    def create_intake_session(
        self,
        household_id: str,
        actor_id: str,
        owner_id: str | None,
        source: str,
        timezone_name: str,
        text: str,
    ) -> dict:
        session_id = str(uuid4())
        now = _now()
        self.ensure_household(household_id, timezone_name)
        self.require_member(household_id, actor_id)
        if owner_id is not None:
            self.require_member(household_id, owner_id)
        self.client.rpc(
            "create_chat_session",
            {
                "session_data": {
                    "id": session_id,
                    "household_id": household_id,
                    "actor_id": actor_id,
                    "kind": "intake",
                    "status": "clarifying",
                    "owner_id": owner_id,
                    "source": source,
                    "timezone": timezone_name,
                    "created_at": now,
                    "updated_at": now,
                },
                "first_message": text,
            },
        ).execute()
        return self.get_intake_session(household_id, session_id, actor_id)

    def get_intake_session(
        self, household_id: str, session_id: str, actor_id: str
    ) -> dict:
        row = self._one(
            self.client.table("chat_sessions")
            .select("*")
            .eq("id", session_id)
            .eq("household_id", household_id)
            .eq("actor_id", actor_id)
            .eq("kind", "intake")
            .limit(1)
            .execute()
        )
        if row is None:
            raise ValueError("Intake conversation not found")
        session = dict(row)
        session["payload"] = json.loads(session.pop("payload_json"))
        session["messages"] = (
            self.client.table("chat_messages")
            .select("role,content")
            .eq("session_id", session_id)
            .order("id")
            .execute()
            .data
            or []
        )
        return session

    def add_intake_message(
        self,
        household_id: str,
        session_id: str,
        actor_id: str,
        role: str,
        content: str,
    ) -> dict:
        session = self.get_intake_session(household_id, session_id, actor_id)
        if session["status"] != "clarifying":
            raise ValueError("Confirm or start over before sending another message")
        self.client.rpc(
            "append_chat_message",
            {
                "target_session_id": session_id,
                "message_role": role,
                "message_content": content,
                "now_text": _now(),
            },
        ).execute()
        return self.get_intake_session(household_id, session_id, actor_id)

    def create_assistant_session(
        self,
        household_id: str,
        actor_id: str,
        timezone_name: str,
        text: str,
    ) -> dict:
        session_id = str(uuid4())
        now = _now()
        self.ensure_household(household_id, timezone_name)
        self.require_member(household_id, actor_id)
        self.client.rpc(
            "create_chat_session",
            {
                "session_data": {
                    "id": session_id,
                    "household_id": household_id,
                    "actor_id": actor_id,
                    "kind": "assistant",
                    "status": "active",
                    "source": "text",
                    "timezone": timezone_name,
                    "created_at": now,
                    "updated_at": now,
                },
                "first_message": text,
            },
        ).execute()
        return self.get_assistant_session(household_id, session_id, actor_id)

    def get_assistant_session(
        self, household_id: str, session_id: str, actor_id: str
    ) -> dict:
        row = self._one(
            self.client.table("chat_sessions")
            .select("*")
            .eq("id", session_id)
            .eq("household_id", household_id)
            .eq("actor_id", actor_id)
            .eq("kind", "assistant")
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if row is None:
            raise ValueError("Assistant conversation not found")
        session = dict(row)
        session["payload"] = json.loads(session.pop("payload_json"))
        session["messages"] = (
            self.client.table("chat_messages")
            .select("role,content")
            .eq("session_id", session_id)
            .order("id")
            .execute()
            .data
            or []
        )
        return session

    def add_assistant_message(
        self,
        household_id: str,
        session_id: str,
        actor_id: str,
        role: str,
        content: str,
    ) -> dict:
        self.get_assistant_session(household_id, session_id, actor_id)
        self.client.rpc(
            "append_chat_message",
            {
                "target_session_id": session_id,
                "message_role": role,
                "message_content": content,
                "now_text": _now(),
            },
        ).execute()
        return self.get_assistant_session(household_id, session_id, actor_id)

    def update_intake_session(
        self,
        household_id: str,
        session_id: str,
        actor_id: str,
        status: str,
        clarification_count: int,
        payload: dict,
    ) -> dict:
        self.get_intake_session(household_id, session_id, actor_id)
        self.client.table("chat_sessions").update(
            {
                "status": status,
                "clarification_count": clarification_count,
                "payload_json": json.dumps(payload, ensure_ascii=False),
                "updated_at": _now(),
            }
        ).eq("id", session_id).execute()
        return self.get_intake_session(household_id, session_id, actor_id)

    def confirm_intake_session(
        self, household_id: str, session_id: str, actor_id: str
    ) -> dict:
        session = self.get_intake_session(household_id, session_id, actor_id)
        if session["status"] != "review":
            raise ValueError("This intake conversation is not ready to confirm")
        payload = session["payload"]
        drafts = payload.get("drafts") or []
        if not drafts:
            raise ValueError("This intake conversation has no items to create")
        user_text = "\n".join(
            message["content"]
            for message in session["messages"]
            if message["role"] == "user"
        )
        item_ids = self.create_items(
            household_id=household_id,
            submission_id=session_id,
            text=user_text,
            source=session["source"],
            timezone_name=session["timezone"],
            actor_id=actor_id,
            owner_id=None,
            drafts=drafts,
        )
        self.client.table("chat_sessions").update(
            {"status": "confirmed", "updated_at": _now()}
        ).eq("id", session_id).execute()
        return {"action": "created", "item_id": item_ids[0], "item_ids": item_ids}

    def get_household(self, household_id: str) -> dict:
        row = self._one(
            self.client.table("households")
            .select("id,name,invite_code,timezone,city,country_code")
            .eq("id", household_id)
            .limit(1)
            .execute()
        )
        return dict(row) if row else {
            "id": household_id,
            "name": "",
            "invite_code": "",
            "timezone": "UTC",
            "city": None,
            "country_code": None,
        }

    def get_weather_location(self, household_id: str) -> dict | None:
        row = self._one(
            self.client.table("households")
            .select("city,country_code,latitude,longitude")
            .eq("id", household_id)
            .limit(1)
            .execute()
        )
        if row is None or row["latitude"] is None or row["longitude"] is None:
            return None
        return dict(row)

    def set_household_location(self, household_id: str, location: dict) -> None:
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError("Invalid city coordinates")
        self.ensure_household(household_id)
        self.client.table("households").update(
            {
                "city": location["city"],
                "country_code": location["country_code"],
                "latitude": latitude,
                "longitude": longitude,
            }
        ).eq("id", household_id).execute()

    def add_member(self, household_id: str, name: str, role: str = "") -> str:
        name = name.strip()
        role = role.strip()
        if not name or len(name) > 40:
            raise ValueError("Member name must be 1 to 40 characters")
        if len(role) > 40:
            raise ValueError("Member role must be at most 40 characters")
        self.ensure_household(household_id)
        names = (
            self.client.table("members")
            .select("name")
            .eq("household_id", household_id)
            .is_("deleted_at", "null")
            .execute()
            .data
            or []
        )
        if any(row["name"].casefold() == name.casefold() for row in names):
            raise ValueError("That family member already exists")
        member_id = str(uuid4())
        self.client.table("members").insert(
            {
                "id": member_id,
                "household_id": household_id,
                "name": name,
                "role": role,
                "created_at": _now(),
            }
        ).execute()
        return member_id

    def delete_member(self, household_id: str, member_id: str) -> None:
        self.require_member(household_id, member_id)
        self.client.table("members").update({"deleted_at": _now()}).eq(
            "id", member_id
        ).eq("household_id", household_id).execute()

    def create_items(
        self,
        household_id: str,
        submission_id: str,
        text: str,
        source: str,
        timezone_name: str,
        actor_id: str,
        owner_id: str | None,
        drafts: list[dict],
    ) -> list[str]:
        self.ensure_household(household_id, timezone_name)
        self.require_member(household_id, actor_id)
        if owner_id is not None:
            self.require_member(household_id, owner_id)

        now = _now()
        items = []
        for index, draft in enumerate(drafts):
            actionable = draft["kind"] != "note"
            item_owner = (
                draft.get("owner_id")
                if actionable and draft.get("owner_id") is not None
                else owner_id if actionable else None
            )
            if item_owner is not None:
                self.require_member(household_id, item_owner)
            assignment_state = (
                "accepted"
                if draft["kind"] == "task" and item_owner == actor_id
                else "pending"
                if draft["kind"] == "task" and item_owner
                else None
            )
            status = (
                "claimed"
                if actionable and item_owner and assignment_state != "pending"
                else "unclaimed"
                if actionable
                else None
            )
            items.append(
                {
                    "id": str(uuid4()),
                    "household_id": household_id,
                    "submission_id": submission_id,
                    "source_index": index,
                    "kind": draft["kind"],
                    "title": draft["title"],
                    "details": draft.get("details", ""),
                    "preparation": draft.get("preparation") if actionable else None,
                    "owner_id": item_owner,
                    "assignment_state": assignment_state,
                    "status": status,
                    "start_at": draft.get("start_at"),
                    "end_at": draft.get("end_at"),
                    "start_date": draft.get("start_date"),
                    "due_at": draft.get("due_at"),
                    "due_date": draft.get("due_date"),
                    "reminder_at": draft.get("reminder_at"),
                    "all_day": int(draft.get("all_day", False)),
                    "recurrence": draft.get("recurrence"),
                    "monthly_on_last_day": int(
                        draft.get("monthly_on_last_day", False)
                    ),
                    "recurrence_until": draft.get("recurrence_until"),
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
                "item_data": items,
            },
        ).execute()
        return response.data or []

    def find_draft_conflicts(
        self, household_id: str, drafts: list[dict], timezone_name: str
    ) -> list[dict]:
        board = self.get_board(household_id)
        conflicts = []
        seen = set()
        for index, draft in enumerate(drafts):
            draft_date = _item_date(draft, timezone_name)
            for item in board["items"]:
                if (
                    item["kind"] == draft["kind"]
                    and item["title"].strip().casefold()
                    == draft["title"].strip().casefold()
                    and _item_date(item, timezone_name) == draft_date
                ):
                    key = ("duplicate", index, item["id"], draft_date)
                    if key not in seen:
                        seen.add(key)
                        conflicts.append(
                            {
                                "kind": "duplicate",
                                "draft_index": index,
                                "existing_id": item["id"],
                                "existing_title": item["title"],
                                "date": draft_date.isoformat() if draft_date else None,
                            }
                        )

            if draft["kind"] != "event" or draft_date is None:
                continue
            horizon = min(
                date.fromisoformat(draft["recurrence_until"])
                if draft.get("recurrence_until")
                else draft_date + timedelta(days=90),
                draft_date + timedelta(days=90),
            )
            occurrences = (
                _base_occurrences(draft, draft_date, horizon, timezone_name)
                if draft.get("recurrence")
                else [
                    datetime.combine(draft_date, time.min, ZoneInfo(timezone_name))
                    if draft.get("all_day")
                    else datetime.fromisoformat(draft["start_at"])
                ]
            )
            existing = self.get_calendar(
                household_id, draft_date, max(draft_date, horizon)
            )["items"]
            duration = (
                datetime.fromisoformat(draft["end_at"])
                - datetime.fromisoformat(draft["start_at"])
                if draft.get("start_at") and draft.get("end_at")
                else None
            )
            for occurrence in occurrences:
                candidate_end = occurrence + duration if duration else None
                for item in existing:
                    if (
                        item["kind"] != "event"
                        or _item_date(item, timezone_name) != occurrence.date()
                    ):
                        continue
                    overlap = draft.get("all_day") or item.get("all_day")
                    if not overlap:
                        existing_start = datetime.fromisoformat(item["start_at"])
                        existing_end = (
                            datetime.fromisoformat(item["end_at"])
                            if item.get("end_at")
                            else None
                        )
                        overlap = (
                            occurrence == existing_start
                            if candidate_end is None or existing_end is None
                            else occurrence < existing_end
                            and existing_start < candidate_end
                        )
                    key = ("time", index, item["id"], occurrence.date())
                    if overlap and key not in seen:
                        seen.add(key)
                        conflicts.append(
                            {
                                "kind": "time",
                                "draft_index": index,
                                "existing_id": item["id"],
                                "existing_title": item["title"],
                                "date": occurrence.date().isoformat(),
                            }
                        )
        return conflicts

    def query_assistant(
        self, household_id: str, timezone_name: str, sql: str
    ) -> list[dict]:
        # ponytail: copy a family-sized board; use scoped SQL views if boards outgrow memory.
        statement = sql.strip().removesuffix(";").strip()
        if (
            not re.match(r"^(SELECT|WITH)\b", statement, re.IGNORECASE)
            or ";" in statement
        ):
            raise ValueError("Assistant queries must be one read-only SELECT")

        board = self.get_board(household_id)
        member_names = {
            member["id"]: member["name"] for member in board["members"]
        }
        item_columns = [
            "id",
            "kind",
            "title",
            "details",
            "preparation",
            "owner_id",
            "owner_name",
            "assignment_state",
            "status",
            "start_at",
            "end_at",
            "start_date",
            "due_at",
            "due_date",
            "reminder_at",
            "recurrence",
            "monthly_on_last_day",
            "recurrence_until",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
            "original_text",
        ]

        zone = ZoneInfo(timezone_name)
        today = datetime.now(zone).date()
        occurrences = self.get_calendar(
            household_id, today - timedelta(days=365), today
        )["items"] + self.get_calendar(
            household_id, today + timedelta(days=1), today + timedelta(days=370)
        )["items"]

        def values(item: dict) -> list:
            projected = {
                **item,
                "owner_name": member_names.get(item.get("owner_id")),
                "created_by_name": member_names.get(item.get("created_by")),
            }
            return [projected.get(column) for column in item_columns]

        database = sqlite3.connect(":memory:")
        database.row_factory = sqlite3.Row
        columns_sql = ", ".join(f"{column} TEXT" for column in item_columns)
        placeholders = ", ".join("?" for _ in item_columns)
        database.execute(
            "CREATE TABLE members (id TEXT, name TEXT, role TEXT)"
        )
        database.execute(f"CREATE TABLE items ({columns_sql})")
        database.execute(
            f"""
            CREATE TABLE occurrences (
                {columns_sql},
                series_id TEXT,
                occurrence_date TEXT,
                is_occurrence INTEGER
            )
            """
        )
        database.executemany(
            "INSERT INTO members VALUES (?, ?, ?)",
            [
                (member["id"], member["name"], member["role"])
                for member in board["members"]
            ],
        )
        database.executemany(
            f"INSERT INTO items VALUES ({placeholders})",
            [values(item) for item in board["items"]],
        )
        database.executemany(
            f"""
            INSERT INTO occurrences VALUES (
                {placeholders}, ?, ?, ?
            )
            """,
            [
                values(item)
                + [
                    item.get("series_id"),
                    item.get("occurrence_date"),
                    int(item.get("is_occurrence", False)),
                ]
                for item in occurrences
            ],
        )

        allowed_tables = {"items", "members", "occurrences"}
        allowed_functions = {
            "abs",
            "avg",
            "coalesce",
            "count",
            "current_date",
            "current_time",
            "current_timestamp",
            "date",
            "datetime",
            "group_concat",
            "julianday",
            "length",
            "like",
            "lower",
            "max",
            "min",
            "round",
            "strftime",
            "sum",
            "total",
            "trim",
            "upper",
        }

        def authorize(action, first, second, _database, _trigger):
            if action in {
                sqlite3.SQLITE_SELECT,
                getattr(sqlite3, "SQLITE_RECURSIVE", -1),
            }:
                return sqlite3.SQLITE_OK
            if action == sqlite3.SQLITE_READ and first in allowed_tables:
                return sqlite3.SQLITE_OK
            if (
                action == sqlite3.SQLITE_FUNCTION
                and (second or first or "").lower() in allowed_functions
            ):
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        steps = 0

        def stop_long_query():
            nonlocal steps
            steps += 1
            return int(steps > 1000)

        database.set_authorizer(authorize)
        database.set_progress_handler(stop_long_query, 1000)
        try:
            rows = database.execute(
                f"SELECT * FROM ({statement}) LIMIT 100"
            ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as exc:
            raise ValueError(f"Assistant query failed: {exc}") from exc
        finally:
            database.close()

    def update_item(
        self,
        household_id: str,
        item_id: str,
        actor_id: str,
        fields: dict,
    ) -> None:
        allowed = {
            "title",
            "details",
            "preparation",
            "owner_id",
            "status",
            "start_at",
            "end_at",
            "start_date",
            "due_at",
            "due_date",
            "reminder_at",
            "all_day",
            "recurrence_until",
        }
        if not fields or set(fields) - allowed:
            raise ValueError("Invalid item fields")

        self.require_member(household_id, actor_id)
        row = self._one(
            self.client.table("items")
            .select("*")
            .eq("id", item_id)
            .eq("household_id", household_id)
            .limit(1)
            .execute()
        )
        if row is None:
            raise ValueError("Item not found")
        item = dict(row)
        item["timezone"] = self.get_household(household_id)["timezone"]
        original_start = (item["start_at"], item["start_date"])
        item.update(fields)
        if not isinstance(item["title"], str):
            raise ValueError("Title must be 1 to 120 characters")
        item["title"] = item["title"].strip()
        if not item["title"] or len(item["title"]) > 120:
            raise ValueError("Title must be 1 to 120 characters")
        if not isinstance(item["details"], str) or len(item["details"]) > 2000:
            raise ValueError("Details must be 2000 characters or fewer")
        if item["preparation"] is not None and (
            not isinstance(item["preparation"], str)
            or len(item["preparation"]) > 500
        ):
            raise ValueError("Preparation must be 500 characters or fewer")

        if item["kind"] == "note":
            if set(fields) - {"title", "details"}:
                raise ValueError("Notes only have a title and details")
        else:
            if "owner_id" in fields:
                if item["owner_id"] is not None:
                    self.require_member(household_id, item["owner_id"])
                item["assignment_state"] = (
                    "pending"
                    if item["kind"] == "task"
                    and item["owner_id"]
                    and item["owner_id"] != actor_id
                    else "accepted"
                    if item["kind"] == "task" and item["owner_id"]
                    else None
                )
                if item["status"] != "done":
                    item["status"] = (
                        "claimed"
                        if item["owner_id"] and item["assignment_state"] != "pending"
                        else "unclaimed"
                    )

            if "status" in fields:
                if item["status"] not in {"unclaimed", "claimed", "done"}:
                    raise ValueError("Invalid status")
                if item["kind"] == "task" and item["assignment_state"] == "pending":
                    raise ValueError(
                        "The assigned member must accept or reject this task"
                    )
                if item["status"] == "unclaimed":
                    item["owner_id"] = None
                    item["assignment_state"] = None
                elif not item["owner_id"]:
                    item["owner_id"] = actor_id
                    if item["kind"] == "task":
                        item["assignment_state"] = "accepted"

        if item["kind"] == "event":
            if set(fields) & {"due_at", "due_date"}:
                raise ValueError("Events do not have task deadlines")
            item["all_day"] = bool(item["all_day"])
            if item["all_day"]:
                if not item["start_date"]:
                    raise ValueError("An all-day event requires a date")
                date.fromisoformat(item["start_date"])
                item["start_at"] = item["end_at"] = None
            else:
                if not item["start_at"]:
                    raise ValueError("A timed event requires a start")
                start = datetime.fromisoformat(item["start_at"])
                if start.utcoffset() is None:
                    raise ValueError("Date-times require a timezone")
                item["start_date"] = None
                if item["end_at"]:
                    end = datetime.fromisoformat(item["end_at"])
                    if end.utcoffset() is None or end < start:
                        raise ValueError("Event end must be after its start")
            first_date = _item_date(item, item["timezone"])
            if item["monthly_on_last_day"] and first_date.day != monthrange(
                first_date.year, first_date.month
            )[1]:
                raise ValueError(
                    "Last-day recurrence must start on a month's last day"
                )
            if item["recurrence_until"] is not None:
                if item["recurrence"] is None:
                    raise ValueError("Only recurring events have an end date")
                if date.fromisoformat(item["recurrence_until"]) < first_date:
                    raise ValueError("Recurrence end date cannot precede its start")
        elif item["kind"] == "task":
            if set(fields) & {"start_at", "end_at", "start_date", "all_day"}:
                raise ValueError("Tasks do not have event start fields")
            if item["due_at"] and item["due_date"]:
                raise ValueError("A task cannot have both due time and due date")
            if item["due_at"]:
                due = datetime.fromisoformat(item["due_at"])
                if due.utcoffset() is None:
                    raise ValueError("Date-times require a timezone")
            if item["due_date"]:
                date.fromisoformat(item["due_date"])
        if item["kind"] != "note" and item["reminder_at"]:
            reminder = datetime.fromisoformat(item["reminder_at"])
            if reminder.utcoffset() is None:
                raise ValueError("Date-times require a timezone")
            if item["kind"] == "event":
                if item["all_day"]:
                    if reminder.date() > date.fromisoformat(item["start_date"]):
                        raise ValueError("Reminder must not follow the event date")
                elif reminder >= datetime.fromisoformat(item["start_at"]):
                    raise ValueError("Reminder must precede the event")
            elif item["due_at"] and reminder >= datetime.fromisoformat(item["due_at"]):
                raise ValueError("Reminder must precede the task deadline")
            elif item["due_date"] and reminder.date() > date.fromisoformat(
                item["due_date"]
            ):
                raise ValueError("Reminder must not follow the task due date")

        update = {
            key: item[key]
            for key in (
                "title",
                "details",
                "preparation",
                "owner_id",
                "assignment_state",
                "status",
                "start_at",
                "end_at",
                "start_date",
                "due_at",
                "due_date",
                "reminder_at",
                "recurrence_until",
            )
        }
        update.update(all_day=int(item["all_day"]), updated_at=_now())
        self.client.table("items").update(update).eq("id", item_id).eq(
            "household_id", household_id
        ).execute()
        if item["recurrence"] and original_start != (
            item["start_at"],
            item["start_date"],
        ):
            self.client.table("recurrence_exceptions").delete().eq(
                "series_id", item_id
            ).execute()

    def respond_to_task_assignment(
        self, household_id: str, item_id: str, actor_id: str, accept: bool
    ) -> None:
        self.require_member(household_id, actor_id)
        item = self._one(
            self.client.table("items")
            .select("kind,owner_id,assignment_state")
            .eq("id", item_id)
            .eq("household_id", household_id)
            .limit(1)
            .execute()
        )
        if item is None:
            raise ValueError("Item not found")
        if (
            item["kind"] != "task"
            or item["owner_id"] != actor_id
            or item["assignment_state"] != "pending"
        ):
            raise ValueError("Only the assigned member can respond to this task")
        self.client.table("items").update(
            {
                "owner_id": actor_id if accept else None,
                "assignment_state": "accepted" if accept else None,
                "status": "claimed" if accept else "unclaimed",
                "updated_at": _now(),
            }
        ).eq("id", item_id).eq("household_id", household_id).execute()

    def delete_item(self, household_id: str, item_id: str, actor_id: str) -> None:
        self.require_member(household_id, actor_id)
        item = self._one(
            self.client.table("items")
            .select("id")
            .eq("id", item_id)
            .eq("household_id", household_id)
            .limit(1)
            .execute()
        )
        if item is None:
            raise ValueError("Item not found")
        self.client.table("items").delete().eq("id", item_id).eq(
            "household_id", household_id
        ).execute()

    def _require_occurrence(
        self,
        household_id: str,
        series_id: str,
        occurrence_date: str,
    ) -> tuple[dict, datetime]:
        row = self._one(
            self.client.table("items")
            .select("*")
            .eq("id", series_id)
            .eq("household_id", household_id)
            .limit(1)
            .execute()
        )
        if row is None:
            raise ValueError("Item not found")
        item = dict(row)
        item["timezone"] = self.get_household(household_id)["timezone"]
        item["all_day"] = bool(item["all_day"])
        item["monthly_on_last_day"] = bool(item["monthly_on_last_day"])
        if item["kind"] != "event" or item["recurrence"] is None:
            raise ValueError("Item is not a recurring event")
        target = date.fromisoformat(occurrence_date)
        occurrences = _base_occurrences(item, target, target, item["timezone"])
        if not occurrences:
            raise ValueError("Occurrence not found")
        return item, occurrences[0]

    def update_occurrence(
        self,
        household_id: str,
        series_id: str,
        occurrence_date: str,
        actor_id: str,
        fields: dict,
    ) -> None:
        allowed = {
            "title",
            "details",
            "preparation",
            "start_at",
            "end_at",
            "start_date",
        }
        if not fields or set(fields) - allowed:
            raise ValueError("Invalid occurrence fields")
        self.require_member(household_id, actor_id)
        item, occurrence = self._require_occurrence(
            household_id, series_id, occurrence_date
        )
        existing = self._one(
            self.client.table("recurrence_exceptions")
            .select("start_at,end_at,start_date,title,details,preparation")
            .eq("series_id", series_id)
            .eq("occurrence_date", occurrence_date)
            .limit(1)
            .execute()
        )
        values = dict(existing) if existing else {
            "start_at": None,
            "end_at": None,
            "start_date": None,
            "title": None,
            "details": None,
            "preparation": None,
        }
        values.update(fields)
        if values["title"] is not None:
            values["title"] = values["title"].strip()
            if not values["title"] or len(values["title"]) > 120:
                raise ValueError("Title must be 1 to 120 characters")
        if values["details"] is not None and len(values["details"]) > 2000:
            raise ValueError("Details must be 2000 characters or fewer")
        if values["preparation"] is not None and len(values["preparation"]) > 500:
            raise ValueError("Preparation must be 500 characters or fewer")
        if values["start_at"] and values["start_date"]:
            raise ValueError("Choose a date or a date-time, not both")
        if values["end_at"] and not values["start_at"]:
            raise ValueError("An occurrence end requires a start")
        if values["start_at"]:
            moved_start = datetime.fromisoformat(values["start_at"])
            if moved_start.utcoffset() is None:
                raise ValueError("Date-times require a timezone")
            if values["end_at"] is None and item.get("end_at"):
                duration = datetime.fromisoformat(
                    item["end_at"]
                ) - datetime.fromisoformat(item["start_at"])
                values["end_at"] = (moved_start + duration).isoformat()
            if values["end_at"]:
                moved_end = datetime.fromisoformat(values["end_at"])
                if moved_end.utcoffset() is None or moved_end < moved_start:
                    raise ValueError("Occurrence end must be after its start")
        elif values["start_date"]:
            date.fromisoformat(values["start_date"])
        self.client.table("recurrence_exceptions").upsert(
            {
                "series_id": series_id,
                "occurrence_date": occurrence.date().isoformat(),
                "cancelled": 0,
                **values,
                "updated_at": _now(),
            },
            on_conflict="series_id,occurrence_date",
        ).execute()

    def cancel_occurrence(
        self,
        household_id: str,
        series_id: str,
        occurrence_date: str,
        actor_id: str,
    ) -> None:
        self.require_member(household_id, actor_id)
        _, occurrence = self._require_occurrence(
            household_id, series_id, occurrence_date
        )
        self.client.table("recurrence_exceptions").upsert(
            {
                "series_id": series_id,
                "occurrence_date": occurrence.date().isoformat(),
                "cancelled": 1,
                "start_at": None,
                "end_at": None,
                "start_date": None,
                "title": None,
                "details": None,
                "preparation": None,
                "updated_at": _now(),
            },
            on_conflict="series_id,occurrence_date",
        ).execute()

    def get_calendar(
        self, household_id: str, start_date: date, end_date: date
    ) -> dict:
        if end_date < start_date:
            raise ValueError("Calendar end must not precede start")
        if (end_date - start_date).days > 370:
            raise ValueError("Calendar range must be 371 days or fewer")
        board = self.get_board(household_id)
        timezone_name = board["household"]["timezone"]
        series_ids = [item["id"] for item in board["items"] if item["recurrence"]]
        exceptions = (
            self.client.table("recurrence_exceptions")
            .select("*")
            .in_("series_id", series_ids)
            .execute()
            .data
            or []
            if series_ids
            else []
        )
        by_series: dict[str, dict[str, dict]] = {}
        for exception in exceptions:
            exception["cancelled"] = bool(exception["cancelled"])
            by_series.setdefault(exception["series_id"], {})[
                exception["occurrence_date"]
            ] = exception

        calendar_items = []
        for item in board["items"]:
            if item["kind"] == "note":
                continue
            if not item["recurrence"]:
                item_date = _item_date(item, timezone_name)
                if item_date and start_date <= item_date <= end_date:
                    calendar_items.append(
                        {
                            **item,
                            "series_id": None,
                            "occurrence_date": item_date.isoformat(),
                            "is_occurrence": False,
                        }
                    )
                continue

            series_exceptions = by_series.get(item["id"], {})
            seen = set()
            for occurrence in _base_occurrences(
                item, start_date, end_date, timezone_name
            ):
                key = occurrence.date().isoformat()
                seen.add(key)
                expanded = _occurrence_item(
                    item, occurrence, series_exceptions.get(key)
                )
                expanded_date = (
                    _item_date(expanded, timezone_name) if expanded else None
                )
                if expanded_date and start_date <= expanded_date <= end_date:
                    calendar_items.append(expanded)

            for key, exception in series_exceptions.items():
                if key in seen or exception["cancelled"]:
                    continue
                original_date = date.fromisoformat(key)
                occurrences = _base_occurrences(
                    item, original_date, original_date, timezone_name
                )
                if not occurrences:
                    continue
                expanded = _occurrence_item(item, occurrences[0], exception)
                expanded_date = (
                    _item_date(expanded, timezone_name) if expanded else None
                )
                if expanded_date and start_date <= expanded_date <= end_date:
                    calendar_items.append(expanded)

        calendar_items.sort(
            key=lambda item: (
                _item_date(item, timezone_name) or date.max,
                item.get("start_at") or "",
                item["title"],
            )
        )
        return {"items": calendar_items}

    def get_board(self, household_id: str) -> dict:
        members = (
            self.client.table("members")
            .select("id,name,role")
            .eq("household_id", household_id)
            .is_("deleted_at", "null")
            .order("created_at")
            .order("id")
            .execute()
            .data
            or []
        )
        rows = (
            self.client.table("items")
            .select(
                "id,submission_id,kind,title,details,preparation,owner_id,"
                "assignment_state,status,start_at,end_at,start_date,due_at,due_date,"
                "reminder_at,all_day,recurrence,monthly_on_last_day,recurrence_until,"
                "created_by,created_at,updated_at,submissions(original_text)"
            )
            .eq("household_id", household_id)
            .order("created_at")
            .order("id")
            .execute()
            .data
            or []
        )
        items = []
        for row in rows:
            item = dict(row)
            submission = item.pop("submissions", None)
            item["original_text"] = (
                submission.get("original_text") if submission else None
            )
            item["all_day"] = bool(item["all_day"])
            item["monthly_on_last_day"] = bool(item["monthly_on_last_day"])
            items.append(item)
        return {
            "household": self.get_household(household_id),
            "members": members,
            "items": items,
        }
