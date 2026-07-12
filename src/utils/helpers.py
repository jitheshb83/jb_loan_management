"""Helper functions for formatting and common operations."""

from datetime import date, datetime

_UNSET = object()


def to_datetime(value, default=_UNSET) -> datetime:
    """
    Normalize a date-like value (str, date, or datetime) to a datetime.

    QDateEdit.date().toPython() returns a plain `datetime.date`, which is
    NOT an instance of `datetime.datetime` — a naive `isinstance(x, datetime)`
    check misses it and silently falls back to "now", discarding whatever
    date the user actually picked. This is the single place that conversion
    should happen.

    `default` is returned as-is (including None) when `value` can't be
    parsed; if omitted entirely, falls back to `datetime.now()`.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    elif isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    return datetime.now() if default is _UNSET else default


def format_currency(amount: float, currency: str = "₹") -> str:
    """Format amount as currency."""
    return f"{currency}{amount:,.2f}"


def format_date(date: datetime, format_str: str = "%d-%m-%Y") -> str:
    """Format datetime to string."""
    if isinstance(date, datetime):
        return date.strftime(format_str)
    return str(date)


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format value as percentage."""
    return f"{value:.{decimal_places}f}%"


def months_to_years_months(months: int) -> tuple:
    """Convert months to years and remaining months."""
    years = months // 12
    remaining_months = months % 12
    return years, remaining_months


def format_duration(months: int) -> str:
    """Format duration in months as readable string."""
    years, remaining_months = months_to_years_months(months)
    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years > 1 else ''}")
    if remaining_months > 0:
        parts.append(f"{remaining_months} month{'s' if remaining_months > 1 else ''}")
    return " ".join(parts) if parts else "0 months"
