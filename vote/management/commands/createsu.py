from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        first_name = os.environ.get('DJANGO_SUPERUSER_FIRSTNAME')
        last_name = os.environ.get('DJANGO_SUPERUSER_LASTNAME')
        voter_id = os.environ.get('DJANGO_SUPERUSER_VOTERID')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                voter_id=voter_id,
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))
