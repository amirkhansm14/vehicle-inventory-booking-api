from rest_framework import mixins, viewsets

from inventory.filters import VehicleFilter
from inventory.models import Booking, Vehicle
from inventory.serializers import BookingSerializer, VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filterset_class = VehicleFilter


class BookingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Bookings are created and read, never edited or deleted in place."""

    queryset = Booking.objects.select_related("vehicle").all()
    serializer_class = BookingSerializer
