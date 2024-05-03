#RestaurantProject

#Onboarding to Project:
Model definitions can be found in ReservationApp/models.py
In our Restaurant Model, we have: 
-DietaryRestriction (Diner's dietary restriction)
-Endorsement (Restaurant's supported dietary restrictions)
-Diner (Individual eating at restaurant)
-Restaurant (Restaurants)
-Table (Table at a Restaurant)
-Reservation (Table reserved, diners eating, Res time)

Our API functionality is found in ReservationApp/views.py
1) find_restaurant_availability(request)
    -takes input of GET request, returns available tables based on query params of diner group size, dining time and dietary restrictions. Error messages are returned for non-valid API usage.
2) create_reservation(request)
    -takes input of POST request, creates reservation based on query params of diner_names, dining time, table_id. Overlapping reservations are checked for. Upon successful reservation, sucess message is returned and reservation is booked. Error messages are returned for non-valid API usage.
3) delete_reservation(request, reservation_id):
    -takes DELETE request, along with query param of reservation_id, and deletes Reservation. If Reservation ID is valid, deletes reservations, returns valid response. Otherwise, error messages are returned for non-valid API usage.

#How do I run this?
- 0) Run tests: 
`python manage.py test ReservationApp.tests`
This command will run all tests located within the ReservationApp.tests package, including testViews.py and testModels.py. (for views/models respectively). "OK" will be printed if all pass (as they should), with errors showing failed tests. Run tests after making any changes.

- 1) Run the server: In terminal, inside root of project /RestaurantProject, run:
`python manage.py runserver`
- Now you will see something like this below:
`Starting development server at http://127.0.0.1:8000/`
- The [http://](http://127.0.0.1:8000/) is the address of your local server

- 2) Create objects to use for API testing. Inside another terminal tab run
`python manage.py shell`
- This will open up a python shell. This is an executable python environment. We will use this to create our objects. Example of object creation to get you started below:
```python
from ReservationApp.models import DietaryRestriction, Endorsement, Diner, Restaurant, Table, Reservation
from django.utils import timezone

# Create dietary restrictions
restriction1 = DietaryRestriction.objects.create(name="Vegan")
restriction2 = DietaryRestriction.objects.create(name="Gluten-Free")
restriction3 = DietaryRestriction.objects.create(name="Vegetarian")

# Create endorsements to match dietary restrictions
endorsement1 = Endorsement.objects.create(name="Vegan-friendly")
endorsement2 = Endorsement.objects.create(name="Gluten-Free-friendly")
endorsement3 = Endorsement.objects.create(name="Vegetarian-friendly")

# Create diners
diner1 = Diner.objects.create(name="John")
diner2 = Diner.objects.create(name="Emma")

# Assign dietary restrictions to diners
diner1.dietary_restrictions.add(restriction1, restriction3)
diner2.dietary_restrictions.add(restriction2)

# Create restaurants
restaurant1 = Restaurant.objects.create(name="Restaurant A")
restaurant2 = Restaurant.objects.create(name="Restaurant B")

# Assign endorsements to restaurants
restaurant1.endorsements.add(endorsement1, endorsement3)
restaurant2.endorsements.add(endorsement2)

# Create tables
table1 = Table.objects.create(restaurant=restaurant1, capacity=4)
table2 = Table.objects.create(restaurant=restaurant2, capacity=6)

# Create reservations
reservation1 = Reservation.objects.create(table=table1, time=timezone.now())

print("Reservation ID:", reservation1.id)
```
- 3) You can now run find_restaurant_availability API like below. Change the http://127.0.0.1:8000/ server to whatever the local server was shown as in step 1 above. You should see some output like below (table_id might be different).
`curl -X GET "http://127.0.0.1:8000/find-restaurant-availability/?group_size=2&time=2024-05-01T19:30:00&dietary_restrictions=Vegan"`
`[{"restaurant_name": "Restaurant A", "table_id": 39}]% `
- 4) Now, to test create_reservation API. Use same query as below, except change table_id to whatever table_id you had returned from find_restaurant_availability (mine was table_id= 39). You should see some successful return response like below.
`curl -X POST "http://127.0.0.1:8000/create-reservation/" -d "diners=John&diners=Emma&time=2024-05-01T19:30:00&table_id=39"`
`{"message": "Reservation created successfully", "reservation": "Reservation ID: 20 for John, Emma at Restaurant A - Table 39"}%`
- 5) Now, to use delete_reservation API.Follow below command, should see response like bwelow. Pass in Reservation ID that is seen from output of step 4, create_reservation API.
`curl -X DELETE "http://127.0.0.1:8000/delete-reservation/20/"`                                                              
`{"message": "Reservation 20 deleted successfully"}%`



#TODO
- Fix CSRF handling that is for now left as @csrf_exempt (unsafe security practice), would be a fast follow to fix this.