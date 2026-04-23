# CataclysmApp
A Django app for a homebrew Starfinder TTRPG campaign.

## Purpose

CataclysmApp is a campaign catalog for a customized Starfinder setting.  
It documents the world timeline, custom rules, factions, people, worlds, events, ships, vehicles, gear, and other unique lore/items used in this homebrew game.

## Quick start with Docker Compose

Set environment variables first (recommended via a local `.env` file that is not committed):

```bash
cat > .env <<'EOF'
DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=CHANGE_ME_TO_STRONG_PASSWORD
EOF
```

Or export them in your shell before running compose.

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`.

## Run in Docker (Portainer-friendly)

Build:

```bash
docker build -t cataclysmapp:latest .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e PORT=8000 \
  -e DEFAULT_USERNAME=admin \
  -e DEFAULT_PASSWORD='YourSecurePasswordHere' \
  cataclysmapp:latest
```

### Environment variables

- `PORT`: Port Django binds to inside the container (default: `8000`)
- `GUNICORN_WORKERS`: Optional Gunicorn worker count (default: `3`)
- `GUNICORN_TIMEOUT`: Optional Gunicorn timeout seconds (default: `120`)
- `DEFAULT_USERNAME`: Optional default admin username created on startup
- `DEFAULT_PASSWORD`: Optional default admin password used when creating the default admin (must satisfy Django password validators: minimum length, non-common, non-numeric, etc.)
- `DEFAULT_PASSWORD_UPDATE`: Optional (`true`/`false`, default `false`); when exactly `true`, updates password for an existing `DEFAULT_USERNAME` only if that user is already staff + superuser

Use Docker/Portainer secrets or a secure environment-variable source for credentials in production.
`EXPOSE 8000` in the Dockerfile is informational; actual listen port is controlled by `PORT`.
The container intentionally binds Gunicorn to `0.0.0.0` so published container ports work; place it behind a reverse proxy/TLS termination in production.
Treat `DEFAULT_PASSWORD_UPDATE=true` as a privileged operation and restrict who can modify runtime environment variables.
