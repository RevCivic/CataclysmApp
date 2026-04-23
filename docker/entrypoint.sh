#!/bin/bash
set -euo pipefail

cd /app/cataclysm

python manage.py migrate --noinput

if [ -n "${DEFAULT_USERNAME:-}" ] && [ -n "${DEFAULT_PASSWORD:-}" ]; then
python manage.py shell <<'PY'
import os
import sys
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

username = os.environ["DEFAULT_USERNAME"]
password = os.environ["DEFAULT_PASSWORD"]
update_existing = os.environ.get("DEFAULT_PASSWORD_UPDATE", "").lower() in {"1", "true", "yes", "on"}
User = get_user_model()
candidate_user = User(username=username)

try:
    validate_password(password, user=candidate_user)
except ValidationError as exc:
    print(f"DEFAULT_PASSWORD failed Django password validation: {'; '.join(exc.messages)}", file=sys.stderr)
    sys.exit(1)

user, created = User.objects.get_or_create(username=username)
if created or update_existing:
    user.set_password(password)
if created:
    user.is_staff = True
    user.is_superuser = True
user.save()
PY
fi

exec gunicorn cataclysm.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"
