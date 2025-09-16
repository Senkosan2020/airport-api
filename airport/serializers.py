from rest_framework import serializers

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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

    def validate(self, attrs):
        source = attrs.get('source') or getattr(self.instance, 'source', None)
        destination = attrs.get('destination') or getattr(
            self.instance,
            'destination',
            None,
        )
        if source and destination and source == destination:
            raise serializers.ValidationError(
                'source must differ from destination'
            )
        return attrs


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = '__all__'


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = '__all__'


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = '__all__'


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

    def validate(self, attrs):
        departure = attrs.get('departure_time') or getattr(
            self.instance,
            'departure_time',
            None,
        )
        arrival = attrs.get('arrival_time') or getattr(
            self.instance,
            'arrival_time',
            None,
        )
        if departure and arrival and not arrival > departure:
            raise serializers.ValidationError(
                'arrival_time must be after departure_time'
            )
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

    def validate(self, attrs):
        flight = attrs.get('flight') or getattr(self.instance, 'flight', None)
        row = attrs.get('row') or getattr(self.instance, 'row', None)
        seat = attrs.get('seat') or getattr(self.instance, 'seat', None)

        if flight and row and row > flight.airplane.rows:
            raise serializers.ValidationError('row exceeds airplane rows')

        if flight and seat and seat > flight.airplane.seats_in_row:
            raise serializers.ValidationError('seat exceeds seats_in_row')

        return attrs
