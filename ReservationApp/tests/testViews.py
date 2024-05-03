from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware

from ReservationApp.models import Diner, Endorsement, Reservation, Restaurant, Table

class ViewTests(TestCase):
    def setUp(self):
        # Set up test data
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.table = Table.objects.create(capacity=4, restaurant=self.restaurant)

        # Create endorsement for vegetarian-friendly
        self.endorsement = Endorsement.objects.create(name="Vegetarian-Friendly")
        
        # Add endorsement to the restaurant
        self.restaurant.endorsements.add(self.endorsement)
        
        self.url = reverse('find-restaurant-availability')

        # Define query parameters for happy case
        self.happy_case_params = {
            'group_size': 4,
            'time': '2024-05-01T19:30:00',
            'dietary_restrictions': 'Vegetarian'
        }

        # Define query parameters for case with no available tables b/c impossibly picky dietary restriction
        self.no_tables_params = {
            'group_size': 4,
            'time': '2024-05-01T19:30:00',
            'dietary_restrictions': 'Impossibly picky',
        }

        # Set up test data for reservation creation
        self.diner1 = Diner.objects.create(name="John Doe")
        self.diner2 = Diner.objects.create(name="Jane Doe")
        self.reservation_url = reverse('create-reservation')

    def test_find_restaurant_availability_happy_case(self):
        # Concatenate query parameters with the base URL
        url = f"{self.url}?{'&'.join([f'{key}={value}' for key, value in self.happy_case_params.items()])}"
        
        # Make the request
        response = self.client.get(url)
        
        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Check if the response contains the expected data
        expected_data = [{'restaurant_name': self.restaurant.name, 'table_id': self.table.id}]
        self.assertEqual(response.json(), expected_data)
    
    def test_find_restaurant_availability_no_tables(self):
        # Concatenate query parameters with the base URL
        url = f"{self.url}?{'&'.join([f'{key}={value}' for key, value in self.no_tables_params.items()])}"
        
         # Make the request
        response = self.client.get(url)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the response contains an empty list, indicating no available tables
        self.assertEqual(response.json(), [])
    
    def test_find_restaurant_availability_non_get_request(self):
        # Make a POST request to the endpoint
        response = self.client.post(self.url)

        # Check if the response status code is 405 (Method Not Allowed)
        self.assertEqual(response.status_code, 405)

        # Check if the response contains the expected error message
        expected_error_message = {'error': 'This endpoint only supports GET requests'}
        self.assertEqual(response.json(), expected_error_message)

    def test_create_reservation_happy_case(self):
        # Define request data
        data = {
            'diners': [self.diner1.name, self.diner2.name],
            'time': (datetime.now() + timedelta(days=1)).isoformat(),
            'table_id': self.table.id,  
        }
        
        # Make the POST request
        response = self.client.post(self.reservation_url, data)
        
        # Check if the reservation was created successfully
        self.assertEqual(response.status_code, 201)
        
        # Check if the response message is as intended
        expected_message = {'message': 'Reservation created successfully', 'reservation': str(Reservation.objects.first())}
        self.assertEqual(response.json(), expected_message)
    
    def test_create_reservation_overlapping(self):
        # Create a reservation that overlaps with the desired time
        overlapping_reservation_time = make_aware(datetime(2024, 5, 1, 19, 0, 0))  # Overlaps with the desired time
        overlapping_reservation = Reservation.objects.create(
            time=overlapping_reservation_time,
            table=self.table,
        )

        # Define request data with overlapping time
        data = {
            'diners': [self.diner1.name, self.diner2.name],
            'time': overlapping_reservation_time.isoformat(),
            'table_id': self.table.id,
        }

        # Make the POST request
        response = self.client.post(self.reservation_url, data)

        # Check if the response status code is 400
        self.assertEqual(response.status_code, 400)

        # Check if the response contains the expected error message
        expected_error_message = {'error': 'Table is not available for the selected time'}
        self.assertEqual(response.json(), expected_error_message)

    def test_create_reservation_non_post_request(self):
        # Make a GET request to the create reservation endpoint
        response = self.client.get(reverse('create-reservation'))

        # Check if the response status code is 405 (Method Not Allowed)
        self.assertEqual(response.status_code, 405)

        # Check if the response contains the expected error message
        expected_error_message = {'error': 'Method not allowed'}
        self.assertEqual(response.json(), expected_error_message)
    
    def test_delete_reservation_happy_case(self):
        # Create a reservation to delete
        reservation_time = datetime.now() + timedelta(days=1)
        reservation = Reservation.objects.create(
            time=reservation_time,
            table=self.table,
        )

        # Define the URL for deleting a reservation
        delete_url = reverse('delete-reservation', kwargs={'reservation_id': reservation.id})

        # Make the DELETE request
        response = self.client.delete(delete_url)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check if the reservation was deleted
        self.assertFalse(Reservation.objects.filter(id=reservation.id).exists())

        # Check if the response message is as intended
        expected_message = {'message': f'Reservation {reservation.id} deleted successfully'}
        self.assertEqual(response.json(), expected_message)

    def test_delete_reservation_invalid_id(self):
        # Define a reservation ID that doesn't exist
        invalid_reservation_id = 9999

        # Define the URL for deleting a reservation with the invalid ID
        delete_url = reverse('delete-reservation', kwargs={'reservation_id': invalid_reservation_id})

        # Make the DELETE request
        response = self.client.delete(delete_url)

        # Check if the response status code is 404 (Not Found)
        self.assertEqual(response.status_code, 404)

        # Check if the response contains the expected error message
        expected_error_message = {'error': 'Invalid reservation ID'}
        self.assertEqual(response.json(), expected_error_message)

    def test_delete_reservation_non_delete_request(self):
        # Make a GET request to the delete reservation endpoint
        response = self.client.get(reverse('delete-reservation', kwargs={'reservation_id': 1}))

        # Check if the response status code is 405 (Method Not Allowed)
        self.assertEqual(response.status_code, 405)

        # Check if the response contains the expected error message
        expected_error_message = {'error': 'Method not allowed'}
        self.assertEqual(response.json(), expected_error_message)