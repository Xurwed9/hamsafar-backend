from django.contrib import admin
from .models import Car, Trip,Booking, Message

# Register your models here.

admin.site.register([Car, Trip, Booking, Message])