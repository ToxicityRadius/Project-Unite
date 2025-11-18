from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordResetForm
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

def purpose_page(request):
    """Purpose page view"""
    return render(request, 'purpose.html')

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
        return JsonResponse({
            'message': 'Login successful.',
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'username': user.username,
            }
        })
    logger.warning(f"Invalid credentials for identifier: {identifier}")
    return JsonResponse({'message': 'Invalid credentials.'}, status=400)

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
        officer_group, created = Group.objects.get_or_create(name='Officer')
        user.groups.add(officer_group)
        logger.info(f"User created successfully: {student_number}")
        return JsonResponse({'message': 'User created successfully.'})
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return JsonResponse({'message': 'Error creating user: %s' % str(e)}, status=500)

@login_required
def dashboard_view(request):
    """Dashboard view - requires authentication"""
    is_executive_or_staff = request.user.groups.filter(name='executive officer').exists() or request.user.groups.filter(name='staff').exists()
    context = {
        'is_executive_or_staff': is_executive_or_staff,
    }
    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    """Profile view for user customization. Supports GET (render) and POST (JSON update).

    POST expects JSON: { first_name, last_name, role }
    """
    # Handle AJAX JSON update
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'message': 'Invalid JSON.'}, status=400)
        first_name = payload.get('first_name', '').strip()
        last_name = payload.get('last_name', '').strip()
        role = payload.get('role', '').strip()
        bio = payload.get('bio', '').strip()
        user = request.user
        changed = False
        if first_name and first_name != user.first_name:
            user.first_name = first_name
            changed = True
        if last_name and last_name != user.last_name:
            user.last_name = last_name
            changed = True
        if bio != user.bio:
            user.bio = bio
            changed = True
        # Update groups: ensure only one of Officer/Mentee/Staff is assigned
        try:
            from django.contrib.auth.models import Group
            possible = ['Officer', 'Mentee', 'Staff', 'Executive Officer']
            for gname in possible:
                try:
                    g = Group.objects.get(name=gname)
                    if g in user.groups.all():
                        user.groups.remove(g)
                except Group.DoesNotExist:
                    continue
            # Add requested role if it exists
            if role:
                try:
                    group, created = Group.objects.get_or_create(name=role)
                    user.groups.add(group)
                    changed = True
                except Exception:
                    # ignore if error
                    pass
        except Exception:
            pass
        if changed:
            try:
                user.save()
            except Exception as e:
                logger.error(f"Error saving user profile: {e}")
                return JsonResponse({'message': 'Error saving profile.'}, status=500)
        return JsonResponse({'message': 'Profile updated successfully.'})

    # GET render
    user_groups = request.user.groups.all()
    if user_groups.filter(name='Executive Officer').exists():
        role = 'Executive Officer'
    elif user_groups.filter(name='Officer').exists():
        role = 'Officer'
    elif user_groups.filter(name='Mentee').exists():
        role = 'Mentee'
    else:
        role = 'Staff'

    # Get recent RFID activities for the user
    from rfid_login.models import TimeLog, Officer
    from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
    from django.contrib.contenttypes.models import ContentType
    from inventory.models import Item
    
    recent_activities = []
    
    # Get RFID time log activities
    try:
        officer = Officer.objects.get(id=request.user.student_number)
        logs = TimeLog.objects.filter(officer=officer).order_by('-date', '-time_in')[:10]
        for log in logs:
            if log.time_out:
                activity = {
                    'text': f"Time Out: {log.date} at {log.time_out.astimezone().strftime('%I:%M %p')}",
                    'timestamp': log.time_out
                }
            else:
                activity = {
                    'text': f"Time In: {log.date} at {log.time_in.astimezone().strftime('%I:%M %p')}",
                    'timestamp': log.time_in
                }
            recent_activities.append(activity)
    except Officer.DoesNotExist:
        pass
    
    # Get inventory management activities from Django admin logs
    try:
        item_content_type = ContentType.objects.get_for_model(Item)
        inventory_logs = LogEntry.objects.filter(
            user=request.user,
            content_type=item_content_type
        ).order_by('-action_time')[:10]
        
        for log in inventory_logs:
            action_text = ""
            if log.action_flag == ADDITION:
                action_text = f"Added inventory item: {log.object_repr}"
            elif log.action_flag == CHANGE:
                action_text = f"Updated inventory item: {log.object_repr}"
            elif log.action_flag == DELETION:
                action_text = f"Deleted inventory item: {log.object_repr}"
            
            if action_text:
                activity = {
                    'text': action_text,
                    'timestamp': log.action_time
                }
                recent_activities.append(activity)
    except Exception:
        pass
    
    # Sort all activities by timestamp and take the most recent 10
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = [activity['text'] for activity in recent_activities[:10]]

    context = {
        'role': role,
        'recent_activities': recent_activities,
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

def password_reset_validate_email(request):
    """Custom password reset view that sends actual reset link via email"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html',
                subject_template_name='registration/password_reset_subject.txt',
                html_email_template_name='registration/password_reset_email.html',
            )
            messages.success(request, 'Password reset email sent. Check your inbox.')
            return redirect('landing')
        else:
            messages.error(request, 'Invalid email address.')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})
