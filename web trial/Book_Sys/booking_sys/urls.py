from django.urls import path
from . import views
app_name = 'booking_sys'
urlpatterns = [
    # Public pages (GET only)
    path('', views.home, name='home'),
    path('facilities/', views.facilities, name='facilities'),
    path('facility/<slug:slug>/', views.facility_detail, name='facility_detail'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('search/', views.search_facilities, name='search_facilities'),
    
    # Authentication (GET and POST)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # User profile (GET and POST)
    path('profile/', views.profile, name='profile'),
    
    # Booking management (GET and POST)
    path('booking/create/', views.create_booking, name='create_booking'),
    path('booking/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Admin functions (GET and POST)
    path('admin/facility/create/', views.create_facility, name='create_facility'),
    path('admin/court/create/', views.create_court, name='create_court'),
    path('admin/slot/create/', views.create_slot, name='create_slot'),
    path('admin/blackout/create/', views.create_blackout, name='create_blackout'),
    path('admin/availability/create/', views.create_availability, name='create_availability'),
]