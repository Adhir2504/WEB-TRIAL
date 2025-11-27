"""
Management command to set up availability and slots for courts that don't have them.
Run: python manage.py setup_court_schedule
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from booking_sys.models import Court, Availability, Slot
from datetime import time

class Command(BaseCommand):
    help = 'Set up availability and slots for courts that don\'t have them'

    def handle(self, *args, **options):
        # Find courts without availability
        courts_without_availability = []
        for court in Court.objects.all():
            if not Availability.objects.filter(court=court).exists():
                courts_without_availability.append(court)
        
        if not courts_without_availability:
            self.stdout.write(self.style.SUCCESS('✓ All courts already have availability schedules'))
            return
        
        self.stdout.write(f'\nFound {len(courts_without_availability)} court(s) without availability schedules\n')
        
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
        
        for court in courts_without_availability:
            self.stdout.write(f'Setting up schedule for: {court.court_name}')
            
            # Create availability for all 7 days of the week
            for day in range(7):
                availability, created = Availability.objects.get_or_create(
                    court=court,
                    day_of_week=day,
                    defaults={
                        'open_time': default_open_time,
                        'close_time': default_close_time,
                        'notes': 'Default schedule'
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Created availability for day {day}')
            
            # Create slots for all 7 days
            for day in range(7):
                for start_time, end_time in default_slot_times:
                    slot, created = Slot.objects.get_or_create(
                        court=court,
                        day_of_week=day,
                        start_time=start_time,
                        end_time=end_time,
                        defaults={
                            'slot_type': 'regular',
                            'slot_status': 'available'
                        }
                    )
                    if created:
                        self.stdout.write(f'  ✓ Created slot for day {day} ({start_time.strftime("%H:%M")} - {end_time.strftime("%H:%M")})')
            
            self.stdout.write(self.style.SUCCESS(f'✓ {court.court_name} schedule complete\n'))
        
        self.stdout.write(self.style.SUCCESS('✓ All courts now have availability and slots!'))
