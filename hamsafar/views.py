from django.shortcuts import render, redirect, get_object_or_404
from .models import Car, Trip, Booking, Message
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.contrib.auth import get_user_model
import re
from django.http import JsonResponse

User = get_user_model()


def trip_list(request):
    trips = Trip.objects.filter(
        free_seats__gt=0,
        
    )
    from_city = request.GET.get('from_city')
    to_city = request.GET.get('to_city')

    if from_city:
        trips = trips.filter(from_city__icontains=from_city)

    if to_city:
        trips = trips.filter(to_city__icontains=to_city)

    trips = trips.order_by('departure_time')

    return render(request, 'hamsafar/trip_list.html', {
        'trips': trips
    })

@login_required
def create_trip(request):
    if not request.user.is_driver:
        return render(request, 'hamsafar/error.html', {'error': 'Танҳо ронандагон метавонанд сафар созанд.'})

    user_cars = Car.objects.filter(owner=request.user)

    if request.method == "POST":
        if 'add_car' in request.POST:
            car_name = request.POST.get('car_name')
            car_number = request.POST.get('car_number', '').upper().strip()
            seats = request.POST.get('seats')
            pattern = r'^\d{4}[A-Z]{2}\d{2}$'

            if not re.fullmatch(pattern, car_number):
                return render(request, 'hamsafar/error.html',{
                'error': 'Фақат рақами давлатии Тоҷикистон иҷозат аст'
                }, status=400)

            Car.objects.create(
                owner=request.user,
                car_name=car_name,
                car_number=car_number,
                seats=seats
            )

            return redirect('create_trip')

        elif 'create_trip' in request.POST:
            car_id = request.POST.get('car_id')
            car = get_object_or_404(Car, id=car_id, owner=request.user)
            
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
        trip.car = get_object_or_404(Car, id=car_id, owner=request.user)
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


@login_required
def my_trips(request):
    trips = Trip.objects.filter(driver=request.user)
    return render(request, 'hamsafar/my_trips.html', {'trips': trips})


@login_required
def book_trip(request, trip_id):
    if getattr(request.user, 'is_driver', False):
        return render(request, 'hamsafar/error.html', {'error': 'Ронандагон наметавонанд сафарро банд кунанд.'})
        
    trip = get_object_or_404(Trip, id=trip_id)
    
    already_booked = Booking.objects.filter(passenger=request.user, trip=trip).exists()
    
    if already_booked:
        return render(request, 'hamsafar/error.html', {'error': 'Шумо ин сафарро аллакай банд кардаед.'})

    if trip.free_seats <= 0:
        return render(request, 'hamsafar/error.html', {'error': 'Дар ин сафар ҷои холӣ намондааст.'})
        
    Booking.objects.create(
        passenger=request.user,
        trip=trip,
        seats=1,
        status='Pending'
    )
    return redirect('passenger_bookings')


@login_required
def passenger_bookings(request):
    bookings = Booking.objects.filter(passenger=request.user)
    return render(request, 'hamsafar/passenger_bookings.html', {'bookings': bookings})


@login_required
def cancel_booking_passenger(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, passenger=request.user)    
    if booking.status == 'Accepted':
        booking.trip.free_seats += booking.seats
        booking.trip.save()
        
    booking.delete()
    return redirect('passenger_bookings')


@login_required
def manage_booking(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id, trip__driver=request.user)
    
    if action == 'accept':
        if booking.trip.free_seats >= booking.seats and booking.status != 'Accepted':
            booking.status = 'Accepted'
            booking.trip.free_seats -= booking.seats  
            booking.trip.save()
            booking.save()
            
    elif action == 'cancel':
        if booking.status == 'Accepted':
            booking.trip.free_seats += booking.seats  
            booking.trip.save()
        booking.status = 'Cancelled'
        booking.save()
        
    return redirect('my_trips')


@login_required
def send_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        text = request.POST.get('text')

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            text=text
        )

        return redirect('inbox')

    return render(request, 'hamsafar/send_message.html', {
        'receiver': receiver
    })



@login_required
def inbox(request):
    messages_list = Message.objects.filter(
        receiver=request.user
    ).order_by('-created_at')

    return render(request, 'hamsafar/inbox.html', {
        'messages': messages_list
    })