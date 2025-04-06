import os
import pickle
import base64
import random
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
from django.shortcuts import render

import random
from rest_framework.decorators import api_view

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserSerializer, VerifyAccountSerializer, LoginSerializer
from rest_framework import status



SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

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

def home(request):
    users = User.objects.all()
    return render(request, 'vote/home.html', {'users': users})



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
from django.views.decorators.csrf import csrf_exempt



def generate_and_send_otp(email,subject, message):
    otp = str(random.randint(100000, 999999))
    sub = subject
    msg = f"{message} {otp}\nUse this to verify your login."

    user = User.objects.filter(email=email).first()
    if not user:
        raise ValueError("User not found")

    user.otp = otp
    user.save()
    send_email(email, sub, msg)

import json
from django.http import JsonResponse, HttpResponse
@csrf_exempt
def send_otp_via_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        try:
            generate_and_send_otp(email, subject="OTP for VoteHala", message="Your OTP is:")
            return JsonResponse({"message": "OTP sent successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)

 
 
@api_view(['POST'])
def verify_otp(request):
    """Handle OTP verification."""
    try:
        serializer = VerifyAccountSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            user = User.objects.filter(email=email).first()
            if not user:
                return Response(
                    {'status': 400, 'message': 'Invalid email'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.otp != otp:  # Check if OTP matches
                return Response(
                    {'status': 400, 'message': 'Wrong OTP'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.is_otp_verified = True  # Mark OTP as verified
            user.save()

            return Response(
                {'status': 200, 'message': 'OTP verified successfully! Redirecting to dashboard...'},
                status=status.HTTP_200_OK
            )

        return Response(
            {'status': 400, 'message': 'Validation failed', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {'status': 500, 'message': 'Internal server error', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def resend_otp(request):
    """Resend OTP to user's email."""
    try:
        email = request.data.get('email')
        if not email:
            return Response({'status': 400, 'message': 'Email is required'}, status=400)

        # Generate and send OTP
        generate_and_send_otp(email, subject="New OTP Resend for VoteHala", message="Your new OTP is:")
        return Response({'status': 200, 'message': 'New OTP sent successfully'}, status=200)

    except Exception as e:
        return Response(
            {'status': 500, 'message': 'Internal server error', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 
 
        
# class VerifyOTPViewSet(APIView):
#     def post(self, request):
#         """Handle OTP verification."""
#         try:
#             serializer = VerifyAccountSerializer(data=request.data)
#             if serializer.is_valid():
#                 email = serializer.validated_data['email']
#                 otp = serializer.validated_data['otp']

#                 user = User.objects.filter(email=email).first()
#                 if not user:
#                     return Response(
#                         {'status': 400, 'message': 'Invalid email'},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 if user.otp != otp:  # Check if OTP matches
#                     return Response(
#                         {'status': 400, 'message': 'Wrong OTP'},
#                         status=status.HTTP_400_BAD_REQUEST
#                     )

#                 user.is_otp_verified = True  # Mark OTP as verified
#                 user.save()

#                 # Redirecting to dashboard after successful OTP verification
#                 return Response(
#                     {'status': 200, 'message': 'OTP verified successfully! Redirecting to dashboard...'},
#                     status=status.HTTP_200_OK
#                 )

#             return Response(
#                 {'status': 400, 'message': 'Validation failed', 'errors': serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception as e:
#             return Response(
#                 {'status': 500, 'message': 'Internal server error', 'error': str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# class ResendOTPViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = VerifyAccountSerializer  # Reuse the OTP verification serializer
#     http_method_names = ['post']  # Allow only POST requests

#     def create(self, request, *args, **kwargs):
#         try:
#             email = request.data.get('email')
#             if not email:
#                 return Response({'status': 400, 'message': 'Email is required'}, status=400)

#             generate_and_send_otp(email,subject = "New OTP Resend", message = "Your new OTP is:")
#             return Response({'status': 200, 'message': 'New OTP sent successfully'}, status=200)

#         except ValueError as ve:
#             return Response({'status': 400, 'message': str(ve)}, status=400)
#         except Exception as e:
#             return Response({'status': 500, 'message': 'Internal server error', 'error': str(e)}, status=500)

            
            
            
