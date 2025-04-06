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

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def index(request):
    users = User.objects.all()
    return render(request, 'vote/index.html', {'users': users})


def dashboard(request):
    return render(request, 'vote/dashboard.html')


# ------------------- Gmail Authentication -------------------
def authenticate_gmail():
    creds = None

    print("Checking for existing token...")
    if os.path.exists("token.pickle"):
        # print("Found existing token.pickle")
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        # print("Credentials not found or expired. Refreshing...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # print("Token refreshed successfully.")
        else:
            # print("Launching OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080, authorization_prompt_message="")
            # print("Authentication successful!")

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
            # print("Token saved!")

    return creds

# ------------------- Gmail API Send Email -------------------
def send_email(recipient, subject, body):
    """Sends an email using Gmail API."""
    creds = authenticate_gmail()  # Get valid credentials

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
        return HttpResponse("✅ Email sent successfully!")
    except Exception as e:
        return HttpResponse(f"❌ Error sending email: {e}")


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        return HttpResponse("Email verified successfully! You can now log in.")
    else:
        return HttpResponse("Invalid or expired link.")


def send_verification_email(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        if user.is_email_verified:
            return HttpResponse("Your email is already verified.")

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_url = request.build_absolute_uri(f"/verify/{uid}/{token}/")

        subject = "Verify Your Email"
        message = f"Click the link to verify your email: {verification_url}"

        send_email(user.email, subject, message)

        return HttpResponse("✅ Verification email sent! Check your inbox.")

    except User.DoesNotExist:
        return HttpResponse("❌ User not found.", status=400)
