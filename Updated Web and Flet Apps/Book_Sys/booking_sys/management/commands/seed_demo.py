from datetime import time, date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from booking_sys.models import (
    Facility,
    Court,
    Slot,
    Availability,
    Booking,
    Announcement,
)


class Command(BaseCommand):
    help = (
        "Populate the database with demo users, facilities, courts, slots and bookings. "
        "Safe to run multiple times – it will only create missing records."
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding UniBook demo data..."))
        demo_admin = self._create_admin_user()
        demo_student = self._create_student_user()
        facilities = self._create_facilities_with_courts()
        self._create_slots_for_facilities(facilities)
        self._create_sample_bookings(demo_student, facilities)
        self._create_sample_announcements(demo_admin)

        self.stdout.write(self.style.SUCCESS("Demo data ready!"))
        self.stdout.write(self.style.NOTICE("You can log in with:"))
        self.stdout.write(self.style.NOTICE("  Admin   -> admin@unibook.mu / Admin123!"))
        self.stdout.write(self.style.NOTICE("  Student -> tony@student.mu / Student123!"))

    # --------------------------------------------------------------------- utils
    def _create_admin_user(self):
        User = get_user_model()
        admin, created = User.objects.get_or_create(
            email="admin@unibook.mu",
            defaults={
                "username": "admin",
                "first_name": "Admin",
                "last_name": "User",
                "member_type": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("Admin123!")
            admin.save()
            self.stdout.write(self.style.SUCCESS("• Created admin user"))
        return admin

    def _create_student_user(self):
        User = get_user_model()
        student, created = User.objects.get_or_create(
            email="tony@student.mu",
            defaults={
                "username": "tony",
                "first_name": "Tony",
                "last_name": "R.",
                "member_type": "student",
            },
        )
        if created:
            student.set_password("Student123!")
            student.save()
            self.stdout.write(self.style.SUCCESS("• Created demo student user"))
        return student

    def _create_facilities_with_courts(self):
        facility_specs = [
            {
                "name": "Futsal Arena",
                "type": "sports",
                "location": "Gymnasium Complex",
                "description": "Full-sized futsal court with digital scoreboards and spectator stands.",
                "likes": 245,
            },
            {
                "name": "Indoor Badminton Hub",
                "type": "sports",
                "location": "Sports Hall",
                "description": "Four professional badminton courts with LED lighting and equipment rental.",
                "likes": 189,
            },
            {
                "name": "Campus Fitness Center",
                "type": "recreation",
                "location": "Wellness Building",
                "description": "Weight machines, cardio zone, stretching studio and locker rooms.",
                "likes": 312,
            },
            {
                "name": "Outdoor Volleyball Courts",
                "type": "sports",
                "location": "Fields – Block B",
                "description": "Two sand courts with lighting up to 10 PM and nearby seating.",
                "likes": 156,
            },
            {
                "name": "Basketball Pavilion",
                "type": "sports",
                "location": "Courtside Plaza",
                "description": "Dual purpose indoor/outdoor pavilion with changing rooms.",
                "likes": 201,
            },
        ]

        facilities = []
        for spec in facility_specs:
            facility, created = Facility.objects.get_or_create(
                facility_name=spec["name"],
                defaults={
                    "facility_type": spec["type"],
                    "location": spec["location"],
                    "description": spec["description"],
                    "facility_status": "available",
                    "likes_count": spec["likes"],
                },
            )
            # Update likes_count even if facility already exists
            if not created:
                facility.likes_count = spec["likes"]
                facility.save(update_fields=['likes_count'])
            else:
                self.stdout.write(self.style.SUCCESS(f"• Created facility: {facility.facility_name}"))
            
            # Always ensure courts exist for this facility
            self._create_default_courts(facility)
            facilities.append(facility)
        return facilities

    def _create_default_courts(self, facility: Facility):
        # Court images mapped by sport type
        court_images = {
            "Futsal": [
                "https://images.unsplash.com/photo-1589487391730-58f20eb2c308?w=800",
                "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800",
            ],
            "Indoor": [
                "https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=800",
                "https://images.unsplash.com/photo-1593787157229-0b6b0c2846da?w=800",
            ],
            "Campus": [
                "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800",
                "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800",
            ],
            "Outdoor": [
                "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800",
                "https://images.unsplash.com/photo-1593786481097-3b3b2f8b9cd9?w=800",
            ],
            "Basketball": [
                "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800",
                "https://images.unsplash.com/photo-1519861531473-9200262188bf?w=800",
            ],
        }
        
        sport_prefix = facility.facility_name.split()[0]
        images = court_images.get(sport_prefix, [
            "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        ])
        
        court_specs = [
            ("Court A", "Main competition court with professional equipment and seating", 12, images[0]),
            ("Court B", "Practice court with training facilities and storage", 10, images[1] if len(images) > 1 else images[0]),
        ]

        for name_suffix, notes, capacity, image_url in court_specs:
            Court.objects.get_or_create(
                facility=facility,
                court_name=f"{sport_prefix} {name_suffix}",
                defaults={
                    "sport_type": sport_prefix,
                    "capacity": capacity,
                    "notes": notes,
                    "image_url": image_url,
                },
            )

    def _create_slots_for_facilities(self, facilities):
        """Create 1-hour slots from 8:00 AM to 6:00 PM for each facility"""
        from datetime import datetime
        
        # Create hourly slots from 8:00 to 18:00 (8 AM to 6 PM)
        slot_hours = [
            (8, 9),    # 8:00-9:00
            (9, 10),   # 9:00-10:00
            (10, 11),  # 10:00-11:00
            (11, 12),  # 11:00-12:00
            (12, 13),  # 12:00-13:00 (Staff priority time)
            (13, 14),  # 13:00-14:00
            (14, 15),  # 14:00-15:00
            (15, 16),  # 15:00-16:00
            (16, 17),  # 16:00-17:00
            (17, 18),  # 17:00-18:00
        ]

        for facility in facilities:
            for court in facility.courts.all():
                for day in range(7):  # 0=Monday to 6=Sunday
                    # Create availability for this day
                    Availability.objects.get_or_create(
                        court=court,
                        day_of_week=day,
                        defaults={
                            "open_time": time(8, 0),
                            "close_time": time(18, 0),
                        },
                    )
                    
                    # Create hourly slots
                    for start_hour, end_hour in slot_hours:
                        Slot.objects.get_or_create(
                            court=court,
                            day_of_week=day,
                            start_time=time(start_hour, 0),
                            end_time=time(end_hour, 0),
                            defaults={"slot_type": "regular"},
                        )

    def _create_sample_bookings(self, user, facilities):
        """Create sample bookings for next week"""
        if Booking.objects.exists():
            return
        
        today = timezone.localdate()
        # Create bookings for next week (avoiding current week restriction)
        next_week_start = today + timedelta(days=7)
        
        # Create a few sample bookings with 1-hour slots
        booking_dates = [
            next_week_start,  # Monday next week
            next_week_start + timedelta(days=3),  # Thursday next week
        ]
        
        for facility in facilities[:2]:  # Just first 2 facilities
            courts = list(facility.courts.all())
            if not courts:
                continue
                
            court = courts[0]
            booking_date = booking_dates.pop(0) if booking_dates else next_week_start
            
            # Create a booking for 10:00 - 11:00 (1 hour slot)
            try:
                Booking.objects.create(
                    user=user,
                    facility=facility,
                    court=court,
                    booking_date=booking_date,
                    start_time=time(10, 0),
                    end_time=time(11, 0),
                    notes=f"Demo booking for {court.court_name}",
                    status='confirmed'
                )
                self.stdout.write(self.style.SUCCESS(f"• Created booking for {facility.facility_name} on {booking_date}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"• Could not create booking: {e}"))

    def _create_sample_announcements(self, admin_user):
        """Create sample announcements"""
        now = timezone.now()
        
        announcements_data = [
            {
                "title": "New Badminton Nets Installed",
                "content": "We've upgraded all badminton courts with professional-grade nets. Enjoy your games with better quality equipment!",
                "priority": "normal",
                "is_featured": True,
            },
            {
                "title": "Inter-Faculty Futsal League Starting Soon",
                "content": "Registration opens next week for the annual inter-faculty futsal tournament. Check with your faculty sports coordinator for more details.",
                "priority": "high",
                "is_featured": True,
                "expiry_date": now + timedelta(days=30),
            },
            {
                "title": "Maintenance Schedule - Basketball Courts",
                "content": "Basketball Pavilion will undergo maintenance from Dec 1-5. Please book alternative facilities during this period.",
                "priority": "urgent",
                "is_featured": False,
                "expiry_date": now + timedelta(days=10),
            },
            {
                "title": "Extended Hours During Exam Period",
                "content": "All sports facilities will be open until 10 PM during the exam period to help students relax and destress.",
                "priority": "normal",
                "is_featured": False,
            },
        ]
        
        for ann_data in announcements_data:
            announcement, created = Announcement.objects.get_or_create(
                title=ann_data["title"],
                defaults={
                    "content": ann_data["content"],
                    "priority": ann_data["priority"],
                    "status": "published",
                    "created_by": admin_user,
                    "is_featured": ann_data.get("is_featured", False),
                    "publish_date": now,
                    "expiry_date": ann_data.get("expiry_date"),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"• Created announcement: {announcement.title}"))

