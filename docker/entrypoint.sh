#!/bin/bash
set -euo pipefail

cd /app/cataclysm

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "${DEFAULT_USERNAME:-}" ] && [ -n "${DEFAULT_PASSWORD:-}" ]; then
python manage.py shell <<'PY'
import os
import sys
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

username = os.environ["DEFAULT_USERNAME"]
password = os.environ["DEFAULT_PASSWORD"]
should_update_password = os.environ.get("DEFAULT_PASSWORD_UPDATE", "").lower() == "true"
User = get_user_model()
validation_user = User(username=username)

try:
    validate_password(password, user=validation_user)
except ValidationError:
    print("DEFAULT_PASSWORD does not meet security requirements. See README for password guidance.", file=sys.stderr)
    sys.exit(1)

user, created = User.objects.get_or_create(username=username)
if created:
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
elif should_update_password:
    if not (user.is_staff and user.is_superuser):
        print("DEFAULT_PASSWORD_UPDATE can only target an existing admin user.", file=sys.stderr)
        sys.exit(1)
    print("Updating password for existing default admin user due to DEFAULT_PASSWORD_UPDATE=true", file=sys.stderr)
    user.set_password(password)
user.save()
PY
fi

exec gunicorn cataclysm.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
