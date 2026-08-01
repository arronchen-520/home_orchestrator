from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from dateutil.rrule import DAILY, FR, MO, MONTHLY, SA, SU, TH, TU, WE, WEEKLY, rrule

WEEKDAY_RULES = {"MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA, "SU": SU}


def item_date(item: dict, timezone_name: str) -> date | None:
    value = item.get("start_date") if item["kind"] == "event" else item.get("due_date")
    if value:
        return date.fromisoformat(value)
    value = item.get("start_at") if item["kind"] == "event" else item.get("due_at")
    return (
        datetime.fromisoformat(value).astimezone(ZoneInfo(timezone_name)).date()
        if value
        else None
    )


def base_occurrences(
    item: dict, start_date: date, end_date: date, timezone_name: str
) -> list[datetime]:
    first_date = item_date(item, timezone_name)
    if first_date is None or item["kind"] != "event":
        return []
    zone = ZoneInfo(timezone_name)
    first = (
        datetime.combine(first_date, time.min, zone)
        if item["all_day"]
        else datetime.fromisoformat(item["start_at"]).astimezone(zone)
    )
    until = min(
        end_date,
        date.fromisoformat(item["recurrence_until"])
        if item.get("recurrence_until")
        else end_date,
    )
    if until < start_date:
        return []
    options = {
        "freq": {"daily": DAILY, "weekly": WEEKLY, "monthly": MONTHLY}[
            item["recurrence"]
        ],
        "dtstart": first,
        "until": datetime.combine(until, time.max, zone),
    }
    if item["recurrence"] == "monthly":
        options["bymonthday"] = -1 if item["monthly_on_last_day"] else first.day
    elif item["recurrence"] == "weekly" and item.get("weekdays"):
        options["byweekday"] = [WEEKDAY_RULES[value] for value in item["weekdays"]]
    return list(
        rrule(**options).between(
            datetime.combine(start_date, time.min, zone),
            datetime.combine(until, time.max, zone),
            inc=True,
        )
    )


def occurrence_item(
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
            datetime.fromisoformat(item["end_at"])
            - datetime.fromisoformat(item["start_at"])
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
            result.update(all_day=True, start_date=exception["start_date"], start_at=None, end_at=None)
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
        offset = datetime.fromisoformat(item["reminder_at"]).astimezone(occurrence.tzinfo) - base_start
        result["reminder_at"] = (effective_start + offset).isoformat()
    return result


def validate_month_end(item: dict, timezone_name: str) -> None:
    first = item_date(item, timezone_name)
    if item.get("monthly_on_last_day") and first and first.day != monthrange(first.year, first.month)[1]:
        raise ValueError("Last-day recurrence must start on a month's last day")
