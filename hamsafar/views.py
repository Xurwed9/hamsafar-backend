from django.shortcuts import render,redirect, get_object_or_404
from .models import Car, Trip, Booking, Message
from django.utils import timezone

# Create your views here.

def trip_list(request):
    active_trips = Trip.objects.filter(
        free_seats__gt=0,
        departure_time__gte=timezone.now()
    ).order_by('departure_time')

    return render(request, 'hamsafar/trip_list.html', {'trips': active_trips})


def create_trip(request):
    if request.method == 'POST':
        car_name = request.POST.get('car_name')
        car_number = request.POST.get('car_number').strip().upper() # Рақамро калон ва бе пробел мекунем
        seats = request.POST.get('seats')
        from_city = request.POST.get('from_city')
        to_city = request.POST.get('to_city')
        departure_time = request.POST.get('departure_time')
        price = request.POST.get('price')
        free_seats = request.POST.get('free_seats')
        car, created = Car.objects.get_or_create(
            owner=request.user,
            car_number=car_number,
            defaults={
                'car_name': car_name,
                'seats': seats
            }
        )
        Trip.objects.create(
            driver=request.user,
            car=car, 
            from_city=from_city,
            to_city=to_city,
            departure_time=departure_time,
            price=price,
            free_seats=free_seats
        )
        
        return redirect('trip_list')

    return render(request, 'hamsafar/create_trip.html')