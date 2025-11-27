from django.core.management.base import BaseCommand
from booking_sys.models import User


class Command(BaseCommand):
    help = 'Make a user a superuser by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to make superuser')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.member_type = 'admin'
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully made {email} a superuser!'))
            self.stdout.write(f'   is_superuser: {user.is_superuser}')
            self.stdout.write(f'   is_staff: {user.is_staff}')
            self.stdout.write(f'   member_type: {user.member_type}')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User with email {email} does not exist'))
