from django.urls import path
from .views import  *
from room_bookings.generate_pdfs.sauna_order import print_sauna_order
from room_bookings.generate_pdfs.reservation_order import print_reservation

urlpatterns=[
        # Reservations
    path('reservations/', reservation, name='reservations'),
    path('add-reservation/', add_reservation, name='add_reservation'),
    path('reservations/<str:id>/', getReservation, name='get_reservation'),
    path('add-customer/', add_customer, name='add_customer'),
    path('fetch_reservation_details/<int:reservation_id>/', fetch_reservation_details, name='fetch_reservation_details'),
    path('print_reservation/<int:id>/', print_reservation, name='print_reservation'),
    
    #Sauna
    path('sauna/', add_sauna, name = 'add_sauna'),
    path('sauna_customers/', sauna_customers, name = 'sauna_customers'),
    path('print_sauna_order/<int:id>/', print_sauna_order, name='print_sauna_order'),
    path('get_sauna_customer/<int:id>/', get_sauna_customer, name='get_sauna_customer'),

    # Room Types and Rooms
    path('roomtypes/', rooms, name='rooms'),
    path('rooms/<str:id>/', rooms_filter, name='rooms-filter'),

]