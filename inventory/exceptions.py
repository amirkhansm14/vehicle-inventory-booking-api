"""Domain-level exceptions raised by the service layer.

These are translated into DRF ``ValidationError`` responses by
``domain_exception_handler`` so services stay framework-agnostic while
views/serializers still return the usual DRF error shape.
"""
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


class BookingError(Exception):
    """Base class for booking business-rule violations."""

    def __init__(self, message: str, field: str = "non_field_errors"):
        self.message = message
        self.field = field
        super().__init__(message)


class VehicleUnavailableError(BookingError):
    """Raised when a vehicle has an overlapping booking for the requested dates."""


def domain_exception_handler(exc, context):
    if isinstance(exc, BookingError):
        exc = ValidationError({exc.field: [exc.message]})
    return exception_handler(exc, context)
