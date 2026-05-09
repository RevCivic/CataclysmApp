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

If you add more published ports later, use separate purpose-based variables (for example `APP_HTTP_PORT`, `APP_METRICS_PORT`) instead of reusing one value.

Use Docker/Portainer secrets or a secure environment-variable source for credentials in production.
The container intentionally binds Gunicorn to `0.0.0.0:8000`; place it behind a reverse proxy/TLS termination in production.
Treat `DEFAULT_PASSWORD_UPDATE=true` as a privileged operation and restrict who can modify runtime environment variables.

## Download crew/species images from Google Sheets

Use the management command below to pull image URLs from the public crew spreadsheet tabs (`Main Crew` and `Other Crew`) and save them to matching `Person.image` and `Species.image` records:

```bash
cd cataclysm
python manage.py download_sheet_images --spreadsheet-id "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit?usp=sharing"
```

Useful options:

- `--tabs "Main Crew" "Other Crew"` (override tabs)
- `--person-url-col <index>` and `--species-url-col <index>` (use explicit URL columns)
- `--dry-run` (report without writing files)
- `--overwrite` (replace existing images)
- `--timeout <seconds>` (HTTP timeout per image download, default `10`)
- `--max-bytes <bytes>` (max bytes per image download, default `10485760`)

For security, downloads only support direct `http/https` image URLs and intentionally do **not** follow HTTP redirects to reduce SSRF-style redirect abuse.
