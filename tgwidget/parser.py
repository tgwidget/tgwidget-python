from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional

from .types import ColorFormat, DateFormat, DateMode, DateOrder


@dataclass
class DateResult:
    date: Optional[str] = None
    time: Optional[str] = None
    date_end: Optional[str] = None
    time_end: Optional[str] = None
    timestamp: Optional[int] = None
    timestamp_end: Optional[int] = None


@dataclass
class ColorResult:
    raw: str
    hex: Optional[str] = None
    rgb: Optional[tuple[int, int, int]] = None
    hsl: Optional[tuple[int, int, int]] = None


@dataclass
class ScheduleDay:
    enabled: bool
    start: Optional[str] = None
    end: Optional[str] = None


@dataclass
class ScheduleResult:
    days: list[ScheduleDay]


def parse_date(
    value: str,
    mode: DateMode = "date",
    format: DateFormat = "default",
    order: DateOrder = "ymd",
) -> DateResult:
    """Parse date widget result string back into structured data."""
    result = DateResult()

    if format in ("unix-s", "unix-ms"):
        parts = value.split("_")
        div = 1000 if format == "unix-s" else 1
        ts = int(parts[0]) * div if format == "unix-s" else int(parts[0])
        result.timestamp = int(parts[0])
        if len(parts) > 1:
            result.timestamp_end = int(parts[1])
        dt = datetime.fromtimestamp(ts / 1000)
        result.date = dt.strftime("%Y-%m-%d")
        result.time = dt.strftime("%H:%M")
        if result.timestamp_end is not None:
            ts_end = int(parts[1]) * div if format == "unix-s" else int(parts[1])
            dt_end = datetime.fromtimestamp(ts_end / 1000)
            result.date_end = dt_end.strftime("%Y-%m-%d")
            result.time_end = dt_end.strftime("%H:%M")
        return result

    if mode == "date":
        result.date = _parse_date_str(value, order)
    elif mode == "time":
        h, m = value.split("-")
        result.time = f"{h}:{m}"
    elif mode == "datetime":
        date_part, time_part = value.split("_")
        result.date = _parse_date_str(date_part, order)
        h, m = time_part.split("-")
        result.time = f"{h}:{m}"
    elif mode == "date-range":
        parts = value.split("_")
        result.date = _parse_date_str(parts[0], order)
        result.date_end = _parse_date_str(parts[1], order)
    elif mode == "time-range":
        parts = value.split("_")
        h1, m1 = parts[0].split("-")
        h2, m2 = parts[1].split("-")
        result.time = f"{h1}:{m1}"
        result.time_end = f"{h2}:{m2}"

    return result


def _parse_date_str(value: str, order: DateOrder) -> str:
    parts = value.split("-")
    if order == "ymd":
        return f"{parts[0]}-{parts[1]}-{parts[2]}"
    elif order == "dmy":
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    else:  # mdy
        return f"{parts[2]}-{parts[0]}-{parts[1]}"


def parse_color(value: str, format: ColorFormat = "hex") -> ColorResult:
    """Parse color widget result string."""
    result = ColorResult(raw=value)
    if format == "hex":
        result.hex = f"#{value}"
    elif format == "rgb":
        parts = value.split("_")
        result.rgb = (int(parts[0]), int(parts[1]), int(parts[2]))
    elif format == "hsl":
        parts = value.split("_")
        result.hsl = (int(parts[0]), int(parts[1]), int(parts[2]))
    return result


def parse_schedule(value: str) -> ScheduleResult:
    """Parse schedule widget result (bunch format: 56 chars, 8 per day)."""
    if len(value) != 56:
        raise ValueError(f"Schedule bunch format must be 56 chars, got {len(value)}")
    days: list[ScheduleDay] = []
    for i in range(7):
        chunk = value[i * 8 : (i + 1) * 8]
        if chunk == "00000000":
            days.append(ScheduleDay(enabled=False))
        else:
            start = f"{chunk[0:2]}:{chunk[2:4]}"
            end = f"{chunk[4:6]}:{chunk[6:8]}"
            days.append(ScheduleDay(enabled=True, start=start, end=end))
    return days
