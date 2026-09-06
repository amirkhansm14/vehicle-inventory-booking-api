from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from inventory.validators import (
    phone_number_validator,
    validate_not_in_the_past,
    validate_year_is_reasonable,
)


class Vehicle(models.Model):
    class FuelType(models.TextChoices):
        PETROL = "petrol", "Petrol"
        DIESEL = "diesel", "Diesel"
        ELECTRIC = "electric", "Electric"
        HYBRID = "hybrid", "Hybrid"

    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, db_index=True)
    year = models.IntegerField(validators=[validate_year_is_reasonable])
    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    fuel_type = models.CharField(
        max_length=20, choices=FuelType.choices, db_index=True
    )
    is_available = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price_per_day__gt=0),
                name="vehicle_price_per_day_positive",
            ),
        ]
        indexes = [
            models.Index(fields=["brand", "fuel_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.year} {self.brand} {self.name}"


class Booking(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.PROTECT, related_name="bookings"
    )
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(
        max_length=10, validators=[phone_number_validator]
    )
    start_date = models.DateField(validators=[validate_not_in_the_past])
    end_date = models.DateField()
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F("start_date")),
                name="booking_end_date_after_start_date",
            ),
            models.CheckConstraint(
                check=models.Q(total_amount__gt=0),
                name="booking_total_amount_positive",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "start_date", "end_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.customer_name} — {self.vehicle} ({self.start_date} to {self.end_date})"

    @property
    def duration_in_days(self) -> int:
        return (self.end_date - self.start_date).days
