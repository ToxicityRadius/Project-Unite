"""
WSGI config for SyncHub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add the outer SyncHub folder (containing inventory, rfid_login) to sys.path
# so local apps can be imported when running from repo root on hosting platforms.
OUTER_SYNC_HUB = Path(__file__).resolve().parent.parent
if str(OUTER_SYNC_HUB) not in sys.path:
    sys.path.insert(0, str(OUTER_SYNC_HUB))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')

application = get_wsgi_application()
