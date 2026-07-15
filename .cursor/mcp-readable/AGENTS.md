# AGENTS.md — MlHub API

Instructions for AI agents (Cursor, Claude, GPT, etc.) consuming the **MlHub** REST API.

## What this API is

MlHub exposes CRUD over data exported from **ML Terminal Snippets**: skill git repositories, project templates, snippet categories, terminal command snippets, SSH connection presets, **crash tracking** (reports, diagnoses, fix strategies, postmortems), and **activity management** (daily logs and tasks) linked to projects.

**Authentication:** none in v1. Do not assume API keys or Bearer tokens.

## How to discover the API

Recommended order:

1. `GET /health?db=1` — confirm the service and database are reachable
2. `GET /openapi.yaml` — full OpenAPI 3 spec (paths, schemas, operationIds, examples)
3. `GET /llms.txt` — compact index (this repo also has `llms.txt` at the root)
4. Read `docs/api.md` for human-oriented curl examples and domain context

## Base URLs

| Environment | URL |
|---|---|
| Local dev | `http://localhost:8080` |
| Docker Compose | `http://localhost:4141` (via `API_PORT` in `.env`) |

## Resource map

| Prefix | Entity | Notes |
|---|---|---|
| `/api/repositories` | Skill git repo | `slug` unique → 409; DELETE blocked if skills or MCP servers exist → 409 |
| `/api/skills` | Cursor Agent Skill | Requires `repositoryId`; `repositorySlug`/`gitURL` read-only |
| `/api/mcp-servers` | Cursor MCP server preset | Requires `repositoryId`; `repositorySlug`/`gitURL` read-only |
| `/api/projects` | Project template | `selectedSkillSlugs` replaced on PUT; DELETE blocked if crash reports, activity logs, or tasks exist → 409 |
| `/api/crash-reports` | App crash report | Requires `projectId`; `projectName` read-only; optional `?projectId=` filter |
| `/api/crash-reports/import` | Crashlytics import | Upsert by `(source=crashlytics, externalId)` |
| `/api/crash-reports/{id}/detail` | Crash workflow aggregate | Report + diagnoses + fix strategy + postmortem |
| `/api/crash-diagnoses` | Crash diagnosis | Requires `crashReportId`; advances status to `diagnosed` |
| `/api/crash-fix-strategies` | Fix strategy | 1:1 per report → 409 on duplicate |
| `/api/crash-postmortems` | Postmortem doc | 1:1 per report; `publishedAt` → status `postmortem_published` |
| `/api/activity-logs` | Daily activity log | Requires `projectId`; `projectName` read-only; optional `?projectId=`, `?logDate=` |
| `/api/activity-logs/{id}/detail` | Activity aggregate | Log + tasks array |
| `/api/activity-tasks` | Activity task | Requires `projectId` + `activityLogId`; optional `?projectId=`, `?activityLogId=`, `?status=`, `?category=` |
| `/api/snippet-categories` | Snippet category | DELETE blocked if snippets exist → 409 |
| `/api/terminal-snippets` | Terminal command | `categoryName` read-only in responses |
| `/api/ssh-connections` | SSH preset | Stores display path, not private key content |
| `/health` | Health | `?db=1` pings PostgreSQL |

Standard CRUD per resource:

- `GET /api/{resource}` — list
- `POST /api/{resource}` — create (body = `Create*` schema in OpenAPI)
- `GET /api/{resource}/{id}` — get by UUID
- `PUT /api/{resource}/{id}` — update (body = `Update*` schema)
- `DELETE /api/{resource}/{id}` — delete → **204 No Content**

## JSON rules

- **camelCase** property names in request and response bodies
- **UUID** strings for `id` path parameters and foreign keys
- **ISO8601** date-time strings for `createdAt` / `updatedAt`
- Do **not** send `categoryName` when creating/updating snippets (server-derived)
- Do **not** send `repositorySlug` or `gitURL` when creating/updating skills or MCP servers (server-derived)
- Do **not** send `id` in POST bodies (server assigns)

## HTTP errors

| Code | When |
|---|---|
| 400 | Validation failed, invalid UUID in path, unknown FK, activity log/project mismatch on task create |
| 404 | Resource not found |
| 409 | Duplicate repository `slug`; delete category with snippets; delete repository with skills or MCP servers; delete project with crash reports, activity logs, or tasks; duplicate fix strategy or postmortem for same crash report; duplicate activity task `externalId` for same project |
| 204 | Successful DELETE (empty body) |

Error body (Vapor):

```json
{
  "reason": "Category has terminal snippets",
  "error": true
}
```

## Minimal examples

List snippets:

```http
GET /api/terminal-snippets HTTP/1.1
Host: localhost:8080
```

Create category:

```http
POST /api/snippet-categories HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "name": "Docker",
  "notes": "Container commands",
  "sortOrder": 0,
  "systemImage": "shippingbox"
}
```

Create repository (check slug uniqueness first via GET):

```http
POST /api/repositories HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "slug": "server-side-swift",
  "name": "Server-side Swift",
  "gitURL": "https://github.com/example/skills.git",
  "isBuiltIn": false,
  "notes": "",
  "skillFolderName": "server-side-swift"
}
```

Create skill (repository must exist first — use `id` from GET/POST repositories):

```http
POST /api/skills HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "repositoryId": "550e8400-e29b-41d4-a716-446655440000",
  "name": "server-side-swift",
  "description": "Vapor and Fluent patterns",
  "localFolderPath": "/Users/me/skills/server-side-swift",
  "invocationExample": "Load when building Vapor backends",
  "cursorRulePath": ".cursor/rules/server-side-swift.mdc",
  "cursorRuleContent": ""
}
```

Create MCP server (repository must exist first — use `id` from GET/POST repositories):

```http
POST /api/mcp-servers HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "repositoryId": "550e8400-e29b-41d4-a716-446655440000",
  "name": "mlhub",
  "description": "Docs-only MCP for MlHub API",
  "localFolderPath": "/Users/me/ml-hub-mcp",
  "invocationExample": "List /api/terminal-snippets methods via MCP",
  "cursorMcpConfig": "{\n  \"mcpServers\": {\n    \"mlhub\": {\n      \"command\": \"node\",\n      \"args\": [\"/Users/me/ml-hub-mcp/dist/server.js\"]\n    }\n  }\n}"
}
```

## Crash incident workflow

Human-readable template: [docs/templates/crash-incident-workflow.md](docs/templates/crash-incident-workflow.md)

Typical agent flow:

1. `GET /health?db=1` → `GET /api/projects` (resolve `projectId` by name)
2. `POST /api/crash-reports` (manual) or `POST /api/crash-reports/import` (Crashlytics)
3. `POST /api/crash-diagnoses` → `POST /api/crash-fix-strategies` → `POST /api/crash-postmortems`
4. `GET /api/crash-reports/{id}/detail` — return full context to the user

Import example:

```http
POST /api/crash-reports/import HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "externalId": "firebase-issue-id",
  "title": "EXC_BAD_ACCESS in ViewModel.load",
  "stackTrace": "Thread 0 Crashed:\n0  MyApp  0x1234",
  "appVersion": "2.1.0",
  "buildNumber": "142",
  "severity": "high",
  "occurredAt": "2026-06-28T14:30:00Z",
  "rawPayload": "{\"issue\":{}}",
  "notes": "From Crashlytics"
}
```

Prompt to paste in Cursor when registering from a filled incident file:

```text
Leia o arquivo de incidente anexo e registre no MlHub:
1. Siga docs/templates/crash-incident-workflow.md
2. Use GET /openapi.yaml para validar schemas
3. Base URL: http://localhost:8080
4. Ao final, mostre GET /api/crash-reports/{id}/detail
```

## Activity management workflow

Schema origin: [docs/template_schemas/schema.json](docs/template_schemas/schema.json)

Typical agent flow:

1. `GET /health?db=1` → `GET /api/projects` (resolve `projectId` by name)
2. `POST /api/activity-logs` (daily log with `logDate`, `startTime`, `endTime`)
3. `POST /api/activity-tasks` (one or more tasks linked to the log)
4. `GET /api/activity-logs/{id}/detail` — return full context to the user

Create activity log example:

```http
POST /api/activity-logs HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "logDate": "2026-07-03",
  "startTime": "09:00",
  "endTime": "12:30",
  "summary": "Manhã de desenvolvimento"
}
```

Create activity task example:

```http
POST /api/activity-tasks HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "projectId": "550e8400-e29b-41d4-a716-446655440000",
  "activityLogId": "660e8400-e29b-41d4-a716-446655440001",
  "externalId": "2026-07-03-01",
  "title": "Implementar feature X",
  "category": "desenvolvimento",
  "status": "concluido",
  "references": ["docs/feature.md"],
  "notes": "PR #42"
}
```

## What agents should avoid

- Inventing fields not present in OpenAPI `Create*` / `Update*` schemas
- Using snake_case in JSON bodies
- Assuming pagination (lists return full arrays)
- Assuming authentication headers
- Sending `projectName` when creating/updating crash reports or activity logs (server-derived)
- Deleting snippet categories without checking for child snippets
- Deleting projects without checking for crash reports, activity logs, or tasks
- Creating activity tasks where `activityLogId` belongs to a different `projectId`

## Domain relationships

See [docs/adr/005-dominio-terminal-snippets.md](docs/adr/005-dominio-terminal-snippets.md):

- `projects` ↔ `project_skill_slugs` ↔ `repositories` (by slug)
- `skills` → `repositories` (required FK)
- `mcp_servers` → `repositories` (required FK)
- `terminal_snippets` → `snippet_categories` (required FK)
- `crash_reports` → `projects` (required FK)
- `crash_diagnoses` → `crash_reports` (cascade delete)
- `crash_fix_strategies` / `crash_postmortems` → `crash_reports` (1:1, cascade delete)
- `activity_logs` → `projects` (required FK)
- `activity_tasks` → `projects` + `activity_logs` (cascade delete with log)
- `ssh_connections` is independent

See also [docs/adr/008-dominio-skills-cursor.md](docs/adr/008-dominio-skills-cursor.md), [docs/adr/009-dominio-mcp-servers-cursor.md](docs/adr/009-dominio-mcp-servers-cursor.md), [docs/adr/010-dominio-crash-tracking.md](docs/adr/010-dominio-crash-tracking.md), and [docs/adr/011-dominio-gestao-atividades.md](docs/adr/011-dominio-gestao-atividades.md).

## References

- [docs/openapi.yaml](docs/openapi.yaml) — source of truth for schemas
- [docs/api.md](docs/api.md) — usage guide with curl
- [docs/adr/](docs/adr/) — architecture decisions
- [llms.txt](llms.txt) — compact discovery index
