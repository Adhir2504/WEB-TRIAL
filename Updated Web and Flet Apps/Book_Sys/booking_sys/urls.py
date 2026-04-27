from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    api_login, api_register, UserViewSet, StudentViewSet, StaffViewSet,
    FacilityViewSet, CourtViewSet, AvailabilityViewSet, SlotViewSet,
    BookingViewSet, BlackoutViewSet, FacilityBlackoutViewSet,
    NotificationViewSet, AuditLogViewSet, AnnouncementViewSet,
    ContactMessageViewSet, SiteSettingsViewSet,
    mobile_facilities,
    mobile_facility_detail,
    mobile_slots,
    mobile_create_booking,
    mobile_my_bookings,
    mobile_cancel_booking,
    mobile_top_facilities,
)

app_name = 'booking_sys'
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('students', StudentViewSet)
router.register('staff', StaffViewSet)
router.register('facilities', FacilityViewSet)
router.register('courts', CourtViewSet)
router.register('availabilities', AvailabilityViewSet)
router.register('slots', SlotViewSet)
router.register('bookings', BookingViewSet)
router.register('blackouts', BlackoutViewSet)
router.register('facility-blackouts', FacilityBlackoutViewSet)
router.register('notifications', NotificationViewSet)
router.register('audit-logs', AuditLogViewSet)
router.register('announcements', AnnouncementViewSet)
router.register('contact-messages', ContactMessageViewSet)
router.register('site-settings', SiteSettingsViewSet)

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
    path('contact/', views.contact, name='contact'),
    path("api/mobile/top-facilities/", mobile_top_facilities, name="mobile_top_facilities"),
    
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
    path('manage/ajax-facilities/', views.ajax_facilities, name='ajax_facilities'),
    
    # API endpoints for calendar booking
    path('api/facility/<uuid:facility_id>/slots/', views.api_get_available_slots, name='api_get_slots'),
    path('api/booking/create/', views.api_create_booking, name='api_create_booking'),
    path('api/facility/<uuid:facility_id>/user-status/', views.api_user_booking_status, name='api_user_status'),
    
    # DRF router and token auth endpoints
    path('api/login/', api_login, name='api_login'),
    path('api/register/', api_register, name='api_register'),
    path('api/mobile/facilities/', mobile_facilities, name='mobile_facilities'),
    path('api/mobile/facilities/<uuid:facility_id>/', mobile_facility_detail, name='mobile_facility_detail'),
    path('api/mobile/facilities/<uuid:facility_id>/slots/', mobile_slots, name='mobile_slots'),
    path('api/mobile/bookings/create/', mobile_create_booking, name='mobile_create_booking'),
    path('api/mobile/bookings/', mobile_my_bookings, name='mobile_my_bookings'),
    path('api/mobile/bookings/<uuid:booking_id>/cancel/', mobile_cancel_booking, name='mobile_cancel_booking'),
    path('api/', include(router.urls)),
]