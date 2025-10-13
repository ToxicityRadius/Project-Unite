import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Get the admin group
admin_group = Group.objects.filter(name='admin').first()
if not admin_group:
    print('Admin group does not exist')
    exit()

# Find the user
user = User.objects.filter(username='JustSors').first()
if user:
    user.groups.remove(admin_group)
    user.save()
    print('User removed from admin group')
