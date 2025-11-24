from datetime import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from booking_sys.models import (
    Facility,
    Court,
    Slot,
    Availability,
    Booking,
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
            },
            {
                "name": "Indoor Badminton Hub",
                "type": "sports",
                "location": "Sports Hall",
                "description": "Four professional badminton courts with LED lighting and equipment rental.",
            },
            {
                "name": "Campus Fitness Center",
                "type": "recreation",
                "location": "Wellness Building",
                "description": "Weight machines, cardio zone, stretching studio and locker rooms.",
            },
            {
                "name": "Outdoor Volleyball Courts",
                "type": "sports",
                "location": "Fields – Block B",
                "description": "Two sand courts with lighting up to 10 PM and nearby seating.",
            },
            {
                "name": "Basketball Pavilion",
                "type": "sports",
                "location": "Courtside Plaza",
                "description": "Dual purpose indoor/outdoor pavilion with changing rooms.",
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
                },
            )
            facilities.append(facility)
            if created:
                self.stdout.write(self.style.SUCCESS(f"• Created facility: {facility.facility_name}"))
                self._create_default_courts(facility)
        return facilities

    def _create_default_courts(self, facility: Facility):
        court_specs = [
            ("Court A", "Main court", 12),
            ("Court B", "Practice court", 10),
        ]

        for name_suffix, notes, capacity in court_specs:
            Court.objects.get_or_create(
                facility=facility,
                court_name=f"{facility.facility_name.split()[0]} {name_suffix}",
                defaults={
                    "sport_type": facility.facility_name.split()[0],
                    "capacity": capacity,
                    "notes": notes,
                },
            )

    def _create_slots_for_facilities(self, facilities):
        slot_blocks = [
            (time(8, 0), time(10, 0)),
            (time(10, 30), time(12, 30)),
            (time(15, 0), time(17, 0)),
            (time(18, 0), time(20, 0)),
        ]

        for facility in facilities:
            for court in facility.courts.all():
                for day in range(7):
                    Availability.objects.get_or_create(
                        court=court,
                        day_of_week=day,
                        defaults={
                            "open_time": time(6, 0),
                            "close_time": time(22, 0),
                        },
                    )
                    for start, end in slot_blocks:
                        Slot.objects.get_or_create(
                            court=court,
                            day_of_week=day,
                            start_time=start,
                            end_time=end,
                            defaults={"slot_type": "regular"},
                        )

    def _create_sample_bookings(self, user, facilities):
        if Booking.objects.exists():
            return
        available_slots = Slot.objects.filter(slot_status="available")[:5]
        for slot in available_slots:
            Booking.objects.create(
                user=user,
                slot=slot,
                notes=f"Demo booking for {slot.court.court_name}",
            )
            slot.change_status("booked")
        self.stdout.write(self.style.SUCCESS("• Added demo bookings"))

