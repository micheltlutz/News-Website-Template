# ml-backoffice-api — Project Patterns

Convenções específicas deste repositório. Leia antes de criar ou alterar código.

## Stack

- Vapor 4.115+, Fluent, FluentPostgresDriver, Swift 6
- Target: `MLBackofficeAPI` (não `App`)
- PostgreSQL `ml-backoffice` (compartilhado com backend Python)
- Front: `ml-backoffice-front` (Next.js)

## Directory Map

```
Sources/MLBackofficeAPI/
├── entrypoint.swift          # @main, Application.make
├── configure.swift           # DB, CORS, JSON dates, autoMigrate
├── routes.swift              # app.register(collection:)
├── Controllers/              # RouteCollection por recurso
├── DTOs/                     # Content, camelCase, toDTO/toModel
├── Infrastructure/Database/
│   ├── Models/               # Fluent models (schema = tabela)
│   └── Repositories/         # protocol Sendable + Database*
├── Migrations/               # Fluent AsyncMigration (subset do schema)
├── Application/Services/     # ProdutoService, OrcamentoService, FileService
├── Services/                 # OrcamentoPricingService, ProdutoCustoService (puro)
└── Infrastructure/FileStorage/

database/migrations/          # SQL NNN_descricao.sql (schema principal)
docs/adr/                     # ADR-001 a ADR-004
```

## Architecture (ADR-003)

**Controller → Repository → Model** com **DTO** na borda.

### Canonical CRUD example

Copy from `FilamentoController`, `FilamentoDTO`, `DatabaseFilamentoRepository`, `Filamento` model.

```swift
// Controller
struct FilamentoController: RouteCollection {
    func boot(routes: any RoutesBuilder) throws {
        let filamentos = routes.grouped("api", "filamentos")
        filamentos.get(use: index)
        filamentos.post(use: create)
        filamentos.get(":id", use: getById)
        filamentos.put(":id", use: update)
        filamentos.delete(":id", use: delete)
    }

    @Sendable func index(req: Request) async throws -> [FilamentoDTO] {
        let repo = DatabaseFilamentoRepository()
        return try await repo.all(on: req.db).map { $0.toDTO() }
    }
    // ...
}
```

### When to add a Service

- Multi-repository orchestration → `Application/Services/` (ex.: `ProdutoController` → `ProdutoService`)
- Pure calculations, no DB → `Services/` (ex.: `OrcamentoPricingService`)
- Simple CRUD → controller calls repository directly (acceptable)

## REST Conventions

| Action | Method | Route | Response |
|--------|--------|-------|----------|
| List | GET | `api/<recurso>` | `[DTO]` |
| Get | GET | `api/<recurso>/:id` | `DTO` or 404 |
| Create | POST | `api/<recurso>` | `DTO` |
| Update | PUT | `api/<recurso>/:id` | `DTO` |
| Delete | DELETE | `api/<recurso>/:id` | 204 |

- IDs: `UUID` via `req.parameters.get("id", as: UUID.self)`
- JSON API: **camelCase**; database columns: **snake_case** (`@Field(key: "custo_por_kg")`)
- Errors: `Abort(.badRequest, reason:)`, `Abort(.notFound)`, `Abort(.conflict)`

## Route Registration Order

In `routes.swift`, register **more specific routes first**:

```swift
try app.register(collection: ProdutoAcessorioController())  // /api/produtos/:id/acessorios
try app.register(collection: ProdutoCategoriaController())    // /api/produtos/categorias
try app.register(collection: ProdutoController())           // /api/produtos/:id
```

Health check: `GET /health` and `GET /health?db=1` (PostgreSQL ping for Docker).

## Migrations (ADR-002)

### Decision checklist

| Change | Where |
|--------|-------|
| New core table (clientes, produtos, etc.) | `database/migrations/NNN_*.sql` |
| Column on existing core table | SQL migration |
| Table owned only by API (volumes, todos) | Fluent `AsyncMigration` |
| API-only column on existing table | Fluent migration (if SQL not yet run) |

### SQL migration template

```sql
-- ============================================================================
-- Migration: NNN_descricao.sql
-- Descrição: ...
-- ============================================================================

CREATE TABLE IF NOT EXISTS ...;
ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...;
CREATE INDEX IF NOT EXISTS ...;
```

Apply: `./database/run-migrations-ml-backoffice.sh`

### Fluent migration

1. Create struct in `Sources/MLBackofficeAPI/Migrations/`
2. Register in `configure.swift`: `app.migrations.add(...)`
3. Runs via `autoMigrate()` on boot

**Rule:** table must exist before Fluent Model references it.

## JSON and Dates (`configure.swift`)

- Output: ISO8601
- Input: ISO8601 or `yyyy-MM-dd`
- Empty string for date → rejected (omit key for optional)
- `Decimal` for prices/weights

## Security (ADR-004)

- CORS: `.all` in dev; restrict in production
- Credentials via env: `DATABASE_URL` or `DATABASE_HOST/USERNAME/PASSWORD/NAME`
- `PORT`, `MAX_UPLOAD_BYTES` (default 10 MB)
- No auth yet — endpoints open on network
- Never commit production secrets

## Domain Context

- 3D printing business: produtos, filamentos, impressoras, embalagens, orçamentos
- E-commerce: Nuvemshop CSV (`templates_ecommerce/`)
- Backup: `BackupController` (pg_dump, SMB volumes)
- File uploads: `FileController`, `LocalFileStorage`, `Public/`

## Anti-Patterns

- ❌ Scaffold `Sources/App/` — use `Sources/MLBackofficeAPI/`
- ❌ New models in `Models/Todo.swift` — use `Infrastructure/Database/Models/`
- ❌ Skip SQL migration for core tables — SQL is source of truth
- ❌ Register generic routes before specific ones in `routes.swift`
- ❌ Mix `Application/Services/` and direct repository calls without reason
- ❌ Use `xcode-cloud` skill — this is SPM/Docker (use `swift-server-ci`)

## New Resource Checklist

- [ ] Decide SQL vs Fluent migration (ADR-002)
- [ ] SQL script in `database/migrations/` if needed
- [ ] Model in `Infrastructure/Database/Models/`
- [ ] DTO in `DTOs/` with `toDTO()` / `toModel()`
- [ ] Repository protocol + `Database*Repository`
- [ ] Controller `RouteCollection`
- [ ] Register in `routes.swift` (order matters)
- [ ] Service only if business logic is non-trivial

## References

- `docs/adr/001-stack-vapor-fluent-postgres.md`
- `docs/adr/002-migrations-sql-e-fluent.md`
- `docs/adr/003-arquitetura-controller-repository-dto.md`
- `docs/adr/004-seguranca-cors-env-erros.md`
- [Vapor Docs](https://docs.vapor.codes/)
