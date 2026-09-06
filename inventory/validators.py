"""Reusable field-level validators shared by models and serializers."""
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="Phone number must be exactly 10 digits.",
)


def validate_not_in_the_past(value: date) -> None:
    if value < date.today():
        raise ValidationError("Date cannot be in the past.")


def validate_year_is_reasonable(value: int) -> None:
    current_year = date.today().year
    if value < 1900 or value > current_year + 1:
        raise ValidationError(
            f"Year must be between 1900 and {current_year + 1}."
        )
