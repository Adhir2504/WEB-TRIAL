"""
URL configuration for Book_Sys project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as auth_views

# Import all your ViewSets and API views from api.py
from booking_sys.api import (
    UserViewSet, StudentViewSet, StaffViewSet, FacilityViewSet,
    CourtViewSet, AvailabilityViewSet, SlotViewSet, BookingViewSet,
    BlackoutViewSet, FacilityBlackoutViewSet, NotificationViewSet,
    AuditLogViewSet, AnnouncementViewSet, ContactMessageViewSet,
    SiteSettingsViewSet,
    # Import the function-based views
    api_register, api_login, mobile_facilities, mobile_facility_detail,
    mobile_slots, mobile_create_booking, mobile_my_bookings,
    mobile_cancel_booking, mobile_top_facilities
)

# Create router and register ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='api-users')
router.register(r'students', StudentViewSet, basename='api-students')
router.register(r'staff', StaffViewSet, basename='api-staff')
router.register(r'facilities', FacilityViewSet, basename='api-facilities')
router.register(r'courts', CourtViewSet, basename='api-courts')
router.register(r'availabilities', AvailabilityViewSet, basename='api-availabilities')
router.register(r'slots', SlotViewSet, basename='api-slots')
router.register(r'bookings', BookingViewSet, basename='api-bookings')
router.register(r'blackouts', BlackoutViewSet, basename='api-blackouts')
router.register(r'facility-blackouts', FacilityBlackoutViewSet, basename='api-facility-blackouts')
router.register(r'notifications', NotificationViewSet, basename='api-notifications')
router.register(r'audit-logs', AuditLogViewSet, basename='api-audit-logs')
router.register(r'announcements', AnnouncementViewSet, basename='api-announcements')
router.register(r'contact-messages', ContactMessageViewSet, basename='api-contact-messages')
router.register(r'site-settings', SiteSettingsViewSet, basename='api-site-settings')

# Main urlpatterns
urlpatterns = [
    # Web application URLs (your existing booking_sys URLs)
    path('', include(('booking_sys.urls', 'booking_sys'), namespace='booking_sys')),
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # Django auth
    path('accounts/', include('django.contrib.auth.urls')),
]

# API URLs
urlpatterns += [
    # Router URLs (ViewSets)
    path('api/', include(router.urls)),
    
    # Authentication endpoints (function-based views - NO include() needed)
    path('api/auth/register/', api_register, name='api_register'),
    path('api/auth/login/', api_login, name='api_login'),
    path('api-token-auth/', auth_views.obtain_auth_token, name='api_token_auth'),
    
    # Mobile-specific endpoints (function-based views)
    path('api/mobile/facilities/', mobile_facilities, name='mobile_facilities'),
    path('api/mobile/facilities/<uuid:facility_id>/', mobile_facility_detail, name='mobile_facility_detail'),
    path('api/mobile/facilities/<uuid:facility_id>/slots/', mobile_slots, name='mobile_slots'),
    path('api/mobile/bookings/create/', mobile_create_booking, name='mobile_create_booking'),
    path('api/mobile/bookings/', mobile_my_bookings, name='mobile_my_bookings'),
    path('api/mobile/bookings/<uuid:booking_id>/cancel/', mobile_cancel_booking, name='mobile_cancel_booking'),
    path('api/mobile/top-facilities/', mobile_top_facilities, name='mobile_top_facilities'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)