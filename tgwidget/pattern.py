from typing import Optional

from .types import DateMode, DateOrder

_DATE_PATTERNS: dict[str, str] = {
    "ymd": "YYYY-MM-DD",
    "dmy": "DD-MM-YYYY",
    "mdy": "MM-DD-YYYY",
}

_TIME_PATTERN = "HH-MM"


def get_pattern(
    widget: str,
    mode: Optional[str] = None,
    format: Optional[str] = None,
    order: Optional[str] = None,
) -> str:
    """Return a human-readable format pattern for the given widget configuration."""
    if widget == "date":
        date_pat = _DATE_PATTERNS.get(order or "ymd", "YYYY-MM-DD")
        m = mode or "date"
        if m == "date":
            return date_pat
        if m == "time":
            return _TIME_PATTERN
        if m == "datetime":
            return f"{date_pat}_{_TIME_PATTERN}"
        if m == "date-range":
            return f"{date_pat}_{date_pat}"
        if m == "time-range":
            return f"{_TIME_PATTERN}_{_TIME_PATTERN}"

    if widget == "color":
        fmt = format or "hex"
        if fmt == "hex":
            return "#RRGGBB"
        if fmt == "rgb":
            return "R, G, B"
        if fmt == "hsl":
            return "H, S, L"

    if widget == "schedule":
        return "HH:MM—HH:MM × 7 days"

    return ""
