import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Create admin group if it doesn't exist
admin_group, created = Group.objects.get_or_create(name='admin')
print('Admin group created:', created)

# Find the user
user = User.objects.filter(username='SlainerBot').first()
if user:
    user.groups.add(admin_group)
    user.save()
    print('User added to admin group')
else:
    print('User not found')
