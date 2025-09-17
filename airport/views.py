from django.db import IntegrityError, transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
    BookSeatSerializer,
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

    @action(detail=True, methods=['get'], url_path='seats')
    def seats(self, request, pk=None):
        flight = self.get_object()
        rows = flight.airplane.rows
        seats_in_row = flight.airplane.seats_in_row

        occupied = set(flight.tickets.values_list('row', 'seat'))

        seat_map = []
        for row_number in range(1, rows + 1):
            row_seats = []
            for seat_number in range(1, seats_in_row + 1):
                is_taken = (row_number, seat_number) in occupied
                row_seats.append(
                    {
                        'row': row_number,
                        'seat': seat_number,
                        'taken': is_taken
                    }
                )
            seat_map.append({'row': row_number, 'seats': row_seats})

        return Response({
            'flight': flight.id,
            'rows': rows,
            'seats_in_row': seats_in_row,
            'seat_map': seat_map,
        })

    @action(
        detail=True,
        methods=['post'],
        url_path='book',
        permission_classes=[IsAuthenticated],
    )
    def book(self, request, pk=None):
        flight = self.get_object()
        serializer = BookSeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        row = serializer.validated_data['row']
        seat = serializer.validated_data['seat']

        total_rows = flight.airplane.rows
        seats_per_row = flight.airplane.seats_in_row

        if row > total_rows or seat > seats_per_row:
            return Response(
                {'detail': 'row/seat exceeds airplane capacity'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user)
                ticket = Ticket.objects.create(
                    flight=flight,
                    order=order,
                    row=row,
                    seat=seat,
                )
        except IntegrityError:
            return Response(
                {'detail': 'seat already taken for this flight'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                'order': order.id,
                'flight': flight.id,
                'ticket': {
                    'id': ticket.id,
                    'row': ticket.row,
                    'seat': ticket.seat
                },
            },
            status=status.HTTP_201_CREATED,
        )


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
