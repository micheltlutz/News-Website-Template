---
name: swift-server-ci
description: CI/CD and deployment for Swift server projects (SPM, Vapor, Hummingbird). Covers Docker, docker-compose, GitHub Actions, environment variables, and production deploy. Use when configuring CI, Docker, GitHub Actions, deploy, or troubleshooting Swift SPM builds in pipelines. Not for iOS/macOS apps — use xcode-cloud instead.
---

# Swift Server CI/CD

CI/CD and deployment for **SPM-based server projects** (Vapor, Hummingbird). No `.xcodeproj` required.

## When This Skill Activates

- Docker, docker-compose, container deploy
- GitHub Actions, CI pipeline, automated tests
- Fly.io, Railway, production server setup
- SPM build failures in CI
- Environment variables for server deploy

## Early Detection

```
Glob: **/*.xcodeproj, **/*.xcworkspace, **/Package.swift, **/Dockerfile
```

| Project type | Skill |
|--------------|-------|
| SPM + Dockerfile (this repo) | **swift-server-ci** |
| `.xcodeproj` / iOS app | **xcode-cloud** |

**ml-backoffice-api** uses Docker — never Xcode Cloud.

## ml-backoffice-api Quick Start

```bash
cp .env.example .env
DOCKER_BUILDKIT=1 docker compose up -d --build
docker compose logs -f api
curl http://localhost:8080/health
curl "http://localhost:8080/health?db=1"
```

Local dev: `./run.sh` or `swift test`

## Workflow

1. Detect project type (SPM vs Xcode)
2. Read existing `Dockerfile`, `docker-compose.yml`, `.env.example`
3. For CI: read `github-actions.md`
4. For Docker details: read `docker-patterns.md`
5. On failures: read `troubleshooting.md`

## Migrations at Deploy

| Type | Location | When applied |
|------|----------|--------------|
| SQL | `database/migrations/` | Manual script or deploy step |
| Fluent | `Sources/.../Migrations/` | `autoMigrate()` on app boot |

Deploy checklist:
- [ ] Run pending SQL migrations before or during deploy
- [ ] Fluent migrations apply on container start
- [ ] Verify `/health?db=1` after deploy

## Environment Variables

From `.env.example`:

- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`
- `DATABASE_HOST_DOCKER`, `DATABASE_PORT_DOCKER` (Mac + `./scripts/db-tunnel.sh`)
- `PORT`, `LOG_LEVEL`, `MAX_UPLOAD_BYTES`
- `PRODUTOS_VOLUME_MOUNT`, `BACKUP_PRODUTOS_VOLUME_MOUNT` (Docker volumes)

Never commit `.env` with production secrets.

## References

- **docker-patterns.md** — Dockerfile, docker-compose, healthcheck
- **github-actions.md** — CI workflow templates
- **troubleshooting.md** — SPM/CI common errors
- [Vapor Docker](https://docs.vapor.codes/deploy/docker/)
- `skills/server-side-swift/deployment-patterns.md` — generic Fly.io/Railway
