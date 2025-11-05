import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rfid_login.models import Officer

User = get_user_model()

# Create admin group if it doesn't exist
admin_group, created = Group.objects.get_or_create(name='admin')
print('Admin group created:', created)

# Find the user by email
user = User.objects.filter(email='healeradobo@gmail.com').first()
if user:
    user.groups.add(admin_group)
    user.save()
    print('User added to admin group')
else:
    print('User not found')

# Create or get officer for the user
officer, created = Officer.objects.get_or_create(
    student_number='2310004',
    defaults={
        'name': 'Admin Officer',
        'position': 'Administrator',
        'rfid_tag': '7654321a'
    }
)
print('Officer created:', created)
