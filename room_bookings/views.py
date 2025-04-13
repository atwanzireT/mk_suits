from django.shortcuts import render
import io
import os
import requests
import csv
from datetime import datetime, time
from datetime import timedelta
from django.db.models import Sum
from io import BytesIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.core.files.temp import NamedTemporaryFile
from core.models import Setting
from .forms import *
from .models import *
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.utils import timezone

# Create your views here.
def fetch_reservation_details(request, reservation_id):
    # Get the reservation object
    reservation = get_object_or_404(RoomReservation, id=reservation_id)

    # Prepare the data to be returned as JSON
    data = {
        "reservation_id": reservation.reservation_id,
        "customer": reservation.customer,
        "reservation_date": reservation.reservation_date,
        "room_number": reservation.room.room_npyumber,
        "total_nights": reservation.total_nights,
        "total_price": reservation.total_price,
        "check_in_date": reservation.check_in_date,
        "check_out_date": reservation.check_out_date,
        "status": reservation.status,
        "special_requests": reservation.special_requests or "None",
        "created_by": reservation.created_by,
    }

    return JsonResponse(data)


# ROOM TYPES VIEW
@login_required(login_url='/user/login/')
def rooms(request):
    room_types = RoomType.objects.all()
    return render(request, "roomtypes.html", {"room_types": room_types})



# FILTER ROOMS BY TYPE
@login_required(login_url='/user/login/')
def rooms_filter(request, id):
    rooms = Room.objects.filter(room_type=id, is_available=True)
    return render(request, "rooms.html", {"rooms": rooms})

# ROOM RESERVATION LIST VIEW
@login_required(login_url='/user/login/')
def reservation(request):
    reservations = RoomReservation.objects.all().select_related('room')
    reservations_list = RoomReservation.objects.all().select_related('room').order_by('-reservation_date')
    paginator = Paginator(reservations_list, 10)
    
    # Get the page number from the request
    page_number = request.GET.get('page')

    # Get the corresponding page
    reservations_list = paginator.get_page(page_number)
    return render(request, "reservations.html", {"reservations_list": reservations_list})

# GET SPECIFIC RESERVATION VIEW
@login_required(login_url="/user/login/")
def getReservation(request, id):
    settings = Setting.objects.first()
    reservation = get_object_or_404(RoomReservation, id=id)
    return render(request, "getreservation.html", {"reservation": reservation, "setting": settings})

# ADD ROOM RESERVATION VIEW
@login_required(login_url='/user/login/')
def add_reservation(request):
    if request.method == 'POST':
        form = RoomReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.created_by = request.user
            reservation.save()
            return redirect('reservations')
    else:
        form = RoomReservationForm()

    return render(request, 'add_reservation.html', {'form': form})

#ADD CUSTOMER VIEW
@login_required(login_url='/user/login/')
def add_customer(request):
    if request.method == 'POST':
        form =CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_reservation')
    else:
        form = CustomerForm()

    return render(request, 'add_customer.html', {'form': form})




    
    
    
#Sauna
@login_required(login_url='/user/login/')
def add_sauna(request):
    if request.method == 'POST':
        form = SaunaUserForm(request.POST)
        if form.is_valid():
            sauna_order = form.save(commit=False)
            sauna_order.created_by = request.user 
            sauna_order.save()
            
            return redirect('sauna_customers')
    else:
        form = SaunaUserForm()

    return render(request, 'add_sauna.html', {'form': form})

#all sauna_customers
@login_required(login_url='/user/login/')
def sauna_customers(request):
    saunacustomers = SaunaUser.objects.all()
    sauna_list = SaunaUser.objects.all().select_related('service', 'created_by').order_by('-order_date')
    paginator = Paginator(sauna_list, 10)
    
    # Get the page number from the request
    page_number = request.GET.get('page')
    
    # Get the corresponding page
    sauna_list = paginator.get_page(page_number)

    return render(request, "sauna_customers.html", {"sauna_list": sauna_list})
#@@@


# View for a single sauna customer's details
@login_required(login_url='/user/login/')
def get_sauna_customer(request, id):
    try:
        # Retrieve the sauna customer by their ID
        
        customer = get_object_or_404(SaunaUser, id=id)
    except SaunaUser.DoesNotExist:
        # If the customer doesn't exist, redirect to the sauna customers list with an error message
        return redirect('sauna_customers')

    # Render the customer's details in the template
    return render(request, 'eachsauna_customer.html', {'customer': customer})