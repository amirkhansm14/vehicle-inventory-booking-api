from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from inventory.models import Booking
from inventory.tests.factories import BookingFactory, VehicleFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def _booking_payload(vehicle, **overrides):
    payload = {
        "vehicle": vehicle.id,
        "customer_name": "John Smith",
        "customer_phone": "9123456789",
        "start_date": (date.today() + timedelta(days=1)).isoformat(),
        "end_date": (date.today() + timedelta(days=4)).isoformat(),
    }
    payload.update(overrides)
    return payload


def test_create_booking_calculates_total_and_marks_vehicle_unavailable(client):
    vehicle = VehicleFactory(price_per_day=Decimal("50.00"), is_available=True)

    response = client.post(reverse("booking-list"), _booking_payload(vehicle))

    assert response.status_code == status.HTTP_201_CREATED
    assert Decimal(response.data["total_amount"]) == Decimal("150.00")

    vehicle.refresh_from_db()
    assert vehicle.is_available is False


def test_create_booking_rejects_overlapping_dates(client):
    vehicle = VehicleFactory()
    BookingFactory(
        vehicle=vehicle,
        start_date=date.today() + timedelta(days=2),
        end_date=date.today() + timedelta(days=6),
    )

    overlapping_payload = _booking_payload(
        vehicle,
        start_date=(date.today() + timedelta(days=4)).isoformat(),
        end_date=(date.today() + timedelta(days=8)).isoformat(),
    )
    response = client.post(reverse("booking-list"), overlapping_payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "vehicle" in response.data


def test_create_booking_allows_non_overlapping_dates_for_same_vehicle(client):
    vehicle = VehicleFactory()
    BookingFactory(
        vehicle=vehicle,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=3),
    )

    non_overlapping_payload = _booking_payload(
        vehicle,
        start_date=(date.today() + timedelta(days=3)).isoformat(),
        end_date=(date.today() + timedelta(days=5)).isoformat(),
    )
    response = client.post(reverse("booking-list"), non_overlapping_payload)

    assert response.status_code == status.HTTP_201_CREATED


def test_create_booking_rejects_start_date_in_the_past(client):
    vehicle = VehicleFactory()

    payload = _booking_payload(
        vehicle, start_date=(date.today() - timedelta(days=1)).isoformat()
    )
    response = client.post(reverse("booking-list"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "start_date" in response.data


def test_create_booking_rejects_end_date_not_after_start_date(client):
    vehicle = VehicleFactory()
    same_day = (date.today() + timedelta(days=1)).isoformat()

    payload = _booking_payload(vehicle, start_date=same_day, end_date=same_day)
    response = client.post(reverse("booking-list"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "end_date" in response.data


@pytest.mark.parametrize("phone", ["12345", "12345678901", "abcdefghij"])
def test_create_booking_rejects_invalid_phone_number(client, phone):
    vehicle = VehicleFactory()

    payload = _booking_payload(vehicle, customer_phone=phone)
    response = client.post(reverse("booking-list"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "customer_phone" in response.data


def test_list_and_retrieve_bookings(client):
    booking = BookingFactory()

    list_response = client.get(reverse("booking-list"))
    assert list_response.status_code == status.HTTP_200_OK
    assert list_response.data["count"] == 1

    detail_response = client.get(reverse("booking-detail", args=[booking.id]))
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.data["vehicle"]["id"] == booking.vehicle.id


def test_booking_list_does_not_expose_update_or_delete(client):
    booking = BookingFactory()
    detail_url = reverse("booking-detail", args=[booking.id])

    assert client.put(detail_url, {}).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert client.delete(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert Booking.objects.filter(id=booking.id).exists()
