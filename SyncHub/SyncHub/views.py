from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.utils import timezone
from .forms import CustomUserCreationForm
from .models import CustomUser
import json
import logging

logger = logging.getLogger(__name__)

def landing_page(request):
    """Landing page view"""
    return render(request, 'index.html')

def about_us(request):
    """About Us page view"""
    return render(request, 'about_us.html')

def _authenticate_identifier_password(request, identifier, password):
    """Authenticate by student number or email."""
    user = None
    if identifier and password:
        # Try as student number if it's 7 digits
        if identifier.isdigit() and len(identifier) == 7:
            user = authenticate(request, username=identifier, password=password)
        else:
            # Try as email
            try:
                user_obj = CustomUser.objects.get(email__iexact=identifier)
                user = authenticate(request, username=user_obj.student_number, password=password)
            except CustomUser.DoesNotExist:
                pass
    return user

@csrf_exempt
def login_api(request):
    """JSON API login endpoint."""
    logger.info(f"Login API request: method={request.method}, content_type={request.content_type}, body_length={len(request.body)}")
    if request.method != 'POST':
        logger.warning(f"Invalid method: {request.method}")
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    if request.content_type != 'application/json':
        logger.warning(f"Invalid content-type: {request.content_type}")
        return JsonResponse({'message': 'Content-Type must be application/json.'}, status=400)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        logger.info(f"Parsed payload: {payload}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        return JsonResponse({'message': 'Invalid JSON.'}, status=400)
    identifier = payload.get('identifier') or payload.get('username')
    password = payload.get('password')
    if not identifier or not password:
        logger.warning("Missing identifier or password")
        return JsonResponse({'message': 'Identifier and password are required.'}, status=400)
    user = _authenticate_identifier_password(request, identifier, password)
    if user is not None:
        auth_login(request, user)
        logger.info(f"Login successful for user: {user.username}")
        return JsonResponse({'message': 'Login successful.'})
    logger.warning(f"Invalid credentials for identifier: {identifier}")
    return JsonResponse({'message': 'Invalid credentials.'}, status=400)


def login_page(request):
    """Login page view with form POST handling"""
    # Traditional form POST
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = _authenticate_identifier_password(request, username, password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def signup_page(request):
    """Signup page view with form handling"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Assign Officer role to new users
            officer_group = Group.objects.get(name='Officer')
            user.groups.add(officer_group)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@csrf_exempt
def signup_api(request):
    """Signup API endpoint that accepts JSON POST to create a new user"""
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    if request.content_type != 'application/json':
        return JsonResponse({'message': 'Content-Type must be application/json.'}, status=400)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'message': 'Invalid JSON.'}, status=400)
    first_name = payload.get('first_name', '').strip()
    last_name = payload.get('last_name', '').strip()
    email = payload.get('email', '').strip()
    password = payload.get('password', '').strip()
    student_number = payload.get('student_number') or payload.get('username', '').strip()
    if not email or not password or not student_number:
        return JsonResponse({'message': 'Email, password, and student number are required.'}, status=400)
    if CustomUser.objects.filter(email__iexact=email).exists():
        return JsonResponse({'message': 'Email already registered.'}, status=400)
    if CustomUser.objects.filter(student_number=student_number).exists():
        return JsonResponse({'message': 'Student number already registered.'}, status=400)
    if not student_number.isdigit() or len(student_number) != 7:
        return JsonResponse({'message': 'Student number must be exactly 7 digits.'}, status=400)
    try:
        user = CustomUser.objects.create_user(
            username=student_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            student_number=student_number
        )
        user.save()
        # Assign Officer role to new users
        officer_group = Group.objects.get(name='Officer')
        user.groups.add(officer_group)
        logger.info(f"User created successfully: {student_number}")
        return JsonResponse({'message': 'User created successfully.'})
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return JsonResponse({'message': 'Error creating user: %s' % str(e)}, status=500)

@login_required
def dashboard_view(request):
    """Dashboard view - requires authentication"""
    return render(request, 'dashboard.html')

@login_required
def profile_view(request):
    """Profile view for user customization"""
    # Determine user role
    user_groups = request.user.groups.all()
    if user_groups.filter(name='Executive Officer').exists():
        role = 'Executive Officer'
    elif user_groups.filter(name='Officer').exists():
        role = 'Officer'
    else:
        role = 'Staff'

    context = {
        'role': role,
    }
    return render(request, 'profile.html', context)

@csrf_exempt
def logout_view(request):
    """Logout view"""
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('landing')

def get_logged_in_superusers():
    """Utility function to get currently logged-in superusers"""
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_ids = set()
    for session in sessions:
        data = session.get_decoded()
        user_id = data.get('_auth_user_id')
        if user_id:
            user_ids.add(int(user_id))
    superusers = User.objects.filter(id__in=user_ids, is_superuser=True)
    return superusers

@user_passes_test(lambda u: u.is_superuser)
def logged_in_superadmins_view(request):
    """View to display currently logged-in superadmin accounts"""
    superusers = get_logged_in_superusers()
    return render(request, 'logged_in_superadmins.html', {'superusers': superusers})

def auth_status_api(request):
    """API endpoint to check authentication status."""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    return JsonResponse({'authenticated': False})
