from __future__ import annotations

import json
import re
from base64 import b64encode
from typing import Any, List, Optional, Union

from .parser import ColorResult, DateResult, ScheduleDay, parse_color, parse_date, parse_schedule
from .pattern import get_pattern
from .types import (
    MAX_UTC_OFFSET_MINUTES,
    MIN_UTC_OFFSET_MINUTES,
    VALID_COLOR_FORMATS,
    VALID_COLOR_SCHEMES,
    VALID_DATE_FORMATS,
    VALID_DATE_MODES,
    VALID_DATE_ORDERS,
    VALID_SCHEDULE_FORMATS,
    ColorFormat,
    ColorScheme,
    DateFormat,
    DateMode,
    DateOrder,
    ScheduleFormat,
    is_valid_utc_offset,
)

BASE_URL = "https://tgwidget.github.io/"

_HEX_RE = re.compile(r"^#?[0-9A-Fa-f]{6}$")


def _validate_hex(color: str, name: str) -> str:
    if not _HEX_RE.match(color):
        raise ValueError(f"{name} must be a valid hex color (e.g. '#FF0000'), got '{color}'")
    return color if color.startswith("#") else f"#{color}"


class TgWidget:
    """Builder for TeleWidget URLs."""

    def __init__(self, bot_username: str) -> None:
        if not bot_username:
            raise ValueError("bot_username is required")
        self._bot_username = bot_username
        self._widget: Optional[str] = None
        self._payload: dict[str, Any] = {}
        self._style: dict[str, Any] = {}

    def date(
        self,
        mode: DateMode = "date",
        format: DateFormat = "default",
        order: DateOrder = "ymd",
        *,
        auto_now: Optional[bool] = None,
        default: Optional[str] = None,
        min: Optional[str] = None,
        max: Optional[str] = None,
        utc_offset: Optional[int] = None,
    ) -> TgWidget:
        if mode not in VALID_DATE_MODES:
            raise ValueError(f"Invalid date mode '{mode}'. Must be one of: {VALID_DATE_MODES}")
        if format not in VALID_DATE_FORMATS:
            raise ValueError(f"Invalid date format '{format}'. Must be one of: {VALID_DATE_FORMATS}")
        if order not in VALID_DATE_ORDERS:
            raise ValueError(f"Invalid date order '{order}'. Must be one of: {VALID_DATE_ORDERS}")
        if utc_offset is not None and not is_valid_utc_offset(utc_offset):
            raise ValueError(
                f"Invalid utc_offset '{utc_offset}'. Must be an integer number of minutes between "
                f"{MIN_UTC_OFFSET_MINUTES} and {MAX_UTC_OFFSET_MINUTES}."
            )
        self._widget = "date"
        self._payload = {"mode": mode, "format": format, "order": order}
        if auto_now is not None:
            self._payload["autoNow"] = auto_now
        if default is not None:
            self._payload["default"] = default
        if min is not None:
            self._payload["min"] = min
        if max is not None:
            self._payload["max"] = max
        if utc_offset is not None:
            self._payload["utcOffset"] = utc_offset
        return self

    def color(self, format: ColorFormat = "hex") -> TgWidget:
        if format not in VALID_COLOR_FORMATS:
            raise ValueError(f"Invalid color format '{format}'. Must be one of: {VALID_COLOR_FORMATS}")
        self._widget = "color"
        self._payload = {"format": format}
        return self

    def schedule(self, format: ScheduleFormat = "range") -> TgWidget:
        if format not in VALID_SCHEDULE_FORMATS:
            raise ValueError(f"Invalid schedule format '{format}'. Must be one of: {VALID_SCHEDULE_FORMATS}")
        self._widget = "schedule"
        self._payload = {"format": format}
        return self

    def style(
        self,
        *,
        color_scheme: ColorScheme = "light",
        accent: Optional[str] = None,
        tint: Optional[str] = None,
        liquid_glass: bool = False,
        adapt_tg_theme: bool = False,
        adopt_tg_palette: bool = False,
    ) -> TgWidget:
        if color_scheme not in VALID_COLOR_SCHEMES:
            raise ValueError(f"Invalid color_scheme '{color_scheme}'. Must be one of: {VALID_COLOR_SCHEMES}")
        self._style = {
            "colorScheme": color_scheme,
            "liquidGlass": liquid_glass,
            "adaptTgTheme": adapt_tg_theme,
            "adoptTgPalette": adopt_tg_palette,
        }
        if accent:
            self._style["accent"] = _validate_hex(accent, "accent")
        if tint:
            self._style["tint"] = _validate_hex(tint, "tint")
        return self

    def _build_payload(self) -> dict[str, Any]:
        if not self._widget:
            raise ValueError("No widget type set. Call .date(), .color(), or .schedule() first.")
        payload: dict[str, Any] = {
            "widget": self._widget,
            "bot_username": self._bot_username,
            **self._payload,
        }
        if self._style:
            payload["style"] = self._style
        return payload

    def url(self, base_url: str = BASE_URL) -> str:
        payload = self._build_payload()
        encoded = b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
        return f"{base_url}?p={encoded}"

    def payload(self) -> dict[str, Any]:
        return self._build_payload()

    @property
    def pattern(self) -> str:
        """Human-readable format pattern for the current widget configuration."""
        if not self._widget:
            raise ValueError("No widget type set. Call .date(), .color(), or .schedule() first.")
        return get_pattern(
            self._widget,
            mode=self._payload.get("mode"),
            format=self._payload.get("format"),
            order=self._payload.get("order"),
        )

    def parse(self, value: str) -> Union[DateResult, ColorResult, List[ScheduleDay]]:
        """Parse widget result using the configured widget type and options."""
        if self._widget == "date":
            return parse_date(
                value,
                mode=self._payload.get("mode", "date"),
                format=self._payload.get("format", "default"),
                order=self._payload.get("order", "ymd"),
                min=self._payload.get("min"),
                max=self._payload.get("max"),
                utc_offset=self._payload.get("utcOffset"),
            )
        elif self._widget == "color":
            return parse_color(value, format=self._payload.get("format", "hex"))
        elif self._widget == "schedule":
            return parse_schedule(value, format=self._payload.get("format", "range"))
        raise ValueError("No widget type set. Call .date(), .color(), or .schedule() first.")
