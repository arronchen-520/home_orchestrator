from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ..domain.calendar import get_calendar
from ..storage.board import BoardDatabase

COLUMNS = [
    "id", "kind", "title", "details", "preparation", "remind_member_id",
    "remind_member_name", "completed_at", "start_at", "end_at", "start_date",
    "due_at", "due_date", "reminder_at", "recurrence", "recurrence_until",
    "created_at", "updated_at", "original_text",
]
ALLOWED_TABLES = {"items", "members", "occurrences", "item_notes"}
ALLOWED_FUNCTIONS = {
    "abs", "avg", "coalesce", "count", "date", "datetime", "group_concat",
    "julianday", "length", "lower", "max", "min", "round", "strftime",
    "sum", "total", "trim", "upper",
}


def query_assistant(
    board_database: BoardDatabase, household_id: str, timezone_name: str, sql: str
) -> list[dict]:
    statement = sql.strip().removesuffix(";").strip()
    if not re.match(r"^(SELECT|WITH)\b", statement, re.IGNORECASE) or ";" in statement:
        raise ValueError("Assistant queries must be one read-only SELECT")
    board = board_database.get_board(household_id)
    names = {member["id"]: member["name"] for member in board["members"]}

    def values(item: dict) -> list:
        projected = {
            **item,
            "remind_member_name": names.get(item.get("remind_member_id")),
        }
        return [projected.get(column) for column in COLUMNS]

    today = datetime.now(ZoneInfo(timezone_name)).date()
    occurrences = get_calendar(
        board_database, household_id, today - timedelta(days=365), today
    )["items"]
    occurrences += get_calendar(
        board_database, household_id, today + timedelta(days=1), today + timedelta(days=370)
    )["items"]
    database = sqlite3.connect(":memory:")
    database.row_factory = sqlite3.Row
    schema = ", ".join(f"{column} TEXT" for column in COLUMNS)
    placeholders = ", ".join("?" for _ in COLUMNS)
    database.execute("CREATE TABLE members (id TEXT, name TEXT, role TEXT)")
    database.execute(f"CREATE TABLE items ({schema})")
    database.execute(
        f"CREATE TABLE occurrences ({schema}, series_id TEXT, occurrence_date TEXT, is_occurrence INTEGER)"
    )
    database.execute(
        "CREATE TABLE item_notes (id TEXT, item_id TEXT, member_id TEXT, member_name TEXT, content TEXT, created_at TEXT)"
    )
    database.executemany(
        "INSERT INTO members VALUES (?, ?, ?)",
        [(member["id"], member["name"], member["role"]) for member in board["members"]],
    )
    database.executemany(
        f"INSERT INTO items VALUES ({placeholders})",
        [values(item) for item in board["items"]],
    )
    database.executemany(
        f"INSERT INTO occurrences VALUES ({placeholders}, ?, ?, ?)",
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
    database.executemany(
        "INSERT INTO item_notes VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                note["id"], item["id"], note["member_id"],
                names.get(note["member_id"]), note["content"], note["created_at"],
            )
            for item in board["items"]
            for note in item["notes"]
        ],
    )

    def authorize(action, first, second, _database, _trigger):
        if action in {sqlite3.SQLITE_SELECT, getattr(sqlite3, "SQLITE_RECURSIVE", -1)}:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ and first in ALLOWED_TABLES:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION and (second or first or "").lower() in ALLOWED_FUNCTIONS:
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
