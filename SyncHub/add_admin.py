import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from SyncHub.models import CustomUser as User
from django.contrib.auth.models import Group

# Create admin group if it doesn't exist
admin_group, created = Group.objects.get_or_create(name='admin')
print('Admin group created:', created)

# Find the user
user = User.objects.filter(student_number='2310170').first()
if user:
    user.groups.add(admin_group)
    user.save()
    print('User added to admin group')
else:
    print('User not found')
