from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from .recurrence import base_occurrences, event_end_date, item_date, occurrence_item, schedule_zone

if TYPE_CHECKING:
    from ..storage.board import BoardDatabase


def overlaps_calendar_range(item: dict, start_date: date, end_date: date, timezone_name: str) -> bool:
    start = item_date(item, timezone_name)
    if start is None:
        return False
    finish = event_end_date(item, timezone_name) if item["kind"] == "event" else start
    return start <= end_date and finish >= start_date


def get_calendar(
    database: BoardDatabase, household_id: str, start_date: date, end_date: date, timezone_name: str
) -> dict:
    if end_date < start_date or (end_date - start_date).days > 370:
        raise ValueError("Invalid calendar range")
    zone = ZoneInfo(timezone_name)
    board = database.get_board(household_id)
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
            if target and overlaps_calendar_range(item, start_date, end_date, timezone_name):
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
        source_zone = schedule_zone(item)
        source_start = datetime.combine(start_date, datetime.min.time(), zone).astimezone(source_zone).date()
        source_end = datetime.combine(end_date + timedelta(days=1), datetime.min.time(), zone).astimezone(source_zone).date()
        source_start -= event_end_date(item, source_zone.key) - item_date(item, source_zone.key)
        for occurrence in base_occurrences(item, source_start, source_end):
            key = occurrence.date().isoformat()
            seen.add(key)
            expanded = occurrence_item(item, occurrence, exceptions_for_series.get(key))
            target = item_date(expanded, timezone_name) if expanded else None
            if target and overlaps_calendar_range(expanded, start_date, end_date, timezone_name):
                result.append(expanded)
        for key, exception in exceptions_for_series.items():
            if key in seen or exception["cancelled"]:
                continue
            original = date.fromisoformat(key)
            occurrences = base_occurrences(item, original, original)
            if occurrences:
                expanded = occurrence_item(item, occurrences[0], exception)
                target = item_date(expanded, timezone_name) if expanded else None
                if target and overlaps_calendar_range(expanded, start_date, end_date, timezone_name):
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
    calendar = get_calendar(database, household_id, target_date, target_date, timezone_name)["items"]
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
    # ponytail: scan one year around today; family boards are small and this handles reminders after an occurrence.
    for start, end in (
        (target_date - timedelta(days=370), target_date - timedelta(days=1)),
        (target_date, target_date + timedelta(days=370)),
    ):
        for item in get_calendar(database, household_id, start, end, timezone_name)["items"]:
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
