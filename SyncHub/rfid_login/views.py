from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, Case, When, FloatField, F
from django.db.models.functions import Extract
from datetime import timedelta
from .models import Officer, TimeLog
from django import forms
from django.contrib.auth.models import User
from SyncHub.models import CustomUser
import json
import csv
import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from io import BytesIO
from django.template.loader import render_to_string

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
            # Try to get officer by ID
            officer = Officer.objects.get(id=officer_id)
        except Officer.DoesNotExist:
            # If officer doesn't exist, check if it's a CustomUser student_number
            try:
                user = CustomUser.objects.get(student_number=officer_id)
                # Create officer record if it doesn't exist
                officer, created = Officer.objects.get_or_create(
                    id=officer_id,
                    defaults={'name': f"{user.first_name} {user.last_name}", 'position': 'Member'}
                )
            except CustomUser.DoesNotExist:
                message = "Invalid officer ID"
                return render(request, 'rfid_login/login.html', {'message': message, 'is_admin': is_admin, 'last_log': last_log})
        try:
            # Check if there's an open time log for today
            today = timezone.now().date()
            open_time_log = TimeLog.objects.filter(officer=officer, date=today, time_out__isnull=True).first()
            if open_time_log:
                # Time out the earliest open log
                open_time_log.time_out = timezone.now()
                open_time_log.save()
                message = f"Time out recorded for {officer.name}"
            else:
                # Time in
                TimeLog.objects.create(officer=officer, time_in=timezone.now(), date=timezone.now().date())
                message = f"Time in recorded for {officer.name}"
            # Get the last log for display
            last_log = TimeLog.objects.filter(officer=officer).order_by('-date', '-time_in').first()
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

    is_executive_or_staff = request.user.groups.filter(name='executive officer').exists() or request.user.groups.filter(name='staff').exists()

    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset for logs_by_date
    logs_by_date = TimeLog.objects.values('date').annotate(
        total_officers=Count('officer', distinct=True)
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

    # Calculate new metrics
    # Most Active Officer and Top 3
    if sorted_officers:
        most_active_officer = sorted_officers[0][0]
        top_3_officers = [name for name, hours in sorted_officers[:3]]
    else:
        most_active_officer = "N/A"
        top_3_officers = []

    # Highest Hours (Single Day)
    highest_single_day_hours = 0
    for log in filtered_logs:
        if log.time_in and log.time_out:
            duration = log.time_out - log.time_in
            hours = duration.total_seconds() / 3600
            if hours > highest_single_day_hours:
                highest_single_day_hours = hours

    # Average Hours per Officer
    total_officers = len(sorted_officers)
    total_hours_all = sum(hours for name, hours in sorted_officers)
    average_hours_per_officer = total_hours_all / total_officers if total_officers > 0 else 0

    # Most Active Date
    date_hours = {}
    for log in filtered_logs:
        date_str = str(log.date)
        duration = log.time_out - log.time_in if log.time_out else timedelta(0)
        hours = duration.total_seconds() / 3600
        date_hours[date_str] = date_hours.get(date_str, 0) + hours
    most_active_date = max(date_hours, key=date_hours.get) if date_hours else "N/A"

    # Total Days Covered
    total_days_covered = len(date_hours)



    # Debug
    print("Dates:", dates)
    print("Officers Count:", officers_count)
    print("Total Hours List:", total_hours_list)
    print("Officer Names:", officer_names)
    print("Officer Total Hours:", officer_total_hours)

    print("Most Active Officer:", most_active_officer)
    print("Top 3 Officers:", top_3_officers)
    print("Highest Single Day Hours:", round(highest_single_day_hours, 2))
    print("Average Hours per Officer:", round(average_hours_per_officer, 2))
    print("Total Officers:", total_officers)
    print("Most Active Date:", most_active_date)
    print("Total Days Covered:", total_days_covered)

    return render(request, 'rfid_login/time_reports.html', {
        'logs_by_date': logs_by_date,
        'officer_hours': sorted_officers,
        'dates': json.dumps(dates),
        'officers_count': json.dumps(officers_count),
        'total_hours_list': json.dumps(total_hours_list),
        'officer_names': json.dumps(officer_names),
        'officer_total_hours': json.dumps(officer_total_hours),
        'is_admin': is_admin,
        'is_executive_or_staff': is_executive_or_staff,
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

def get_time_reports_data(request):
    """Helper function to get time reports data, reused in main view and exports."""
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    if not is_admin:
        return None  # Or raise permission denied

    # Get filter parameters from GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Base queryset for logs_by_date
    logs_by_date = TimeLog.objects.values('date').annotate(
        total_officers=Count('officer', distinct=True)
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

    # Calculate new metrics
    # Most Active Officer and Top 3
    if sorted_officers:
        most_active_officer = sorted_officers[0][0]
        top_3_officers = [name for name, hours in sorted_officers[:3]]
    else:
        most_active_officer = "N/A"
        top_3_officers = []

    # Highest Hours (Single Day)
    highest_single_day_hours = 0
    for log in filtered_logs:
        if log.time_in and log.time_out:
            duration = log.time_out - log.time_in
            hours = duration.total_seconds() / 3600
            if hours > highest_single_day_hours:
                highest_single_day_hours = hours

    # Average Hours per Officer
    total_officers = len(sorted_officers)
    total_hours_all = sum(hours for name, hours in sorted_officers)
    average_hours_per_officer = total_hours_all / total_officers if total_officers > 0 else 0

    # Most Active Date
    date_hours = {}
    for log in filtered_logs:
        date_str = str(log.date)
        duration = log.time_out - log.time_in if log.time_out else timedelta(0)
        hours = duration.total_seconds() / 3600
        date_hours[date_str] = date_hours.get(date_str, 0) + hours
    most_active_date = max(date_hours, key=date_hours.get) if date_hours else "N/A"

    # Total Days Covered
    total_days_covered = len(date_hours)

    return {
        'logs_by_date': logs_by_date,
        'officer_hours': sorted_officers,
        'dates': dates,
        'officers_count': officers_count,
        'total_hours_list': total_hours_list,
        'officer_names': officer_names,
        'officer_total_hours': officer_total_hours,
        'most_active_officer': most_active_officer,
        'top_3_officers': top_3_officers,
        'highest_single_day_hours': round(highest_single_day_hours, 2),
        'average_hours_per_officer': round(average_hours_per_officer, 2),
        'total_officers': total_officers,
        'most_active_date': most_active_date,
        'total_days_covered': total_days_covered,
        'filters': {'start_date': start_date, 'end_date': end_date}
    }

def export_csv(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    if not is_admin:
        return HttpResponse('Access denied', status=403)

    data = get_time_reports_data(request)
    if not data:
        return HttpResponse('No data available', status=404)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="officer_hours_summary.csv"'

    writer = csv.writer(response)
    writer.writerow(['Officer Name', 'Total Hours'])

    for name, hours in data['officer_hours']:
        writer.writerow([name, round(hours, 2)])

    return response

def export_pdf(request):
    is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Executive Officer', 'Staff']).exists()
    if not is_admin:
        return HttpResponse('Access denied', status=403)

    data = get_time_reports_data(request)
    if not data:
        return HttpResponse('No data available', status=404)

    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.Color(0, 123/255, 255/255),  # Blue color matching website
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.Color(102/255, 126/255, 234/255),  # Purple gradient start color
    )

    # Title
    elements.append(Paragraph("Time Reports Summary", title_style))
    elements.append(Spacer(1, 12))

    # Filters info
    filters = data['filters']
    filter_text = f"Date Range: {filters['start_date'] or 'All'} to {filters['end_date'] or 'All'}"
    elements.append(Paragraph(filter_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Summary metrics
    elements.append(Paragraph("Summary Metrics", heading_style))
    metrics_data = [
        ["Total Officers", str(data['total_officers'])],
        ["Total Days Covered", str(data['total_days_covered'])],
        ["Most Active Officer", data['most_active_officer']],
        ["Most Active Date", data['most_active_date']],
        ["Highest Single Day Hours", f"{data['highest_single_day_hours']} hours"],
        ["Average Hours per Officer", f"{data['average_hours_per_officer']:.2f} hours"],
    ]
    metrics_table = Table(metrics_data, colWidths=[2*inch, 3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(102/255, 126/255, 234/255)),  # Purple gradient start color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0, 123/255, 255/255, 0.1)),  # Light blue background for rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 20))

    # Officer Hours Table
    elements.append(Paragraph("Officer Hours Summary", heading_style))
    officer_data = [['Officer Name', 'Total Hours']] + [[name, f"{hours:.2f}"] for name, hours in data['officer_hours']]
    officer_table = Table(officer_data, colWidths=[3*inch, 2*inch])
    officer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(102/255, 126/255, 234/255)),  # Purple gradient start color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0, 123/255, 255/255, 0.1)),  # Light blue background for rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(officer_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    # Create response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="time_reports.pdf"'

    return response
