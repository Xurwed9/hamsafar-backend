from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
    path('create-trip/', views.create_trip, name='create_trip'),
    path('update-trip/<int:pk>/', views.update_trip, name='update_trip'),
    path('delete-trip/<int:pk>/', views.delete_trip, name='delete_trip'),
    path('trip/<int:trip_id>/book/', views.book_trip, name='book_trip'),
    path('my-bookings/', views.passenger_bookings, name='passenger_bookings'),
    path('booking/<int:booking_id>/cancel-my/', views.cancel_booking_passenger, name='cancel_booking_passenger'),
    path('my-trips/', views.my_trips, name='my_trips'),
]