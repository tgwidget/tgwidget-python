from typing import Literal

DateMode = Literal["date", "time", "datetime", "date-range", "time-range"]
DateFormat = Literal["default", "unix-s", "unix-ms"]
DateOrder = Literal["ymd", "dmy", "mdy"]
ColorFormat = Literal["hex", "rgb", "hsl"]
ColorScheme = Literal["light", "dark", "auto"]
ScheduleFormat = Literal["bunch"]

VALID_DATE_MODES = {"date", "time", "datetime", "date-range", "time-range"}
VALID_DATE_FORMATS = {"default", "unix-s", "unix-ms"}
VALID_DATE_ORDERS = {"ymd", "dmy", "mdy"}
VALID_COLOR_FORMATS = {"hex", "rgb", "hsl"}
VALID_COLOR_SCHEMES = {"light", "dark", "auto"}
