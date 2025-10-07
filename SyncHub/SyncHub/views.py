from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.utils import timezone
import json

def landing_page(request):
    """Landing page view"""
    return render(request, 'index.html')

def _authenticate_identifier_password(request, identifier, password):
    """Authenticate by username or email."""
    user = None
    if identifier and password:
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=identifier, password=password)
    return user

@csrf_exempt
def login_api(request):
    """JSON API login endpoint."""
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed.'}, status=405)
    if request.content_type != 'application/json':
        return JsonResponse({'message': 'Content-Type must be application/json.'}, status=400)
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'message': 'Invalid JSON.'}, status=400)
    identifier = payload.get('identifier') or payload.get('username')
    password = payload.get('password')
    user = _authenticate_identifier_password(request, identifier, password)
    if user is not None:
        auth_login(request, user)
        return JsonResponse({'message': 'Login successful.'})
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
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Basic validation
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'signup.html')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'signup.html')

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'signup.html')

    return render(request, 'signup.html')

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
    username = payload.get('username', '').strip()
    email = payload.get('email', '').strip()
    password = payload.get('password', '').strip()
    if not username or not email or not password:
        return JsonResponse({'message': 'All fields are required.'}, status=400)
    if User.objects.filter(username__iexact=username).exists():
        return JsonResponse({'message': 'Username already exists.'}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'message': 'Email already registered.'}, status=400)
    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return JsonResponse({'message': 'User created successfully.'})
    except Exception as e:
        return JsonResponse({'message': 'Error creating user: %s' % str(e)}, status=500)

@login_required
def dashboard_view(request):
    """Dashboard view - requires authentication"""
    return render(request, 'dashboard.html')

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
