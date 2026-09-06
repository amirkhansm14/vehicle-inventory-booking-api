from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.db.utils import DataError

from inventory.tests.factories import BookingFactory, VehicleFactory

pytestmark = pytest.mark.django_db


def test_vehicle_str_representation():
    vehicle = VehicleFactory(name="Corolla", brand="Toyota", year=2023)
    assert str(vehicle) == "2023 Toyota Corolla"


def test_vehicle_rejects_non_positive_price():
    vehicle = VehicleFactory.build(price_per_day=Decimal("0.00"))
    with pytest.raises((IntegrityError, DataError)):
        vehicle.save()


def test_booking_duration_in_days():
    booking = BookingFactory(
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=4),
    )
    assert booking.duration_in_days == 3


def test_booking_rejects_end_date_not_after_start_date():
    vehicle = VehicleFactory()
    booking = BookingFactory.build(
        vehicle=vehicle,
        start_date=date.today() + timedelta(days=2),
        end_date=date.today() + timedelta(days=2),
        total_amount=Decimal("50.00"),
    )
    with pytest.raises(IntegrityError):
        booking.save()
