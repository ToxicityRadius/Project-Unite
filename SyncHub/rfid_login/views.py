from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Case, When, FloatField, F
from django.db.models.functions import Extract
from datetime import timedelta
from .models import Officer, TimeLog
from django import forms
import json

class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['id', 'name', 'position']

def login_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    last_log = None
    if request.method == 'POST':
        officer_id = request.POST.get('officer_id')
        try:
            officer = Officer.objects.get(id=officer_id)
            # Check if there's an open time log for today
            today = timezone.now().date()
            time_log = TimeLog.objects.filter(officer=officer, date=today).first()
            if time_log and not time_log.time_out:
                # Time out
                time_log.time_out = timezone.now()
                time_log.save()
                message = f"Time out recorded for {officer.name}"
            else:
                # Time in
                TimeLog.objects.create(officer=officer, time_in=timezone.now(), date=timezone.now().date())
                message = f"Time in recorded for {officer.name}"
            # Get the last log for display
            last_log = TimeLog.objects.filter(officer=officer).order_by('-date', '-time_in').first()
            return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
        except Officer.DoesNotExist:
            message = "Invalid officer ID"
            return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
        except ValueError:
            message = "Invalid officer ID format"
            return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
    return render(request, 'rfid_login/login.html', {'is_admin': is_admin, 'last_log': last_log})

def time_log_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    if not is_admin:
        return render(request, 'rfid_login/time_log.html', {'error': 'Access denied. Admin privileges required.', 'is_admin': is_admin})

    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    officer_id = request.GET.get('officer_id')

    # Start with base queryset
    time_logs = TimeLog.objects.all().order_by('-date')

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

def time_reports_view(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    if not is_admin:
        return render(request, 'rfid_login/time_reports.html', {'error': 'Access denied. Admin privileges required.', 'is_admin': is_admin})

    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset for logs_by_date
    logs_by_date = TimeLog.objects.values('date').annotate(
        total_officers=Count('officer', distinct=True),
        total_hours=Sum(
            Case(
                When(time_out__isnull=False, then=(timezone.now() - timezone.now())),  # Placeholder
                default=0,
                output_field=FloatField()
            )
        )
    )

    # Apply filters
    if start_date:
        logs_by_date = logs_by_date.filter(date__gte=start_date)
    if end_date:
        logs_by_date = logs_by_date.filter(date__lte=end_date)

    logs_by_date = logs_by_date.order_by('date')

    # Calculate hours manually
    for log in logs_by_date:
        total_seconds = 0
        time_logs = TimeLog.objects.filter(date=log['date'], time_out__isnull=False)
        for tl in time_logs:
            duration = tl.time_out - tl.time_in
            total_seconds += duration.total_seconds()
        log['total_hours'] = total_seconds / 3600  # Convert to hours

    # Prepare data for first chart (overall by date)
    dates = [log['date'].strftime('%b %d') for log in logs_by_date]
    officers_count = [log['total_officers'] for log in logs_by_date]
    total_hours_list = [round(log['total_hours'] or 0, 2) for log in logs_by_date]

    # Second chart: Total hours per officer for filtered dates
    filtered_logs = TimeLog.objects.filter(time_out__isnull=False)
    if start_date:
        filtered_logs = filtered_logs.filter(date__gte=start_date)
    if end_date:
        filtered_logs = filtered_logs.filter(date__lte=end_date)

    officer_hours_dict = {}
    for log in filtered_logs:
        name = log.officer.name
        duration = log.time_out - log.time_in
        hours = duration.total_seconds() / 3600
        officer_hours_dict[name] = officer_hours_dict.get(name, 0) + hours

    # Sort by total hours descending
    sorted_officers = sorted(officer_hours_dict.items(), key=lambda x: x[1], reverse=True)
    officer_names = [name for name, hours in sorted_officers]
    officer_total_hours = [round(hours, 2) for name, hours in sorted_officers]

    # Debug
    print("Dates:", dates)
    print("Officers Count:", officers_count)
    print("Total Hours List:", total_hours_list)
    print("Officer Names:", officer_names)
    print("Officer Total Hours:", officer_total_hours)

    return render(request, 'rfid_login/time_reports.html', {
        'logs_by_date': logs_by_date,
        'officer_hours': sorted_officers,
        'dates': json.dumps(dates),
        'officers_count': json.dumps(officers_count),
        'total_hours_list': json.dumps(total_hours_list),
        'officer_names': json.dumps(officer_names),
        'officer_total_hours': json.dumps(officer_total_hours),
        'is_admin': is_admin,
        'filters': {'start_date': start_date, 'end_date': end_date}
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
