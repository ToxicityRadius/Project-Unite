import os
import sys
import django

# Add the SyncHub directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SyncHub'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')
django.setup()

from django.db import connection

# Delete all admin migrations from history
cursor = connection.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app='admin'")
connection.commit()
print("Deleted all admin migrations from migration history")
