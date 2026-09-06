from django.contrib import admin

from inventory.models import Booking, Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "year", "fuel_type", "price_per_day", "is_available"]
    list_filter = ["brand", "fuel_type", "is_available"]
    search_fields = ["name", "brand"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        "vehicle",
        "customer_name",
        "customer_phone",
        "start_date",
        "end_date",
        "total_amount",
    ]
    list_filter = ["start_date", "end_date"]
    search_fields = ["customer_name", "customer_phone"]
    autocomplete_fields = ["vehicle"]
