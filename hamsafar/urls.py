from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
]