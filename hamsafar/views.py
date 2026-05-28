from django.shortcuts import render,redirect, get_object_or_404
from .models import Car, Trip, Booking, Message
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def trip_list(request):
    active_trips = Trip.objects.filter(
        free_seats__gt=0,
        departure_time__gte=timezone.now()
    ).order_by('departure_time')

    return render(request, 'hamsafar/trip_list.html', {'trips': active_trips})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Car, Trip

@login_required
def create_trip(request):
    if not request.user.is_driver:
        return render(request, 'hamsafar/error.html', {'error': 'Only drivers can access this page.'})

    user_cars = Car.objects.filter(owner=request.user)

    if request.method == "POST":
        if 'add_car' in request.POST:
            car_name = request.POST.get('car_name')
            car_number = request.POST.get('car_number')
            seats = request.POST.get('seats')
            Car.objects.create(
                owner=request.user,
                car_name=car_name,
                car_number=car_number,
                seats=seats
            )
            return redirect('create_trip')

        elif 'create_trip' in request.POST:
            car_id = request.POST.get('car_id')
            car = Car.objects.get(id=car_id, owner=request.user)
            Trip.objects.create(
                driver=request.user,
                car=car,
                from_city=request.POST.get('from_city'),
                to_city=request.POST.get('to_city'),
                departure_time=request.POST.get('departure_time'),
                price=request.POST.get('price'),
                free_seats=request.POST.get('free_seats')
            )
            return redirect('trip_list')

    return render(request, 'hamsafar/create_trip.html', {'user_cars': user_cars})



@login_required
def update_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk, driver=request.user)
    user_cars = Car.objects.filter(owner=request.user)

    if request.method == "POST":
        car_id = request.POST.get('car_id')
        trip.car = Car.objects.get(id=car_id, owner=request.user)
        trip.from_city = request.POST.get('from_city')
        trip.to_city = request.POST.get('to_city')
        trip.departure_time = request.POST.get('departure_time')
        trip.price = request.POST.get('price')
        trip.free_seats = request.POST.get('free_seats')
        trip.save()
        return redirect('trip_list')

    return render(request, 'hamsafar/update_trip.html', {'trip': trip, 'user_cars': user_cars})


@login_required
def delete_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk, driver=request.user)
    if request.method == "POST":
        trip.delete()
        return redirect('trip_list')
    return render(request, 'hamsafar/delete_trip.html', {'trip': trip})