from datetime import datetime, timedelta

from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import Diner, Restaurant, Table, Reservation

@csrf_exempt
def find_restaurant_availability(request):
    #TODO: take care ofCSRF verification failure 
    if request.method == 'GET':
        try:
            # Get query parameters
            group_size = int(request.GET.get('group_size'))
            time_str = request.GET.get('time')
            
            try:
                time = timezone.datetime.fromisoformat(time_str)
            except ValueError:
                return JsonResponse({'error': 'Invalid time format'}, status=400)

            dietary_restrictions = request.GET.getlist('dietary_restrictions')

            # Initialize an empty query
            query = Q()

            # Iterate over each dietary restriction
            for dietary_restriction in dietary_restrictions:
                # Add a condition to the query to check if endorsements contain the dietary restriction
                query |= Q(endorsements__name__icontains=dietary_restriction)

            # Filter restaurants by capacity and dietary restrictions
            restaurants = Restaurant.objects.filter(
                query,
                tables__capacity__gte=group_size
            ).distinct()

            # Filter tables with no overlapping reservations
            available_tables = []
            for restaurant in restaurants:
                tables = Table.objects.filter(restaurant=restaurant, capacity__gte=group_size)
                for table in tables:
                    reservations = table.reservation_set.filter(
                        time__lte=time,
                        time__gte=time - timedelta(hours=2)
                    )
                    if not reservations.exists():
                        available_tables.append(table)

            # Serialize the data
            data = [{'restaurant_name': table.restaurant.name, 'table_id': table.id} for table in available_tables]

            return JsonResponse(data, status=200, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'This endpoint only supports GET requests'}, status=405)



@csrf_exempt
def create_reservation(request):
    #TODO: take care of CSRF verification failure 
    """
    Endpoint to create a reservation for a group of users.
    """
    if request.method == 'POST':
        try:
            # Parse request data
            data = request.POST
            diner_names = data.getlist('diners')
            time_str = data.get('time')
            time = datetime.fromisoformat(time_str)
            table_id = int(data.get('table_id'))

            # Get or create diners
            diners = [Diner.objects.get_or_create(name=name)[0] for name in diner_names]

            # Check if any diner has overlapping reservations
            for diner in diners:
                if diner.reservation_set.filter(
                    Q(time__lt=time + timedelta(hours=2)) & Q(time__gt=time - timedelta(hours=2))
                ).exists():
                    return JsonResponse({'error': f'{diner.name} already has a reservation that overlaps with the selected time'}, status=400)

            # Get the table
            table = Table.objects.get(id=table_id)

            # Check if the table is available
            overlapping_reservations = table.reservation_set.filter(
                time__lt=time + timedelta(hours=2),
                time__gt=time - timedelta(hours=2)
            )
            if overlapping_reservations.exists():
                return JsonResponse({'error': 'Table is not available for the selected time'}, status=400)

            # Create reservation
            reservation = Reservation.objects.create(table=table, time=time)
            reservation.diners.add(*diners)

            return JsonResponse({'message': 'Reservation created successfully','reservation': str(reservation)
                                 }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def delete_reservation(request, reservation_id):
    #TODO take care of CSRF 
    #want to use 204 code, as customary for DELETING, but
    #opted for 200 code, to give return message. CURL seems to not return
    #response body for 204
    """
    Endpoint to delete an existing reservation.
    """
    if request.method == 'DELETE':
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.delete()
            return JsonResponse({'message': f'Reservation {reservation_id} deleted successfully'}, status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Invalid reservation ID'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
