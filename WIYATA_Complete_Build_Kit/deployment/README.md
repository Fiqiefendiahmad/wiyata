# Deployment Starter

## Important

The supplied Compose file starts only the platform PostgreSQL database and Redis. It does not yet deploy a completed WIYATA frontend, backend, or sandbox worker. Those services must be implemented and given Dockerfiles.

## Local setup

1. Install Docker Engine or Docker Desktop.
2. Copy `.env.example` to `.env`.
3. Change all passwords and secrets.
4. Start dependencies:

```bash
docker compose --env-file .env -f docker-compose.yml up -d
```

5. Verify:

```bash
docker compose -f docker-compose.yml ps
```

6. Apply platform database migrations after the backend exists.

## Production requirements

- Do not publish database ports to the public internet.
- Use managed secrets or an encrypted secret store.
- Configure TLS at the reverse proxy.
- Configure backups and test restores.
- Add health checks and resource limits.
- Use non-root containers.
- Use private networks for sandbox workers.
- Restrict sandbox egress.
- Scan images and dependencies.
- Configure logs and alerting without logging secrets.
- Define retention and deletion policies.
