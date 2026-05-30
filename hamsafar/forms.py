from django import forms
from .models import User, Car


class CarForm(forms.Form):

    car_name = forms.CharField(
        max_length=100,
        label='Номи мошин'
    )

    car_number = forms.CharField(
        max_length=20,
        label='Рақами мошин'
    )

    seats = forms.IntegerField(
        min_value=1,
        max_value=8,
        label='Шумораи ҷойҳо'
    )


