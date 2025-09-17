from rest_framework.routers import DefaultRouter

from .views import (
    AirplaneTypeViewSet,
    AirplaneViewSet,
    AirportViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    RouteViewSet,
    TicketViewSet,
)

router = DefaultRouter()
router.register('airports', AirportViewSet)
router.register('routes', RouteViewSet)
router.register('airplane-types', AirplaneTypeViewSet)
router.register('airplanes', AirplaneViewSet)
router.register('crews', CrewViewSet)
router.register('flights', FlightViewSet)
router.register('orders', OrderViewSet)
router.register('tickets', TicketViewSet)

urlpatterns = router.urls
