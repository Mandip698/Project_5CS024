from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe

User = get_user_model()

class CustomAdminAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_email_verified:
            verify_url = reverse("send_verification_email", args=[user.pk])
            verify_button = f'<br><a href="{verify_url}" class="button">Resend Verification Email</a>'
            raise forms.ValidationError(
                mark_safe(f"Your email is not verified. {verify_button}"), code="email_not_verified")
