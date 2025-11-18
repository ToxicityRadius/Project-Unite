**Project Unite (SyncHub)**

Project Unite (a.k.a. SyncHub) is a Django-based web app for officer attendance logging and inventory tracking. It includes an inventory management UI, RFID-enabled login/time-logging, and admin pages. This repo is configured for hosting on Render with WhiteNoise static serving.

**Key Features**
- **Inventory management**: Add/edit/delete items, batch delete, CSV/reporting support.
- **RFID login / time logs**: Officer authentication and time reports.
- **Responsive UI**: Built with Poppins font and adaptive layout.
- **Deployment-ready**: `Procfile`, `wsgi` shims, and `requirements.txt` prepared for Render (Gunicorn + WhiteNoise).

**Tech Stack**
- **Framework**: Django 5.x
- **DB**: PostgreSQL (production; repo uses `dj-database-url` and reads `DATABASE_URL`)
- **WSGI**: Gunicorn
- **Static files**: WhiteNoise (serves `/static/` in production)
- **Storage**: Optional S3-compatible backend via `django-storages` + `boto3`

**Quick-start (local development)**
1. Clone the repo:
   ```bash
   git clone https://github.com/ToxicityRadius/Project-Unite.git
   cd Project-Unite
   ```
2. Create & activate a virtualenv (Windows PowerShell example):
   ```powershell
   python -m venv .venv
   & .\.venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Create environment variables (recommended: copy `.env.example` -> `.env` or set in your shell):
   - `SECRET_KEY` (required in production)
   - `DEBUG` (0 or 1)
   - `ALLOWED_HOSTS` (comma-separated)
   - `DATABASE_URL` (Postgres connection)
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (for email features)
   - Optional S3 vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`

4. Run migrations & collect static:
   ```powershell
   & .\.venv\Scripts\python.exe SyncHub\manage.py migrate
   & .\.venv\Scripts\python.exe SyncHub\manage.py collectstatic --noinput
   ```

5. Start dev server:
   ```powershell
   & .\.venv\Scripts\python.exe SyncHub\manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/`.

**Deploying to Render (or similar)**
- Render build command typically: `pip install -r requirements.txt && cd SyncHub && python manage.py collectstatic --noinput`
- Start command (Procfile): `web: gunicorn wsgi:application --bind 0.0.0.0:$PORT`
- Ensure Render environment variables include `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS` and any AWS or email credentials. Render runs `collectstatic` during build — WhiteNoise and `STATIC_ROOT` must be configured (this repo includes those settings).

**Static files notes & common issues**
- Always set `STATIC_URL = '/static/'` (leading slash). Relative `static/` can break routes like `/inventory`.
- WhiteNoise middleware must be in `MIDDLEWARE` (just after `SecurityMiddleware`) and `STATICFILES_STORAGE` set to `whitenoise.storage.CompressedManifestStaticFilesStorage` for hashed file names.
- If you see `collectstatic` warnings about duplicate destination paths, check for duplicate files under `static/` and `app/static/`. Canonical pattern: app-level static should live in `yourapp/static/yourapp/...` and shared assets under repository `static/` folders included in `STATICFILES_DIRS`.

**Database & secrets**
- The project uses `dj-database-url` to convert `DATABASE_URL` to Django `DATABASES`.
- DO NOT commit secrets. Rotate any credentials accidentally committed and set them in your host's environment variables.

**Troubleshooting**
- Error: `ModuleNotFoundError: No module named 'whitenoise'` → install with `pip install whitenoise` and ensure `requirements.txt` includes it.
- Static 404s on production → verify `collectstatic` ran successfully and that `STATIC_URL` is absolute (`/static/`). Use an incognito window to rule out caching.
- App import errors on deploy (e.g. `ModuleNotFoundError: No module named 'inventory'`) → ensure your WSGI entrypoint runs from project root or adjust `sys.path` in `wsgi.py`. This repo contains a root-level `wsgi.py` shim to handle common path problems.

**Developer notes**
- Main Django project lives in `SyncHub/SyncHub/`.
- Apps: `inventory`, `rfid_login`, and `SyncHub` (custom user model in `SyncHub.models`).
- Static assets for the inventory app are under `SyncHub/inventory/static/inventory/`.

**Contributing**
- Open issues or PRs on GitHub. Keep changes small and run `python manage.py test` where applicable.

**License**
- See `LICENSE` in the repository root.

# PROJECT-UNITE
