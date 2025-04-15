import os
import pickle
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from email.mime.text import MIMEText
from vote.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth import login
from datetime import timedelta
from django.shortcuts import redirect
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def index(request):
    users = User.objects.all()
    return render(request, 'vote/index.html', {'users': users})


def dashboard(request):
    return render(request, 'vote/dashboard.html')


# ------------------- Gmail Authentication -------------------
def authenticate_gmail():
    creds = None
    token_path = "token.pickle"
    # Load existing credentials
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
    # If there are no valid credentials, handle login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            #Save the refreshed token
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
            # Save the new token
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)
    return creds


def send_email(recipient, subject, body):
    """Sends an email using Gmail API."""
    creds = authenticate_gmail()
    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEText(body)
        message["to"] = recipient
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()
        return JsonResponse({"message":"Email sent successfully!"})
    except Exception as e:
        return JsonResponse({"error": f"Error sending email: {e}"})

import random
def generate_otp(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        otp = f"{random.randint(100000, 999999)}"
        subject = "Verify Login With OTP"
        message = f"Your verification code is: {otp}"

        otp_creation_key = f'otp_creation_{uid}_{token}'
        request.session[otp_creation_key] = timezone.now().isoformat()
        request.session[f'otp_{uid}_{token}'] = otp
        request.session.set_expiry(60)
        send_email(user.email, subject, message)

        request.session["otp_user_id"] = user.id
        request.session["otp_uid"] = uid
        request.session["otp_token"] = token

        return JsonResponse({"message": "OTP sent!", "uid": uid, "token": token})
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=400)


def verify_otp(request):
    if request.method == "POST":
        try:
            data = data = request.POST
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid or empty JSON."}, status=400)

        uidb64 = data.get("uid")
        token = data.get("token")
        otp_raw = data.get("otp", "")
        input_otp = otp_raw[:6]
        input_voter_id = otp_raw[6:]
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return JsonResponse({"error": "Invalid or expired token."}, status=400)

            session_key = f'otp_{uidb64}_{token}'
            stored_otp = request.session.get(session_key)

            if not stored_otp:
                return JsonResponse({"error": "OTP expired or not found."}, status=400)

            otp_creation_key = f'otp_creation_{uidb64}_{token}'
            otp_creation_str = request.session.get(otp_creation_key)
            if otp_creation_str:
                otp_creation_time = parse_datetime(otp_creation_str)
                otp_expiry_time = otp_creation_time + timedelta(seconds=180)
                if timezone.now() > otp_expiry_time:
                    return JsonResponse({"error": "OTP has expired."}, status=400)
            if input_otp == stored_otp:
                if user.voter_id == input_voter_id:
                    login(request, user)
                    del request.session[session_key]
                    return redirect('dashboard')
            else:
                return JsonResponse({"error": "Incorrect OTP."}, status=400)
        except (User.DoesNotExist, ValueError, TypeError):
            return JsonResponse({"error": "Invalid user."}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)


@require_GET
def resend_otp(request):
    user_id = request.session.get('otp_user_id')
    uid = request.session.get('otp_uid')
    token = request.session.get('otp_token')

    if not user_id or not uid or not token:
        return JsonResponse({"error": "Session expired or invalid. Please login again."}, status=400)
    try:
        session_key = f'otp_{uid}_{token}'
        if session_key in request.session:
            del request.session[session_key]
        generate_otp(request, user_id)
        return JsonResponse({"message": "OTP resent successfully!"})
    except Exception as e:
        return JsonResponse({"error": f"Failed to resend OTP. {str(e)}"}, status=400)