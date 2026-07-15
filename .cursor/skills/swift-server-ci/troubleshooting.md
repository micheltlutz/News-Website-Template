# Troubleshooting — Swift Server CI

## Swift Version Mismatch

**Symptom:** Build works locally, fails in CI or Docker.

**Fix:**
- Align Swift versions: `Package.swift` tools version, Docker `swift:6.1-noble`, CI `setup-swift`
- Run `./clean-run.sh` locally after Xcode/Swift upgrade
- Delete `.build` and `Package.resolved` conflicts

## SPM Resolve Failures

**Symptom:** `swift package resolve` hangs or fails.

**Fix:**
```bash
rm -rf .build
swift package reset
swift package resolve
```

In Docker: ensure `Package.resolved` is copied before full source for cache layer.

## Docker Build OOM

**Symptom:** `Killed` during `swift build -c release`.

**Fix:**
- Increase Docker memory (8 GB+ recommended for release builds)
- Use `DOCKER_BUILDKIT=1` for better caching
- Build on CI with larger runner if needed

## Container Starts but Healthcheck Fails

**Symptom:** `unhealthy` in `docker compose ps`.

**Checks:**
1. `docker compose logs api` — migration or DB connection errors?
2. `curl http://localhost:8080/health` — app listening?
3. Database reachable from container (Mac: `db-tunnel.sh` + `DATABASE_HOST_DOCKER`)
4. Increase `start_period` if migrations are slow

## Database Connection from Docker (Mac)

Docker Desktop cannot reach LAN IPs directly.

```bash
./scripts/db-tunnel.sh   # separate terminal
# .env:
DATABASE_HOST_DOCKER=host.docker.internal
DATABASE_PORT_DOCKER=15432
```

## Fluent Migration Errors on Boot

**Symptom:** App crashes on `autoMigrate()`.

**Fix:**
- Table/column must exist — run SQL migration first (ADR-002)
- Check migration order in `configure.swift`
- Verify Model `schema` matches actual table name

## Missing SQL Migration in Environment

**Symptom:** `relation "xxx" does not exist`.

**Fix:**
```bash
./database/run-migrations-ml-backoffice.sh
```

## Permission Errors on Volumes

**Symptom:** Cannot write to SMB mount in container.

**Fix:**
- Mount SMB on host before `docker compose up`
- Set `APP_UID`/`APP_GID` to match host user
- Check `PRODUTOS_VOLUME_MOUNT` path exists on host

## pg_dump / Backup Failures

**Symptom:** Backup endpoint fails in container.

**Checks:**
- `PG_DUMP_PATH=/usr/bin/pg_dump` (set in Dockerfile)
- `postgresql-client` installed in runtime image
- `DATABASE_PASSWORD` available in container env
- `BACKUP_EXPORT_TIMEOUT_SECONDS` sufficient for large DBs

## GitHub Actions Specific

| Issue | Solution |
|-------|----------|
| Cache stale | Bump cache key or clear Actions cache |
| Tests need DB | Add `services: postgres` job |
| Wrong product | Use `--product MLBackofficeAPI` |
| Long build times | Cache `.build` + separate resolve layer in Docker |

## Quick Diagnostic Commands

```bash
swift build -c release --product MLBackofficeAPI
swift test
docker compose logs -f api
curl -fsS "http://localhost:8080/health?db=1"
docker exec ml-backoffice-api ./MLBackofficeAPI routes
```
