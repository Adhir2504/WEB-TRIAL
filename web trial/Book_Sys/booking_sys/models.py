from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
from datetime import datetime, timedelta, date
from django.utils import timezone
import uuid
import calendar

class User(AbstractUser):
    MEMBER_TYPES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Administrator'),
    ]

    #username - defined through AbstractUser - username = models.CharField(max_length=150, unique=True)
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="User Email")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    member_type = models.CharField(max_length=10, choices=MEMBER_TYPES)
    user_phone = models.CharField(max_length=15, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name', 'member_type']
    
    def __str__(self):
        return f"{self.username} ({self.member_type})"
    
    def get_display_name(self):
        """Returns the display name for user profiles"""
        return self.username
    
    def edit_credentials(self, first_name, last_name, email, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.user_phone = phone
        self.save()
    
    def display_credentials(self):
        return f"Name: {self.first_name} {self.last_name}\nEmail: {self.email}\nPhone: {self.user_phone}"
    
    def deactivate_account(self):
        self.is_active = False
        self.save()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_id = models.CharField(max_length=20, unique=True)
    
    def clean(self):
        if self.user.member_type != 'student':
            raise ValidationError("Only users with member_type 'student' can have a Student profile.")

    def __str__(self):
        return f"{self.user.username} - {self.student_id}"
    

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=100)

    def clean(self):
        if self.user.member_type != 'staff':
            raise ValidationError("Only users with member_type 'staff' can have a Staff profile.")
    
    def __str__(self):
        return f"{self.user.username} - {self.department}"

class Facility(models.Model):
    FACILITY_TYPES = [
        ('sports', 'Sports'),
        ('recreation', 'Recreation'),
        ('academic', 'Academic'),
        ('other', 'Other'),
    ]
    
    FACILITY_STATUS = [
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('closed', 'Closed'),
    ]
    
    facility_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility_name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES)
    location = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    facility_status = models.CharField(max_length=20, choices=FACILITY_STATUS, default='available')
    likes_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.facility_name
    
    def change_status(self, new_status):
        self.facility_status = new_status
        self.save()

class Court(models.Model):
    COURT_STATUS = [
        ('available', 'Available'),
        ('maintenance', 'Under Maintenance'),
        ('closed', 'Closed'),
    ]
    
    court_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='courts')
    court_name = models.CharField(max_length=200)
    sport_type = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000)])
    notes = models.TextField(blank=True, default="None")
    image_url = models.URLField(blank=True, null=True)
    court_status = models.CharField(max_length=20, choices=COURT_STATUS, default='available')
    
    def __str__(self):
        return f"{self.court_name} ({self.facility.facility_name})"
    
    def is_available_on(self, day, time):
        """Check if court is available on given day and time"""
        try:
            availability = self.availabilities.get(day_of_week=day)
            if not (availability.open_time <= time <= availability.close_time):
                return False
        except Availability.DoesNotExist:
            return False
        
        dummy_date = datetime(2025, 1, 1)
        check_dt = make_aware(datetime.combine(dummy_date, time))

        """Check for Blackouts"""
        blackout_exists = self.blackouts.filter(
            start_date_time__lte=check_dt,
            end_date_time__gte=check_dt
        ).exists()

        if blackout_exists:
            return False

        """Check for existing bookings"""
        slot = self.slots.filter(
            day_of_week=day,
            start_time__lte=time,
            end_time__gte=time,
            slot_status='available'
        ).first()

        if slot is None:
            return False

        # If the slot exists but is booked
        if slot.slot_status != 'available':
            return False

        return True
    
    def edit_notes(self, new_notes):
        self.notes = new_notes
        self.save()
    
    def change_status(self, new_status):
        self.court_status = new_status
        self.save()

class Availability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    open_time = models.TimeField()
    close_time = models.TimeField()
    notes = models.TextField(blank=True, default="None")
    
    class Meta:
        unique_together = ('court', 'day_of_week')

    def clean(self):
        if self.open_time >= self.close_time:
            raise ValidationError("Opening time must be earlier than closing time.")

    
    def __str__(self):
        return f"{self.court.court_name} - {self.day_of_week} ({self.open_time} to {self.close_time})"
    
    def edit_notes(self, new_notes):
        self.notes = new_notes
        self.save()

class Slot(models.Model):
    SLOT_TYPES = [
        ('regular', 'Regular'),
        ('peak', 'Peak Hours'),
        ('off_peak', 'Off-Peak'),
    ]
    
    SLOT_STATUS = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('blocked', 'Blocked'),
    ]
    
    slot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='slots')
    day_of_week = models.IntegerField(choices=Availability.DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_type = models.CharField(max_length=10, choices=SLOT_TYPES, default='regular')
    slot_status = models.CharField(max_length=20, choices=SLOT_STATUS, default='available')
    
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Slot start time must be earlier than end time.")


    def __str__(self):
        return f"{self.court.court_name} - {self.day_of_week} {self.start_time}-{self.end_time}"
    
    def change_status(self, new_status):
        self.slot_status = new_status
        self.save()

class Booking(models.Model):
    FULFILLMENT_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    facility = models.ForeignKey('Facility', on_delete=models.CASCADE, related_name='bookings')
    court = models.ForeignKey('Court', on_delete=models.CASCADE, related_name='bookings')
    
    # Actual booking date (not when the booking was made)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # When the booking was created
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, default="")
    status = models.CharField(max_length=10, choices=FULFILLMENT_STATUS, default='confirmed')
    
    # Reference to slot template (optional, for tracking which slot pattern was used)
    slot = models.ForeignKey('Slot', on_delete=models.SET_NULL, null=True, blank=True, related_name='date_bookings')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['court', 'booking_date', 'start_time'], 
                name='unique_court_date_time_booking'
            )
        ]
        ordering = ['booking_date', 'start_time']
        indexes = [
            models.Index(fields=['user', 'booking_date']),
            models.Index(fields=['facility', 'booking_date']),
            models.Index(fields=['court', 'booking_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.court.court_name} on {self.booking_date} at {self.start_time}"
    
    def clean(self):
        """Validate booking constraints"""
        # Check if booking date is in the past
        if self.booking_date < timezone.localdate():
            raise ValidationError("Cannot book for past dates.")
        
        # Check if user has already booked this facility this week
        if not self.pk:  # Only check for new bookings
            # Get week boundaries
            week_start = self.booking_date - timedelta(days=self.booking_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            # Check weekly limit (1 booking per week per facility)
            weekly_bookings = Booking.objects.filter(
                user=self.user,
                facility=self.facility,
                booking_date__gte=week_start,
                booking_date__lte=week_end,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk if self.pk else None)
            
            if weekly_bookings.exists():
                raise ValidationError(
                    f"You can only book {self.facility.facility_name} once per week. "
                    f"You already have a booking for this week."
                )
            
            # Check monthly limit (4 bookings per month per facility)
            month_start = self.booking_date.replace(day=1)
            if self.booking_date.month == 12:
                month_end = date(self.booking_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(self.booking_date.year, self.booking_date.month + 1, 1) - timedelta(days=1)
            
            monthly_bookings = Booking.objects.filter(
                user=self.user,
                facility=self.facility,
                booking_date__gte=month_start,
                booking_date__lte=month_end,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk if self.pk else None)
            
            if monthly_bookings.count() >= 4:
                raise ValidationError(
                    f"You can only book {self.facility.facility_name} 4 times per month. "
                    f"You have reached your monthly limit."
                )
        
        # Validate time slot
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def cancel_booking(self):
        """Cancel the booking"""
        self.status = 'cancelled'
        self.save()
    
    def complete_booking(self):
        """Mark booking as completed"""
        self.status = 'completed'
        self.save()
    
    @staticmethod
    def get_user_weekly_bookings(user, facility, target_date):
        """Get user's bookings for the week containing target_date"""
        week_start = target_date - timedelta(days=target_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        return Booking.objects.filter(
            user=user,
            facility=facility,
            booking_date__gte=week_start,
            booking_date__lte=week_end,
            status__in=['pending', 'confirmed']
        )
    
    @staticmethod
    def get_user_monthly_bookings(user, facility, target_date):
        """Get user's bookings for the month containing target_date"""
        month_start = target_date.replace(day=1)
        if target_date.month == 12:
            month_end = date(target_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)
        
        return Booking.objects.filter(
            user=user,
            facility=facility,
            booking_date__gte=month_start,
            booking_date__lte=month_end,
            status__in=['pending', 'confirmed']
        )
    
    @staticmethod
    def can_user_book(user, facility, target_date):
        """Check if user can book for the target date"""
        # Check weekly limit
        weekly_bookings = Booking.get_user_weekly_bookings(user, facility, target_date)
        if weekly_bookings.exists():
            return False, "You can only book this facility once per week."
        
        # Check monthly limit
        monthly_bookings = Booking.get_user_monthly_bookings(user, facility, target_date)
        if monthly_bookings.count() >= 4:
            return False, "You have reached your monthly booking limit (4 bookings per month)."
        
        return True, "You can book this facility."
    
    @staticmethod
    def is_slot_available(court, booking_date, start_time, end_time):
        """Check if a time slot is available for booking"""
        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            court=court,
            booking_date=booking_date,
            status__in=['pending', 'confirmed']
        ).filter(
            models.Q(start_time__lt=end_time) & models.Q(end_time__gt=start_time)
        )
        
        return not overlapping.exists()

class Blackout(models.Model):
    blackout_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='blackouts')
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    reason = models.TextField()

    def clean(self):
        # Only check for overlaps if we have the required fields
        if self.court and self.start_date_time and self.end_date_time:
            overlaps = Blackout.objects.filter(
                court=self.court,
                start_date_time__lt=self.end_date_time,
                end_date_time__gt=self.start_date_time
            ).exclude(pk=self.pk)

            if overlaps.exists():
                raise ValidationError("Blackout period overlaps with an existing blackout.")
    
    def __str__(self):
        return f"Blackout {self.blackout_id} - {self.court.court_name}"


class FacilityBlackout(models.Model):
    """Facility-wide blackout for maintenance, events, or full facility closure"""
    facility_blackout_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='blackouts')
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    reason = models.TextField()
    
    def clean(self):
        # Only check for overlaps if we have the required fields
        if self.facility and self.start_date_time and self.end_date_time:
            overlaps = FacilityBlackout.objects.filter(
                facility=self.facility,
                start_date_time__lt=self.end_date_time,
                end_date_time__gt=self.start_date_time
            ).exclude(pk=self.pk)
            
            if overlaps.exists():
                raise ValidationError("Facility blackout period overlaps with an existing blackout.")
    
    def __str__(self):
        return f"Facility Blackout {self.facility_blackout_id} - {self.facility.facility_name}"


class Notification(models.Model):
    NOTIFICATION_CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both'),
    ]
    
    notif_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_text = models.TextField()
    notif_channel = models.CharField(max_length=10, choices=NOTIFICATION_CHANNELS, default='email')
    sent_date_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification {self.notif_id} - {self.user.first_name}"

class AuditLog(models.Model):
    ENTRY_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('booking', 'Booking'),
        ('cancellation', 'Cancellation'),
    ]
    
    audit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    entry_sub_type = models.CharField(max_length=50, blank=True)
    user_involved = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    entry_date_time = models.DateTimeField(auto_now_add=True)
    entry_desc = models.TextField(default="None")
    
    def __str__(self):
        return f"Audit {self.audit_id} - {self.entry_type}"
    
    @classmethod
    def create_entry(cls, entry_type, entry_sub_type="", user=None, description="None"):
        return cls.objects.create(
            entry_type=entry_type,
            entry_sub_type=entry_sub_type,
            user_involved=user,
            entry_desc=description
        )


class Announcement(models.Model):
    """Site-wide announcements that can be displayed on the homepage and other pages"""
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    announcement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(null=True, blank=True, help_text="When to publish this announcement")
    expiry_date = models.DateTimeField(null=True, blank=True, help_text="When this announcement should expire")
    is_featured = models.BooleanField(default=False, help_text="Show on homepage prominently")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def is_active(self):
        """Check if announcement is currently active"""
        from django.utils import timezone
        now = timezone.now()
        
        if self.status != 'published':
            return False
        
        if self.publish_date and self.publish_date > now:
            return False
        
        if self.expiry_date and self.expiry_date < now:
            return False
        
        return True
    
    def publish(self):
        """Publish the announcement"""
        from django.utils import timezone
        self.status = 'published'
        if not self.publish_date:
            self.publish_date = timezone.now()
        self.save()
    
    def archive(self):
        """Archive the announcement"""
        self.status = 'archived'
        self.save()