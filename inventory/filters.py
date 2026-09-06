import django_filters

from inventory.models import Vehicle


class VehicleFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="iexact")
    fuel_type = django_filters.ChoiceFilter(choices=Vehicle.FuelType.choices)
    is_available = django_filters.BooleanFilter()

    class Meta:
        model = Vehicle
        fields = ["brand", "fuel_type", "is_available"]
