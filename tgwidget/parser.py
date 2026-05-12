from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional

from .types import (
    ColorFormat,
    DateFormat,
    DateMode,
    DateOrder,
    ScheduleFormat,
    SCHEDULE_RANGE_LENGTH,
    SCHEDULE_SINGLE_LENGTH,
    SCHEDULE_SINGLE_DISABLED,
)


def _strip_command(value: str) -> str:
    """Strip Telegram bot command prefix (e.g. '/start ') from value."""
    if value.startswith("/"):
        parts = value.split(None, 1)
        if len(parts) > 1:
            return parts[1]
    return value


def _time_to_seconds(time_str: str) -> int:
    parts = [int(p) for p in time_str.replace(":", "-").split("-")]
    h = parts[0] if len(parts) > 0 else 0
    m = parts[1] if len(parts) > 1 else 0
    s = parts[2] if len(parts) > 2 else 0
    return h * 3600 + m * 60 + s


def _validate_range(
    value: str, mode: DateMode, min_val: Optional[str], max_val: Optional[str]
) -> None:
    if min_val is None and max_val is None:
        return

    if mode in ("time", "time-seconds"):
        sec = _time_to_seconds(value)
        if min_val is not None and sec < _time_to_seconds(min_val):
            raise ValueError(f"Value {value} is below minimum {min_val}")
        if max_val is not None and sec > _time_to_seconds(max_val):
            raise ValueError(f"Value {value} is above maximum {max_val}")
    elif mode in ("date", "datetime"):
        normalized = value.replace("_", "T").replace("-", ":", 2) if "_" in value else value
        try:
            ts = datetime.fromisoformat(normalized.replace("-", ":", 2) if mode == "datetime" else normalized)
        except ValueError:
            return
        if min_val is not None:
            min_norm = min_val.replace("_", "T")
            try:
                if ts < datetime.fromisoformat(min_norm):
                    raise ValueError(f"Value {value} is below minimum {min_val}")
            except (ValueError, TypeError):
                pass
        if max_val is not None:
            max_norm = max_val.replace("_", "T")
            try:
                if ts > datetime.fromisoformat(max_norm):
                    raise ValueError(f"Value {value} is above maximum {max_val}")
            except (ValueError, TypeError):
                pass


@dataclass
class DateResult:
    date: Optional[str] = None
    time: Optional[str] = None
    date_end: Optional[str] = None
    time_end: Optional[str] = None
    timestamp: Optional[int] = None
    timestamp_end: Optional[int] = None
    datetime_obj: Optional[datetime] = None
    datetime_end_obj: Optional[datetime] = None
    date_obj: Optional[date] = None
    date_end_obj: Optional[date] = None
    time_obj: Optional[time] = None
    time_end_obj: Optional[time] = None


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
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    time_str: Optional[str] = None
    time_obj: Optional[time] = None


def _parse_date_str(value: str, order: DateOrder) -> str:
    parts = value.split("-")
    if order == "ymd":
        return f"{parts[0]}-{parts[1]}-{parts[2]}"
    elif order == "dmy":
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    else:  # mdy
        return f"{parts[2]}-{parts[0]}-{parts[1]}"


def parse_date(
    value: str,
    mode: DateMode = "date",
    format: DateFormat = "default",
    order: DateOrder = "ymd",
    *,
    min: Optional[str] = None,
    max: Optional[str] = None,
) -> DateResult:
    """Parse date widget result string back into structured data.

    Raises ValueError if value is outside the min/max range.
    """
    value = _strip_command(value)
    result = DateResult()

    _validate_range(value, mode, min, max)

    if format in ("unix-s", "unix-ms"):
        parts = value.split("_")
        ts_raw = int(parts[0])
        result.timestamp = ts_raw
        ts_seconds = ts_raw if format == "unix-s" else ts_raw / 1000
        dt = datetime.fromtimestamp(ts_seconds)
        result.date = dt.strftime("%Y-%m-%d")
        result.time = dt.strftime("%H:%M")
        result.datetime_obj = dt
        result.date_obj = dt.date()
        result.time_obj = dt.time().replace(second=0, microsecond=0)
        if len(parts) > 1:
            ts_end_raw = int(parts[1])
            result.timestamp_end = ts_end_raw
            ts_end_seconds = ts_end_raw if format == "unix-s" else ts_end_raw / 1000
            dt_end = datetime.fromtimestamp(ts_end_seconds)
            result.date_end = dt_end.strftime("%Y-%m-%d")
            result.time_end = dt_end.strftime("%H:%M")
            result.datetime_end_obj = dt_end
            result.date_end_obj = dt_end.date()
            result.time_end_obj = dt_end.time().replace(second=0, microsecond=0)
        return result

    if mode == "date":
        date_str = _parse_date_str(value, order)
        result.date = date_str
        result.date_obj = date.fromisoformat(date_str)
    elif mode == "time":
        h, m = value.split("-")
        result.time = f"{h}:{m}"
        result.time_obj = time(int(h), int(m))
    elif mode == "time-seconds":
        h, m, s = value.split("-")
        result.time = f"{h}:{m}:{s}"
        result.time_obj = time(int(h), int(m), int(s))
    elif mode == "datetime":
        date_part, time_part = value.split("_")
        date_str = _parse_date_str(date_part, order)
        h, m = time_part.split("-")
        result.date = date_str
        result.time = f"{h}:{m}"
        result.date_obj = date.fromisoformat(date_str)
        result.time_obj = time(int(h), int(m))
        result.datetime_obj = datetime.combine(result.date_obj, result.time_obj)
    elif mode == "date-range":
        parts = value.split("_")
        date_str = _parse_date_str(parts[0], order)
        date_end_str = _parse_date_str(parts[1], order)
        result.date = date_str
        result.date_end = date_end_str
        result.date_obj = date.fromisoformat(date_str)
        result.date_end_obj = date.fromisoformat(date_end_str)
    elif mode == "time-range":
        parts = value.split("_")
        h1, m1 = parts[0].split("-")
        h2, m2 = parts[1].split("-")
        result.time = f"{h1}:{m1}"
        result.time_end = f"{h2}:{m2}"
        result.time_obj = time(int(h1), int(m1))
        result.time_end_obj = time(int(h2), int(m2))

    return result


def parse_color(value: str, format: ColorFormat = "hex") -> ColorResult:
    """Parse color widget result string."""
    value = _strip_command(value)
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


def _detect_schedule_format(value: str, format: ScheduleFormat) -> ScheduleFormat:
    if format != "range":
        return format
    if len(value) == SCHEDULE_SINGLE_LENGTH:
        return "single"
    return "range"


def _parse_range_schedule(value: str) -> list[ScheduleDay]:
    if len(value) != SCHEDULE_RANGE_LENGTH:
        raise ValueError(f"Schedule range format must be {SCHEDULE_RANGE_LENGTH} chars, got {len(value)}")
    if not value.isdigit():
        raise ValueError("Schedule value must contain only digits")
    days: list[ScheduleDay] = []
    for i in range(7):
        chunk = value[i * 8 : (i + 1) * 8]
        if chunk == "00000000":
            days.append(ScheduleDay(enabled=False))
        else:
            start_str = f"{chunk[0:2]}:{chunk[2:4]}"
            end_str = f"{chunk[4:6]}:{chunk[6:8]}"
            days.append(ScheduleDay(
                enabled=True,
                start=start_str,
                end=end_str,
                start_time=time(int(chunk[0:2]), int(chunk[2:4])),
                end_time=time(int(chunk[4:6]), int(chunk[6:8])),
            ))
    return days


def _parse_single_schedule(value: str) -> list[ScheduleDay]:
    if len(value) != SCHEDULE_SINGLE_LENGTH:
        raise ValueError(f"Schedule single format must be {SCHEDULE_SINGLE_LENGTH} chars, got {len(value)}")
    if not value.isdigit():
        raise ValueError("Schedule value must contain only digits")
    days: list[ScheduleDay] = []
    for i in range(7):
        chunk = value[i * 4 : (i + 1) * 4]
        if chunk == SCHEDULE_SINGLE_DISABLED:
            days.append(ScheduleDay(enabled=False))
        else:
            t_str = f"{chunk[0:2]}:{chunk[2:4]}"
            days.append(ScheduleDay(
                enabled=True,
                time_str=t_str,
                time_obj=time(int(chunk[0:2]), int(chunk[2:4])),
            ))
    return days


def parse_schedule(value: str, format: ScheduleFormat = "range") -> list[ScheduleDay]:
    """Parse schedule widget result.

    Supports two formats:
    - 'range': 56 chars (8 per day), each day = HHMMHHMM (start/end range)
    - 'single': 28 chars (4 per day), each day = HHMM (single time point)
    """
    value = _strip_command(value)
    resolved = _detect_schedule_format(value, format)
    if resolved == "single":
        return _parse_single_schedule(value)
    return _parse_range_schedule(value)
