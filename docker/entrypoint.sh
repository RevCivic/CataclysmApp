#!/bin/sh
set -eu

cd /app/cataclysm

python manage.py migrate --noinput

if [ -n "${DEFAULT_USERNAME:-}" ] && [ -n "${DEFAULT_PASSWORD:-}" ]; then
python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

username = os.environ["DEFAULT_USERNAME"]
password = os.environ["DEFAULT_PASSWORD"]
update_existing = os.environ.get("DEFAULT_PASSWORD_UPDATE", "").lower() in {"1", "true", "yes", "on"}
User = get_user_model()

user, created = User.objects.get_or_create(username=username)
if created or update_existing:
    user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()
PY
fi

exec gunicorn cataclysm.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
