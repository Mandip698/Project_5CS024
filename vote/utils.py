import uuid
import string
import secrets
import hashlib
from vote.models import User
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import default_token_generator


def generate_otp(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        otp = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        # Save OTP and metadata in session
        otp_creation_key = f'otp_creation_{uid}_{token}'
        session_key = f'otp_{uid}_{token}'
        request.session[otp_creation_key] = timezone.now().isoformat()
        request.session[session_key] = otp
        # Email OTP
        subject = "Verify Login With OTP"
        message = f"Your verification code is: {otp}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        # Store metadata for resending
        request.session["otp_user_id"] = user.id
        request.session["otp_uid"] = uid
        request.session["otp_token"] = token
        request.session.set_expiry(180)
        return {"uid": uid, "token": token, "success": True}
    except ObjectDoesNotExist:
        return {"error": "User not found.", "success": False}


def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_random_unique_id():
    return uuid.uuid4().hex


def consistent_color(text):
    # Generate an MD5 hash and convert to integer
    hash_digest = hashlib.md5(text.encode('utf-8')).hexdigest()
    return f"#{hash_digest[:6]}"


def send_otp(request, user_id, mail_type="login"):
    try:
        user = User.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        otp = ''.join(str(secrets.randbelow(10)) for _ in range(6))
        otp_creation_key = f'otp_creation_{uid}_{token}'
        session_key = f'otp_{uid}_{token}'

        # Store the creation time and OTP in session
        request.session[otp_creation_key] = timezone.now().isoformat()
        request.session[session_key] = otp
        
        # Debugging: Log session contents
        print(f"OTP Generated: {otp}")
        print(f"Session key for OTP: {session_key}")
        print(f"Session keys: {request.session.keys()}")  # Log all session keys

        # Send OTP via email
        if mail_type == "resend":
            subject = "Your OTP Code Has Been Resent"
            message = f"Hi {user.first_name},\n\nYou requested a new OTP. Your verification code is: {otp}\n\nIf you did not request this, please ignore this email."
        else:
            subject = "Verify Your Login - OTP Code"
            message = f"Hi {user.first_name},\n\nTo complete your login, please enter the following verification code: {otp}\n\nThis code is valid for the next 3 minutes. If the OTP expired , please request a new one clicking resend otp button."

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        # Store UID and Token for later verification
        request.session["otp_user_id"] = user.id
        request.session["otp_uid"] = uid
        request.session["otp_token"] = token
        request.session.set_expiry(180)  # Session expiration time in seconds

        return {"uid": uid, "token": token, "success": True}
    except ObjectDoesNotExist:
        return {"error": "User not found.", "success": False}


def generate_otp(request, user_id):
    try:
        # Fetch the user by user_id
        user = User.objects.get(pk=user_id)
        # Call the send_otp function to send OTP to the user
        return send_otp(request, user.id)
    except User.DoesNotExist:
        return {"error": "User not found.", "success": False}