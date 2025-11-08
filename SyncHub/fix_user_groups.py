import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from django.contrib.auth.models import Group
from SyncHub.models import CustomUser

def fix_user_groups():
    officer_group, created = Group.objects.get_or_create(name='Officer')
    users = CustomUser.objects.all()
    for user in users:
        if not user.groups.filter(name='Officer').exists():
            user.groups.add(officer_group)
            print(f'Added Officer group to {user.username}')

if __name__ == '__main__':
    fix_user_groups()
