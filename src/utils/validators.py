"""Input validation utilities."""

from datetime import date, datetime


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_loan_input(
    principal: float,
    annual_rate: float,
    tenure_months: int,
    start_date: datetime
) -> bool:
    """Validate loan input parameters."""
    if not validate_amount(principal):
        raise ValidationError("Principal amount must be a positive number")

    if annual_rate < 0 or annual_rate > 100:
        raise ValidationError("Annual rate must be between 0 and 100")

    if tenure_months <= 0:
        raise ValidationError("Tenure must be greater than 0 months")

    if not validate_date(start_date):
        raise ValidationError("Invalid start date")

    return True


def validate_amount(amount: float) -> bool:
    """Validate that amount is a positive number."""
    try:
        amount_float = float(amount)
        return amount_float > 0
    except (ValueError, TypeError):
        return False


def validate_date(value) -> bool:
    """Validate a date-like value (datetime, date, or ISO string).

    Accepts plain `datetime.date` too — QDateEdit.date().toPython() returns
    a `date`, not a `datetime`, and it is a perfectly valid loan date.
    """
    if isinstance(value, (datetime, date)):
        return True
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False
    return False


def validate_percentage(value: float, min_val: float = 0, max_val: float = 100) -> bool:
    """Validate percentage value."""
    try:
        val_float = float(value)
        return min_val <= val_float <= max_val
    except (ValueError, TypeError):
        return False
