from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Route,
    Ticket,
)

User = get_user_model()


class BookingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='u1',
            password='pass12345',
        )
        a1 = Airport.objects.create(name='Boryspil', closest_big_city='Kyiv')
        a2 = Airport.objects.create(name='Lviv', closest_big_city='Lviv')
        route = Route.objects.create(source=a1, destination=a2, distance=468)

        at = AirplaneType.objects.create(name='Airbus A320')
        plane = Airplane.objects.create(
            name='UR-AAA',
            rows=3,
            seats_in_row=4,
            airplane_type=at,
        )
        crew1 = Crew.objects.create(
            first_name='Olena',
            last_name='Ivanenko'
        )
        crew2 = (Crew.objects.create(
            first_name='Andrii',
            last_name='Shevchenko'
        ))

        now = timezone.now()
        self.flight = Flight.objects.create(
            route=route,
            airplane=plane,
            departure_time=now + timedelta(days=1),
            arrival_time=now + timedelta(days=1, hours=1),
        )
        self.flight.crews.set([crew1, crew2])

        self.client = APIClient()

    def auth(self):
        assert self.client.login(username='u1', password='pass12345')

    def test_seat_map_ok(self):
        url = f'/api/flights/{self.flight.id}/seats/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['flight'], self.flight.id)
        self.assertEqual(data['rows'], 3)
        self.assertEqual(data['seats_in_row'], 4)
        taken_flags = [
            s['taken']
            for row in data['seat_map']
            for s in row['seats']
        ]
        self.assertTrue(all(flag is False for flag in taken_flags))

    def test_booking_requires_auth(self):
        url = f'/api/flights/{self.flight.id}/book/'
        res = self.client.post(url, {'row': 1, 'seat': 1}, format='json')
        self.assertEqual(res.status_code, 401)

    def test_booking_success(self):
        self.auth()
        url = f'/api/flights/{self.flight.id}/book/'
        res = self.client.post(url, {'row': 2, 'seat': 3}, format='json')
        self.assertEqual(res.status_code, 201)
        payload = res.json()
        self.assertIn('order', payload)
        self.assertIn('ticket', payload)
        self.assertEqual(payload['flight'], self.flight.id)
        ticket = Ticket.objects.get(id=payload['ticket']['id'])
        self.assertEqual(ticket.row, 2)
        self.assertEqual(ticket.seat, 3)
        self.assertEqual(ticket.flight_id, self.flight.id)
        self.assertEqual(ticket.order.user_id, self.user.id)

    def test_booking_conflict(self):
        self.auth()
        url = f'/api/flights/{self.flight.id}/book/'
        res1 = self.client.post(url, {'row': 1, 'seat': 1}, format='json')
        self.assertEqual(res1.status_code, 201)

        res2 = self.client.post(url, {'row': 1, 'seat': 1}, format='json')
        self.assertEqual(res2.status_code, 400)
        self.assertIn('detail', res2.json())

    def test_booking_out_of_capacity(self):
        self.auth()
        url = f'/api/flights/{self.flight.id}/book/'
        res1 = self.client.post(url, {'row': 99, 'seat': 1}, format='json')
        self.assertEqual(res1.status_code, 400)
        res2 = self.client.post(url, {'row': 1, 'seat': 99}, format='json')
        self.assertEqual(res2.status_code, 400)
