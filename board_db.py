from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BoardDatabase:
    def __init__(self, path: str | Path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 5000")

    def setup(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS households (
                id TEXT PRIMARY KEY,
                timezone TEXT NOT NULL DEFAULT 'UTC',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                household_id TEXT NOT NULL REFERENCES households(id),
                name TEXT NOT NULL,
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
                owner_id TEXT REFERENCES members(id),
                status TEXT CHECK (
                    status IS NULL OR status IN ('unclaimed', 'claimed', 'done')
                ),
                start_at TEXT,
                end_at TEXT,
                start_date TEXT,
                due_at TEXT,
                due_date TEXT,
                all_day INTEGER NOT NULL DEFAULT 0 CHECK (all_day IN (0, 1)),
                created_by TEXT NOT NULL REFERENCES members(id),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (submission_id, source_index)
            );

            CREATE INDEX IF NOT EXISTS items_household_status
                ON items(household_id, status);
            CREATE INDEX IF NOT EXISTS items_household_start
                ON items(household_id, start_at, start_date);
            CREATE INDEX IF NOT EXISTS items_household_due
                ON items(household_id, due_at, due_date);
            """
        )
        self.connection.commit()

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
            "SELECT 1 FROM members WHERE id = ? AND household_id = ?",
            (member_id, household_id),
        ).fetchone() is None:
            raise ValueError("Choose a valid family member first")
        return member_id

    def require_member(self, household_id: str, member_id: str | None) -> str:
        return self._require_member(self.connection.cursor(), household_id, member_id)

    def add_member(self, household_id: str, name: str) -> str:
        name = name.strip()
        if not name or len(name) > 40:
            raise ValueError("Member name must be 1 to 40 characters")
        with self.connection:
            self.ensure_household(household_id)
            names = self.connection.execute(
                "SELECT name FROM members WHERE household_id = ?", (household_id,)
            )
            if any(row["name"].casefold() == name.casefold() for row in names):
                raise ValueError("That family member already exists")
            member_id = str(uuid4())
            self.connection.execute(
                """
                INSERT INTO members (id, household_id, name, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (member_id, household_id, name, _now()),
            )
        return member_id

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
                item_owner = owner_id if actionable else None
                status = (
                    ("claimed" if item_owner else "unclaimed")
                    if actionable
                    else None
                )
                now = _now()
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO items (
                        id, household_id, submission_id, source_index, kind,
                        title, details, owner_id, status, start_at, end_at,
                        start_date, due_at, due_date, all_day, created_by,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid4()),
                        household_id,
                        submission_id,
                        index,
                        draft["kind"],
                        draft["title"],
                        draft.get("details", ""),
                        item_owner,
                        status,
                        draft.get("start_at"),
                        draft.get("end_at"),
                        draft.get("start_date"),
                        draft.get("due_at"),
                        draft.get("due_date"),
                        int(draft.get("all_day", False)),
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

    def update_item(
        self,
        household_id: str,
        item_id: str,
        actor_id: str,
        fields: dict,
    ) -> None:
        if not fields or set(fields) - {"owner_id", "status"}:
            raise ValueError("Only owner and status can be changed")

        with self.connection:
            cursor = self.connection.cursor()
            self._require_member(cursor, household_id, actor_id)
            row = cursor.execute(
                """
                SELECT kind, owner_id, status FROM items
                WHERE id = ? AND household_id = ?
                """,
                (item_id, household_id),
            ).fetchone()
            if row is None:
                raise ValueError("Item not found")
            if row["kind"] == "note":
                raise ValueError("Notes do not have owners or status")

            owner_id, status = row["owner_id"], row["status"]
            if "owner_id" in fields:
                owner_id = fields["owner_id"]
                if owner_id is not None:
                    self._require_member(cursor, household_id, owner_id)
                if status != "done":
                    status = "claimed" if owner_id else "unclaimed"

            if "status" in fields:
                status = fields["status"]
                if status not in {"unclaimed", "claimed", "done"}:
                    raise ValueError("Invalid status")
                if status == "unclaimed":
                    owner_id = None
                elif not owner_id:
                    owner_id = actor_id

            cursor.execute(
                """
                UPDATE items
                SET owner_id = ?, status = ?, updated_at = ?
                WHERE id = ? AND household_id = ?
                """,
                (owner_id, status, _now(), item_id, household_id),
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

    def get_board(self, household_id: str) -> dict:
        members = [
            dict(row)
            for row in self.connection.execute(
                """
                SELECT id, name FROM members
                WHERE household_id = ?
                ORDER BY created_at, rowid
                """,
                (household_id,),
            )
        ]
        rows = self.connection.execute(
            """
            SELECT
                i.id, i.submission_id, i.kind, i.title, i.details,
                i.owner_id, i.status, i.start_at, i.end_at, i.start_date,
                i.due_at, i.due_date, i.all_day, i.created_by,
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
            items.append(item)
        return {"members": members, "items": items}

    def import_legacy_state(self, household_id: str, values: dict) -> None:
        migration_key = f"legacy_checkpoint_v1:{household_id}"
        if self.connection.execute(
            "SELECT 1 FROM app_meta WHERE key = ?", (migration_key,)
        ).fetchone():
            return

        with self.connection:
            self.ensure_household(household_id)
            for member in values.get("members", []):
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO members (
                        id, household_id, name, created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        member["id"],
                        household_id,
                        member["name"],
                        member.get("created_at", _now()),
                    ),
                )
            for item in values.get("items", []):
                now = item.get("created_at", _now())
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO items (
                        id, household_id, kind, title, details, owner_id,
                        status, start_at, end_at, due_at, all_day, created_by,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item["id"],
                        household_id,
                        item["kind"],
                        item["title"],
                        item.get("details", ""),
                        item.get("owner_id"),
                        item.get("status"),
                        item.get("start_at"),
                        item.get("end_at"),
                        item.get("due_at"),
                        int(item.get("all_day", False)),
                        item["created_by"],
                        now,
                        now,
                    ),
                )
            self.connection.execute(
                "INSERT INTO app_meta (key, value) VALUES (?, ?)",
                (migration_key, _now()),
            )
