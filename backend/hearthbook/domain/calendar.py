from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from .recurrence import base_occurrences, item_date, occurrence_item

if TYPE_CHECKING:
    from ..storage.board import BoardDatabase


def get_calendar(
    database: BoardDatabase, household_id: str, start_date: date, end_date: date
) -> dict:
    if end_date < start_date or (end_date - start_date).days > 370:
        raise ValueError("Invalid calendar range")
    board = database.get_board(household_id)
    timezone_name = board["household"]["timezone"]
    series_ids = [item["id"] for item in board["items"] if item.get("recurrence")]
    exceptions = (
        database.client.table("recurrence_exceptions")
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
        by_series.setdefault(exception["series_id"], {})[
            exception["occurrence_date"]
        ] = exception
    result = []
    for item in board["items"]:
        if item["kind"] == "note":
            continue
        if not item.get("recurrence"):
            target = item_date(item, timezone_name)
            if target and start_date <= target <= end_date:
                result.append(
                    {
                        **item,
                        "series_id": None,
                        "occurrence_date": target.isoformat(),
                        "is_occurrence": False,
                    }
                )
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
    result.sort(
        key=lambda item: (
            item_date(item, timezone_name) or date.max,
            item.get("start_at") or "",
            item["title"],
        )
    )
    return {"items": result}


def get_today(
    database: BoardDatabase,
    household_id: str,
    target_date: date,
    timezone_name: str,
) -> dict:
    zone = ZoneInfo(timezone_name)
    calendar = get_calendar(database, household_id, target_date, target_date)["items"]
    board = database.get_board(household_id)
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
    # ponytail: expand one year; family boards are small and calendar owns recurrence correctness.
    for item in get_calendar(
        database, household_id, target_date, target_date + timedelta(days=370)
    )["items"]:
        if item.get("reminder_at") and datetime.fromisoformat(
            item["reminder_at"]
        ).astimezone(zone).date() == target_date:
            add(item, "reminder_today")
    for item in board["items"]:
        if item["kind"] == "note" or item.get("completed_at"):
            continue
        if item.get("reminder_at") and datetime.fromisoformat(
            item["reminder_at"]
        ).astimezone(zone).date() == target_date:
            add(item, "reminder_today")
        if item["kind"] == "task":
            due = item_date(item, timezone_name)
            if due and due < target_date:
                add(item, "overdue")
    priority = {
        "overdue": 0,
        "reminder_today": 1,
        "happens_today": 2,
        "due_today": 2,
    }
    items = list(chosen.values())
    items.sort(
        key=lambda item: (
            min(priority[reason] for reason in item["today_reasons"]),
            item.get("start_at") or item.get("due_at") or "",
            item["title"],
        )
    )
    return {"date": target_date.isoformat(), "items": items}
