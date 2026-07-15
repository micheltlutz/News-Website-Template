# AGENTS.md — swift-server-ci

Skill para **CI/CD e deploy** de projetos Swift servidor (SPM, Vapor). Use para Docker, GitHub Actions e troubleshooting de build.

## Quando usar esta skill

- `Dockerfile`, `docker-compose.yml`, container deploy
- GitHub Actions, pipeline CI, `swift build` / `swift test` em runner
- Variáveis de ambiente de produção
- Healthcheck, migrations no deploy, falhas de build SPM

**Não use para apps iOS/macOS** — veja `../xcode-cloud/AGENTS.md`.

**ml-backoffice-api** é SPM + Docker — **nunca** Xcode Cloud neste repo.

## Setup commands

```bash
cp .env.example .env
DOCKER_BUILDKIT=1 docker compose up -d --build
docker compose ps
docker compose logs -f api
curl http://localhost:8080/health
curl "http://localhost:8080/health?db=1"
```

Local (sem Docker):

```bash
./run.sh
swift test
swift build -c release --product MLBackofficeAPI
```

## Dev environment tips

- Product SPM: `MLBackofficeAPI` (não `App`)
- Mac + Docker Desktop: rode `./scripts/db-tunnel.sh` e use `DATABASE_HOST_DOCKER=host.docker.internal` no `.env`
- PostgreSQL é **externo** ao compose — configure host/port/user/password
- Volumes SMB: montar no host **antes** de `docker compose up`
- Rede Docker `ml-backoffice` é compartilhada com `ml-backoffice-front`

## Deploy checklist

- [ ] `.env` com credenciais de produção (não commitado)
- [ ] SQL migrations aplicadas: `./database/run-migrations-ml-backoffice.sh`
- [ ] Fluent migrations rodam no boot via `autoMigrate()`
- [ ] `curl -fsS "http://localhost:8080/health?db=1"` retorna ok
- [ ] CORS restrito ao front em produção (ADR-004)
- [ ] `PRODUTOS_VOLUME_MOUNT` e `BACKUP_PRODUTOS_VOLUME_MOUNT` existem no host

## Testing instructions

```bash
swift package resolve
swift build -c release --product MLBackofficeAPI
swift test
docker build -t ml-backoffice-api:local .
```

- Em CI: alinhar versão Swift com `swift:6.1-noble` do Dockerfile
- Testes com DB: usar service PostgreSQL no workflow — ver `github-actions.md`
- Corrija falhas de build/test antes de merge

## Troubleshooting

| Sintoma | Ação |
|---------|------|
| Build local ok, CI falha | Alinhar Swift 6.1; limpar `.build` |
| Healthcheck unhealthy | `docker compose logs api`; checar DB |
| DB inacessível no Mac | `db-tunnel.sh` + `DATABASE_HOST_DOCKER` |
| `relation does not exist` | Rodar migrations SQL |
| OOM no docker build | Aumentar memória Docker; `DOCKER_BUILDKIT=1` |

Detalhes: `troubleshooting.md`

## Security

- Nunca commitar `.env` com secrets de produção
- GitHub Actions: usar `secrets.*` para `DATABASE_*`
- `DATABASE_PASSWORD` no container só para ambientes controlados
- Backup (`pg_dump`) expõe dados — restringir rede

## Referências nesta skill

| Arquivo | Uso |
|---------|-----|
| `SKILL.md` | Entry point, detecção SPM vs Xcode |
| `docker-patterns.md` | Dockerfile e docker-compose deste projeto |
| `github-actions.md` | Workflow CI sugerido |
| `troubleshooting.md` | Erros comuns SPM/Docker |

## Documentação oficial

- [Vapor Docker](https://docs.vapor.codes/deploy/docker/)
- Variáveis: `.env.example` na raiz do repo
