from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import (
    User, Student, Staff, Facility, Court, Slot, Booking, 
    Blackout, FacilityBlackout, Availability, Notification, Announcement
)
from datetime import datetime, date, time
import re


# User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    member_type = forms.ChoiceField(
        choices=User.MEMBER_TYPES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    user_phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (optional)'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'member_type', 'user_phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Email regex validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Please enter a valid email address.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Username regex: alphanumeric and underscores only, 3-30 characters
        username_pattern = r'^[a-zA-Z0-9_]{3,30}$'
        if not re.match(username_pattern, username):
            raise ValidationError("Username must be 3-30 characters and contain only letters, numbers, and underscores.")
        return username


# User Profile Edit Form
class UserProfileEditForm(forms.ModelForm):
    user_phone = forms.CharField(
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'user_phone')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Please enter a valid email address.")
        return email


# Student Profile Form
class StudentProfileForm(forms.ModelForm):
    student_id = forms.CharField(
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{6,20}$',
                message="Student ID must be 6-20 characters, uppercase letters and numbers only."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student ID (e.g., STU123456)'})
    )
    
    class Meta:
        model = Student
        fields = ('student_id',)
    
    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        # Convert to uppercase for consistency
        student_id = student_id.upper()
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError("A student with this ID already exists.")
        return student_id


# Staff Profile Form
class StaffProfileForm(forms.ModelForm):
    department = forms.CharField(
        max_length=100,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\-&]{2,100}$',
                message="Department name must be 2-100 characters and contain only letters, spaces, hyphens, and ampersands."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department (e.g., IT, HR, Sports)'})
    )
    
    class Meta:
        model = Staff
        fields = ('department',)


# Facility Form
class FacilityForm(forms.ModelForm):
    facility_name = forms.CharField(
        max_length=200,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_]{3,200}$',
                message="Facility name must be 3-200 characters and contain only letters, numbers, spaces, hyphens, and underscores."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Facility Name'})
    )
    
    location = forms.CharField(
        max_length=300,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-,.#]{5,300}$',
                message="Location must be 5-300 characters and contain valid address characters."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'})
    )
    image_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Image URL (optional)'
        })
    )
    
    class Meta:
        model = Facility
        fields = ('facility_name', 'facility_type', 'location', 'description', 'facility_status','image_url')
        widgets = {
            'facility_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description'}),
            'facility_status': forms.Select(attrs={'class': 'form-control'}),
        }


# Court Form
class CourtForm(forms.ModelForm):
    court_name = forms.CharField(
        max_length=200,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_]{2,200}$',
                message="Court name must be 2-200 characters and contain only letters, numbers, spaces, hyphens, and underscores."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Court Name'})
    )
    
    sport_type = forms.CharField(
        max_length=100,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s\-]{2,100}$',
                message="Sport type must be 2-100 characters and contain only letters, spaces, and hyphens."
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sport Type (e.g., Basketball, Tennis)'})
    )
    
    class Meta:
        model = Court
        fields = ('facility', 'court_name', 'sport_type', 'capacity', 'image_url', 'notes', 'court_status')
        widgets = {
            'facility': forms.Select(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Capacity'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Image URL (e.g., https://example.com/image.jpg)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes'}),
            'court_status': forms.Select(attrs={'class': 'form-control'}),
        }


# Availability Form
class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ('court', 'day_of_week', 'open_time', 'close_time', 'notes')
        widgets = {
            'court': forms.Select(attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'open_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        open_time = cleaned_data.get('open_time')
        close_time = cleaned_data.get('close_time')
        
        if open_time and close_time and open_time >= close_time:
            raise ValidationError("Opening time must be earlier than closing time.")
        
        return cleaned_data


# Slot Form
class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = ('court', 'day_of_week', 'start_time', 'end_time', 'slot_type', 'slot_status')
        widgets = {
            'court': forms.Select(attrs={'class': 'form-control'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'slot_type': forms.Select(attrs={'class': 'form-control'}),
            'slot_status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("Slot start time must be earlier than end time.")
        
        return cleaned_data


# Booking Form
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('slot', 'notes')
        widgets = {
            'slot': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Filter slots to show only available ones
        if user:
            self.fields['slot'].queryset = Slot.objects.filter(slot_status='available')
        else:
            self.fields['slot'].queryset = Slot.objects.filter(slot_status='available')


# Blackout Form
class BlackoutForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    class Meta:
        model = Blackout
        fields = ('court', 'reason')
        widgets = {
            'court': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Reason for blackout'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')
        
        if start_date and start_time and end_date and end_time:
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            # Make timezone-aware using the current timezone
            from django.utils import timezone
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)
            
            if start_datetime >= end_datetime:
                raise ValidationError("Start date/time must be earlier than end date/time.")
            
            cleaned_data['start_date_time'] = start_datetime
            cleaned_data['end_date_time'] = end_datetime
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_date_time = self.cleaned_data['start_date_time']
        instance.end_date_time = self.cleaned_data['end_date_time']
        if commit:
            instance.save()
        return instance


# Facility Blackout Form (for facility-wide blackouts)
class FacilityBlackoutForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    class Meta:
        model = FacilityBlackout
        fields = ('facility', 'reason')
        widgets = {
            'facility': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Reason for facility blackout (e.g., Maintenance, Staff Training, Special Event)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')
        facility = cleaned_data.get('facility')
        
        if start_date and start_time and end_date and end_time:
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            
            # Make timezone-aware using the current timezone
            from django.utils import timezone
            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)
            
            if start_datetime >= end_datetime:
                raise ValidationError("Start date/time must be earlier than end date/time.")
            
            # Check for overlapping facility blackouts
            if facility:
                overlaps = FacilityBlackout.objects.filter(
                    facility=facility,
                    start_date_time__lt=end_datetime,
                    end_date_time__gt=start_datetime
                ).exclude(pk=self.instance.pk if self.instance.pk else None)
                
                if overlaps.exists():
                    raise ValidationError("Facility blackout period overlaps with an existing blackout.")
            
            cleaned_data['start_date_time'] = start_datetime
            cleaned_data['end_date_time'] = end_datetime
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_date_time = self.cleaned_data['start_date_time']
        instance.end_date_time = self.cleaned_data['end_date_time']
        if commit:
            instance.save()
        return instance


# Notification Form (for admin use)
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('booking', 'user', 'notif_text', 'notif_channel')
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'notif_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Notification message'}),
            'notif_channel': forms.Select(attrs={'class': 'form-control'}),
        }


# Announcement Form
class AnnouncementForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Announcement Title'})
    )
    
    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Announcement content...'})
    )
    
    class Meta:
        model = Announcement
        fields = ('title', 'content', 'priority', 'status', 'publish_date', 'expiry_date', 'is_featured')
        widgets = {
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'publish_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expiry_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
