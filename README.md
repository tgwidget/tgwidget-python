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

# Schedule
url = TgWidget("your_bot").schedule().url()

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

# Date result
result = parse_date("2025-03-15", mode="date")
# DateResult(date='2025-03-15', time=None, ...)

# Date range with unix timestamps
result = parse_date("1710460800_1718236800", mode="date-range", format="unix-s")
# DateResult(timestamp=1710460800, timestamp_end=1718236800, date='2025-03-15', ...)

# Color result
result = parse_color("FF6600", format="hex")
# ColorResult(raw='FF6600', hex='#FF6600')

# Schedule result (56-char bunch format)
result = parse_schedule("09001800090018000000000009001800090018000000000000000000")
# [ScheduleDay(enabled=True, start='09:00', end='18:00'), ...]
```

## API

### `TgWidget(bot_username)`

Create a widget builder.

- `.date(mode, format, order)` — Date/time picker
- `.color(format)` — Color picker
- `.schedule()` — Weekly schedule
- `.style(color_scheme, accent, tint, liquid_glass, adapt_tg_theme, adopt_tg_palette)` — Styling
- `.url(base_url)` — Generate the final URL
- `.payload()` — Get the raw payload dict

### Parsers

- `parse_date(value, mode, format, order)` → `DateResult`
- `parse_color(value, format)` → `ColorResult`
- `parse_schedule(value)` → `list[ScheduleDay]`
