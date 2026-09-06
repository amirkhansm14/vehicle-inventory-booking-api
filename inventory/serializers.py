from datetime import date

from rest_framework import serializers

from inventory.models import Booking, Vehicle
from inventory.services.booking_service import create_booking


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "name",
            "brand",
            "year",
            "price_per_day",
            "fuel_type",
            "is_available",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VehicleBriefSerializer(serializers.ModelSerializer):
    """Compact vehicle representation nested inside a booking response."""

    class Meta:
        model = Vehicle
        fields = ["id", "name", "brand", "fuel_type", "price_per_day"]


class BookingSerializer(serializers.ModelSerializer):
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())

    class Meta:
        model = Booking
        fields = [
            "id",
            "vehicle",
            "customer_name",
            "customer_phone",
            "start_date",
            "end_date",
            "total_amount",
            "created_at",
        ]
        read_only_fields = ["id", "total_amount", "created_at"]

    def validate_start_date(self, value: date) -> date:
        if value < date.today():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["end_date"] <= attrs["start_date"]:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )
        return attrs

    def create(self, validated_data: dict) -> Booking:
        return create_booking(
            vehicle_id=validated_data["vehicle"].id,
            customer_name=validated_data["customer_name"],
            customer_phone=validated_data["customer_phone"],
            start_date=validated_data["start_date"],
            end_date=validated_data["end_date"],
        )

    def to_representation(self, instance: Booking) -> dict:
        representation = super().to_representation(instance)
        representation["vehicle"] = VehicleBriefSerializer(instance.vehicle).data
        return representation
