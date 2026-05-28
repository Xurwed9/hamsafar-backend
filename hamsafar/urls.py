from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
    path('create-trip/', views.create_trip, name='create_trip'),
    path('update-trip/<int:pk>/', views.update_trip, name='update_trip'),
    path('delete-trip/<int:pk>/', views.delete_trip, name='delete_trip'),
]