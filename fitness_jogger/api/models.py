import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import CustomUserManager
from django.utils import timezone
from django.contrib.gis.db.models import PointField
from api.helpers import get_weather_conditons

# These fields tie to the roles!
ADMIN = 1
USER_MANAGER = 2
USER = 3

ROLE_CHOICES = (
    (ADMIN, 'Admin'),
    (USER_MANAGER, 'User_Manager'),
    (USER, 'User')
)


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(unique=True, editable=False,
                          default=uuid.uuid4, primary_key=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=500, blank=False, null=False)
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES, blank=True, null=True, default=3)
    is_active = models.BooleanField(default=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.email


class Jog(models.Model):
    id = models.UUIDField(unique=True, editable=False,
                          default=uuid.uuid4, primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    distance = models.DecimalField(
        max_digits=7, decimal_places=2, null=False, blank=False
    )
    time = models.FloatField()
    location = PointField(null=False)
    weather = models.JSONField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        self.weather = get_weather_conditons(self.location)
        super().save()
