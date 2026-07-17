# tgwidget

Python SDK for [TeleWidget](https://tgwidget.github.io/) — beautiful Telegram Mini App widgets for bots.

## Install

```bash
pip install tgwidget
```

## Usage

### Generate widget URL

```python
from tgwidget import TgWidget

# Date picker
url = TgWidget("your_bot").date(mode="datetime", format="unix-s").url()

# Color picker
url = TgWidget("your_bot").color(format="hex").url()

# Schedule (range — time windows per day)
url = TgWidget("your_bot").schedule().url()

# Schedule (single — fixed time per day)
url = TgWidget("your_bot").schedule(format="single").url()

# With styling
url = (
    TgWidget("your_bot")
    .date(mode="date")
    .style(color_scheme="dark", accent="#FF6600", adopt_tg_palette=True)
    .url()
)
```

### Parse results

When a user completes the widget, the result comes back via deep link `t.me/your_bot?start=VALUE`. Parse the value:

```python
from tgwidget import parse_date, parse_color, parse_schedule

# Date result — returns native datetime.date object
result = parse_date("2025-03-15", mode="date")
# result.date == '2025-03-15'
# result.date_obj == datetime.date(2025, 3, 15)

# Datetime — returns native datetime object
result = parse_date("2025-03-15_14-30", mode="datetime")
# result.datetime_obj == datetime.datetime(2025, 3, 15, 14, 30)
# result.date_obj == datetime.date(2025, 3, 15)
# result.time_obj == datetime.time(14, 30)

# Time — returns native datetime.time
result = parse_date("14-30", mode="time")
# result.time_obj == datetime.time(14, 30)

# Date range with unix timestamps
result = parse_date("1710460800_1718236800", mode="date-range", format="unix-s")
# result.datetime_obj, result.datetime_end_obj — native datetime objects

# Color result
result = parse_color("FF6600", format="hex")
# ColorResult(raw='FF6600', hex='#FF6600')

# Schedule result — range (56-char range format)
result = parse_schedule("09001800090018000000000009001800090018000000000000000000")
# [ScheduleDay(enabled=True, start='09:00', end='18:00',
#              start_time=datetime.time(9, 0), end_time=datetime.time(18, 0)), ...]

# Schedule result — single (28-char single format)
result = parse_schedule("1200120099991200120099999999", format="single")
# [ScheduleDay(enabled=True, time_str='12:00', time_obj=datetime.time(12, 0)), ...]
```

All parsers automatically handle Telegram bot command prefixes — you can pass raw `/start payload` strings directly:

```python
result = parse_date("/start 2025-03-15", mode="date")
# result.date_obj == datetime.date(2025, 3, 15)

result = parse_color("/start FF6600", format="hex")
# result.hex == '#FF6600'
```

> **⚠️ `datetime_obj`/`date_obj`/`time_obj` are naive for `format="default"`.**
> They carry no `tzinfo` — they're the literal digits the picker sent, not
> an absolute instant. If you need an actual moment in time (e.g. to store
> and compare against `datetime.now()` elsewhere, like a scheduled-send
> time), call `.timestamp()` or `.astimezone()` on them rather than assuming
> they're already UTC: for a naive `datetime`, Python interprets it as the
> **host process's local timezone** (`TZ` env var / system setting) when
> doing either conversion. Treating it as UTC instead — e.g.
> `calendar.timegm(dt.timetuple())` — silently produces a value shifted by
> your host's UTC offset. This is standard `datetime` behavior, not
> something this library adds, but it's an easy trap: pin your process's
> `TZ` to whatever zone your users pick dates in, and let naive datetimes
> flow through `.timestamp()`/`.astimezone()` rather than reimplementing
> the conversion yourself.
>
> `format="unix-s"`/`"unix-ms"` sidestep this entirely — `datetime_obj` is
> already timezone-aware (`tzinfo=timezone.utc`), since it's derived from
> an unambiguous timestamp rather than raw digits.

### Date options

The `.date()` method accepts extra keyword arguments for controlling initial state and validation:

```python
# Duration picker: no auto-select, starts at 00:00:00
url = TgWidget("your_bot").date(mode="time-seconds", auto_now=False).url()

# Duration with custom default
url = TgWidget("your_bot").date(mode="time-seconds", auto_now=False, default="01-30-00").url()

# Time picker with allowed range
url = TgWidget("your_bot").date(mode="time", min="09-00", max="18-00").url()

# Range validation in parser
widget = TgWidget("your_bot").date(mode="time-seconds", min="00-00-00", max="23-59-59")
widget.parse("25-00-00")  # raises ValueError
```

| Option | Type | Description |
|--------|------|-------------|
| `auto_now` | `bool` | Auto-select current time on open. Default: `True` for time/datetime, not set otherwise. |
| `default` | `str` | Default value in widget format (e.g. `"01-30-00"`). Used when `auto_now` is `False`. |
| `min` | `str` | Minimum allowed value. Validated both in frontend and by SDK parser. |
| `max` | `str` | Maximum allowed value. Validated both in frontend and by SDK parser. |

### Pattern (informational format string)

Each widget exposes a `.pattern` property — a human-readable format hint you can show to users:

```python
widget = TgWidget("your_bot").date(mode="datetime")
widget.pattern  # "YYYY-MM-DD HH:MM"

widget2 = TgWidget("your_bot").date(mode="date", order="dmy")
widget2.pattern  # "DD-MM-YYYY"

widget3 = TgWidget("your_bot").color(format="hex")
widget3.pattern  # "#RRGGBB"

# Use in bot messages:
await ctx.reply(f"Введите дату в формате {widget.pattern}")
```

You can also use the standalone `get_pattern(widget, mode, format, order)` function directly.

### Widget-level parsing with `parse()`

If you keep a reference to the widget builder, you can call `.parse()` directly — it automatically uses the configured widget type and options:

```python
widget = TgWidget("your_bot").date(mode="datetime")
url = widget.url()

# Later, when the user completes the widget:
result = widget.parse("/start 2025-03-15_14-30")
# result.datetime_obj == datetime.datetime(2025, 3, 15, 14, 30)
```

## API

### `TgWidget(bot_username)`

Create a widget builder.

- `.date(mode, format, order, *, auto_now, default, min, max)` — Date/time picker
- `.color(format)` — Color picker
- `.schedule(format)` — Weekly schedule (format: `'range'` | `'single'`)
- `.style(color_scheme, accent, tint, liquid_glass, adapt_tg_theme, adopt_tg_palette)` — Styling
- `.url(base_url)` — Generate the final URL
- `.payload()` — Get the raw payload dict
- `.pattern` — Human-readable format string (e.g. `"YYYY-MM-DD HH:MM"`)
- `.parse(value)` — Parse a widget result string (auto-detects parser from widget type)

### Parsers

- `parse_date(value, mode, format, order, *, min, max)` → `DateResult` (raises `ValueError` if outside min/max)
- `parse_color(value, format)` → `ColorResult`
- `parse_schedule(value, format)` → `list[ScheduleDay]`

### Result types

#### `DateResult`
- `date`, `time`, `date_end`, `time_end` — string representations
- `timestamp`, `timestamp_end` — raw integer timestamps (unix modes)
- `datetime_obj`, `datetime_end_obj` — native `datetime.datetime` (naive for `format="default"`, `tzinfo=timezone.utc` for unix formats — see warning above)
- `date_obj`, `date_end_obj` — native `datetime.date`
- `time_obj`, `time_end_obj` — native `datetime.time`

#### `ColorResult`
- `raw` — original value string
- `hex` — e.g. `'#FF6600'`
- `rgb` — e.g. `(255, 102, 0)`
- `hsl` — e.g. `(24, 100, 50)`

#### `ScheduleDay`
- `enabled` — whether the day is active
- `start`, `end` — time strings e.g. `'09:00'` (range format)
- `start_time`, `end_time` — native `datetime.time` (range format)
- `time_str` — single time string e.g. `'12:00'` (single format)
- `time_obj` — native `datetime.time` (single format)
