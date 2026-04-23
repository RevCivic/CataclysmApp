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
User = get_user_model()

user, _ = User.objects.get_or_create(username=username)
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.save()
PY
fi

exec python manage.py runserver "0.0.0.0:${PORT:-8000}"
