import os
import json
import secrets
from datetime import timedelta
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.dateparse import parse_date
from django.utils.dateparse import parse_datetime
from django.utils.http import urlsafe_base64_decode 
from vote.models import User, UserVote, Poll, Option
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from .utils import generate_random_password, generate_random_unique_id, generate_otp, send_otp, consistent_color



def index(request):
    return render(request, 'vote/index.html')


def registration(request):
    if request.method == 'GET':
        return render(request, 'vote/registration.html')

    if request.method == 'POST':
        # Collect fields
        first_name = request.POST.get('firstName', '').strip()
        middle_name = request.POST.get('middleName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        dob = parse_date(request.POST.get('dob', ''))
        user_photo = request.FILES.get('userPhotoUpload')
        voter_card = request.FILES.get('voterCardUpload')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already exists.'}, status=400)
        # Check email duplication
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists.'}, status=400)
        # Save uploaded images to static/images/user_images/
        upload_dir = os.path.join(settings.BASE_DIR, 'static/images/user_images/')
        os.makedirs(upload_dir, exist_ok=True)
        fs = FileSystemStorage(location=upload_dir)

        user_photo_name = fs.save(user_photo.name, user_photo)
        voter_card_name = fs.save(voter_card.name, voter_card)

        user_photo_path = f'user_images/{user_photo_name}'
        voter_card_path = f'user_images/{voter_card_name}'

        # Generate credentials
        generated_password = generate_random_password()
        voter_id = generate_random_unique_id()

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=generated_password,
            middle_name=middle_name,
            dob=dob,
            voter_id=voter_id,
            voter_id_image=voter_card_path,
            avatar=user_photo_path
        )
        # Send welcome email
        subject = "Welcome to Voteहालः!"
        body = (
            f"Dear {user.first_name} {user.last_name},\n\n"
            f"Your account has been created.\n"
            f"Username: {user.username}\n"
            f"Email: {user.email}\n"
            f"Password: {generated_password}\n"
            f"Unique Voter Id: {voter_id}\n\n"
            f"Please login and change your password immediately.\n"
            f"Please copy or write down the Unique Voter Id as it is necessary to Vote.\n\n"
            f"To login, please visit: https://project-5cs024.onrender.com/login_view/\n\n"
            f"If you have any questions, feel free to reach out.\n\n"
            "Best regards,\nVoteहालः Team"
        )
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        except Exception as e:
            user.delete()  # Rollback user creation if email fails
            return JsonResponse({'status': 'error', 'message': f'Failed to send email to {user.email}: {e}'}, status=500)
        return JsonResponse({'status': 'success', 'message': 'Registration successful! Check your email for login details.', 'redirect_url': reverse('login_view')})
    

@login_required
def dashboard(request):
    if 'next' in request.GET:
        messages.warning(request, 'User should be logged in to view this page.')
    polls = Poll.objects.all().order_by('-created_on')
    for poll in polls:
        if poll.end_date < timezone.now() and poll.status != "closed":
            poll.status = "closed"
            poll.save()
    return render(request, 'vote/dashboard.html', {'polls': polls})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        subject = f'New Contact Form Submission from {name}'
        full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"
        try:
            send_mail(
                subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            print(e)
    return render(request, 'vote/contact.html')


def about(request):
    return render(request, 'vote/about.html')


@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        # Get the new username
        new_username = request.POST.get('username')

        # Check if the new username already exists in other users
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            messages.error(request, "This username is already taken by another user.")
            return redirect('user-profile')

        # Update the user's profile if the username is unique
        user.username = new_username
        user.first_name = request.POST.get('first_name')
        user.middle_name = request.POST.get('middle_name')
        user.last_name = request.POST.get('last_name')
        user.dob = request.POST.get('dob')

        upload_dir = os.path.join(settings.BASE_DIR, 'static/images/user_images/')
        os.makedirs(upload_dir, exist_ok=True)
        fs = FileSystemStorage(location=upload_dir)
        user.dob = request.POST.get('dob')

        upload_dir = os.path.join(settings.BASE_DIR, 'static/images/user_images/')
        os.makedirs(upload_dir, exist_ok=True)
        fs = FileSystemStorage(location=upload_dir)

        # Update the avatar and voter ID image 
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            avatar_name = fs.save(avatar_file.name, avatar_file)
            user.avatar = f'user_images/{avatar_name}'

        if 'voter_id_image' in request.FILES:
            voter_id_file = request.FILES['voter_id_image']
            voter_id_name = fs.save(voter_id_file.name, voter_id_file)
            user.voter_id_image = f'user_images/{voter_id_name}'
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            avatar_name = fs.save(avatar_file.name, avatar_file)
            user.avatar = f'user_images/{avatar_name}'

        if 'voter_id_image' in request.FILES:
            voter_id_file = request.FILES['voter_id_image']
            voter_id_name = fs.save(voter_id_file.name, voter_id_file)
            user.voter_id_image = f'user_images/{voter_id_name}'

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('dashboard')
    return render(request, 'vote/user_profile.html')


def login_view(request):
    if 'next' in request.GET:
        messages.warning(request, 'User should be logged in to view this page.')
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': "User not found."})
        user = authenticate(request, email=email, password=password)
        if user is not None:
            generate_otp(request, user.id)
            user_id = request.session.get("otp_user_id")
            uid = request.session.get("otp_uid")
            token = request.session.get("otp_token")
            if not user_id or not uid or not token:
                return JsonResponse({'success': False, 'error': "OTP generation failed. Please try again."})
            return JsonResponse({
                'success': True,
                'show_otp_modal': True,
                'uid': uid,
                'token': token
            })
        else:
            return JsonResponse({'success': False, 'error': "Invalid credentials."})
    return render(request, 'vote/login.html')


def verify_otp(request):
    if request.method == "POST":
        # Getting submitted data
        uidb64 = request.session.get("otp_uid")
        token = request.session.get("otp_token")
        # Getting submitted data
        uidb64 = request.session.get("otp_uid")
        token = request.session.get("otp_token")
        otp_input = request.POST.get("otp", "")

        def error_response(msg):
            return JsonResponse({'success': False, 'error': msg})

        try:
            # Decode UID and retrieve the user
            # Decode UID and retrieve the user
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response("Invalid user.")
        
        # Check if token is still valid
        
        # Check if token is still valid
        if not default_token_generator.check_token(user, token):
            return error_response("Invalid or expired token.")
        
        # Fetch stored OTP and creation time from session
        
        # Fetch stored OTP and creation time from session
        session_key = f'otp_{uidb64}_{token}'
        otp_creation_key = f'otp_creation_{uidb64}_{token}'
        stored_otp = request.session.get(session_key)
        
        # Debugging: Check what's in the session for OTP
        print("Stored OTP in session:", stored_otp)
        print("Session keys:", list(request.session.keys()))  # Print all session keys for debugging
        
        
        # Debugging: Check what's in the session for OTP
        print("Stored OTP in session:", stored_otp)
        print("Session keys:", list(request.session.keys()))  # Print all session keys for debugging
        
        if not stored_otp:
            return error_response("OTP expired or not found.")
        
        # Check if the OTP is still within the valid time window
        
        # Check if the OTP is still within the valid time window
        otp_creation_str = request.session.get(otp_creation_key)
        if otp_creation_str:
            otp_creation_time = parse_datetime(otp_creation_str)
            print("OTP creation time:", otp_creation_time)  # Debugging
            print("OTP creation time:", otp_creation_time)  # Debugging
            if timezone.now() > otp_creation_time + timedelta(seconds=120):  # OTP expiry after 2 minutes  # OTP expiry after 2 minutes
                return error_response("OTP has expired.")


        if otp_input != stored_otp :
            return error_response("Incorrect OTP.")
        
        # Clean up session keys once OTP is used
        
        # Clean up session keys once OTP is used
        request.session.pop(session_key, None)
        request.session.pop(otp_creation_key, None)
        
        # Log the user in
        
        # Log the user in
        login(request, user)
        messages.success(request, f'Welcome {user.first_name}! You have logged in successfully.')

        # Redirect to password change page if required

        # Redirect to password change page if required
        if user.change_password:
            return JsonResponse({'success': True, 'redirect_url': reverse('change_password')})


        return JsonResponse({'success': True, 'redirect_url': reverse('dashboard')})

    return JsonResponse({'success': False, 'error': "Invalid request method."})


@csrf_exempt
@require_http_methods(["POST"])
def resend_otp(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return JsonResponse({"success": False, "error": "Session expired. Please login again."})

    try:
        old_uid = request.session.get("otp_uid")
        old_token = request.session.get("otp_token")
        if old_uid and old_token:
            request.session.pop(f'otp_{old_uid}_{old_token}', None)
            request.session.pop(f'otp_creation_{old_uid}_{old_token}', None)
        keys_to_delete = [key for key in request.session.keys() if key.startswith('otp_')]
        for key in keys_to_delete:
            del request.session[key]

        # Use the same logic as generate_otp but as a reusable function
        result = send_otp(request, user_id, mail_type="resend")
        if not result.get("success"):
            return JsonResponse({"success": False, "error": "Failed to resend OTP."})

        return JsonResponse({"success": True, "message": "OTP resent successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        has_error = False
        if not check_password(old_password, request.user.password):
            messages.error(request, "Old password is incorrect.")
            has_error = True

        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            has_error = True

        if len(new_password1) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            has_error = True

        if has_error:
            return redirect('change_password')

        request.user.set_password(new_password1)
        request.user.change_password = False
        request.user.save()
        # update_session_auth_hash(request, request.user)
        messages.success(request, "Your password has been updated successfully!")
        return redirect('login_view')
    return render(request, "vote/change_password.html")


@login_required
def vote_poll(request, poll_id):
    if 'next' in request.GET:
        messages.warning(request, 'User should be logged in to view this page.')
    poll = get_object_or_404(Poll, id=poll_id)
    options = poll.option_set.all()
    user_vote = None
    if request.user.is_authenticated:
        user_vote = UserVote.objects.filter(poll=poll, user=request.user).first()
    poll_data = {
        "poll_id": poll.id,
        "question": poll.topic,
        "options": [
            {
                "id": option.id,
                "name": option.option_text,
                "votes": UserVote.objects.filter(poll=poll, option=option).count(),
                "color": consistent_color(option.option_text),
            }
            for option in options
        ],
        "user_voted_option_id": user_vote.option.id if user_vote else None,
        "user_voted": bool(user_vote),
    }
    return render(request, "vote/vote_poll.html", {
        "poll": poll,
        "options": options,
        "poll_data_json": json.dumps(poll_data, cls=DjangoJSONEncoder),
        "user_voted_option_id": user_vote.option.id if user_vote else None,
    })


@require_POST
def submit_vote(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'error': 'User must be logged in'}, status=403)
    try:
        data = json.loads(request.body)
        poll_id = data.get('poll_id')
        option_id = data.get('option_id')
        poll = Poll.objects.get(id=poll_id)
        option = Option.objects.get(id=option_id, poll=poll)
        # Check if user already voted
        if UserVote.objects.filter(poll=poll, user=user).exists():
            return JsonResponse({'error': 'You have already voted on this poll.'}, status=400)
        # Record the vote
        UserVote.objects.create(poll=poll, option=option, user=user)
        vote_count = UserVote.objects.filter(option=option).count()
        return JsonResponse({
            'message': 'Vote submitted!',
            'option_id': option.id,
            'votes': vote_count
        })
    except (Poll.DoesNotExist, Option.DoesNotExist):
        return JsonResponse({'error': 'Invalid poll or option'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def forgot_password_request(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        user = User.objects.get(email=email)
        result = generate_otp(request, user.id)
        user_id = request.session.get("otp_user_id")
        uid = request.session.get("otp_uid")
        token = request.session.get("otp_token")
        if not user_id or not uid or not token:
            return JsonResponse({'success': False, 'error': "OTP generation failed. Please try again."})
        if result.get("success"):
            return JsonResponse({'success': True, 'uid': uid, 'token': token})
        else:
            return JsonResponse({'success': False, 'error': result.get("error", "OTP generation failed")})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Email not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def reset_password_after_otp(request):
    try:
        if request.method == "POST":
            uidb64 = request.POST.get("uid")
            token = request.POST.get("token")
            otp_input = request.POST.get("forgotOtp", "")
            input_otp = otp_input[:6]
            input_voter_id = otp_input[6:]

        def error_response(msg):
            return JsonResponse({'success': False, 'error': msg})

        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            return error_response("Invalid or expired token")
        session_key = f'otp_{uidb64}_{token}'
        creation_key = f'otp_creation_{uidb64}_{token}'
        stored_otp = request.session.get(session_key)
        if not stored_otp:
            return error_response("OTP expired or not found")
        if stored_otp != input_otp:
            return error_response("Incorrect OTP")
        if user.voter_id != input_voter_id:
            return error_response("Voter ID mismatch")
        otp_time_str = request.session.get(creation_key)
        if otp_time_str:
            otp_time = parse_datetime(otp_time_str)
            if timezone.now() > otp_time + timedelta(seconds=120):
                return error_response("OTP expired")
        # Clear old OTP
        request.session.pop(session_key, None)
        request.session.pop(creation_key, None)
        # Generate and set new password
        new_password = secrets.token_urlsafe(8)
        user.set_password(new_password)
        user.change_password = True
        user.save()
        # Send email with new password
        send_mail(
            "Your New Password",
            f"Your new password is: {new_password}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return JsonResponse({
            'success': True,
            'message': 'Password reset successfully. Check your email.',
            'redirect_url': reverse('login_view')
        })
    except (User.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Invalid user'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def verify_voter(request):
    try:
        data = json.loads(request.body)
        input_voter_id = data.get("voter")

        # Get current logged-in user's voter_id
        user_voter_id = request.user.voter_id

        if str(input_voter_id).strip() == str(user_voter_id).strip():
            return JsonResponse({'status': 'success', 'message': 'Voter verified successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Voter ID does not match your account.'}, status=403)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')
    return redirect('index')