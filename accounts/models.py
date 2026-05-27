from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone  = models.CharField(max_length=14, blank=True)
    photo = models.ImageField(upload_to='users/', blank=True, null=True)
    is_driver = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.email} {self.username} -> {self.phone}'



class EmailConfirm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.user.username
    
    