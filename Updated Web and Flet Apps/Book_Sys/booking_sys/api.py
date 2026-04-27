from django.contrib.auth import authenticate
from rest_framework import viewsets, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count

from .models import (
    User, Student, Staff, Facility, Court, Availability, Slot,
    Booking, Blackout, FacilityBlackout, Notification, AuditLog,
    Announcement, ContactMessage, SiteSettings
)
from .serializers import (
    RegisterSerializer, UserSerializer, StudentSerializer, StaffSerializer,
    FacilitySerializer, CourtSerializer, AvailabilitySerializer, SlotSerializer,
    BookingSerializer, BlackoutSerializer, FacilityBlackoutSerializer,
    NotificationSerializer, AuditLogSerializer, AnnouncementSerializer,
    ContactMessageSerializer, SiteSettingsSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all().order_by('facility_name')
    serializer_class = FacilitySerializer
    permission_classes = [permissions.IsAuthenticated]


class CourtViewSet(viewsets.ModelViewSet):
    queryset = Court.objects.all().order_by('court_name')
    serializer_class = CourtSerializer
    permission_classes = [permissions.IsAuthenticated]


class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]


class SlotViewSet(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    permission_classes = [permissions.IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-booking_date', 'start_time')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BlackoutViewSet(viewsets.ModelViewSet):
    queryset = Blackout.objects.all()
    serializer_class = BlackoutSerializer
    permission_classes = [permissions.IsAuthenticated]


class FacilityBlackoutViewSet(viewsets.ModelViewSet):
    queryset = FacilityBlackout.objects.all()
    serializer_class = FacilityBlackoutSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all().order_by('-created_at')
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_facilities(request):
    facilities = Facility.objects.filter(facility_status='available').order_by('facility_name')

    data = []
    for f in facilities:
        data.append({
            'facility_id': str(f.facility_id),
            'facility_name': f.facility_name,
            'facility_type': f.facility_type,
            'location': f.location,
            'description': f.description,
            'image_url': f.image_url,
            'likes_count': f.likes_count,
            'courts_count': f.courts.filter(court_status='available').count(),
        })

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_facility_detail(request, facility_id):
    facility = get_object_or_404(Facility, facility_id=facility_id)

    courts = []
    for c in facility.courts.filter(court_status='available'):
        courts.append({
            'court_id': str(c.court_id),
            'court_name': c.court_name,
            'sport_type': c.sport_type,
            'capacity': c.capacity,
            'notes': c.notes,
            'image_url': c.image_url,
        })

    return Response({
        'facility_id': str(facility.facility_id),
        'facility_name': facility.facility_name,
        'facility_type': facility.facility_type,
        'location': facility.location,
        'description': facility.description,
        'image_url': facility.image_url,
        'courts': courts,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_slots(request, facility_id):
    facility = get_object_or_404(Facility, facility_id=facility_id)
    date_str = request.GET.get('date')

    if not date_str:
        return Response({'error': 'Date is required'}, status=400)

    try:
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)

    if booking_date < timezone.localdate():
        return Response({'error': 'Cannot book past dates'}, status=400)

    can_book, message = Booking.can_user_book(request.user, facility, booking_date)

    day_of_week = booking_date.weekday()
    courts_data = []

    for court in Court.objects.filter(facility=facility, court_status='available'):
        slots = Slot.objects.filter(
            court=court,
            day_of_week=day_of_week,
            slot_status='available'
        ).order_by('start_time')

        available_slots = []

        for slot in slots:
            if Booking.is_slot_available(court, booking_date, slot.start_time, slot.end_time):
                allowed, reason = Booking.check_time_slot_restriction(
                    request.user,
                    slot.start_time,
                    slot.end_time
                )

                if allowed:
                    available_slots.append({
                        'slot_id': str(slot.slot_id),
                        'court_id': str(court.court_id),
                        'court_name': court.court_name,
                        'start_time': slot.start_time.strftime('%H:%M'),
                        'end_time': slot.end_time.strftime('%H:%M'),
                        'start_time_display': slot.start_time.strftime('%I:%M %p'),
                        'end_time_display': slot.end_time.strftime('%I:%M %p'),
                        'slot_type': slot.slot_type,
                    })

        if available_slots:
            courts_data.append({
                'court_id': str(court.court_id),
                'court_name': court.court_name,
                'sport_type': court.sport_type,
                'capacity': court.capacity,
                'slots': available_slots,
            })

    return Response({
        'facility_id': str(facility.facility_id),
        'facility_name': facility.facility_name,
        'date': date_str,
        'can_book': can_book,
        'message': message,
        'courts': courts_data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mobile_create_booking(request):
    facility_id = request.data.get('facility_id')
    court_id = request.data.get('court_id')
    booking_date_str = request.data.get('booking_date')
    start_time_str = request.data.get('start_time')
    end_time_str = request.data.get('end_time')
    notes = request.data.get('notes', '')

    if not all([facility_id, court_id, booking_date_str, start_time_str, end_time_str]):
        return Response({'error': 'Missing required fields'}, status=400)

    facility = get_object_or_404(Facility, facility_id=facility_id)
    court = get_object_or_404(Court, court_id=court_id)

    try:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        return Response({'error': 'Invalid date or time format'}, status=400)

    if not Booking.is_slot_available(court, booking_date, start_time, end_time):
        return Response({'error': 'This slot is already booked'}, status=400)

    allowed, reason = Booking.check_time_slot_restriction(request.user, start_time, end_time)
    if not allowed:
        return Response({'error': reason}, status=400)

    try:
        booking = Booking.objects.create(
            user=request.user,
            facility=facility,
            court=court,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            status='confirmed'
        )
    except ValidationError as e:
        return Response({'error': str(e)}, status=400)

    return Response({
        'success': True,
        'message': 'Booking created successfully',
        'booking_id': str(booking.booking_id),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-start_time')

    data = []
    for b in bookings:
        data.append({
            'booking_id': str(b.booking_id),
            'facility_name': b.facility.facility_name,
            'court_name': b.court.court_name,
            'booking_date': b.booking_date.strftime('%Y-%m-%d'),
            'start_time': b.start_time.strftime('%H:%M'),
            'end_time': b.end_time.strftime('%H:%M'),
            'time_display': f"{b.start_time.strftime('%I:%M %p')} - {b.end_time.strftime('%I:%M %p')}",
            'status': b.status,
            'notes': b.notes,
        })

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mobile_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if booking.status == 'cancelled':
        return Response({'error': 'Booking already cancelled'}, status=400)

    booking.status = 'cancelled'
    booking.save()

    return Response({
        'success': True,
        'message': 'Booking cancelled successfully'
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def mobile_top_facilities(request):
    top_facilities = (
        Facility.objects
        .filter(facility_status="available")
        .annotate(bookings_count=Count("bookings"))
        .filter(bookings_count__gt=0)
        .order_by("-bookings_count", "facility_name")[:3]
    )

    top_facilities = list(top_facilities)

    if len(top_facilities) < 3:
        existing_ids = [facility.facility_id for facility in top_facilities]

        fallback_facilities = (
            Facility.objects
            .filter(facility_status="available")
            .exclude(facility_id__in=existing_ids)
            .order_by("facility_name")[:3 - len(top_facilities)]
        )

        facilities = top_facilities + list(fallback_facilities)
    else:
        facilities = top_facilities

    data = []

    for facility in facilities:
        data.append({
            "facility_id": str(facility.facility_id),
            "facility_name": facility.facility_name,
            "facility_type": facility.facility_type,
            "location": facility.location,
            "description": facility.description,
            "image_url": facility.image_url,
            "bookings_count": getattr(facility, "bookings_count", 0),
            "courts_count": facility.courts.filter(court_status="available").count(),
        })

    return Response(data)