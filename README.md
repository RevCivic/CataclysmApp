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
  -e DEFAULT_PASSWORD='Use-A-Strong-Secret-Here' \
  cataclysmapp:latest
```

### Environment variables

- `PORT`: Port Django binds to inside the container (default: `8000`)
- `DEFAULT_USERNAME`: Optional default admin username created on startup
- `DEFAULT_PASSWORD`: Optional default admin password used when creating the default admin
- `DEFAULT_PASSWORD_UPDATE`: Optional (`true`/`false`, default `false`); when `true`, updates password for an existing `DEFAULT_USERNAME`

Use Docker/Portainer secrets or a secure environment-variable source for credentials in production.
