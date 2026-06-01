from django import forms
from .models import Trip

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'car',
            'from_city',
            'to_city',
            'departure_time',
            'price',
            'free_seats',
        ]