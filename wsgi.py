"""Root-level WSGI shim for hosting platforms.

Some hosts run gunicorn from the repository root and struggle to import
the inner project package (e.g. `SyncHub.wsgi`). This shim ensures a
stable import path and delegates to the actual `SyncHub.wsgi.application`.
"""
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SyncHub.settings')

try:
    # Delegate to the real WSGI application
    from SyncHub.wsgi import application
except Exception:
    # If import fails, re-raise with context
    raise
