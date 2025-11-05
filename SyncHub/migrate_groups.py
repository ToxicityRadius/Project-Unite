import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from django.contrib.auth.models import Group

# Create new groups
executive_officer_group, created = Group.objects.get_or_create(name='Executive Officer')
print(f'Executive Officer group created: {created}')

officer_group, created = Group.objects.get_or_create(name='Officer')
print(f'Officer group created: {created}')

staff_group, created = Group.objects.get_or_create(name='Staff')
print(f'Staff group created: {created}')

print('Group creation completed. Migration of users will be done manually if needed.')
