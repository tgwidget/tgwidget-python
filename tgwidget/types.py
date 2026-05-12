from typing import Literal, get_args

DateMode = Literal["date", "time", "time-seconds", "datetime", "date-range", "time-range"]
DateFormat = Literal["default", "unix-s", "unix-ms"]
DateOrder = Literal["ymd", "dmy", "mdy"]
ColorFormat = Literal["hex", "rgb", "hsl"]
ColorScheme = Literal["light", "dark", "auto"]
ScheduleFormat = Literal["range", "single"]

VALID_DATE_MODES: set[str] = set(get_args(DateMode))
VALID_DATE_FORMATS: set[str] = set(get_args(DateFormat))
VALID_DATE_ORDERS: set[str] = set(get_args(DateOrder))
VALID_COLOR_FORMATS: set[str] = set(get_args(ColorFormat))
VALID_COLOR_SCHEMES: set[str] = set(get_args(ColorScheme))
VALID_SCHEDULE_FORMATS: set[str] = set(get_args(ScheduleFormat))

SCHEDULE_RANGE_LENGTH = 56
SCHEDULE_SINGLE_LENGTH = 28
SCHEDULE_SINGLE_DISABLED = "9999"
