from django.contrib import admin
from .models import EmailConfirm, User


admin.site.register(EmailConfirm)
admin.site.register(User)