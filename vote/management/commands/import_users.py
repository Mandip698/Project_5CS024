import math
import requests
import pandas as pd
from vote.models import User
from django.conf import settings
from django.core.mail import send_mail
from dateutil.parser import parse as parse_date
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from vote.utils import generate_random_password, generate_random_unique_id


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            required_fields = [
                "username", "first_name", "last_name",
                "is_superuser", "is_staff", "is_active", "email", "date_joined"
            ]

            if settings.IMPORT_MODE == "API":
                api_url = settings.USER_API_LINK
                response = requests.get(api_url)
                response.raise_for_status()
                users = response.json()
            else:
                df = pd.read_excel(settings.EXCELFILE_DIRS)
                users = df.to_dict(orient="records")

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
                    date_val = user_data["date_joined"]
                    if isinstance(date_val, pd.Timestamp):
                        _ = date_val.to_pydatetime()
                    else:
                        _ = parse_date(str(date_val))
                except Exception as e:
                    raise ValueError(f"Failed to parse date for user '{user_data.get('username', '')}': {e}")

            new_users = [] 
            for user_data in users:
                user = User.objects.filter(username=user_data["username"]).first()
                if not user:
                    user = User.objects.filter(email=user_data["email"]).first()
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
                # Proper datetime parsing with timezone-awareness check
                date_val = user_data["date_joined"]
                if isinstance(date_val, pd.Timestamp):
                    dt = date_val.to_pydatetime()
                else:
                    dt = parse_date(str(date_val))
                user.date_joined = make_aware(dt) if dt.tzinfo is None else dt
                if is_new:
                    generated_password = generate_random_password()
                    user.password = make_password(generated_password)
                    unique_id = generate_random_unique_id()
                    user.voter_id = unique_id
                    new_users.append((user, generated_password, unique_id))
                user.save()

            for user, generated_password, unique_id in new_users:
                subject = "Welcome to Voteहालः!"
                body = (
                    f"Dear {user.first_name} {user.last_name},\n\n"
                    f"Your account has been created.\n"
                    f"Username: {user.username}\n"
                    f"Email: {user.email}\n"
                    f"Password: {generated_password}\n"
                    f"Unique Voter Id: {unique_id}\n\n"
                    f"Please login and change your password immediately.\n\n"
                    f"Please copy or write down the Unique Voter Id as it is necessary to Vote.\n\n"
                    f"To login, please visit: https://project-5cs024.onrender.com/login_view/\n\n"
                    f"If you have any questions, feel free to reach out.\n\n"
                    "Best regards,\nVoteहालः Team"
                )
                try:
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
                except Exception as e:
                    self.stderr.write(f"Failed to send email to {user.email}: {e}")

            self.stdout.write(self.style.SUCCESS("All users imported and sent mail successfully."))
        except Exception as e:
            raise CommandError(str(e))

