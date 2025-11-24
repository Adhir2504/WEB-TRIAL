from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    User, Student, Staff, Facility, Court, Slot, Booking, 
    Blackout, Availability, Notification
)
from .forms import (
    UserRegistrationForm, UserProfileEditForm, StudentProfileForm, 
    StaffProfileForm, FacilityForm, CourtForm, SlotForm, BookingForm, 
    BlackoutForm, AvailabilityForm, NotificationForm
)


# Home view - GET only
def home(request):
    """Home page view - displays welcome page"""
    facilities = Facility.objects.filter(facility_status='available')[:6]
    return render(request, 'home.html', {'facilities': facilities})


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


# Facility detail view - GET and POST
@require_http_methods(["GET", "POST"])
def facility_detail(request, slug):
    """Display facility details and handle bookings - GET and POST requests"""
    # For now, using slug as facility name search
    facility = get_object_or_404(Facility, facility_name__icontains=slug.replace('-', ' '))
    courts = Court.objects.filter(facility=facility)
    
    if request.method == 'GET':
        # Get available slots for all courts in this facility
        available_slots = Slot.objects.filter(
            court__facility=facility,
            slot_status='available'
        ).select_related('court')
        
        booking_form = None
        if request.user.is_authenticated:
            booking_form = BookingForm(user=request.user)
            # Filter slots to only show those for this facility's courts
            booking_form.fields['slot'].queryset = available_slots
        
        return render(request, 'facility_details.html', {
            'facility': facility,
            'courts': courts,
            'available_slots': available_slots,
            'booking_form': booking_form
        })
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to make a booking.')
            return redirect('booking_sys:login')
        
        booking_form = BookingForm(request.POST, user=request.user)
        if booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.user = request.user
            
            # Verify the slot belongs to this facility
            slot = booking.slot
            if slot.court.facility != facility:
                messages.error(request, 'Invalid slot selected.')
                return redirect('booking_sys:facility_detail', slug=slug)
            
            booking.save()
            
            # Update slot status
            slot.change_status('booked')
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_sys:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            available_slots = Slot.objects.filter(
                court__facility=facility,
                slot_status='available'
            ).select_related('court')
            return render(request, 'facility_details.html', {
                'facility': facility,
                'courts': courts,
                'available_slots': available_slots,
                'booking_form': booking_form
            })


# Calendar view - GET only
@require_http_methods(["GET"])
def calendar_view(request):
    """Display interactive calendar view"""
    courts = Court.objects.filter(court_status='available')

    # Get user's bookings if logged in
    user_bookings = []
    if request.user.is_authenticated:
        user_bookings = Booking.objects.filter(user=request.user, fulfilled='no').order_by('booking_date_time')[:10]

    upcoming_bookings = Booking.objects.filter(fulfilled='no').select_related(
        'slot__court__facility'
    ).order_by('slot__day_of_week', 'slot__start_time')

    selected_day_param = request.GET.get('day')
    try:
        selected_day = int(selected_day_param) if selected_day_param is not None else None
        if selected_day is not None and selected_day not in range(7):
            selected_day = None
    except ValueError:
        selected_day = None

    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    calendar_days = []
    for idx, name in enumerate(day_names):
        day_bookings = [b for b in upcoming_bookings if b.slot.day_of_week == idx]
        calendar_days.append({
            'index': idx,
            'name': name,
            'bookings': day_bookings,
            'count': len(day_bookings),
            'is_selected': selected_day == idx
        })

    selected_index = 0
    selected_day_bookings = []
    selected_entry = None
    if calendar_days:
        if selected_day is not None:
            selected_index = selected_day
        else:
            calendar_days[0]['is_selected'] = True
        selected_entry = calendar_days[selected_index]
        selected_day_bookings = selected_entry['bookings']

    context = {
        'courts': courts,
        'user_bookings': user_bookings,
        'upcoming_bookings': upcoming_bookings[:20],
        'calendar_days': calendar_days,
        'selected_day_bookings': selected_day_bookings,
        'selected_day_index': selected_index,
        'selected_day_entry': selected_entry,
        'current_month_label': timezone.localdate().strftime('%B %Y'),
    }
    return render(request, 'calendar.html', context)


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
        
        bookings = Booking.objects.filter(user=user).order_by('-booking_date_time')[:10]
        
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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('booking_sys:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
        
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
    if request.method == 'GET':
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', {'form': form})
    
    elif request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile based on member type
            member_type = form.cleaned_data.get('member_type')
            if member_type == 'student':
                student_id = request.POST.get('student_id', '').strip().upper()
                if student_id:
                    Student.objects.create(user=user, student_id=student_id)
                else:
                    messages.warning(request, 'Student ID not provided. You can add it later in your profile.')
            elif member_type == 'staff':
                department = request.POST.get('department', '').strip()
                if department:
                    Staff.objects.create(user=user, department=department)
                else:
                    messages.warning(request, 'Department not provided. You can add it later in your profile.')
            
            # Auto-login after registration
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome {user.first_name}! Registration successful.')
                return redirect('booking_sys:home')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, 'registration/register.html', {'form': form})


# Booking creation - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_booking(request):
    """Create a booking - handles GET and POST requests"""
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


# Facility creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_facility(request):
    """Create a facility - handles GET and POST requests (Admin only)"""
    if not request.user.is_staff and request.user.member_type != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = FacilityForm()
        return render(request, 'admin/create_facility.html', {'form': form})
    
    elif request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            facility = form.save()
            messages.success(request, f'Facility "{facility.facility_name}" created successfully!')
            return redirect('booking_sys:facilities')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_facility.html', {'form': form})


# Court creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_court(request):
    """Create a court - handles GET and POST requests (Admin only)"""
    if not request.user.is_staff and request.user.member_type != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('booking_sys:home')
    
    if request.method == 'GET':
        form = CourtForm()
        return render(request, 'admin/create_court.html', {'form': form})
    
    elif request.method == 'POST':
        form = CourtForm(request.POST)
        if form.is_valid():
            court = form.save()
            messages.success(request, f'Court "{court.court_name}" created successfully!')
            return redirect('booking_sys:facilities')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_court.html', {'form': form})


# Slot creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_slot(request):
    """Create a slot - handles GET and POST requests (Admin only)"""
    if not request.user.is_staff and request.user.member_type != 'admin':
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
            return redirect('booking_sys:calendar')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_slot.html', {'form': form})


# Blackout creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_blackout(request):
    """Create a blackout period - handles GET and POST requests (Admin only)"""
    if not request.user.is_staff and request.user.member_type != 'admin':
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
            return redirect('booking_sys:calendar')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_blackout.html', {'form': form})


# Availability creation (Admin) - GET and POST
@login_required
@require_http_methods(["GET", "POST"])
def create_availability(request):
    """Create availability schedule - handles GET and POST requests (Admin only)"""
    if not request.user.is_staff and request.user.member_type != 'admin':
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
            return redirect('booking_sys:calendar')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'admin/create_availability.html', {'form': form})


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
        
        facilities_with_slots.append({
            'facility': facility,
            'next_slot': next_slot,
            'capacity': total_capacity,
            'courts_count': courts.count()
        })
    
    return render(request, 'facilities.html', {
        'facilities_data': facilities_with_slots,
        'query': query,
        'selected_type': facility_type
    })
