from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Officer, TimeLog
from django import forms

class OfficerForm(forms.ModelForm):
    class Meta:
        model = Officer
        fields = ['name', 'position', 'rfid_tag']

def login_view(request):
    if request.method == 'POST':
        rfid_tag = request.POST.get('rfid_tag')
        try:
            officer = Officer.objects.get(rfid_tag=rfid_tag)
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
            return render(request, 'rfid_login/login.html', {'message': message})
        except Officer.DoesNotExist:
            message = "Invalid RFID tag"
            return render(request, 'rfid_login/login.html', {'message': message})
    return render(request, 'rfid_login/login.html')

def time_log_view(request):
    time_logs = TimeLog.objects.all().order_by('-date')
    return render(request, 'rfid_login/time_log.html', {'time_logs': time_logs})

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
