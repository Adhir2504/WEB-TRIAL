from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Delete all users from the database (with safety checks)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--keep-superusers',
            action='store_true',
            help='Keep superuser accounts',
        )
        parser.add_argument(
            '--keep-staff',
            action='store_true',
            help='Keep staff accounts',
        )

    def handle(self, *args, **options):
        force = options['force']
        keep_superusers = options['keep_superusers']
        keep_staff = options['keep_staff']
        
        # Build queryset
        users_to_delete = User.objects.all()
        
        if keep_superusers:
            users_to_delete = users_to_delete.filter(is_superuser=False)
            self.stdout.write(self.style.WARNING("Keeping superuser accounts"))
        
        if keep_staff:
            users_to_delete = users_to_delete.filter(is_staff=False)
            self.stdout.write(self.style.WARNING("Keeping staff accounts"))
        
        count = users_to_delete.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No users to delete."))
            return
        
        # Show what will be deleted
        self.stdout.write(self.style.WARNING(f"\n⚠️  WARNING: This will delete {count} user(s) from the database!"))
        self.stdout.write("\nUsers that will be deleted:")
        for user in users_to_delete[:10]:  # Show first 10
            self.stdout.write(f"  - {user.email} ({user.username}) - {user.member_type}")
        if count > 10:
            self.stdout.write(f"  ... and {count - 10} more")
        
        # Show what will be kept
        kept_count = User.objects.count() - count
        if kept_count > 0:
            self.stdout.write(f"\nUsers that will be kept: {kept_count}")
            kept_users = User.objects.exclude(pk__in=users_to_delete.values_list('pk', flat=True))
            for user in kept_users:
                self.stdout.write(f"  - {user.email} ({user.username})")
        
        # Confirmation
        if not force:
            confirm = input("\nAre you sure you want to delete these users? Type 'yes' to confirm: ")
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR("Operation cancelled."))
                return
        
        # Delete users
        try:
            with transaction.atomic():
                deleted_count = users_to_delete.count()
                users_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f"\n✓ Successfully deleted {deleted_count} user(s)!"))
                remaining = User.objects.count()
                self.stdout.write(f"Remaining users in database: {remaining}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Error deleting users: {str(e)}"))
            self.stdout.write(self.style.ERROR("Operation rolled back. No users were deleted."))

