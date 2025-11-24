from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix admin user permissions - ensures user has is_staff and is_superuser set to True'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email of the user to fix',
            required=True,
        )

    def handle(self, *args, **options):
        email = options['email'].lower().strip()
        
        try:
            user = User.objects.get(email=email)
            
            self.stdout.write(f"Found user: {user.username} ({user.email})")
            self.stdout.write(f"Current status:")
            self.stdout.write(f"  - is_active: {user.is_active}")
            self.stdout.write(f"  - is_staff: {user.is_staff}")
            self.stdout.write(f"  - is_superuser: {user.is_superuser}")
            self.stdout.write(f"  - member_type: {user.member_type}")
            
            # Fix permissions
            needs_update = False
            if not user.is_staff:
                user.is_staff = True
                needs_update = True
                self.stdout.write(self.style.WARNING("  -> Setting is_staff to True"))
            
            if not user.is_superuser:
                user.is_superuser = True
                needs_update = True
                self.stdout.write(self.style.WARNING("  -> Setting is_superuser to True"))
            
            if not user.is_active:
                user.is_active = True
                needs_update = True
                self.stdout.write(self.style.WARNING("  -> Setting is_active to True"))
            
            if needs_update:
                user.save()
                self.stdout.write(self.style.SUCCESS(f"\n[SUCCESS] User '{user.email}' has been updated with admin permissions!"))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n[SUCCESS] User '{user.email}' already has correct admin permissions!"))
            
            self.stdout.write(f"\nYou can now log in to Django admin with:")
            self.stdout.write(self.style.SUCCESS(f"  Email: {user.email}"))
            self.stdout.write(self.style.SUCCESS(f"  Username: {user.username}"))
            self.stdout.write(self.style.WARNING("  Note: Use EMAIL (not username) to log in to Django admin!"))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"[ERROR] User with email '{email}' not found!"))
            self.stdout.write("\nAvailable users:")
            for u in User.objects.all():
                self.stdout.write(f"  - {u.email} (username: {u.username}, staff: {u.is_staff}, superuser: {u.is_superuser})")

