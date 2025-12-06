from django.core.management.base import BaseCommand
from main_app.models import CustomUser
import os

class Command(BaseCommand):
    help = 'Creates a test superuser for Cypress testing'

    def handle(self, *args, **kwargs):
        email = os.environ.get('TEST_SUPERUSER_EMAIL', 'ijtaba@ijtaba.com')
        password = os.environ.get('TEST_SUPERUSER_PASSWORD', 'ijtaba')
        
        user, created = CustomUser.objects.get_or_create(email=email)
        
        if created:
            user.set_password(password)
            user.user_type = '1'  # 1 is Admin/HOD
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{email}"'))
        else:
            # Ensure password and permissions are correct even if user exists
            user.set_password(password)
            user.user_type = '1'
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing user "{email}" to be a superuser'))
