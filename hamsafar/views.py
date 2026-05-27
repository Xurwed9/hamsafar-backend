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