from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from django.db import models
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date
import json
from .models import (
    User, Student, Staff, Facility, Court, Slot, Booking, 
    Blackout, FacilityBlackout, Availability, Notification, Announcement
)
from .forms import (
    UserRegistrationForm, UserProfileEditForm, StudentProfileForm, 
    StaffProfileForm, FacilityForm, CourtForm, SlotForm, BookingForm, 
    BlackoutForm, FacilityBlackoutForm, AvailabilityForm, NotificationForm, AnnouncementForm
)


# Home view - GET only
def home(request):
    """Home page view - displays welcome page"""
    from django.utils import timezone
    from django.db.models import Count
    from datetime import timedelta
    from .models import SiteSettings
    
    # Get site settings
    settings = SiteSettings.get_settings()
    
    # Get top 3 most booked facilities this week
    now = timezone.now()
    week_start = now - timedelta(days=now.weekday())  # Monday of current week
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    facilities = Facility.objects.filter(
        facility_status='available'
    ).annotate(
        bookings_this_week=Count(
            'bookings',
            filter=models.Q(bookings__booking_date__gte=week_start.date())
        )
    ).order_by('-bookings_this_week')[:3]
    
    # Get active announcements
    announcements = Announcement.objects.filter(
        status='published'
    ).filter(
        models.Q(publish_date__isnull=True) | models.Q(publish_date__lte=now)
    ).filter(
        models.Q(expiry_date__isnull=True) | models.Q(expiry_date__gte=now)
    ).order_by('-is_featured', '-created_at')[:5]
    
    return render(request, 'home.html', {
        'facilities': facilities,
        'announcements': announcements,
        'site_settings': settings
    })


# Facilities list view - GET only
def facilities(request):
    """Display all facilities - GET request"""
    if request.method == 'GET':
        facility_type = request.GET.get('type', '')
        facilities_list = Facility.objects.all()
        
        if facility_type:
            facilities_list = facilities_list.filter(facility_type=facility_type)
        
        # Get next available slots for each facility
        facilities_with_slots = []
        for facility in facilities_list:
            # Get courts for this facility
            courts = Court.objects.filter(facility=facility, court_status='available')
            # Get next available slot
            next_slot = None
            if courts.exists():
                slots = Slot.objects.filter(
                    court__in=courts,
                    slot_status='available'
                ).order_by('day_of_week', 'start_time').first()
                if slots:
                    next_slot = slots
            
            # Get total capacity from courts
            total_capacity = sum(court.capacity for court in courts) if courts.exists() else 0
            
            facilities_with_slots.append({
                'facility': facility,
                'next_slot': next_slot,
                'capacity': total_capacity,
                'courts_count': courts.count()
            })
        
        return render(request, 'facilities.html', {
            'facilities_data': facilities_with_slots,
            'selected_type': facility_type
        })
    return HttpResponse(status=405)


# Facility detail view - GET only (no booking here)
@require_http_methods(["GET"])
def facility_detail(request, slug):
    """Display facility details only (no booking UI)"""
    # For now, using slug as facility name search
    facility = get_object_or_404(Facility, facility_name__icontains=slug.replace('-', ' '))
    courts = Court.objects.filter(facility=facility)

    return render(request, 'facility_details.html', {
        'facility': facility,
        'courts': courts,
    })


# Facility courts / booking view - GET only (booking via per-slot actions)
@login_required
@require_http_methods(["GET"])
def facility_courts(request, slug):
    """Display courts for a facility with available slots for selected date"""
    facility = get_object_or_404(Facility, facility_name__icontains=slug.replace('-', ' '))
    
    # Get date from query parameter
    date_str = request.GET.get('date')
    selected_date = None
    court_data = []
    
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if date is in the past
            if selected_date < timezone.localdate():
                messages.warning(request, 'Cannot view slots for past dates.')
                selected_date = None
            else:
                # Get all available courts for this facility
                courts = Court.objects.filter(facility=facility, court_status='available').order_by('court_name')
                
                # Get day of week for the selected date
                day_of_week = selected_date.weekday()
                
                for court in courts:
                    # Check if court is available on this day
                    try:
                        availability = Availability.objects.get(court=court, day_of_week=day_of_week)
                    except Availability.DoesNotExist:
                        continue
                    
                    # Get slots for this court and day
                    slots = Slot.objects.filter(
                        court=court,
                        day_of_week=day_of_week,
                        slot_status='available'
                    ).order_by('start_time')
                    
                    # Check which slots are actually available (not booked)
                    available_slots = []
                    for slot in slots:
                        is_available = Booking.is_slot_available(
                            court, selected_date, slot.start_time, slot.end_time
                        )
                        if is_available:
                            available_slots.append(slot)
                    
                    if available_slots:
                        court_data.append({
                            'court': court,
                            'slots': available_slots,
                            'slot_count': len(available_slots),
                        })
        except ValueError:
            messages.error(request, 'Invalid date format.')
            selected_date = None
    
    # Get user's booking status if logged in
    user_booking_status = None
    if request.user.is_authenticated and selected_date:
        weekly_bookings = Booking.get_user_weekly_bookings(request.user, facility, selected_date)
        monthly_bookings = Booking.get_user_monthly_bookings(request.user, facility, selected_date)
        user_booking_status = {
            'weekly_count': weekly_bookings.count(),
            'monthly_count': monthly_bookings.count(),
            'weekly_limit': 1,
            'monthly_limit': 4,
            'can_book_this_week': weekly_bookings.count() < 1,
            'can_book_this_month': monthly_bookings.count() < 4,
        }
    
    return render(request, 'facility_courts.html', {
        'facility': facility,
        'court_data': court_data,
        'selected_date': selected_date,
        'date_str': date_str,
        'today': timezone.localdate(),
        'user_booking_status': user_booking_status,
    })


# Profile view - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def profile(request):
    """User profile view - handles GET and POST requests"""
    user = request.user
    
    if request.method == 'GET':
        # Display profile form
        profile_form = UserProfileEditForm(instance=user)
        
        # Get additional profile data
        student_profile = None
        staff_profile = None
        student_form = None
        staff_form = None
        
        if hasattr(user, 'student'):
            student_profile = user.student
            student_form = StudentProfileForm(instance=student_profile)
        elif user.member_type == 'student':
            student_form = StudentProfileForm()
        
        if hasattr(user, 'staff'):
            staff_profile = user.staff
            staff_form = StaffProfileForm(instance=staff_profile)
        elif user.member_type == 'staff':
            staff_form = StaffProfileForm()
        
        bookings = Booking.objects.filter(user=user).order_by('-booking_date', '-start_time')[:10]
        
        return render(request, 'profile.html', {
            'profile_form': profile_form,
            'student_form': student_form,
            'staff_form': staff_form,
            'student_profile': student_profile,
            'staff_profile': staff_profile,
            'bookings': bookings,
        })
    
    elif request.method == 'POST':
        # Handle profile update
        form_type = request.POST.get('form_type', 'profile')
        
        if form_type == 'profile':
            profile_form = UserProfileEditForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('booking_sys:profile')
            else:
                messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'student':
            if user.member_type == 'student':
                if hasattr(user, 'student'):
                    student_form = StudentProfileForm(request.POST, instance=user.student)
                else:
                    student_form = StudentProfileForm(request.POST)
                
                if student_form.is_valid():
                    student = student_form.save(commit=False)
                    student.user = user
                    student.save()
                    messages.success(request, 'Student profile updated successfully!')
                    return redirect('booking_sys:profile')
                else:
                    messages.error(request, 'Please correct the errors below.')
        
        elif form_type == 'staff':
            if user.member_type == 'staff':
                if hasattr(user, 'staff'):
                    staff_form = StaffProfileForm(request.POST, instance=user.staff)
                else:
                    staff_form = StaffProfileForm(request.POST)
                
                if staff_form.is_valid():
                    staff = staff_form.save(commit=False)
                    staff.user = user
                    staff.save()
                    messages.success(request, 'Staff profile updated successfully!')
                    return redirect('booking_sys:profile')
                else:
                    messages.error(request, 'Please correct the errors below.')
        
        # Re-render with errors
        return render(request, 'profile.html', {
            'profile_form': profile_form if form_type == 'profile' else UserProfileEditForm(instance=user),
            'student_form': student_form if form_type == 'student' else (StudentProfileForm(instance=user.student) if hasattr(user, 'student') else StudentProfileForm()),
            'staff_form': staff_form if form_type == 'staff' else (StaffProfileForm(instance=user.staff) if hasattr(user, 'staff') else StaffProfileForm()),
        })


# Login view - GET and POST
@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view - handles GET and POST requests"""
    if request.user.is_authenticated:
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})
    
    elif request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if email and password:
            # Authenticate using email (since USERNAME_FIELD is 'email')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Personalized welcome message based on time and user type
                    from django.utils import timezone
                    hour = timezone.localtime(timezone.now()).hour
                    if hour < 12:
                        greeting = "Good morning"
                    elif hour < 18:
                        greeting = "Good afternoon"
                    else:
                        greeting = "Good evening"
                    
                    messages.success(request, f'{greeting}, {user.first_name}! Welcome back to UniBook.')
                    
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('booking_sys:home')
                else:
                    messages.error(request, 'This account has been deactivated.')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'Please provide both email and password.')
        
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})


# Logout view
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('booking_sys:home')


# User Registration - GET and POST
@require_http_methods(["GET", "POST"])
def register(request):
    """User registration view - handles GET and POST requests"""
    if request.user.is_authenticated:
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'form': form})
    
    elif request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Create profile based on member type
                member_type = form.cleaned_data.get('member_type')
                profile_created = False
                
                if member_type == 'student':
                    student_id = request.POST.get('student_id', '').strip().upper()
                    if student_id:
                        Student.objects.create(user=user, student_id=student_id)
                        profile_created = True
                elif member_type == 'staff':
                    department = request.POST.get('department', '').strip()
                    if department:
                        Staff.objects.create(user=user, department=department)
                        profile_created = True
                
                # Auto-login after registration
                # Use the raw password before it was hashed
                raw_password = form.cleaned_data.get('password1')
                # Authenticate using the email (since USERNAME_FIELD is 'email')
                authenticated_user = authenticate(request, username=user.email, password=raw_password)
                
                if authenticated_user is not None:
                    login(request, authenticated_user)
                    # Welcome message with next steps
                    welcome_msg = f'🎉 Welcome to UniBook, {user.first_name}! Your account has been created successfully.'
                    messages.success(request, welcome_msg)
                    
                    if not profile_created and member_type != 'admin':
                        messages.info(request, 'Complete your profile to unlock all features.')
                    else:
                        messages.info(request, 'You can now browse facilities and make bookings.')
                    
                    return redirect('booking_sys:home')
                else:
                    # If auto-login fails, still redirect to login but with success message
                    messages.success(request, f'Account created successfully! Please log in with your credentials.')
                    return redirect('booking_sys:login')
            except Exception as e:
                messages.error(request, f'An error occurred during registration: {str(e)}')
        else:
            # Display specific validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_name = form.fields[field].label if field in form.fields else field
                        messages.error(request, f'{field_name}: {error}')
        
        return render(request, 'registration/register.html', {'form': form})


# Booking creation - legacy generic view (kept for compatibility, not linked in UI)
@login_required
@require_http_methods(["GET", "POST"])
def create_booking(request):
    """Create a booking - generic form (not used in new flow)"""
    if request.method == 'GET':
        form = BookingForm(user=request.user)
        available_slots = Slot.objects.filter(slot_status='available')
        return render(request, 'booking/create_booking.html', {
            'form': form,
            'available_slots': available_slots
        })
    
    elif request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            
            # Update slot status
            slot = booking.slot
            slot.change_status('booked')
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_sys:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            available_slots = Slot.objects.filter(slot_status='available')
            return render(request, 'booking/create_booking.html', {
                'form': form,
                'available_slots': available_slots
            })


@login_required
@require_http_methods(["POST"])
def book_slot(request, slot_id):
    """Book a specific slot from the facility courts page"""
    slot = get_object_or_404(Slot, slot_id=slot_id, slot_status='available')
    
    # Check for blackout periods
    from datetime import datetime as dt
    booking_date = dt.now().date()  # Get current booking context
    start_datetime = dt.combine(booking_date, slot.start_time)
    end_datetime = dt.combine(booking_date, slot.end_time)
    
    blackout_conflicts = Blackout.objects.filter(
        court=slot.court,
        start_date_time__lt=end_datetime,
        end_date_time__gt=start_datetime
    )
    
    if blackout_conflicts.exists():
        blackout = blackout_conflicts.first()
        messages.error(request, f'This court is unavailable during this time due to blackout: {blackout.reason}')
        return redirect('booking_sys:profile')

    # Create booking
    booking = Booking.objects.create(user=request.user, slot=slot)

    # Update slot status
    slot.change_status('booked')

    messages.success(request, f'Booking created for {slot.court.court_name} on slot {slot.start_time} - {slot.end_time}.')
    return redirect('booking_sys:profile')


# Facility creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_facility(request):
    """Create a facility - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = FacilityForm()
        return render(request, 'admin/create_facility.html', {'form': form, 'is_edit': False})
    
    elif request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            facility = form.save()
            messages.success(request, f'Facility "{facility.facility_name}" created successfully!')
            return redirect('booking_sys:facilities')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_facility.html', {'form': form, 'is_edit': False})


# Facility edit (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def edit_facility(request, facility_id):
    """Edit a facility - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    facility = get_object_or_404(Facility, facility_id=facility_id)
    
    if request.method == 'GET':
        form = FacilityForm(instance=facility)
        return render(request, 'admin/create_facility.html', {
            'form': form,
            'facility': facility,
            'is_edit': True
        })
    
    elif request.method == 'POST':
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            facility = form.save()
            messages.success(request, f'Facility "{facility.facility_name}" updated successfully!')
            return redirect('booking_sys:facilities')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_facility.html', {
                'form': form,
                'facility': facility,
                'is_edit': True
            })


# Court creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_court(request):
    """Create or edit a court - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    court = None
    court_id = request.GET.get('edit')
    is_edit = False
    
    if court_id:
        try:
            court = Court.objects.get(pk=court_id)
            is_edit = True
        except Court.DoesNotExist:
            messages.error(request, 'Court not found.')
            return redirect('booking_sys:facilities')
    
    if request.method == 'GET':
        if is_edit:
            form = CourtForm(instance=court)
        else:
            form = CourtForm()
        return render(request, 'admin/create_court.html', {
            'form': form,
            'court': court,
            'is_edit': is_edit
        })
    
    elif request.method == 'POST':
        if is_edit:
            form = CourtForm(request.POST, instance=court)
        else:
            form = CourtForm(request.POST)
        
        if form.is_valid():
            court = form.save()
            action = 'updated' if is_edit else 'created'
            messages.success(request, f'Court "{court.court_name}" {action} successfully!')
            return redirect('booking_sys:facilities')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_court.html', {
                'form': form,
                'court': court,
                'is_edit': is_edit
            })


# Slot creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_slot(request):
    """Create a slot - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = SlotForm()
        return render(request, 'admin/create_slot.html', {'form': form})
    
    elif request.method == 'POST':
        form = SlotForm(request.POST)
        if form.is_valid():
            slot = form.save()
            messages.success(request, 'Slot created successfully!')
            return redirect('booking_sys:admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_slot.html', {'form': form})


# Blackout creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_blackout(request):
    """Create a blackout period - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = BlackoutForm()
        return render(request, 'admin/create_blackout.html', {'form': form})
    
    elif request.method == 'POST':
        form = BlackoutForm(request.POST)
        if form.is_valid():
            blackout = form.save()
            messages.success(request, 'Blackout period created successfully!')
            return redirect('booking_sys:admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_blackout.html', {'form': form})


# Facility Blackout creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_facility_blackout(request):
    """Create a facility-wide blackout period - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = FacilityBlackoutForm()
        return render(request, 'admin/create_facility_blackout.html', {'form': form})
    
    elif request.method == 'POST':
        form = FacilityBlackoutForm(request.POST)
        if form.is_valid():
            facility_blackout = form.save()
            messages.success(request, f'Facility-wide blackout created successfully for {facility_blackout.facility.facility_name}!')
            return redirect('booking_sys:admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_facility_blackout.html', {'form': form})


# Availability creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_availability(request):
    """Create availability schedule - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = AvailabilityForm()
        return render(request, 'admin/create_availability.html', {'form': form})
    
    elif request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save()
            messages.success(request, 'Availability schedule created successfully!')
            return redirect('booking_sys:admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_availability.html', {'form': form})


# Announcement creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_announcement(request):
    """Create an announcement - handles GET and POST requests (Admin only)"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = AnnouncementForm()
        return render(request, 'admin/create_announcement.html', {'form': form})
    
    elif request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, f'Announcement "{announcement.title}" created successfully!')
            return redirect('booking_sys:admin_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_announcement.html', {'form': form})


# Admin Dashboard - GET only
@login_required
@require_http_methods(["GET"])
def admin_dashboard(request):
    """Admin dashboard with quick stats and actions"""
    if not (request.user.is_staff or request.user.member_type == 'admin'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    # Get statistics
    from django.utils import timezone
    from datetime import timedelta
    
    total_facilities = Facility.objects.count()
    total_courts = Court.objects.count()
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status__in=['pending', 'confirmed']).count()
    total_users = User.objects.count()
    recent_announcements = Announcement.objects.filter(status='published').order_by('-created_at')[:5]
    
    # Recent activity
    recent_bookings = Booking.objects.order_by('-created_at')[:10]
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # All facilities for management
    all_facilities = Facility.objects.all().order_by('facility_name')
    
    context = {
        'total_facilities': total_facilities,
        'total_courts': total_courts,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_users': total_users,
        'recent_announcements': recent_announcements,
        'recent_bookings': recent_bookings,
        'recent_users': recent_users,
        'all_facilities': all_facilities,
    }
    
    return render(request, 'admin/dashboard.html', context)


# Cancel booking - POST only
@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    """Cancel a booking - POST request only"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.cancel_booking()
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('booking_sys:profile')
    
    return HttpResponse(status=405)


# Search facilities - GET only
@require_http_methods(["GET"])
def search_facilities(request):
    """Search facilities by name or type - GET request"""
    query = request.GET.get('q', '')
    facility_type = request.GET.get('type', '')
    date_str = request.GET.get('date', '')
    
    facilities_list = Facility.objects.all()
    
    if query:
        facilities_list = facilities_list.filter(facility_name__icontains=query)
    
    if facility_type:
        facilities_list = facilities_list.filter(facility_type=facility_type)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request - return JSON
        results = [{
            'id': str(f.facility_id),
            'name': f.facility_name,
            'type': f.get_facility_type_display(),
            'location': f.location,
            'status': f.get_facility_status_display()
        } for f in facilities_list]
        return JsonResponse({'facilities': results})
    
    # Get next available slots for each facility (same as facilities view)
    facilities_with_slots = []
    for facility in facilities_list:
        courts = Court.objects.filter(facility=facility, court_status='available')
        next_slot = None
        if courts.exists():
            slots = Slot.objects.filter(
                court__in=courts,
                slot_status='available'
            ).order_by('day_of_week', 'start_time').first()
            if slots:
                next_slot = slots
        
        total_capacity = sum(court.capacity for court in courts) if courts.exists() else 0
        
        # Check for facility-wide blackout on selected date
        facility_blackout = None
        facility_unavailable_during = None
        if date_str:
            try:
                from datetime import datetime
                # Parse the date string (format: YYYY-MM-DD)
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Check for overlapping facility blackouts
                # We need to check if any blackout period covers any time on this date
                start_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
                end_of_day = timezone.make_aware(datetime.combine(date_obj, datetime.max.time()))
                
                from .models import FacilityBlackout
                blackout = FacilityBlackout.objects.filter(
                    facility=facility,
                    start_date_time__lt=end_of_day,
                    end_date_time__gt=start_of_day
                ).first()
                
                if blackout:
                    facility_blackout = blackout
                    # Format the unavailable time range
                    blackout_start = blackout.start_date_time.strftime('%I:%M %p')
                    blackout_end = blackout.end_date_time.strftime('%I:%M %p')
                    facility_unavailable_during = f"{blackout_start} - {blackout_end}"
            except Exception:
                pass
        
        facilities_with_slots.append({
            'facility': facility,
            'next_slot': next_slot,
            'capacity': total_capacity,
            'courts_count': courts.count(),
            'facility_blackout': facility_blackout,
            'facility_unavailable_during': facility_unavailable_during
        })
    
    return render(request, 'facilities.html', {
        'facilities_data': facilities_with_slots,
        'query': query,
        'selected_type': facility_type,
        'selected_date': date_str
    })


# API endpoint to get available slots for a specific date and facility
@login_required
@require_http_methods(["GET"])
def api_get_available_slots(request, facility_id):
    """API endpoint to get available slots for a specific date and facility"""
    try:
        facility = get_object_or_404(Facility, facility_id=facility_id)
        date_str = request.GET.get('date')
        
        if not date_str:
            return JsonResponse({'error': 'Date parameter is required'}, status=400)
        
        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
        
        # Check if date is in the past
        if booking_date < timezone.localdate():
            return JsonResponse({'error': 'Cannot book for past dates'}, status=400)
        
        # Check 2-month booking window constraint
        today = timezone.localdate()
        two_months_ago = today - timedelta(days=60)
        two_months_later = today + timedelta(days=60)
        
        if booking_date < two_months_ago or booking_date > two_months_later:
            return JsonResponse({
                'error': f'Bookings can only be made within 2 months from today. '
                         f'You can book between {two_months_ago.strftime("%B %d, %Y")} and {two_months_later.strftime("%B %d, %Y")}.',
                'booking_window_exceeded': True
            }, status=400)
        
        # Check user's booking eligibility for this facility
        can_book, message = Booking.can_user_book(request.user, facility, booking_date)
        
        # Check for facility-wide blackout on this date
        day_start = datetime.combine(booking_date, datetime.min.time())
        day_end = datetime.combine(booking_date, datetime.max.time())
        day_start_aware = timezone.make_aware(day_start) if timezone.is_naive(day_start) else day_start
        day_end_aware = timezone.make_aware(day_end) if timezone.is_naive(day_end) else day_end
        
        facility_blackout = FacilityBlackout.objects.filter(
            facility=facility,
            start_date_time__lt=day_end_aware,
            end_date_time__gt=day_start_aware
        ).first()
        
        if facility_blackout:
            blackout_start = facility_blackout.start_date_time.strftime('%I:%M %p')
            blackout_end = facility_blackout.end_date_time.strftime('%I:%M %p')
            return JsonResponse({
                'error': f'Facility is unavailable during this time',
                'facility_closed': True,
                'blackout_reason': facility_blackout.reason,
                'blackout_time': f'{blackout_start} - {blackout_end}',
                'message': f'{facility_blackout.reason} ({blackout_start} - {blackout_end})'
            }, status=400)
        
        # Get all courts for this facility
        courts = Court.objects.filter(facility=facility, court_status='available')
        
        courts_data = []
        for court in courts:
            # Get day of week (0=Monday, 6=Sunday)
            day_of_week = booking_date.weekday()
            
            # Get availability for this day
            try:
                availability = Availability.objects.get(court=court, day_of_week=day_of_week)
            except Availability.DoesNotExist:
                continue  # Court not available on this day
            
            # Check for blackouts on this date
            blackouts_today = Blackout.objects.filter(
                court=court,
                start_date_time__lt=day_end_aware,
                end_date_time__gt=day_start_aware
            ).order_by('start_date_time')
            
            # Get slots for this court and day
            slots = Slot.objects.filter(
                court=court,
                day_of_week=day_of_week,
                slot_status='available'
            ).order_by('start_time')
            
            # Check which slots are actually available (not booked)
            available_slots = []
            restricted_slots = []
            for slot in slots:
                is_available = Booking.is_slot_available(
                    court, booking_date, slot.start_time, slot.end_time
                )
                
                # Also check for blackout periods
                blackout_reason = None
                if is_available:
                    start_datetime = datetime.combine(booking_date, slot.start_time)
                    end_datetime = datetime.combine(booking_date, slot.end_time)
                    
                    blackout_conflicts = Blackout.objects.filter(
                        court=court,
                        start_date_time__lt=end_datetime,
                        end_date_time__gt=start_datetime
                    )
                    
                    if blackout_conflicts.exists():
                        blackout = blackout_conflicts.first()
                        is_available = False
                        blackout_reason = blackout.reason
                
                # Check time slot restrictions based on user member type
                time_allowed, time_message = Booking.check_time_slot_restriction(
                    request.user, slot.start_time, slot.end_time
                )
                
                slot_display = {
                    'slot_id': str(slot.slot_id),
                    'start_time': slot.start_time.strftime('%H:%M'),
                    'end_time': slot.end_time.strftime('%H:%M'),
                    'start_time_display': slot.start_time.strftime('%I:%M %p'),
                    'end_time_display': slot.end_time.strftime('%I:%M %p'),
                    'slot_type': slot.get_slot_type_display(),
                }
                
                if is_available and time_allowed:
                    # Slot is available and user is allowed to book it
                    available_slots.append(slot_display)
                elif is_available and not time_allowed:
                    # Slot is available but user is restricted from booking it
                    restricted_slots.append({
                        **slot_display,
                        'reason': time_message,
                        'reason_type': 'time_restriction'
                    })
                elif blackout_reason:
                    # Slot has a blackout
                    restricted_slots.append({
                        **slot_display,
                        'reason': blackout_reason,
                        'reason_type': 'blackout'
                    })
            
            # Only add court if it has slots (available or restricted)
            if available_slots or restricted_slots:
                court_data = {
                    'court_id': str(court.court_id),
                    'court_name': court.court_name,
                    'sport_type': court.sport_type,
                    'capacity': court.capacity,
                    'notes': court.notes,
                    'image_url': court.image_url,
                    'slots': available_slots,
                }
                
                # Add restricted information if there are restricted slots
                if restricted_slots:
                    court_data['restricted_slots'] = restricted_slots
                
                courts_data.append(court_data)
        
        return JsonResponse({
            'can_book': can_book,
            'message': message,
            'courts': courts_data,
            'date': date_str,
            'facility_name': facility.facility_name
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# API endpoint to create a booking
@login_required
@require_http_methods(["POST"])
def api_create_booking(request):
    """API endpoint to create a booking"""
    try:
        data = json.loads(request.body)
        
        facility_id = data.get('facility_id')
        court_id = data.get('court_id')
        booking_date_str = data.get('booking_date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        notes = data.get('notes', '')
        
        # Validate required fields
        if not all([facility_id, court_id, booking_date_str, start_time_str, end_time_str]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Get models
        facility = get_object_or_404(Facility, facility_id=facility_id)
        court = get_object_or_404(Court, court_id=court_id)
        
        # Parse date and times
        try:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError as e:
            return JsonResponse({'error': f'Invalid date/time format: {str(e)}'}, status=400)
        
        # Check if date is in the past
        if booking_date < timezone.localdate():
            return JsonResponse({'error': 'Cannot book for past dates'}, status=400)
        
        # Check 2-month booking window constraint
        today = timezone.localdate()
        two_months_ago = today - timedelta(days=60)
        two_months_later = today + timedelta(days=60)
        
        if booking_date < two_months_ago or booking_date > two_months_later:
            return JsonResponse({
                'error': f'Bookings can only be made within 2 months from today. '
                         f'You can book between {two_months_ago.strftime("%B %d, %Y")} and {two_months_later.strftime("%B %d, %Y")}.'
            }, status=400)
        
        # Check for blackout periods
        start_datetime = datetime.combine(booking_date, start_time)
        end_datetime = datetime.combine(booking_date, end_time)
        
        # Make timezone-aware using the current timezone
        if timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime)
        if timezone.is_naive(end_datetime):
            end_datetime = timezone.make_aware(end_datetime)
        
        # Check for facility-level blackouts FIRST (highest priority)
        facility_blackout_conflicts = FacilityBlackout.objects.filter(
            facility=facility,
            start_date_time__lt=end_datetime,
            end_date_time__gt=start_datetime
        )
        
        if facility_blackout_conflicts.exists():
            facility_blackout = facility_blackout_conflicts.first()
            return JsonResponse({
                'error': f'This facility is closed during this time: {facility_blackout.reason}'
            }, status=400)
        
        # Check for court-level blackouts
        blackout_conflicts = Blackout.objects.filter(
            court=court,
            start_date_time__lt=end_datetime,
            end_date_time__gt=start_datetime
        )
        
        if blackout_conflicts.exists():
            blackout = blackout_conflicts.first()
            return JsonResponse({
                'error': f'This court is unavailable during this time due to blackout: {blackout.reason}'
            }, status=400)
        
        # Check if slot is still available
        if not Booking.is_slot_available(court, booking_date, start_time, end_time):
            return JsonResponse({'error': 'This time slot has already been booked'}, status=400)
        
        # Check time slot restrictions based on user member type
        time_restriction_allowed, time_restriction_message = Booking.check_time_slot_restriction(
            request.user, start_time, end_time
        )
        if not time_restriction_allowed:
            return JsonResponse({'error': time_restriction_message}, status=400)
        
        # Check weekly limit (1 booking per facility per week)
        weekly_bookings = Booking.get_user_weekly_bookings(request.user, facility, booking_date)
        if weekly_bookings.count() >= 1:
            return JsonResponse({
                'error': 'You have already booked this facility once this week. You can only book 1 time per facility per week.'
            }, status=400)
        
        # Check monthly limit (4 bookings per facility per month)
        monthly_bookings = Booking.get_user_monthly_bookings(request.user, facility, booking_date)
        if monthly_bookings.count() >= 4:
            return JsonResponse({
                'error': 'You have reached the monthly limit for this facility. You can only book 4 times per facility per month.'
            }, status=400)
        
        # Create booking
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
        
        return JsonResponse({
            'success': True,
            'message': 'Booking created successfully!',
            'booking_id': str(booking.booking_id),
            'booking': {
                'facility': facility.facility_name,
                'court': court.court_name,
                'date': booking_date.strftime('%Y-%m-%d'),
                'time': f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            }
        })
        
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# API endpoint to check user's booking status
@login_required
@require_http_methods(["GET"])
def api_user_booking_status(request, facility_id):
    """Get user's booking status for a facility"""
    try:
        facility = get_object_or_404(Facility, facility_id=facility_id)
        target_date_str = request.GET.get('date')
        
        if not target_date_str:
            target_date = timezone.localdate()
        else:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format'}, status=400)
        
        # Get weekly bookings
        weekly_bookings = Booking.get_user_weekly_bookings(request.user, facility, target_date)
        
        # Get monthly bookings
        monthly_bookings = Booking.get_user_monthly_bookings(request.user, facility, target_date)
        
        return JsonResponse({
            'weekly_bookings': weekly_bookings.count(),
            'monthly_bookings': monthly_bookings.count(),
            'weekly_limit': 1,
            'monthly_limit': 4,
            'can_book_this_week': weekly_bookings.count() < 1,
            'can_book_this_month': monthly_bookings.count() < 4,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Contact page - GET and POST
@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact form page"""
    from .forms import ContactMessageForm
    from .models import ContactMessage, SiteSettings
    
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            contact_msg = form.save(commit=False)
            # If user is logged in, associate the message with them
            if request.user.is_authenticated:
                contact_msg.user = request.user
            contact_msg.save()
            
            messages.success(request, 'Thank you! Your message has been sent. Our support team will get back to you soon.')
            return redirect('booking_sys:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactMessageForm()
        # Pre-fill email if user is logged in
        if request.user.is_authenticated:
            form.fields['email'].initial = request.user.email
            form.fields['name'].initial = f"{request.user.first_name} {request.user.last_name}"
    
    site_settings = SiteSettings.get_settings()
    
    return render(request, 'contact.html', {
        'form': form,
        'site_settings': site_settings
    })
