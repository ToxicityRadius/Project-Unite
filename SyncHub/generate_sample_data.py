import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from rfid_login.models import TimeLog, Officer
from django.utils import timezone

def generate_sample_data():
    # Clear existing logs
    TimeLog.objects.all().delete()

    # Create officers from the example data
    officers_data = [
        # Oct 15, 2025 (7 Students)
        {'name': 'Jon Snow', 'student_number': '2310170'},
        {'name': 'Rhaenyra Targaryen', 'student_number': '2310171'},
        {'name': 'Daemon Targaryen', 'student_number': '2310172'},
        {'name': 'Arya Stark', 'student_number': '2310173'},
        {'name': 'Alicent Hightower', 'student_number': '2310174'},
        {'name': 'Robb Stark', 'student_number': '2310175'},
        {'name': 'Otto Hightower', 'student_number': '2310176'},

        # Oct 30, 2025 (15 Students)
        {'name': 'Daenerys Targaryen', 'student_number': '2310177'},
        {'name': 'Tyrion Lannister', 'student_number': '2310178'},
        {'name': 'Aemond Targaryen', 'student_number': '2310179'},
        {'name': 'Cersei Lannister', 'student_number': '2310180'},
        {'name': 'Aegon II Targaryen', 'student_number': '2310181'},
        {'name': 'Jaime Lannister', 'student_number': '2310182'},
        {'name': 'Rhaenys Targaryen', 'student_number': '2310183'},
        {'name': 'Jacaerys Velaryon', 'student_number': '2310184'},
        {'name': 'Sandor Clegane', 'student_number': '2310185'},
        {'name': 'Brienne of Tarth', 'student_number': '2310186'},
        {'name': 'Criston Cole', 'student_number': '2310187'},
        {'name': 'Sansa Stark', 'student_number': '2310188'},
        {'name': 'Viserys I Targaryen', 'student_number': '2310189'},
        {'name': 'Larys Strong', 'student_number': '2310190'},
        {'name': 'Theon Greyjoy', 'student_number': '2310191'},

        # Nov 2, 2025 (3 Students)
        {'name': 'Davos Seaworth', 'student_number': '2310192'},
        {'name': 'Helaena Targaryen', 'student_number': '2310193'},
        {'name': 'Melisandre', 'student_number': '2310194'},
    ]

    officers = []
    for officer_data in officers_data:
        officer, created = Officer.objects.get_or_create(
            student_number=officer_data['student_number'],
            defaults={
                'name': officer_data['name'],
                'position': 'Officer',
                'rfid_tag': f'RFID{officer_data["student_number"]}'
            }
        )
        officers.append(officer)

    # Generate time logs based on the example dates
    dates_and_counts = [
        (datetime(2025, 10, 15).date(), 7),  # Oct 15, 2025 (7 Students)
        (datetime(2025, 10, 30).date(), 15), # Oct 30, 2025 (15 Students)
        (datetime(2025, 11, 2).date(), 3),  # Nov 2, 2025 (3 Students)
    ]

    log_count = 0
    for date, count in dates_and_counts:
        # Use officers from the appropriate index ranges
        if date == datetime(2025, 10, 15).date():
            day_officers = officers[:7]  # First 7 officers
        elif date == datetime(2025, 10, 30).date():
            day_officers = officers[7:22]  # Next 15 officers
        elif date == datetime(2025, 11, 2).date():
            day_officers = officers[22:]  # Last 3 officers

        for i in range(count):
            officer = day_officers[i]

            # Create base time for the day
            base_time = timezone.now().replace(year=date.year, month=date.month, day=date.day,
                                             hour=8, minute=0, second=0, microsecond=0)

            # Random time in between 8 AM and 12 PM
            hour_offset = random.randint(0, 3)
            minute_offset = random.randint(0, 59)
            time_in = base_time.replace(hour=8 + hour_offset, minute=minute_offset)

            # Random time out between 4 PM and 8 PM
            hour_offset_out = random.randint(4, 7)
            minute_offset_out = random.randint(0, 59)
            time_out = base_time.replace(hour=16 + hour_offset_out, minute=minute_offset_out)

            TimeLog.objects.create(
                officer=officer,
                time_in=time_in,
                time_out=time_out,
                date=date
            )
            # Override the auto_now_add date field
            log = TimeLog.objects.filter(officer=officer, time_in=time_in).first()
            if log:
                log.date = date
                log.save()
            log_count += 1

    print(f'Created {log_count} time logs across {len(dates_and_counts)} dates')
    print('Sample logs by date:')

    for date, count in dates_and_counts:
        logs = TimeLog.objects.filter(date=date).order_by('time_in')[:3]
        print(f'\n{date.strftime("%B %d, %Y")} ({count} Students):')
        for log in logs:
            duration = log.time_out - log.time_in
            hours = round(duration.total_seconds() / 3600, 2)
            print(f'  {log.officer.name}: {log.time_in.strftime("%I:%M %p")} - {log.time_out.strftime("%I:%M %p")} ({hours} hours)')

if __name__ == '__main__':
    generate_sample_data()
