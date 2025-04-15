from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Option, Poll, UserVote

User = get_user_model()

# class CustomAdminAuthenticationForm(AuthenticationForm):
#     def confirm_login_allowed(self, user):
#         if not user.is_email_verified:
#             verify_url = reverse("send_verification_email", args=[user.pk])
#             verify_button = f'<br><a href="{verify_url}" class="button">Resend Verification Email</a>'
#             raise forms.ValidationError(
#                 mark_safe(f"Your email is not verified. {verify_button}"), code="email_not_verified")


class VoteForm(forms.Form):
    option = forms.ModelChoiceField(
        queryset=Option.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        required=True,
        label="Choose an option to vote"
    )

    def __init__(self, *args, **kwargs):
        poll = kwargs.pop('poll')
        super().__init__(*args, **kwargs)
        self.fields['option'].queryset = poll.options.all()