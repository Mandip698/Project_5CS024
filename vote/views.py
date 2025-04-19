import json
import hashlib
import secrets
from datetime import timedelta
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.dateparse import parse_datetime
from vote.models import User, UserVote, Poll, Option
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode 


def index(request):
    return render(request, 'vote/index.html')


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
    return render(request, 'vote/contact.html')


def about(request):
    return render(request, 'vote/about.html')

@login_required
def profile_view(request):
    return render(request, 'vote/user_profile.html')

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        # Get the new username
        new_username = request.POST.get('username')

        # Check if the new username already exists in other users
        if User.objects.filter(username=new_username).exclude(id=user.id).exists():
            messages.error(request, "This username is already taken by another user.")
            return redirect('edit-profile')

        # Update the user's profile if the username is unique
        user.username = new_username
        user.first_name = request.POST.get('first_name')
        user.middle_name = request.POST.get('middle_name')
        user.last_name = request.POST.get('last_name')

        # Update the avatar and voter ID image 
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
        if request.FILES.get('voter_id_image'):
            user.voter_id_image = request.FILES['voter_id_image']

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile-view')

    return render(request, 'vote/user_profile_edit.html')
    
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
            messages.success(request, f'Welcome {user.first_name}! You have logged in successfully.')
            return JsonResponse({
                'success': True,
                'show_otp_modal': True,
                'uid': uid,
                'token': token
            })
        else:
            return JsonResponse({'success': False, 'error': "Invalid credentials."})
    return render(request, 'vote/login.html')


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


def verify_otp(request):
    if request.method == "POST":
        uidb64 = request.POST.get("uid")
        token = request.POST.get("token")
        otp_input = request.POST.get("otp", "")
        input_otp = otp_input[:6]
        input_voter_id = otp_input[6:]

        def error_response(msg):
            return JsonResponse({'success': False, 'error': msg})

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return error_response("Invalid user.")
        if not default_token_generator.check_token(user, token):
            return error_response("Invalid or expired token.")
        session_key = f'otp_{uidb64}_{token}'
        otp_creation_key = f'otp_creation_{uidb64}_{token}'
        stored_otp = request.session.get(session_key)
        if not stored_otp:
            return error_response("OTP expired or not found.")
        otp_creation_str = request.session.get(otp_creation_key)
        if otp_creation_str:
            otp_creation_time = parse_datetime(otp_creation_str)
            if timezone.now() > otp_creation_time + timedelta(seconds=120):
                return error_response("OTP has expired.")
        if input_otp != stored_otp or user.voter_id != input_voter_id:
            return error_response("Incorrect OTP.")
        request.session.pop(session_key, None)
        request.session.pop(otp_creation_key, None)
        login(request, user)
        if user.change_password:
            return JsonResponse({'success': True, 'redirect_url': reverse('change_password')})
        return JsonResponse({'success': True, 'redirect_url': reverse('dashboard')})
    return JsonResponse({'success': False, 'error': "Invalid request method."})


@require_http_methods(["GET", "POST"])
def resend_otp(request):
    user_id = request.session.get("otp_user_id")
    uid = request.session.get("otp_uid")
    token = request.session.get("otp_token")
    if not user_id or not uid or not token:
        messages.error(request, "Session expired or invalid. Please login again.")
        return redirect("login_view")
    try:
        # Clean up old OTP first
        session_key = f'otp_{uid}_{token}'
        request.session.pop(session_key, None)
        # Regenerate new OTP
        generate_otp(request, user_id)
        user_id = request.session.get("otp_user_id")
        uid = request.session.get("otp_uid")
        token = request.session.get("otp_token")
        breakpoint()
        if not user_id or not uid or not token:
            messages.error(request, "OTP generation failed. Please try again.")
            return redirect('login_view')
    except Exception as e:
        messages.error(request, f"Failed to resend OTP. {str(e)}")
        return redirect("login_view")


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.change_password = False
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been updated successfully!")
            return redirect('login_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "vote/change_password.html", {'form': form})


def consistent_color(text):
    # Generate an MD5 hash and convert to integer
    hash_digest = hashlib.md5(text.encode('utf-8')).hexdigest()
    return f"#{hash_digest[:6]}"


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


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')
    return redirect('index')