from django.urls import path
from . import views
app_name = 'booking_sys'
urlpatterns = [
    # Public pages (GET only)
    path('', views.home, name='home'),
    path('facilities/', views.facilities, name='facilities'),
    path('facility/<slug:slug>/', views.facility_detail, name='facility_detail'),
    path('facility/<slug:slug>/courts/', views.facility_courts, name='facility_courts'),
    path('search/', views.search_facilities, name='search_facilities'),
    
    # Authentication (GET and POST)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # User profile (GET and POST)
    path('profile/', views.profile, name='profile'),
    
    # Booking management (GET and POST)
    path('booking/create/', views.create_booking, name='create_booking'),
    path('booking/slot/<uuid:slot_id>/book/', views.book_slot, name='book_slot'),
    path('booking/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Admin functions (GET and POST) - using 'manage' prefix to avoid conflict with Django admin
    path('manage/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/facility/create/', views.create_facility, name='create_facility'),
    path('manage/facility/<uuid:facility_id>/edit/', views.edit_facility, name='edit_facility'),
    path('manage/court/create/', views.create_court, name='create_court'),
    path('manage/slot/create/', views.create_slot, name='create_slot'),
    path('manage/blackout/create/', views.create_blackout, name='create_blackout'),
    path('manage/facility-blackout/create/', views.create_facility_blackout, name='create_facility_blackout'),
    path('manage/availability/create/', views.create_availability, name='create_availability'),
    path('manage/announcement/create/', views.create_announcement, name='create_announcement'),
    
    # API endpoints for calendar booking
    path('api/facility/<uuid:facility_id>/slots/', views.api_get_available_slots, name='api_get_slots'),
    path('api/booking/create/', views.api_create_booking, name='api_create_booking'),
    path('api/facility/<uuid:facility_id>/user-status/', views.api_user_booking_status, name='api_user_status'),
]