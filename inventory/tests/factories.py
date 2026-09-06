from datetime import date, timedelta

import factory

from inventory.models import Booking, Vehicle


class VehicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehicle

    name = factory.Sequence(lambda n: f"Model {n}")
    brand = "Toyota"
    year = 2022
    price_per_day = "50.00"
    fuel_type = Vehicle.FuelType.PETROL
    is_available = True


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    vehicle = factory.SubFactory(VehicleFactory)
    customer_name = "Jane Doe"
    customer_phone = "9876543210"
    start_date = factory.LazyFunction(lambda: date.today() + timedelta(days=1))
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=3))
    total_amount = "100.00"
