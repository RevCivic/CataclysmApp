# CataclysmApp
A Django app for a homebrew Starfinder TTRPG campaign.

## Purpose

CataclysmApp is a campaign catalog for a customized Starfinder setting.  
It documents the world timeline, custom rules, factions, people, worlds, events, ships, vehicles, gear, and other unique lore/items used in this homebrew game.

## Quick start with Docker Compose

Set environment variables first (recommended via a local `.env` file that is not committed):

```bash
cat > .env <<'EOF'
DEFAULT_USERNAME=your_username
DEFAULT_PASSWORD=***REPLACE-WITH-SECURE-PASSWORD***
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
```

Or export them in your shell before running compose.

Never commit real credentials. For production, prefer Docker/Portainer secrets or another secure secret-management system.

```bash
docker compose up --build
```

The app will be available at `http://localhost:${PORT:-8000}`.

## Run in Docker (Portainer-friendly)

Build:

```bash
docker build -t cataclysmapp:latest .
```

Run:

```bash
docker run --rm -p 8080:8000 \
  -e DEFAULT_USERNAME=admin \
  -e DEFAULT_PASSWORD='YourSecurePasswordHere' \
  cataclysmapp:latest
```

### Environment variables

- `PORT`: Host port published by Docker Compose (default: `8000`). The container always listens on port `8000`.
- `GUNICORN_WORKERS`: Optional Gunicorn worker count (default: `3`)
- `GUNICORN_TIMEOUT`: Optional Gunicorn timeout seconds (default: `120`)
- `DEFAULT_USERNAME`: Optional default admin username created on startup
- `DEFAULT_PASSWORD`: Optional default admin password used when creating the default admin (must satisfy Django password validators: minimum length, non-common, non-numeric, etc.)
- `DEFAULT_PASSWORD_UPDATE`: Optional (`true`/`false`, default `false`); when exactly `true`, updates password for an existing `DEFAULT_USERNAME` only if that user is already staff + superuser
- `ALLOWED_HOSTS`: Comma-separated Django allowed hosts list (default: `localhost,127.0.0.1,[::1]`; for example `localhost,127.0.0.1,app.example.com`)
- `EMAIL_ADDRESS`: Gmail address used as the SMTP sender for password-reset emails (for example `yourname@gmail.com`)
- `EMAIL_APP_PASSWORD`: [Gmail App Password](https://support.google.com/accounts/answer/185833) for the above address. Both `EMAIL_ADDRESS` **and** `EMAIL_APP_PASSWORD` must be set to enable live email delivery; when either is absent the console backend is used (emails are printed to stdout only).

If you add more published ports later, use separate purpose-based variables (for example `APP_HTTP_PORT`, `APP_METRICS_PORT`) instead of reusing one value.

Use Docker/Portainer secrets or a secure environment-variable source for credentials in production.
The container intentionally binds Gunicorn to `0.0.0.0:8000`; place it behind a reverse proxy/TLS termination in production.
Treat `DEFAULT_PASSWORD_UPDATE=true` as a privileged operation and restrict who can modify runtime environment variables.

### Password reset

Users can reset their password at `/accounts/password_reset/`. The link is also accessible from the sidebar navigation when not logged in.

Reset tokens expire after **24 hours** and can only be used **once**.

The response to a reset request is intentionally identical whether or not the email address belongs to an existing account, to prevent account enumeration.

#### Gmail App Password setup

1. Enable 2-Step Verification on the Gmail account you want to use as the sender.
2. Go to **Google Account → Security → App passwords**, generate a new app password (select "Mail" / "Other").
3. Set `EMAIL_ADDRESS=yourname@gmail.com` and `EMAIL_APP_PASSWORD=<generated-password>` in your environment or `.env` file.

#### Admin runbook

**Test email delivery** (without restarting):

```bash
cd cataclysm
python manage.py shell -c "
from django.core.mail import send_mail
send_mail('Test', 'Works!', None, ['you@example.com'])
"
```

**Recover a locked-out admin** (no email required):

```bash
cd cataclysm
python manage.py changepassword <username>
```

**Troubleshoot email issues:**

- Confirm `EMAIL_ADDRESS` and `EMAIL_APP_PASSWORD` are set in the running container environment.
- Check that Gmail 2-Step Verification is enabled and the App Password is correct.
- Verify `ALLOWED_HOSTS` includes the domain used in reset links so links in emails are correct.
- For SMTP connection errors, confirm port 587 is not blocked by the host firewall or container networking.
- If reset links arrive with `localhost` or the wrong host, place the app behind a reverse proxy that sets the `Host` header correctly, or use `CSRF_TRUSTED_ORIGINS` / `USE_X_FORWARDED_HOST` as appropriate.

#### Rate limiting

Django does not include built-in rate limiting for the password reset endpoint. It is strongly recommended to configure rate limiting at the reverse-proxy level (for example nginx `limit_req`) to prevent abuse.

## Download crew/species images from Google Sheets

Use the management command below to pull image URLs from the public crew spreadsheet tabs (`Main Crew` and `Other Crew`) and save them to matching `Person.image` and `Species.image` records. The command also stores the source URL in `Person.image_source_url` / `Species.image_source_url` and supports common Google Drive share-link formats:

```bash
cd cataclysm
python manage.py download_sheet_images --spreadsheet-id "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit?usp=sharing"
```

`download_sheet_images` reads sheet cells via the Google Sheets v4 grid-data endpoint so hyperlink URLs embedded in cells are preserved. Set `GOOGLE_API_KEY` if your environment requires an API key for `sheets.googleapis.com`.

Useful options:

- `--tabs "Main Crew" "Other Crew"` (override tabs)
- `--person-url-col <index>` and `--species-url-col <index>` (use explicit URL columns)
- `--dry-run` (report without writing files)
- `--overwrite` (replace existing images)
- `--timeout <seconds>` (HTTP timeout per image download, default `10`)
- `--max-bytes <bytes>` (max bytes per image download, default `10485760`)

Without `--overwrite`, images are skipped only when the stored `image_source_url` already matches the current sheet URL; if the sheet URL changed, the image is refreshed.

For security, downloads only support direct `http/https` image URLs and intentionally do **not** follow HTTP redirects to reduce SSRF-style redirect abuse.

## Preview or import crew data from Google Sheets

The schema-driven crew importer understands the different layouts of the
`Main Crew` and `Other Crew` tabs. It is read-only by default:

```bash
cd cataclysm
python manage.py import_crew_workbook \
  --spreadsheet-id "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit" \
  --tabs "Main Crew" "Other Crew"
```

Review the created/updated/unresolved counts and warnings. To write the parsed
records and their source-row provenance, rerun with the explicit `--apply`
flag. A JSON report can be produced in either mode:

```bash
python manage.py import_crew_workbook \
  --spreadsheet-id "$SPREADSHEET_ID" \
  --tabs "Main Crew" "Other Crew" \
  --report-json /tmp/crew-import-report.json \
  --apply
```

Imports preserve qualified/unknown ages as text, use separate trait maps for
the two tabs, retain raw row values, and reuse source-row bindings on later
runs. Applying an unchanged row is a no-op. Ambiguous duplicate names are
reported as unresolved rather than guessed. Existing manually curated traits
are not removed by an import.

The People index can search imported aliases, species, roles, organizations,
and profile facts. Its advanced filters support species, traits, capabilities,
organizations, status, rank, role, and location/origin. Repeating trait or
capability selections uses **match all** semantics, and all filter state remains
in the URL so filtered directories can be bookmarked or shared.

Authenticated users can save the current filter set as a private or shared
named view from the People index. Shared views are readable by anyone with
access to the app; private views are restricted to their owner. The same panel
exports the filtered results as CSV. CSV values that spreadsheet applications
could interpret as formulas are escaped before download.
