"""Business logic for creating bookings.

Kept out of serializers/views so the booking rules (overlap checking,
pricing, availability toggling) live in one place and are unit-testable in
isolation from the HTTP layer.
"""
from datetime import date
from decimal import Decimal

from django.db import transaction

from inventory.exceptions import VehicleUnavailableError
from inventory.models import Booking, Vehicle


def _has_overlapping_booking(vehicle: Vehicle, start_date: date, end_date: date) -> bool:
    return vehicle.bookings.filter(
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()


def _calculate_total_amount(vehicle: Vehicle, start_date: date, end_date: date) -> Decimal:
    days = (end_date - start_date).days
    return vehicle.price_per_day * days


@transaction.atomic
def create_booking(
    *,
    vehicle_id: int,
    customer_name: str,
    customer_phone: str,
    start_date: date,
    end_date: date,
) -> Booking:
    """Validate booking rules and persist a booking, locking the vehicle row
    for the duration of the transaction to prevent concurrent double-booking.
    """
    vehicle = Vehicle.objects.select_for_update().get(pk=vehicle_id)

    if _has_overlapping_booking(vehicle, start_date, end_date):
        raise VehicleUnavailableError(
            "This vehicle is already booked for an overlapping date range.",
            field="vehicle",
        )

    booking = Booking.objects.create(
        vehicle=vehicle,
        customer_name=customer_name,
        customer_phone=customer_phone,
        start_date=start_date,
        end_date=end_date,
        total_amount=_calculate_total_amount(vehicle, start_date, end_date),
    )

    vehicle.is_available = False
    vehicle.save(update_fields=["is_available", "updated_at"])

    return booking
