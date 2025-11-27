"""
Django signals for booking_sys app.
Automatically creates availability and slots when a new court is created.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import time
from .models import Court, Availability, Slot


@receiver(post_save, sender=Court)
def create_court_availability_and_slots(sender, instance, created, **kwargs):
    """
    Signal handler that creates default availability and slots when a new court is created.
    """
    if not created:
        return
    
    # Check if availability already exists
    if Availability.objects.filter(court=instance).exists():
        return
    
    # Default availability: 6 AM to 10 PM, Monday to Sunday
    default_open_time = time(6, 0)  # 6 AM
    default_close_time = time(22, 0)  # 10 PM
    
    # Default time slots: every 2 hours from 8 AM to 8 PM
    default_slot_times = [
        (time(8, 0), time(10, 0)),
        (time(10, 30), time(12, 30)),
        (time(13, 0), time(15, 0)),
        (time(15, 30), time(17, 30)),
        (time(18, 0), time(20, 0)),
    ]
    
    # Create availability for all 7 days of the week (0=Monday to 6=Sunday)
    for day in range(7):
        Availability.objects.get_or_create(
            court=instance,
            day_of_week=day,
            defaults={
                'open_time': default_open_time,
                'close_time': default_close_time,
                'notes': 'Default schedule'
            }
        )
    
    # Create slots for all 7 days
    for day in range(7):
        for start_time, end_time in default_slot_times:
            Slot.objects.get_or_create(
                court=instance,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time,
                defaults={
                    'slot_type': 'regular',
                    'slot_status': 'available'
                }
            )
