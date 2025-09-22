from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='routes_from',
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name='routes_to',
    )
    distance = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'destination'],
                name='uniq_route_src_dst',
            ),
            models.CheckConstraint(
                condition=~Q(source=F('destination')),
                name='route_src_ne_dst',
            ),
        ]

    def __str__(self):
        return f'{self.source} → {self.destination}'


class AirplaneType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.PositiveSmallIntegerField()
    seats_in_row = models.PositiveSmallIntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.PROTECT,
        related_name='airplanes',
    )

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name='flights',
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name='flights',
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name='flights', blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(arrival_time__gt=F('departure_time')),
                name='flight_arrival_after_departure',
            ),
        ]

    def __str__(self):
        return f'Flight {self.id}'


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f'Order {self.id}'


class Ticket(models.Model):
    row = models.PositiveSmallIntegerField()
    seat = models.PositiveSmallIntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='tickets',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['flight', 'row', 'seat'],
                name='uniq_ticket_place_per_flight',
            ),
        ]

    def __str__(self):
        return (
            f'T{self.id} F{self.flight_id} '
            f'r{self.row}s{self.seat}'
        )
