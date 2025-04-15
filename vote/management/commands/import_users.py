import math
import requests
from django.core.management.base import BaseCommand, CommandError
from vote.models import User
from django.contrib.auth.hashers import make_password
from email.utils import parsedate_to_datetime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        api_url = "http://localhost:5000/api/users"
        default_password = "VoteHala123"
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

                user = (
                    User.objects.filter(username=user_data["username"]).first()
                    or User.objects.filter(email=user_data["email"]).first()
                )
                if not user:
                    user = User(username=user_data["username"])

                user.first_name = user_data["first_name"]
                middle_name = user_data.get("middle_name")
                if isinstance(middle_name, float) and math.isnan(middle_name):
                    user.middle_name = None
                else:
                    user.middle_name = middle_name
                user.last_name = user_data["last_name"]
                user.is_superuser = user_data["is_superuser"]
                user.is_staff = user_data["is_staff"]
                user.is_active = user_data["is_active"]
                user.email = user_data["email"]
                user.voter_id = user_data["voter_id"]

                try:
                    user.date_joined = parsedate_to_datetime(user_data["date_joined"])
                except Exception as e:
                    raise ValueError(f"Failed to parse date for user '{user.username}': {e}")

                if not user.pk:
                    user.password = make_password(default_password)

                user.save()

            self.stdout.write(self.style.SUCCESS("All users imported successfully."))

        except Exception as e:
            raise CommandError(str(e))