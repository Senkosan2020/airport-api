from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
    Ticket,
)
from .serializers import (
    AirplaneSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    RouteSerializer,
    TicketSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all().order_by('id')
    serializer_class = AirportSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'closest_big_city']


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        'source',
        'destination'
    ).order_by('id')
    serializer_class = RouteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source', 'destination']


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all().order_by('id')
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related('airplane_type').order_by('id')
    serializer_class = AirplaneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['airplane_type']
    search_fields = ['name']


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all().order_by('id')
    serializer_class = CrewSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.select_related('route', 'airplane')
        .prefetch_related('crews')
        .order_by('id')
    )
    serializer_class = FlightSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        'route',
        'airplane',
        'crews',
        'departure_time',
        'arrival_time'
    ]
    ordering_fields = ['departure_time', 'arrival_time', 'id']


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('user').order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user']


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related('flight', 'order').order_by('id')
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['flight', 'order']
