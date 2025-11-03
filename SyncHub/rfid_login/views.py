from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Officer, TimeLog
from django import forms
from supabase import create_client
import os

class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['name', 'position', 'rfid_tag', 'student_number']

def get_supabase_client():
    url = "https://oneeklvijvdpbeeusmnw.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9uZWVrbHZpanZkcGJlZXVzbW53Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA4NjUxNTgsImV4cCI6MjA3NjQ0MTE1OH0.8UdkO9ew0WCuyAbLyzPYvPalj5BiXZSSa5yTxBh8MbQ"
    return create_client(url, key)

def sync_to_supabase(log_entry):
    """Sync a TimeLog entry to Supabase"""
    try:
        supabase = get_supabase_client()
        data = {
            'officer_name': log_entry.officer.name,
            'officer_student_number': log_entry.officer.student_number,
            'rfid_tag': log_entry.officer.rfid_tag,
            'date': log_entry.date.isoformat(),
            'time_in': log_entry.time_in.isoformat() if log_entry.time_in else None,
            'time_out': log_entry.time_out.isoformat() if log_entry.time_out else None,
            'total_hours': None
        }

        if log_entry.time_in and log_entry.time_out:
            duration = log_entry.time_out - log_entry.time_in
            data['total_hours'] = round(duration.total_seconds() / 3600, 2)

        # Insert into Supabase (assuming table name 'time_logs')
        result = supabase.table('time_logs').insert(data).execute()
        print(f"Synced to Supabase: {data}")
        return True
    except Exception as e:
        print(f"Failed to sync to Supabase: {e}")
        return False

def login_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name='admin').exists()
    last_log = None
    if request.method == 'POST':
        student_number = request.POST.get('student_number')
        try:
            officer = Officer.objects.get(student_number=student_number)
            # Check if there's an open time log for today
            today = timezone.now().date()
            time_log = TimeLog.objects.filter(officer=officer, date=today).first()
            if time_log and not time_log.time_out:
                # Time out
                time_log.time_out = timezone.now()
                time_log.save()
                # Sync to Supabase
                sync_to_supabase(time_log)
                message = f"Time out recorded for {officer.name}"
            else:
                # Time in
                time_log = TimeLog.objects.create(officer=officer, time_in=timezone.now())
                # Sync to Supabase
                sync_to_supabase(time_log)
                message = f"Time in recorded for {officer.name}"
            # Get the last log for display
            last_log = TimeLog.objects.filter(officer=officer).order_by('-date', '-time_in').first()
            return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
        except Officer.DoesNotExist:
            message = "Invalid student number"
            return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
        except ValueError:
            message = "Invalid student number format"
            return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
    return render(request, 'rfid_login/login.html', {'is_admin': is_admin, 'last_log': last_log})

def time_log_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name='admin').exists()
    if not is_admin:
        return render(request, 'rfid_login/time_log.html', {'error': 'Access denied. Admin privileges required.', 'is_admin': is_admin})

    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    officer_id = request.GET.get('officer_id')

    # Start with base queryset
    time_logs = TimeLog.objects.all().order_by('-date', '-time_in')

    # Apply filters
    if start_date:
        time_logs = time_logs.filter(date__gte=start_date)
    if end_date:
        time_logs = time_logs.filter(date__lte=end_date)
    if officer_id:
        time_logs = time_logs.filter(officer_id=officer_id)

    # Get all officers for dropdown
    officers = Officer.objects.all()

    # Calculate total hours for each log and add to context
    logs_with_hours = []
    for log in time_logs:
        if log.time_in and log.time_out:
            duration = log.time_out - log.time_in
            total_hours = round(duration.total_seconds() / 3600, 2)  # Convert to hours, round to 2 decimals
        else:
            total_hours = None
        logs_with_hours.append({
            'log': log,
            'total_hours': total_hours
        })

    return render(request, 'rfid_login/time_log.html', {
        'time_logs': logs_with_hours,  # Now a list of dicts with log and hours
        'officers': officers,
        'is_admin': is_admin,
        'filters': {'start_date': start_date, 'end_date': end_date, 'officer_id': officer_id}  # For form pre-filling
    })

# Additional simple officer CRUD for UI

def officer_list(request):
    officers = Officer.objects.all()
    return render(request, 'rfid_login/officer_list.html', {'officers': officers})

def officer_add(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rfid_login:officer_list')
    else:
        form = OfficerForm()
    return render(request, 'rfid_login/officer_form.html', {'form': form, 'action': 'Add Officer'})

def officer_edit(request, pk):
    officer = get_object_or_404(Officer, pk=pk)
    if request.method == 'POST':
        form = OfficerForm(request.POST, instance=officer)
        if form.is_valid():
            form.save()
            return redirect('rfid_login:officer_list')
    else:
        form = OfficerForm(instance=officer)
    return render(request, 'rfid_login/officer_form.html', {'form': form, 'action': 'Edit Officer', 'officer': officer})

def officer_delete(request, pk):
    officer = get_object_or_404(Officer, pk=pk)
    if request.method == 'POST':
        officer.delete()
        return redirect('rfid_login:officer_list')
    return render(request, 'rfid_login/officer_delete.html', {'officer': officer})

def time_reports_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name='admin').exists()
    if not is_admin:
        return render(request, 'rfid_login/time_log.html', {'error': 'Access denied. Admin privileges required.', 'is_admin': is_admin})

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Default to current month if no dates provided
    if not start_date or not end_date:
        from datetime import datetime
        today = datetime.today()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

    # Filter logs by date range
    logs = TimeLog.objects.filter(date__gte=start_date, date__lte=end_date)

    # Aggregate total hours per officer
    officer_hours = {}
    for log in logs:
        if log.time_in and log.time_out:
            duration = log.time_out - log.time_in
            hours = round(duration.total_seconds() / 3600, 2)
            officer_name = log.officer.name
            officer_hours[officer_name] = officer_hours.get(officer_name, 0) + hours

    # Prepare data for Chart.js
    labels = list(officer_hours.keys())
    data = list(officer_hours.values())

    import json
    return render(request, 'rfid_login/time_reports.html', {
        'is_admin': is_admin,
        'start_date': start_date,
        'end_date': end_date,
        'labels_json': json.dumps(labels),
        'data_json': json.dumps(data),
        'officer_hours': officer_hours,
    })
