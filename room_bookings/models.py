from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import random
import uuid
import random
import string

# Create your models here.

class RoomType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    room_image = models.ImageField(upload_to="rooms", blank=True, null=True)

    def __str__(self):
        return self.name

class HotelBranch(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    hotel = models.ForeignKey(HotelBranch, on_delete=models.CASCADE, related_name='rooms', blank=True, null=True)
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    price_per_night =  models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    room_image = models.ImageField(upload_to="rooms", blank=True, null=True)
    floor = models.IntegerField()

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    NIN = models.CharField(max_length=100, default="")
    customerid_image = models.ImageField(upload_to="rooms", blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class RoomReservation(models.Model):
    RESERVATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Checked-In', 'Checked-In'),
        ('Checked-Out', 'Checked-Out'),
    ]

    reservation_id = models.BigIntegerField(unique=True, editable=False, default=0)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    customer = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    NIN = models.CharField(max_length=100, default="")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    reservation_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS_CHOICES, default='Pending')
    special_requests = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0.00)

    def __str__(self):
        return f"Reservation for {self.customer} - Room {self.room.room_number}"

    @property
    def total_nights(self):
        return (self.check_out_date - self.check_in_date).days

    @property
    def is_active(self):
        return self.check_in_date <= timezone.now().date() <= self.check_out_date

    def calculate_total_price(self):
        if self.room.price_per_night and self.total_nights > 0:
            return self.total_nights * self.room.price_per_night
        return 0

    def clean(self):
        # Ensure check-in date is not in the past
        if self.check_in_date < timezone.now().date():
            raise ValidationError("Check-in date cannot be in the past.")

        # Ensure checkout date is after check-in date
        if self.check_out_date <= self.check_in_date:
            raise ValidationError("Checkout date must be after the check-in date.")

    def save(self, *args, **kwargs):
        # Assign a unique 9-digit reservation ID if not set
        if not self.reservation_id or self.reservation_id < 100000000:
            self.reservation_id = random.randint(100000000, 999999999)

        # Calculate total price
        self.total_price = self.calculate_total_price()

        # Run validation before saving
        self.clean()

        super().save(*args, **kwargs)



#SAUNA
class Sauna_services(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.IntegerField(blank=True, null=True)


    def __str__(self):
        return self.name
    


class SaunaUser(models.Model):
    KEY_CHOICES = [
    (f"key_{str(i).zfill(3)}", f"key_{str(i).zfill(3)}") for i in range(1, 17)
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        
    ]
    customer_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    service = models.ForeignKey(Sauna_services, on_delete=models.CASCADE)
    keys = models.CharField(max_length=100, choices=KEY_CHOICES)
    price = models.IntegerField(blank=True, null=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def save(self, *args, **kwargs):
      
        if self.service:
            self.price = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer_name



