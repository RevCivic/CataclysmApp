# CataclysmApp
A Django Project with a Postgres Data structure for a homebrew starfinder campaign

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
- `DEFAULT_PASSWORD_UPDATE`: Optional (`true`/`false`, default `false`); when exactly `true`, updates password for an existing `DEFAULT_USERNAME` (existing staff/superuser flags are preserved)

Use Docker/Portainer secrets or a secure environment-variable source for credentials in production.
`EXPOSE 8000` in the Dockerfile is informational; actual listen port is controlled by `PORT`.
The container intentionally binds Gunicorn to `0.0.0.0` so published container ports work; place it behind a reverse proxy/TLS termination in production.
Treat `DEFAULT_PASSWORD_UPDATE=true` as a privileged operation and restrict who can modify runtime environment variables.
