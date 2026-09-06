import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from inventory.models import Vehicle
from inventory.tests.factories import VehicleFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def test_list_vehicles(client):
    VehicleFactory.create_batch(3)

    response = client.get(reverse("vehicle-list"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3


def test_filter_vehicles_by_brand(client):
    VehicleFactory(brand="Toyota")
    VehicleFactory(brand="Honda")

    response = client.get(reverse("vehicle-list"), {"brand": "toyota"})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["brand"] == "Toyota"


def test_filter_vehicles_by_fuel_type_and_availability(client):
    VehicleFactory(fuel_type=Vehicle.FuelType.ELECTRIC, is_available=True)
    VehicleFactory(fuel_type=Vehicle.FuelType.ELECTRIC, is_available=False)
    VehicleFactory(fuel_type=Vehicle.FuelType.PETROL, is_available=True)

    response = client.get(
        reverse("vehicle-list"), {"fuel_type": "electric", "is_available": "true"}
    )

    assert response.data["count"] == 1


def test_create_vehicle(client):
    payload = {
        "name": "Civic",
        "brand": "Honda",
        "year": 2023,
        "price_per_day": "45.00",
        "fuel_type": "petrol",
    }

    response = client.post(reverse("vehicle-list"), payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert Vehicle.objects.filter(name="Civic").exists()


def test_create_vehicle_rejects_invalid_year(client):
    payload = {
        "name": "Civic",
        "brand": "Honda",
        "year": 1800,
        "price_per_day": "45.00",
        "fuel_type": "petrol",
    }

    response = client.post(reverse("vehicle-list"), payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "year" in response.data


def test_retrieve_update_delete_vehicle(client):
    vehicle = VehicleFactory()

    detail_url = reverse("vehicle-detail", args=[vehicle.id])
    assert client.get(detail_url).status_code == status.HTTP_200_OK

    update_response = client.put(
        detail_url,
        {
            "name": "Updated",
            "brand": vehicle.brand,
            "year": vehicle.year,
            "price_per_day": "60.00",
            "fuel_type": vehicle.fuel_type,
        },
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.data["name"] == "Updated"

    delete_response = client.delete(detail_url)
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert not Vehicle.objects.filter(id=vehicle.id).exists()
