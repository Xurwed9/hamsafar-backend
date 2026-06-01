from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

# Create your models here.

User = get_user_model()

class Car(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cars'
    )
    car_name = models.CharField(max_length=100)
    car_number = models.CharField(max_length=20)
    seats = models.IntegerField()
    photo = models.ImageField(upload_to='cars/', null=True, blank=True)

    def __str__(self):
        return f"{self.car_name} ({self.car_number})"
    

class Trip(models.Model):
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='trips'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE
    )
    from_city = models.CharField(max_length=100)
    to_city = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    free_seats = models.IntegerField()
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    slug = models.SlugField(unique=True, null=True,blank=True)
    is_delete = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.is_delete=True
        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.from_city)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.from_city} -> {self.to_city}"
    


class Booking(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Cancelled', 'Cancelled'),
    )
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    seats = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.passenger.username} - {self.trip}"
    


class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.sender} -> {self.receiver}"