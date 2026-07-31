from __future__ import annotations

import json
import re
import sqlite3
from calendar import monthrange
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

from dateutil.rrule import DAILY, MONTHLY, WEEKLY, rrule

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
    def __init__(self, path: str | Path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 5000")

    def setup(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS households (
                id TEXT PRIMARY KEY,
                timezone TEXT NOT NULL DEFAULT 'UTC',
                city TEXT,
                country_code TEXT,
                latitude REAL,
                longitude REAL,
                memory TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                household_id TEXT NOT NULL REFERENCES households(id),
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT '',
                deleted_at TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                household_id TEXT NOT NULL REFERENCES households(id),
                created_by TEXT NOT NULL REFERENCES members(id),
                source TEXT NOT NULL CHECK (source IN ('text', 'audio')),
                original_text TEXT NOT NULL,
                timezone TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                household_id TEXT NOT NULL REFERENCES households(id),
                submission_id TEXT REFERENCES submissions(id),
                source_index INTEGER,
                kind TEXT NOT NULL CHECK (kind IN ('event', 'task', 'note')),
                title TEXT NOT NULL,
                details TEXT NOT NULL DEFAULT '',
                preparation TEXT,
                owner_id TEXT REFERENCES members(id),
                assignment_state TEXT CHECK (
                    assignment_state IS NULL OR assignment_state IN ('pending', 'accepted')
                ),
                status TEXT CHECK (
                    status IS NULL OR status IN ('unclaimed', 'claimed', 'done')
                ),
                start_at TEXT,
                end_at TEXT,
                start_date TEXT,
                due_at TEXT,
                due_date TEXT,
                reminder_at TEXT,
                all_day INTEGER NOT NULL DEFAULT 0 CHECK (all_day IN (0, 1)),
                recurrence TEXT CHECK (
                    recurrence IS NULL OR recurrence IN ('daily', 'weekly', 'monthly')
                ),
                monthly_on_last_day INTEGER NOT NULL DEFAULT 0 CHECK (
                    monthly_on_last_day IN (0, 1)
                ),
                recurrence_until TEXT,
                created_by TEXT NOT NULL REFERENCES members(id),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (submission_id, source_index)
            );

            CREATE TABLE IF NOT EXISTS recurrence_exceptions (
                series_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                occurrence_date TEXT NOT NULL,
                cancelled INTEGER NOT NULL DEFAULT 0 CHECK (cancelled IN (0, 1)),
                start_at TEXT,
                end_at TEXT,
                start_date TEXT,
                title TEXT,
                details TEXT,
                preparation TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (series_id, occurrence_date)
            );

            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                household_id TEXT NOT NULL REFERENCES households(id),
                actor_id TEXT NOT NULL REFERENCES members(id),
                kind TEXT NOT NULL CHECK (kind IN ('intake', 'assistant')),
                status TEXT NOT NULL CHECK (
                    status IN ('active', 'clarifying', 'review', 'confirmed')
                ),
                owner_id TEXT REFERENCES members(id),
                source TEXT NOT NULL CHECK (source IN ('text', 'audio')),
                timezone TEXT NOT NULL,
                clarification_count INTEGER NOT NULL DEFAULT 0,
                payload_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS items_household_status
                ON items(household_id, status);
            CREATE INDEX IF NOT EXISTS items_household_start
                ON items(household_id, start_at, start_date);
            CREATE INDEX IF NOT EXISTS items_household_due
                ON items(household_id, due_at, due_date);
            CREATE INDEX IF NOT EXISTS chat_messages_session
                ON chat_messages(session_id, id);
            """
        )
        self._upgrade_chat_sessions()
        if "recurrence" not in {
            row["name"] for row in self.connection.execute("PRAGMA table_info(items)")
        }:
            self.connection.execute(
                """
                ALTER TABLE items ADD COLUMN recurrence TEXT CHECK (
                    recurrence IS NULL OR recurrence IN ('daily', 'weekly', 'monthly')
                )
                """
            )
        if "monthly_on_last_day" not in {
            row["name"] for row in self.connection.execute("PRAGMA table_info(items)")
        }:
            self.connection.execute(
                """
                ALTER TABLE items ADD COLUMN monthly_on_last_day INTEGER
                NOT NULL DEFAULT 0 CHECK (monthly_on_last_day IN (0, 1))
                """
            )
        if "recurrence_until" not in {
            row["name"] for row in self.connection.execute("PRAGMA table_info(items)")
        }:
            self.connection.execute(
                "ALTER TABLE items ADD COLUMN recurrence_until TEXT"
            )
        if "assignment_state" not in {
            row["name"] for row in self.connection.execute("PRAGMA table_info(items)")
        }:
            self.connection.execute(
                """
                ALTER TABLE items ADD COLUMN assignment_state TEXT CHECK (
                    assignment_state IS NULL OR assignment_state IN ('pending', 'accepted')
                )
                """
            )
        if "reminder_at" not in {
            row["name"] for row in self.connection.execute("PRAGMA table_info(items)")
        }:
            self.connection.execute("ALTER TABLE items ADD COLUMN reminder_at TEXT")
        if "preparation" not in {
            row["name"] for row in self.connection.execute("PRAGMA table_info(items)")
        }:
            self.connection.execute("ALTER TABLE items ADD COLUMN preparation TEXT")
        if "preparation" not in {
            row["name"]
            for row in self.connection.execute(
                "PRAGMA table_info(recurrence_exceptions)"
            )
        }:
            self.connection.execute(
                "ALTER TABLE recurrence_exceptions ADD COLUMN preparation TEXT"
            )
        self.connection.execute(
            """
            UPDATE items SET assignment_state = 'accepted'
            WHERE kind = 'task' AND owner_id IS NOT NULL AND assignment_state IS NULL
            """
        )
        household_columns = {
            row["name"]
            for row in self.connection.execute("PRAGMA table_info(households)")
        }
        for name, sql_type in {
            "city": "TEXT",
            "country_code": "TEXT",
            "latitude": "REAL",
            "longitude": "REAL",
            "memory": "TEXT NOT NULL DEFAULT ''",
        }.items():
            if name not in household_columns:
                self.connection.execute(
                    f"ALTER TABLE households ADD COLUMN {name} {sql_type}"
                )
        member_columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(members)")
        }
        if "role" not in member_columns:
            self.connection.execute("ALTER TABLE members ADD COLUMN role TEXT NOT NULL DEFAULT ''")
        if "deleted_at" not in member_columns:
            self.connection.execute("ALTER TABLE members ADD COLUMN deleted_at TEXT")
        self.connection.commit()

    def _upgrade_chat_sessions(self) -> None:
        schema = self.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'chat_sessions'"
        ).fetchone()
        if schema is None or "'assistant'" in schema["sql"]:
            return
        self.connection.commit()
        self.connection.execute("PRAGMA foreign_keys = OFF")
        try:
            self.connection.executescript(
                """
                BEGIN IMMEDIATE;
                ALTER TABLE chat_messages RENAME TO old_chat_messages;
                ALTER TABLE chat_sessions RENAME TO old_chat_sessions;

                CREATE TABLE chat_sessions (
                    id TEXT PRIMARY KEY,
                    household_id TEXT NOT NULL REFERENCES households(id),
                    actor_id TEXT NOT NULL REFERENCES members(id),
                    kind TEXT NOT NULL CHECK (kind IN ('intake', 'assistant')),
                    status TEXT NOT NULL CHECK (
                        status IN ('active', 'clarifying', 'review', 'confirmed')
                    ),
                    owner_id TEXT REFERENCES members(id),
                    source TEXT NOT NULL CHECK (source IN ('text', 'audio')),
                    timezone TEXT NOT NULL,
                    clarification_count INTEGER NOT NULL DEFAULT 0,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                INSERT INTO chat_sessions SELECT * FROM old_chat_sessions;
                INSERT INTO chat_messages SELECT * FROM old_chat_messages;
                DROP TABLE old_chat_messages;
                DROP TABLE old_chat_sessions;
                CREATE INDEX chat_messages_session ON chat_messages(session_id, id);
                COMMIT;
                """
            )
        except Exception:
            self.connection.rollback()
            raise
        finally:
            self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self) -> None:
        self.connection.close()

    def ensure_household(self, household_id: str, timezone_name: str = "UTC") -> None:
        self.connection.execute(
            """
            INSERT INTO households (id, timezone, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (household_id, timezone_name, _now()),
        )

    def _require_member(
        self, cursor: sqlite3.Cursor, household_id: str, member_id: str | None
    ) -> str:
        if not member_id or cursor.execute(
            "SELECT 1 FROM members WHERE id = ? AND household_id = ? AND deleted_at IS NULL",
            (member_id, household_id),
        ).fetchone() is None:
            raise ValueError("Choose a valid family member first")
        return member_id

    def require_member(self, household_id: str, member_id: str | None) -> str:
        return self._require_member(self.connection.cursor(), household_id, member_id)

    def get_household_memory(self, household_id: str) -> str:
        row = self.connection.execute(
            "SELECT memory FROM households WHERE id = ?", (household_id,)
        ).fetchone()
        return row["memory"] if row else ""

    def set_household_memory(self, household_id: str, memory: str) -> None:
        memory = memory.strip()
        if len(memory) > HOUSEHOLD_MEMORY_MAX_CHARS:
            shortened = memory[:HOUSEHOLD_MEMORY_MAX_CHARS]
            memory = shortened.rsplit("\n", 1)[0].strip() or shortened.rstrip()
        with self.connection:
            self.ensure_household(household_id)
            self.connection.execute(
                "UPDATE households SET memory = ? WHERE id = ?",
                (memory, household_id),
            )

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
        with self.connection:
            self.ensure_household(household_id, timezone_name)
            self._require_member(self.connection.cursor(), household_id, actor_id)
            if owner_id is not None:
                self._require_member(self.connection.cursor(), household_id, owner_id)
            self.connection.execute(
                """
                INSERT INTO chat_sessions (
                    id, household_id, actor_id, kind, status, owner_id, source,
                    timezone, created_at, updated_at
                ) VALUES (?, ?, ?, 'intake', 'clarifying', ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    household_id,
                    actor_id,
                    owner_id,
                    source,
                    timezone_name,
                    now,
                    now,
                ),
            )
            self.connection.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, created_at)
                VALUES (?, 'user', ?, ?)
                """,
                (session_id, text, now),
            )
        return self.get_intake_session(household_id, session_id, actor_id)

    def get_intake_session(
        self, household_id: str, session_id: str, actor_id: str
    ) -> dict:
        row = self.connection.execute(
            """
            SELECT * FROM chat_sessions
            WHERE id = ? AND household_id = ? AND actor_id = ? AND kind = 'intake'
            """,
            (session_id, household_id, actor_id),
        ).fetchone()
        if row is None:
            raise ValueError("Intake conversation not found")
        session = dict(row)
        session["payload"] = json.loads(session.pop("payload_json"))
        session["messages"] = [
            dict(message)
            for message in self.connection.execute(
                """
                SELECT role, content FROM chat_messages
                WHERE session_id = ? ORDER BY id
                """,
                (session_id,),
            )
        ]
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
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, _now()),
            )
            self.connection.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
                (_now(), session_id),
            )
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
        with self.connection:
            self.ensure_household(household_id, timezone_name)
            self._require_member(self.connection.cursor(), household_id, actor_id)
            self.connection.execute(
                """
                INSERT INTO chat_sessions (
                    id, household_id, actor_id, kind, status, source,
                    timezone, created_at, updated_at
                ) VALUES (?, ?, ?, 'assistant', 'active', 'text', ?, ?, ?)
                """,
                (session_id, household_id, actor_id, timezone_name, now, now),
            )
            self.connection.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, created_at)
                VALUES (?, 'user', ?, ?)
                """,
                (session_id, text, now),
            )
        return self.get_assistant_session(household_id, session_id, actor_id)

    def get_assistant_session(
        self, household_id: str, session_id: str, actor_id: str
    ) -> dict:
        row = self.connection.execute(
            """
            SELECT * FROM chat_sessions
            WHERE id = ? AND household_id = ? AND actor_id = ?
                AND kind = 'assistant' AND status = 'active'
            """,
            (session_id, household_id, actor_id),
        ).fetchone()
        if row is None:
            raise ValueError("Assistant conversation not found")
        session = dict(row)
        session["payload"] = json.loads(session.pop("payload_json"))
        session["messages"] = [
            dict(message)
            for message in self.connection.execute(
                """
                SELECT role, content FROM chat_messages
                WHERE session_id = ? ORDER BY id
                """,
                (session_id,),
            )
        ]
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
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, _now()),
            )
            self.connection.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
                (_now(), session_id),
            )
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
        with self.connection:
            self.connection.execute(
                """
                UPDATE chat_sessions
                SET status = ?, clarification_count = ?, payload_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    status,
                    clarification_count,
                    json.dumps(payload, ensure_ascii=False),
                    _now(),
                    session_id,
                ),
            )
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
        with self.connection:
            self.connection.execute(
                """
                UPDATE chat_sessions SET status = 'confirmed', updated_at = ?
                WHERE id = ?
                """,
                (_now(), session_id),
            )
        return {"action": "created", "item_id": item_ids[0], "item_ids": item_ids}

    def get_household(self, household_id: str) -> dict:
        row = self.connection.execute(
            """
            SELECT id, timezone, city, country_code
            FROM households WHERE id = ?
            """,
            (household_id,),
        ).fetchone()
        return dict(row) if row else {
            "id": household_id,
            "timezone": "UTC",
            "city": None,
            "country_code": None,
        }

    def get_weather_location(self, household_id: str) -> dict | None:
        row = self.connection.execute(
            """
            SELECT city, country_code, latitude, longitude
            FROM households WHERE id = ?
            """,
            (household_id,),
        ).fetchone()
        if row is None or row["latitude"] is None or row["longitude"] is None:
            return None
        return dict(row)

    def set_household_location(self, household_id: str, location: dict) -> None:
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError("Invalid city coordinates")
        with self.connection:
            self.ensure_household(household_id)
            self.connection.execute(
                """
                UPDATE households
                SET city = ?, country_code = ?, latitude = ?, longitude = ?
                WHERE id = ?
                """,
                (
                    location["city"],
                    location["country_code"],
                    latitude,
                    longitude,
                    household_id,
                ),
            )

    def add_member(self, household_id: str, name: str, role: str = "") -> str:
        name = name.strip()
        role = role.strip()
        if not name or len(name) > 40:
            raise ValueError("Member name must be 1 to 40 characters")
        if len(role) > 40:
            raise ValueError("Member role must be at most 40 characters")
        with self.connection:
            self.ensure_household(household_id)
            names = self.connection.execute(
                "SELECT name FROM members WHERE household_id = ? AND deleted_at IS NULL", (household_id,)
            )
            if any(row["name"].casefold() == name.casefold() for row in names):
                raise ValueError("That family member already exists")
            member_id = str(uuid4())
            self.connection.execute(
                """
                INSERT INTO members (id, household_id, name, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (member_id, household_id, name, role, _now()),
            )
        return member_id

    def delete_member(self, household_id: str, member_id: str) -> None:
        with self.connection:
            cursor = self.connection.execute(
                "UPDATE members SET deleted_at = ? WHERE id = ? AND household_id = ? AND deleted_at IS NULL",
                (_now(), member_id, household_id),
            )
            if not cursor.rowcount:
                raise ValueError("Family member not found")

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
        with self.connection:
            cursor = self.connection.cursor()
            self.ensure_household(household_id, timezone_name)
            self._require_member(cursor, household_id, actor_id)
            if owner_id is not None:
                self._require_member(cursor, household_id, owner_id)
            cursor.execute(
                "UPDATE households SET timezone = ? WHERE id = ?",
                (timezone_name, household_id),
            )
            cursor.execute(
                """
                INSERT OR IGNORE INTO submissions (
                    id, household_id, created_by, source, original_text,
                    timezone, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    submission_id,
                    household_id,
                    actor_id,
                    source,
                    text,
                    timezone_name,
                    _now(),
                ),
            )

            for index, draft in enumerate(drafts):
                actionable = draft["kind"] != "note"
                item_owner = (
                    draft.get("owner_id")
                    if actionable and draft.get("owner_id") is not None
                    else owner_id if actionable else None
                )
                if item_owner is not None:
                    self._require_member(cursor, household_id, item_owner)
                assignment_state = (
                    "accepted" if draft["kind"] == "task" and item_owner == actor_id
                    else "pending" if draft["kind"] == "task" and item_owner
                    else None
                )
                status = (
                    ("claimed" if item_owner and assignment_state != "pending" else "unclaimed")
                    if actionable else None
                )
                now = _now()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO items (
                        id, household_id, submission_id, source_index, kind,
                        title, details, preparation, owner_id, assignment_state, status, start_at, end_at,
                        start_date, due_at, due_date, reminder_at, all_day, recurrence,
                        monthly_on_last_day, recurrence_until, created_by,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid4()),
                        household_id,
                        submission_id,
                        index,
                        draft["kind"],
                        draft["title"],
                        draft.get("details", ""),
                        draft.get("preparation") if actionable else None,
                        item_owner,
                        assignment_state,
                        status,
                        draft.get("start_at"),
                        draft.get("end_at"),
                        draft.get("start_date"),
                        draft.get("due_at"),
                        draft.get("due_date"),
                        draft.get("reminder_at"),
                        int(draft.get("all_day", False)),
                        draft.get("recurrence"),
                        int(draft.get("monthly_on_last_day", False)),
                        draft.get("recurrence_until"),
                        actor_id,
                        now,
                        now,
                    ),
                )

            rows = cursor.execute(
                """
                SELECT id FROM items
                WHERE submission_id = ?
                ORDER BY source_index
                """,
                (submission_id,),
            ).fetchall()
        return [row["id"] for row in rows]

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

        with self.connection:
            cursor = self.connection.cursor()
            self._require_member(cursor, household_id, actor_id)
            row = cursor.execute(
                """
                SELECT i.*, h.timezone
                FROM items AS i
                JOIN households AS h ON h.id = i.household_id
                WHERE i.id = ? AND i.household_id = ?
                """,
                (item_id, household_id),
            ).fetchone()
            if row is None:
                raise ValueError("Item not found")
            item = dict(row)
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
                        self._require_member(cursor, household_id, item["owner_id"])
                    item["assignment_state"] = (
                        "pending"
                        if item["kind"] == "task" and item["owner_id"]
                        and item["owner_id"] != actor_id
                        else "accepted"
                        if item["kind"] == "task" and item["owner_id"]
                        else None
                    )
                    if item["status"] != "done":
                        item["status"] = "claimed" if item["owner_id"] and item["assignment_state"] != "pending" else "unclaimed"

                if "status" in fields:
                    if item["status"] not in {"unclaimed", "claimed", "done"}:
                        raise ValueError("Invalid status")
                    if item["kind"] == "task" and item["assignment_state"] == "pending":
                        raise ValueError("The assigned member must accept or reject this task")
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
                elif item["due_date"] and reminder.date() > date.fromisoformat(item["due_date"]):
                    raise ValueError("Reminder must not follow the task due date")

            cursor.execute(
                """
                UPDATE items
                SET title = ?, details = ?, preparation = ?, owner_id = ?, assignment_state = ?, status = ?,
                    start_at = ?, end_at = ?, start_date = ?,
                    due_at = ?, due_date = ?, reminder_at = ?, all_day = ?,
                    recurrence_until = ?, updated_at = ?
                WHERE id = ? AND household_id = ?
                """,
                (
                    item["title"],
                    item["details"],
                    item["preparation"],
                    item["owner_id"],
                    item["assignment_state"],
                    item["status"],
                    item["start_at"],
                    item["end_at"],
                    item["start_date"],
                    item["due_at"],
                    item["due_date"],
                    item["reminder_at"],
                    int(item["all_day"]),
                    item["recurrence_until"],
                    _now(),
                    item_id,
                    household_id,
                ),
            )
            if item["recurrence"] and original_start != (
                item["start_at"],
                item["start_date"],
            ):
                cursor.execute(
                    "DELETE FROM recurrence_exceptions WHERE series_id = ?",
                    (item_id,),
                )

    def respond_to_task_assignment(
        self, household_id: str, item_id: str, actor_id: str, accept: bool
    ) -> None:
        with self.connection:
            cursor = self.connection.cursor()
            self._require_member(cursor, household_id, actor_id)
            item = cursor.execute(
                """
                SELECT kind, owner_id, assignment_state FROM items
                WHERE id = ? AND household_id = ?
                """,
                (item_id, household_id),
            ).fetchone()
            if item is None:
                raise ValueError("Item not found")
            if item["kind"] != "task" or item["owner_id"] != actor_id or item["assignment_state"] != "pending":
                raise ValueError("Only the assigned member can respond to this task")
            cursor.execute(
                """
                UPDATE items
                SET owner_id = ?, assignment_state = ?, status = ?, updated_at = ?
                WHERE id = ? AND household_id = ?
                """,
                (
                    actor_id if accept else None,
                    "accepted" if accept else None,
                    "claimed" if accept else "unclaimed",
                    _now(), item_id, household_id,
                ),
            )

    def delete_item(self, household_id: str, item_id: str, actor_id: str) -> None:
        with self.connection:
            cursor = self.connection.cursor()
            self._require_member(cursor, household_id, actor_id)
            deleted = cursor.execute(
                "DELETE FROM items WHERE id = ? AND household_id = ?",
                (item_id, household_id),
            ).rowcount
            if not deleted:
                raise ValueError("Item not found")

    def _require_occurrence(
        self,
        cursor: sqlite3.Cursor,
        household_id: str,
        series_id: str,
        occurrence_date: str,
    ) -> tuple[dict, datetime]:
        row = cursor.execute(
            """
            SELECT i.*, h.timezone
            FROM items AS i
            JOIN households AS h ON h.id = i.household_id
            WHERE i.id = ? AND i.household_id = ?
            """,
            (series_id, household_id),
        ).fetchone()
        if row is None:
            raise ValueError("Item not found")
        item = dict(row)
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
        with self.connection:
            cursor = self.connection.cursor()
            self._require_member(cursor, household_id, actor_id)
            item, occurrence = self._require_occurrence(
                cursor, household_id, series_id, occurrence_date
            )
            existing = cursor.execute(
                """
                SELECT start_at, end_at, start_date, title, details, preparation
                FROM recurrence_exceptions
                WHERE series_id = ? AND occurrence_date = ?
                """,
                (series_id, occurrence_date),
            ).fetchone()
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
            cursor.execute(
                """
                INSERT INTO recurrence_exceptions (
                    series_id, occurrence_date, cancelled, start_at, end_at,
                    start_date, title, details, preparation, updated_at
                ) VALUES (?, ?, 0, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(series_id, occurrence_date) DO UPDATE SET
                    cancelled = 0,
                    start_at = excluded.start_at,
                    end_at = excluded.end_at,
                    start_date = excluded.start_date,
                    title = excluded.title,
                    details = excluded.details,
                    preparation = excluded.preparation,
                    updated_at = excluded.updated_at
                """,
                (
                    series_id,
                    occurrence.date().isoformat(),
                    values["start_at"],
                    values["end_at"],
                    values["start_date"],
                    values["title"],
                    values["details"],
                    values["preparation"],
                    _now(),
                ),
            )

    def cancel_occurrence(
        self,
        household_id: str,
        series_id: str,
        occurrence_date: str,
        actor_id: str,
    ) -> None:
        with self.connection:
            cursor = self.connection.cursor()
            self._require_member(cursor, household_id, actor_id)
            _, occurrence = self._require_occurrence(
                cursor, household_id, series_id, occurrence_date
            )
            cursor.execute(
                """
                INSERT INTO recurrence_exceptions (
                    series_id, occurrence_date, cancelled, updated_at
                ) VALUES (?, ?, 1, ?)
                ON CONFLICT(series_id, occurrence_date) DO UPDATE SET
                    cancelled = 1,
                    start_at = NULL,
                    end_at = NULL,
                    start_date = NULL,
                    title = NULL,
                    details = NULL,
                    preparation = NULL,
                    updated_at = excluded.updated_at
                """,
                (series_id, occurrence.date().isoformat(), _now()),
            )

    def get_calendar(
        self, household_id: str, start_date: date, end_date: date
    ) -> dict:
        if end_date < start_date:
            raise ValueError("Calendar end must not precede start")
        if (end_date - start_date).days > 370:
            raise ValueError("Calendar range must be 371 days or fewer")
        board = self.get_board(household_id)
        timezone_name = board["household"]["timezone"]
        exceptions = [
            dict(row)
            for row in self.connection.execute(
                """
                SELECT e.*
                FROM recurrence_exceptions AS e
                JOIN items AS i ON i.id = e.series_id
                WHERE i.household_id = ?
                """,
                (household_id,),
            )
        ]
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
        members = [
            dict(row)
            for row in self.connection.execute(
                """
                SELECT id, name, role FROM members
                WHERE household_id = ? AND deleted_at IS NULL
                ORDER BY created_at, rowid
                """,
                (household_id,),
            )
        ]
        rows = self.connection.execute(
            """
            SELECT
                i.id, i.submission_id, i.kind, i.title, i.details, i.preparation,
                i.owner_id, i.assignment_state, i.status, i.start_at, i.end_at, i.start_date,
                i.due_at, i.due_date, i.reminder_at, i.all_day, i.recurrence,
                i.monthly_on_last_day, i.recurrence_until, i.created_by,
                i.created_at, i.updated_at, s.original_text
            FROM items AS i
            LEFT JOIN submissions AS s ON s.id = i.submission_id
            WHERE i.household_id = ?
            ORDER BY i.created_at, i.rowid
            """,
            (household_id,),
        )
        items = []
        for row in rows:
            item = dict(row)
            item["all_day"] = bool(item["all_day"])
            item["monthly_on_last_day"] = bool(item["monthly_on_last_day"])
            items.append(item)
        return {
            "household": self.get_household(household_id),
            "members": members,
            "items": items,
        }
