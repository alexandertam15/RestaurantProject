from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from ReservationApp.models import DietaryRestriction, Diner, Endorsement, Reservation, Restaurant, Table

class ModelTests(TestCase):
    def setUp(self):
        # Set up common test data
        self.restaurant = Restaurant.objects.create(name="Sample Restaurant")
        self.table = Table.objects.create(restaurant=self.restaurant, capacity=4)
        self.diner = Diner.objects.create(name="John Doe")
        self.time = timezone.now() + timedelta(days=1)

    def test_dietary_restriction_creation(self):
        dietary_restriction = DietaryRestriction.objects.create(name="Gluten-Free")
        self.assertEqual(dietary_restriction.name, "Gluten-Free")

    def test_endorsement_creation(self):
        endorsement = Endorsement.objects.create(name="Vegan-friendly")
        self.assertEqual(endorsement.name, "Vegan-friendly")

    def test_diner_creation(self):
        self.assertEqual(self.diner.name, "John Doe")

    def test_restaurant_creation(self):
        self.assertEqual(self.restaurant.name, "Sample Restaurant")

    def test_table_creation(self):
        self.assertEqual(self.table.restaurant, self.restaurant)
        self.assertEqual(self.table.capacity, 4)

    def test_reservation_creation(self):
        reservation = Reservation.objects.create(table=self.table, time=self.time)
        
        # Associate diner with reservation
        reservation.diners.add(self.diner)
        
        self.assertEqual(reservation.table, self.table)
        self.assertIn(self.diner, reservation.diners.all())
    
