import math
import string
import secrets
import requests
from vote.models import User
from django.conf import settings
from django.core.mail import send_mail
from email.utils import parsedate_to_datetime
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        api_url = "settings.USER_API_LINK"
        required_fields = [
            "username", "first_name", "last_name",
            "is_superuser", "is_staff", "is_active", "email",
            "voter_id", "date_joined"
        ]
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            users = response.json()
            for user_data in users:
                for field in required_fields:
                    value = user_data.get(field)
                    if (
                        value is None or
                        value == "" or
                        (isinstance(value, str) and value.lower() == "nan") or
                        (isinstance(value, float) and math.isnan(value))
                    ):
                        raise ValueError(f"Error: Field '{field}' is missing or invalid for user: {user_data}")
                try:
                    parsedate_to_datetime(user_data["date_joined"])
                except Exception as e:
                    raise ValueError(f"Failed to parse date for user '{user_data.get('username', '')}': {e}")

            new_users = [] 
            for user_data in users:
                user = (
                    User.objects.filter(username=user_data["username"]).first()
                    or User.objects.filter(email=user_data["email"]).first()
                )
                is_new = False
                if not user:
                    user = User(username=user_data["username"])
                    is_new = True

                user.first_name = user_data["first_name"]
                middle_name = user_data.get("middle_name")
                user.middle_name = None if isinstance(middle_name, float) and math.isnan(middle_name) else middle_name
                user.last_name = user_data["last_name"]
                user.is_superuser = user_data["is_superuser"]
                user.is_staff = user_data["is_staff"]
                user.is_active = user_data["is_active"]
                user.email = user_data["email"]
                user.voter_id = user_data["voter_id"]
                user.date_joined = parsedate_to_datetime(user_data["date_joined"])
                if is_new:
                    generated_password = self.generate_random_password()
                    user.password = make_password(generated_password)
                    new_users.append((user, generated_password))
                user.save()

                for user, generated_password in new_users:
                    subject = "Welcome to Voteहालः!"
                    body = (
                        f"Dear {user.first_name} {user.last_name},\n\n"
                        f"Your account has been created.\n"
                        f"Username: {user.username}\n"
                        f"Password: {generated_password}\n\n"
                        f"Please login and change your password immediately.\n\n"
                        f"To login, please visit: http://localhost:8000/login_view/\n\n"
                        f"When verifying with OTP, enter your OTP from mail and Voter Id provided by you. Example: OTPVoterId \n\n"
                        f"If you have any questions, feel free to reach out.\n\n"
                        "Best regards,\nVoteहालः Team"
                    )
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            self.stdout.write(self.style.SUCCESS("All users imported and sent mail successfully successfully."))
        except Exception as e:
            raise CommandError(str(e))

    def generate_random_password(self, length=10):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))