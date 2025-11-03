from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Officer, TimeLog
from django import forms

class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['name', 'position', 'rfid_tag', 'student_number']

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
                message = f"Time out recorded for {officer.name}"
            else:
                # Time in
                TimeLog.objects.create(officer=officer, time_in=timezone.now())
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
    time_logs = TimeLog.objects.all().order_by('-date')
    return render(request, 'rfid_login/time_log.html', {'time_logs': time_logs, 'is_admin': is_admin})

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
