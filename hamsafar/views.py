from django.shortcuts import render, redirect, get_object_or_404
from .models import Car, Trip, Booking, Message
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.contrib.auth import get_user_model
import re
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from .forms import TripForm

User = get_user_model()

class TripListView(LoginRequiredMixin,generic.ListView):
    model=Trip
    def get_queryset(self):
        queryset = Trip.objects.select_related('driver', 'car').filter(free_seats__gt=0)
        from_city = self.request.GET.get('from_city')
        to_city = self.request.GET.get('to_city')
        if from_city:
            queryset = queryset.filter(from_city__icontains=from_city)
        if to_city:
            queryset = queryset.filter(to_city__icontains=to_city)
        return queryset.order_by('departure_time')



# def trip_list(request):
#     trips = Trip.objects.filter(
#         free_seats__gt=0,
        
#     )
#     from_city = request.GET.get('from_city')
#     to_city = request.GET.get('to_city')

#     if from_city:
#         trips = trips.filter(from_city__icontains=from_city)

#     if to_city:
#         trips = trips.filter(to_city__icontains=to_city)

#     trips = trips.order_by('departure_time')

#     return render(request, 'hamsafar/trip_list.html', {
#         'trips': trips
#     })



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
            photo = request.FILES.get('photo')
            try:
                seats = int(seats)

                if seats < 1 or seats > 8:
                    return render(request, 'hamsafar/error.html',{
                    'error': 'Шумораи ҷойҳо бояд аз 1 то 8 бошад'
                    }, status=400)

            except ValueError:
                return render(request, 'hamsafar/error.html',{
        'error': 'Шумораи ҷойҳо бояд рақам бошад'
    }, status=400)
            pattern = r'^\d{4}[A-Z]{2}\d{2}$'

            if not re.fullmatch(pattern, car_number):
                return render(request, 'hamsafar/error.html',{
                'error': 'Фақат рақами давлатии Тоҷикистон иҷозат аст'
                }, status=400)

            Car.objects.create(
                owner=request.user,
                car_name=car_name,
                car_number=car_number,
                seats=seats,
                photo=photo
            )

            return redirect('create_trip')

        elif 'create_trip' in request.POST:
            car_id = request.POST.get('car_id')
            car = get_object_or_404(Car, id=car_id, owner=request.user)

            from_city = request.POST.get('from_city')
            to_city = request.POST.get('to_city')
            departure_time = request.POST.get('departure_time')

        
            price = request.POST.get('price')
            try:
                price = float(price)
                if price <= 0:
                    return render(request, 'hamsafar/error.html',{
                        'error': 'Нарх бояд аз 0 калон бошад'
                    }, status=400)
            except ValueError:
                return render(request, 'hamsafar/error.html',{
                    'error': 'Нарх бояд рақам бошад'
                }, status=400)
    
            free_seats = request.POST.get('free_seats')
            try:
                free_seats = int(free_seats)
                if free_seats < 1:
                    return render(request, 'hamsafar/error.html',{
                        'error': 'Шумораи ҷойҳо бояд аз 1 калон бошад'
                    }, status=400)
            except ValueError:
                return render(request, 'hamsafar/error.html',{
                    'error': 'Шумораи ҷойҳо бояд рақам бошад'
                }, status=400)
    
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

    return render(request, 'hamsafar/create_trip.html', {'user_cars': user_cars})


# @login_required
# def update_trip(request, pk):
#     trip = get_object_or_404(Trip, pk=pk, driver=request.user)
#     user_cars = Car.objects.filter(owner=request.user)

#     if request.method == "POST":
#         car_id = request.POST.get('car_id')
#         trip.car = get_object_or_404(Car, id=car_id, owner=request.user)
#         trip.from_city = request.POST.get('from_city')
#         trip.to_city = request.POST.get('to_city')
#         trip.departure_time = request.POST.get('departure_time')
#         trip.price = request.POST.get('price')
#         trip.free_seats = request.POST.get('free_seats')
#         if request.FILES.get("photo"):
#             trip.car.photo = request.FILES["photo"]
#         trip.save()
#         trip.car.save()
#         return redirect('trip_list')

#     return render(request, 'hamsafar/update_trip.html', {'trip': trip, 'user_cars': user_cars})
class TripUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Trip
    fields = [
    'car',
    'from_city',
    'to_city',
    'departure_time',
    'price',
    'free_seats',
]
    template_name = 'hamsafar/update_trip.html'
    success_url = reverse_lazy('trip_list')
    def get_queryset(self):
        return Trip.objects.filter(driver=self.request.user)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trip'] = self.object
        context['user_cars'] = Car.objects.filter(owner=self.request.user)
        return context
    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.FILES.get("photo"):
            self.object.car.photo = self.request.FILES["photo"]
            self.object.car.save()

        return response


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
        return render(request, 'hamsafar/error.html', {
            'error': 'Ронандагон наметавонанд сафарро банд кунанд.'
        })

    trip = get_object_or_404(Trip, id=trip_id)

    if Booking.objects.filter(passenger=request.user, trip=trip).exists():
        return render(request, 'hamsafar/error.html', {
            'error': 'Шумо ин сафарро аллакай банд кардаед.'
        })

    if request.method == "POST":
        seats = int(request.POST.get('seats', 1))

        if seats > trip.free_seats:
            return render(request, 'hamsafar/book_trip.html', {
                'trip': trip,
                'error': 'Ин қадар ҷой дастрас нест.'
            })

        Booking.objects.create(
            passenger=request.user,
            trip=trip,
            seats=seats,
            status='Pending'
        )

        return redirect('passenger_bookings')

    return render(request, 'hamsafar/book_trip.html', {
        'trip': trip
    })


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