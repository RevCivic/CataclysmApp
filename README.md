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
  -e DEFAULT_PASSWORD=change-me \
  cataclysmapp:latest
```

### Environment variables

- `PORT`: Port Django binds to inside the container (default: `8000`)
- `DEFAULT_USERNAME`: Optional default admin username created/updated on startup
- `DEFAULT_PASSWORD`: Optional default admin password created/updated on startup
