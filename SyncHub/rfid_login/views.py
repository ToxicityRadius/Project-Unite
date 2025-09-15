from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Officer, TimeLog

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
