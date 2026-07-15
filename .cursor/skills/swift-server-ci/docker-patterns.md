# Docker Patterns — ml-backoffice-api

Based on project `Dockerfile` and `docker-compose.yml`.

## Multi-Stage Dockerfile

### Build stage (`swift:6.1-noble`)

1. Install `libjemalloc-dev`
2. Copy `Package.swift` + `Package.resolved` → `swift package resolve` (cache layer)
3. Copy full source → `swift build -c release --product MLBackofficeAPI --static-swift-stdlib`
4. Stage binary + `.resources` bundles + `Public/` + `Resources/`

### Run stage (`ubuntu:noble`)

- Runtime: `libjemalloc2`, `curl`, `postgresql-client`, `tar`, `gzip`
- User: `vapor:vapor`, workdir `/app`
- `PG_DUMP_PATH=/usr/bin/pg_dump` for backups
- `EXPOSE 8080`
- `ENTRYPOINT ["./MLBackofficeAPI"]`
- `CMD ["serve", "--env", "production", "--hostname", "0.0.0.0", "--port", "8080"]`

## docker-compose.yml

```yaml
services:
  api:
    build: .
    env_file: .env
    ports:
      - "${API_PORT:-8080}:8080"
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:8080/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 60s
    networks:
      ml-backoffice:
        aliases: [api]
```

### Key settings

- **External PostgreSQL** — no db service in compose; configure via env
- **Network** `ml-backoffice` — shared with `ml-backoffice-front`
- **Volumes**: SMB mounts for produtos/backups, `api-sql-backups` for SQL dumps
- **Mac Docker Desktop**: run `./scripts/db-tunnel.sh`, set `DATABASE_HOST_DOCKER=host.docker.internal`

## Commands

```bash
# Build + start
DOCKER_BUILDKIT=1 docker compose up -d --build

# Status / logs
docker compose ps
docker compose logs -f api

# Stop
docker compose down

# Rebuild without cache
docker compose build --no-cache api
```

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness (compose healthcheck) |
| `GET /health?db=1` | PostgreSQL connectivity |

Use `?db=1` in staging/production validation after deploy.

## Production Checklist

- [ ] `.env` with production DB credentials (not committed)
- [ ] CORS restricted to front origin (ADR-004)
- [ ] SQL migrations applied (`database/run-migrations-ml-backoffice.sh`)
- [ ] SMB volumes mounted on host before compose up
- [ ] `APP_UID`/`APP_GID` match host for volume write access
- [ ] TLS termination at reverse proxy (nginx) if public

## Generic Vapor Docker Tips

- Cache SPM resolve layer separately from source copy
- Use `--static-swift-stdlib` for smaller runtime images
- Copy `Public/` read-only (`chmod -R a-w`)
- Set `SWIFT_BACKTRACE` env for crash reporting in production

See [Vapor Docker docs](https://docs.vapor.codes/deploy/docker/).
