from rest_framework import serializers
from .models import (
    User, Student, Staff, Facility, Court, Availability, Slot,
    Booking, Blackout, FacilityBlackout, Notification, AuditLog,
    Announcement, ContactMessage, SiteSettings
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'password', 'first_name',
            'last_name', 'member_type', 'user_phone', 'is_active'
        ]
        read_only_fields = ['user_id', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            'user_id', 'username', 'email', 'password', 'first_name',
            'last_name', 'member_type', 'user_phone'
        ]
        read_only_fields = ['user_id']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['user', 'student_id']


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['user', 'department']


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = [
            'facility_id', 'facility_name', 'facility_type', 'location',
            'description', 'image_url', 'facility_status', 'likes_count'
        ]
        read_only_fields = ['facility_id']


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = [
            'court_id', 'facility', 'court_name', 'sport_type', 'capacity',
            'notes', 'image_url', 'court_status'
        ]
        read_only_fields = ['court_id']


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['id', 'court', 'day_of_week', 'open_time', 'close_time', 'notes']


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = [
            'slot_id', 'court', 'day_of_week', 'start_time', 'end_time',
            'slot_type', 'slot_status'
        ]
        read_only_fields = ['slot_id']


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'user', 'facility', 'court', 'booking_date',
            'start_time', 'end_time', 'notes', 'status', 'slot',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['booking_id', 'user', 'created_at', 'updated_at']


class BlackoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blackout
        fields = ['blackout_id', 'court', 'start_date_time', 'end_date_time', 'reason']
        read_only_fields = ['blackout_id']


class FacilityBlackoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityBlackout
        fields = [
            'facility_blackout_id', 'facility', 'start_date_time',
            'end_date_time', 'reason'
        ]
        read_only_fields = ['facility_blackout_id']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notif_id', 'booking', 'user', 'notif_text', 'notif_channel', 'sent_date_time']
        read_only_fields = ['notif_id', 'sent_date_time']


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ['audit_id', 'entry_type', 'entry_sub_type', 'user_involved', 'entry_date_time', 'entry_desc']
        read_only_fields = ['audit_id', 'entry_date_time']


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'announcement_id', 'title', 'content', 'priority', 'status',
            'created_by', 'created_at', 'updated_at', 'publish_date',
            'expiry_date', 'is_featured'
        ]
        read_only_fields = ['announcement_id', 'created_at', 'updated_at']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            'contact_id', 'user', 'name', 'email', 'phone', 'subject',
            'message', 'status', 'created_at', 'updated_at', 'admin_response'
        ]
        read_only_fields = ['contact_id', 'created_at', 'updated_at']


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            'id', 'hero_image_url', 'hero_title', 'hero_subtitle',
            'support_email', 'support_phone'
        ]
