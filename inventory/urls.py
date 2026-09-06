from rest_framework.routers import DefaultRouter

from inventory.views import BookingViewSet, VehicleViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
