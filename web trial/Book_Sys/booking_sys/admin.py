from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django import forms
from .models import (
    User, Student, Staff, Facility, Court, Slot, Booking, 
    Blackout, Availability, Notification, AuditLog, Announcement
)


# ==================== CUSTOM ADMIN AUTHENTICATION ====================
class EmailAuthenticationForm(AuthenticationForm):
    """Custom authentication form that uses email instead of username"""
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your email address',
            'autofocus': True
        })
        if self.fields.get('password'):
            self.fields['password'].widget.attrs.update({
                'placeholder': 'Enter your password'
            })
    
    def clean_username(self):
        email = self.cleaned_data.get('username')
        if email:
            email = email.lower().strip()
        return email
    
    def clean(self):
        """Override clean to use email for authentication"""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username is not None and password:
            from django.contrib.auth import authenticate
            # Since USERNAME_FIELD is 'email', authenticate with email
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


# ==================== USER ADMIN ====================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    
    list_display = ['username', 'email', 'full_name', 'member_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    list_filter = ['member_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['user_id', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user_id', 'username', 'email', 'first_name', 'last_name', 'member_type')
        }),
        ('Contact Information', {
            'fields': ('user_phone',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    
    add_fieldsets = (
        ('User Information', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'member_type', 'password1', 'password2'),
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
    
    actions = ['activate_users', 'deactivate_users', 'make_staff', 'remove_staff', 'make_superuser', 'remove_superuser']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} user(s) granted staff status.')
    make_staff.short_description = 'Grant staff status to selected users'
    
    def remove_staff(self, request, queryset):
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'{updated} user(s) removed staff status.')
    remove_staff.short_description = 'Remove staff status from selected users'
    
    def make_superuser(self, request, queryset):
        updated = queryset.update(is_superuser=True, is_staff=True)
        self.message_user(request, f'{updated} user(s) granted superuser status.')
    make_superuser.short_description = 'Grant superuser status to selected users'
    
    def remove_superuser(self, request, queryset):
        updated = queryset.update(is_superuser=False)
        self.message_user(request, f'{updated} user(s) removed superuser status.')
    remove_superuser.short_description = 'Remove superuser status from selected users'


# ==================== STUDENT ADMIN ====================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user_link', 'user_email', 'user_name']
    list_filter = ['user__is_active']
    search_fields = ['student_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user']
    
    def user_link(self, obj):
        url = reverse('admin:booking_sys_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.short_description = 'Name'


# ==================== STAFF ADMIN ====================
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['department', 'user_link', 'user_email', 'user_name']
    list_filter = ['department', 'user__is_active']
    search_fields = ['department', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['user']
    
    def user_link(self, obj):
        url = reverse('admin:booking_sys_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_name.short_description = 'Name'


# ==================== AVAILABILITY INLINE ====================
class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1
    fields = ['day_of_week', 'open_time', 'close_time', 'notes']
    verbose_name = 'Availability Schedule'
    verbose_name_plural = 'Availability Schedules'


# ==================== SLOT INLINE ====================
class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1
    fields = ['day_of_week', 'start_time', 'end_time', 'slot_type', 'slot_status']
    verbose_name = 'Time Slot'
    verbose_name_plural = 'Time Slots'


# ==================== BLACKOUT INLINE ====================
class BlackoutInline(admin.TabularInline):
    model = Blackout
    extra = 0
    fields = ['start_date_time', 'end_date_time', 'reason']
    verbose_name = 'Blackout Period'
    verbose_name_plural = 'Blackout Periods'


# ==================== COURT ADMIN ====================
@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['court_name', 'facility_link', 'sport_type', 'capacity', 'court_status', 'bookings_count']
    list_filter = ['court_status', 'sport_type', 'facility']
    search_fields = ['court_name', 'sport_type', 'facility__facility_name']
    readonly_fields = ['court_id']
    inlines = [AvailabilityInline, SlotInline, BlackoutInline]
    ordering = ['facility', 'court_name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('court_id', 'facility', 'court_name', 'sport_type', 'capacity')
        }),
        ('Status', {
            'fields': ('court_status',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['mark_as_available', 'mark_as_maintenance', 'mark_as_closed']
    
    def facility_link(self, obj):
        url = reverse('admin:booking_sys_facility_change', args=[obj.facility.pk])
        return format_html('<a href="{}">{}</a>', url, obj.facility.facility_name)
    facility_link.short_description = 'Facility'
    
    def bookings_count(self, obj):
        count = Booking.objects.filter(slot__court=obj, fulfilled='no').count()
        return count
    bookings_count.short_description = 'Active Bookings'
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(court_status='available')
        self.message_user(request, f'{updated} court(s) marked as available.')
    mark_as_available.short_description = 'Mark selected courts as available'
    
    def mark_as_maintenance(self, request, queryset):
        updated = queryset.update(court_status='maintenance')
        self.message_user(request, f'{updated} court(s) marked as under maintenance.')
    mark_as_maintenance.short_description = 'Mark selected courts as under maintenance'
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(court_status='closed')
        self.message_user(request, f'{updated} court(s) marked as closed.')
    mark_as_closed.short_description = 'Mark selected courts as closed'


# ==================== FACILITY ADMIN ====================
class CourtInline(admin.TabularInline):
    model = Court
    extra = 1
    fields = ['court_name', 'sport_type', 'capacity', 'court_status']
    verbose_name = 'Court'
    verbose_name_plural = 'Courts'


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['facility_name', 'facility_type', 'facility_status', 'location', 'courts_count']
    list_filter = ['facility_type', 'facility_status']
    search_fields = ['facility_name', 'location', 'description']
    readonly_fields = ['facility_id']
    inlines = [CourtInline]
    ordering = ['facility_name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('facility_id', 'facility_name', 'facility_type', 'location')
        }),
        ('Status', {
            'fields': ('facility_status',)
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    
    actions = ['mark_as_available', 'mark_as_maintenance', 'mark_as_closed']
    
    def courts_count(self, obj):
        count = obj.courts.count()
        return count
    courts_count.short_description = 'Courts'
    
    def mark_as_available(self, request, queryset):
        updated = queryset.update(facility_status='available')
        self.message_user(request, f'{updated} facility(ies) marked as available.')
    mark_as_available.short_description = 'Mark selected facilities as available'
    
    def mark_as_maintenance(self, request, queryset):
        updated = queryset.update(facility_status='maintenance')
        self.message_user(request, f'{updated} facility(ies) marked as under maintenance.')
    mark_as_maintenance.short_description = 'Mark selected facilities as under maintenance'
    
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(facility_status='closed')
        self.message_user(request, f'{updated} facility(ies) marked as closed.')
    mark_as_closed.short_description = 'Mark selected facilities as closed'


# ==================== AVAILABILITY ADMIN ====================
@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['court_link', 'day_of_week', 'time_range', 'notes']
    list_filter = ['day_of_week', 'court__facility']
    search_fields = ['court__court_name', 'court__facility__facility_name', 'notes']
    fieldsets = (
        ('Court Information', {
            'fields': ('court',)
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'open_time', 'close_time')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def court_link(self, obj):
        url = reverse('admin:booking_sys_court_change', args=[obj.court.pk])
        return format_html('<a href="{}">{}</a>', url, obj.court.court_name)
    court_link.short_description = 'Court'
    
    def time_range(self, obj):
        return f"{obj.open_time.strftime('%I:%M %p')} - {obj.close_time.strftime('%I:%M %p')}"
    time_range.short_description = 'Time Range'


# ==================== SLOT ADMIN ====================
@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ['slot_id_short', 'court_link', 'day_of_week', 'time_range', 'slot_type', 'slot_status', 'bookings_count']
    list_filter = ['slot_status', 'slot_type', 'day_of_week', 'court__facility']
    search_fields = ['court__court_name', 'court__facility__facility_name']
    readonly_fields = ['slot_id']
    fieldsets = (
        ('Court Information', {
            'fields': ('court',)
        }),
        ('Schedule', {
            'fields': ('day_of_week', 'start_time', 'end_time')
        }),
        ('Slot Details', {
            'fields': ('slot_type', 'slot_status')
        }),
    )
    
    def slot_id_short(self, obj):
        return str(obj.slot_id)[:8] + '...'
    slot_id_short.short_description = 'Slot ID'
    
    def court_link(self, obj):
        url = reverse('admin:booking_sys_court_change', args=[obj.court.pk])
        return format_html('<a href="{}">{}</a>', url, obj.court.court_name)
    court_link.short_description = 'Court'
    
    def time_range(self, obj):
        return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"
    time_range.short_description = 'Time Range'
    
    def bookings_count(self, obj):
        count = obj.bookings.filter(fulfilled='no').count()
        return count
    bookings_count.short_description = 'Active Bookings'


# ==================== BOOKING ADMIN ====================
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id_short', 'user_link', 'facility_court', 'booking_date', 'slot_time', 'fulfilled']
    list_filter = ['fulfilled', 'booking_date_time', 'slot__court__facility']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'slot__court__court_name']
    readonly_fields = ['booking_id', 'booking_date_time']
    date_hierarchy = 'booking_date_time'
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'slot', 'booking_date_time')
        }),
        ('Status', {
            'fields': ('fulfilled',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    actions = ['mark_as_fulfilled', 'mark_as_cancelled']
    
    def booking_id_short(self, obj):
        return str(obj.booking_id)[:8] + '...'
    booking_id_short.short_description = 'Booking ID'
    
    def user_link(self, obj):
        url = reverse('admin:booking_sys_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, f"{obj.user.first_name} {obj.user.last_name}")
    user_link.short_description = 'User'
    
    def facility_court(self, obj):
        return f"{obj.slot.court.facility.facility_name} - {obj.slot.court.court_name}"
    facility_court.short_description = 'Facility - Court'
    
    def booking_date(self, obj):
        return obj.booking_date_time.strftime('%Y-%m-%d %I:%M %p')
    booking_date.short_description = 'Booking Date'
    
    def slot_time(self, obj):
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[obj.slot.day_of_week]
        return f"{day_name} {obj.slot.start_time.strftime('%I:%M %p')} - {obj.slot.end_time.strftime('%I:%M %p')}"
    slot_time.short_description = 'Slot Time'
    
    def mark_as_fulfilled(self, request, queryset):
        updated = queryset.update(fulfilled='yes')
        self.message_user(request, f'{updated} booking(s) marked as fulfilled.')
    mark_as_fulfilled.short_description = 'Mark selected bookings as fulfilled'
    
    def mark_as_cancelled(self, request, queryset):
        for booking in queryset:
            booking.cancel_booking()
        self.message_user(request, f'{queryset.count()} booking(s) cancelled.')
    mark_as_cancelled.short_description = 'Cancel selected bookings'


# ==================== BLACKOUT ADMIN ====================
@admin.register(Blackout)
class BlackoutAdmin(admin.ModelAdmin):
    list_display = ['blackout_id_short', 'court_link', 'date_range', 'reason_short']
    list_filter = ['court__facility', 'start_date_time']
    search_fields = ['court__court_name', 'court__facility__facility_name', 'reason']
    readonly_fields = ['blackout_id']
    date_hierarchy = 'start_date_time'
    fieldsets = (
        ('Court Information', {
            'fields': ('court',)
        }),
        ('Blackout Period', {
            'fields': ('start_date_time', 'end_date_time')
        }),
        ('Reason', {
            'fields': ('reason',)
        }),
    )
    
    def blackout_id_short(self, obj):
        return str(obj.blackout_id)[:8] + '...'
    blackout_id_short.short_description = 'Blackout ID'
    
    def court_link(self, obj):
        url = reverse('admin:booking_sys_court_change', args=[obj.court.pk])
        return format_html('<a href="{}">{}</a>', url, obj.court.court_name)
    court_link.short_description = 'Court'
    
    def date_range(self, obj):
        start = obj.start_date_time.strftime('%Y-%m-%d %I:%M %p')
        end = obj.end_date_time.strftime('%Y-%m-%d %I:%M %p')
        return f"{start} to {end}"
    date_range.short_description = 'Date Range'
    
    def reason_short(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    reason_short.short_description = 'Reason'


# ==================== NOTIFICATION ADMIN ====================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['notif_id_short', 'user_link', 'booking_link', 'notif_channel', 'sent_date']
    list_filter = ['notif_channel', 'sent_date_time']
    search_fields = ['user__username', 'user__email', 'notif_text']
    readonly_fields = ['notif_id', 'sent_date_time']
    date_hierarchy = 'sent_date_time'
    fieldsets = (
        ('Notification Information', {
            'fields': ('notif_id', 'booking', 'user', 'notif_channel', 'sent_date_time')
        }),
        ('Message', {
            'fields': ('notif_text',)
        }),
    )
    
    def notif_id_short(self, obj):
        return str(obj.notif_id)[:8] + '...'
    notif_id_short.short_description = 'Notification ID'
    
    def user_link(self, obj):
        url = reverse('admin:booking_sys_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, f"{obj.user.first_name} {obj.user.last_name}")
    user_link.short_description = 'User'
    
    def booking_link(self, obj):
        url = reverse('admin:booking_sys_booking_change', args=[obj.booking.pk])
        return format_html('<a href="{}">Booking {}</a>', url, str(obj.booking.booking_id)[:8])
    booking_link.short_description = 'Booking'
    
    def sent_date(self, obj):
        return obj.sent_date_time.strftime('%Y-%m-%d %I:%M %p')
    sent_date.short_description = 'Sent Date'


# ==================== AUDIT LOG ADMIN ====================
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['audit_id_short', 'entry_type', 'entry_sub_type', 'user_link', 'entry_date', 'entry_desc_short']
    list_filter = ['entry_type', 'entry_date_time']
    search_fields = ['entry_sub_type', 'entry_desc', 'user_involved__username', 'user_involved__email']
    readonly_fields = ['audit_id', 'entry_date_time']
    date_hierarchy = 'entry_date_time'
    fieldsets = (
        ('Audit Information', {
            'fields': ('audit_id', 'entry_type', 'entry_sub_type', 'entry_date_time')
        }),
        ('User Information', {
            'fields': ('user_involved',)
        }),
        ('Description', {
            'fields': ('entry_desc',)
        }),
    )
    
    def audit_id_short(self, obj):
        return str(obj.audit_id)[:8] + '...'
    audit_id_short.short_description = 'Audit ID'
    
    def user_link(self, obj):
        if obj.user_involved:
            url = reverse('admin:booking_sys_user_change', args=[obj.user_involved.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user_involved.username)
        return '-'
    user_link.short_description = 'User'
    
    def entry_date(self, obj):
        return obj.entry_date_time.strftime('%Y-%m-%d %I:%M %p')
    entry_date.short_description = 'Date'
    
    def entry_desc_short(self, obj):
        return obj.entry_desc[:50] + '...' if len(obj.entry_desc) > 50 else obj.entry_desc
    entry_desc_short.short_description = 'Description'


# ==================== ANNOUNCEMENT ADMIN ====================
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority_badge', 'status_badge', 'is_featured', 'created_by', 'created_at', 'publish_date']
    list_filter = ['status', 'priority', 'is_featured', 'created_at', 'publish_date']
    search_fields = ['title', 'content', 'created_by__email', 'created_by__username']
    readonly_fields = ['announcement_id', 'created_at', 'updated_at', 'created_by']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Announcement Information', {
            'fields': ('announcement_id', 'title', 'content')
        }),
        ('Settings', {
            'fields': ('priority', 'status', 'is_featured')
        }),
        ('Publishing', {
            'fields': ('publish_date', 'expiry_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_announcements', 'archive_announcements', 'mark_as_featured', 'unmark_as_featured']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new announcement
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def priority_badge(self, obj):
        colors = {
            'low': '#6b7280',
            'normal': '#3b82f6',
            'high': '#f59e0b',
            'urgent': '#ef4444'
        }
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_priority_display().upper()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'draft': '#6b7280',
            'published': '#10b981',
            'archived': '#ef4444'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def publish_announcements(self, request, queryset):
        from django.utils import timezone
        count = 0
        for announcement in queryset:
            announcement.status = 'published'
            if not announcement.publish_date:
                announcement.publish_date = timezone.now()
            announcement.save()
            count += 1
        self.message_user(request, f'{count} announcement(s) published.')
    publish_announcements.short_description = 'Publish selected announcements'
    
    def archive_announcements(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} announcement(s) archived.')
    archive_announcements.short_description = 'Archive selected announcements'
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} announcement(s) marked as featured.')
    mark_as_featured.short_description = 'Mark selected as featured'
    
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} announcement(s) unmarked as featured.')
    unmark_as_featured.short_description = 'Unmark selected as featured'


# ==================== ADMIN SITE CUSTOMIZATION ====================
# Override the admin site's login form to use email
admin.site.login_form = EmailAuthenticationForm
admin.site.site_header = "UniBook Administration"
admin.site.site_title = "UniBook Admin"
admin.site.index_title = "Welcome to UniBook Administration Portal"
