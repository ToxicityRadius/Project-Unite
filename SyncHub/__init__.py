import os

# Make the inner `SyncHub` package directory visible as part of this package's
# import search path. The project layout contains `SyncHub/SyncHub/` (outer
# folder containing inner package). Some hosting environments import
# `SyncHub.wsgi` from the repository root; adding the inner folder to
# `__path__` allows `import SyncHub.wsgi` to find the inner `wsgi.py`.
_inner_path = os.path.join(os.path.dirname(__file__), 'SyncHub')
if os.path.isdir(_inner_path):
    __path__.insert(0, _inner_path)
