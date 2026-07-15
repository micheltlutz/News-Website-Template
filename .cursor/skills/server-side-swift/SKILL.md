---
name: server-side-swift
description: Server-side Swift development with Vapor and Fluent. Covers routing, controllers, ORM, authentication, and API design. Use when building backends or APIs in Swift, working with Vapor, Fluent, PostgreSQL, or server-side Swift patterns.
---

# Server-Side Swift

Guides server-side Swift development with **Vapor 4** (default). Hummingbird only when explicitly requested.

## When This Skill Activates

- Create or extend a Swift backend/API
- Mentions Vapor, Fluent, PostgreSQL, RouteCollection, AsyncMigration
- JWT, sessions, or authentication on the server
- Shared Codable models between iOS and server
- WebSockets, validation, middleware

**Not for CI/deploy** — use `skills/swift-server-ci/SKILL.md` for Docker, GitHub Actions.

## Project Detection

### ml-backoffice-api (this repo)

If `Package.swift` contains target `MLBackofficeAPI`:

1. **Do not** scaffold `Sources/App/` or generic Vapor template
2. Read **`ml-backoffice-patterns.md`** immediately
3. Follow ADRs in `docs/adr/`
4. Default: Vapor + Fluent + PostgreSQL (already configured)

### Existing Vapor project

```
Glob: **/Package.swift, **/configure.swift, **/routes.swift
Grep: "import Vapor" or "RouteCollection" or "AsyncMigration"
```

Extend existing code. Ask (via AskQuestion or conversation) only if replacing vs extending is unclear.

### Greenfield project

Ask only when no `Package.swift` exists:

1. Framework: Vapor (default) or Hummingbird → see `hummingbird-patterns.md`
2. Database: PostgreSQL (default), SQLite, or none
3. Authentication: JWT, session, none
4. Shared models with iOS client: yes/no

## Default Framework: Vapor 4

- Swift 6, async/await exclusively (no EventLoopFuture)
- Official docs: [docs.vapor.codes](https://docs.vapor.codes)

| Topic | Documentation |
|-------|---------------|
| Routing | [basics/routing](https://docs.vapor.codes/basics/routing/) |
| Content / JSON | [basics/content](https://docs.vapor.codes/basics/content/) |
| Validation | [basics/validation](https://docs.vapor.codes/basics/validation/) |
| Errors | [basics/errors](https://docs.vapor.codes/basics/errors/) |
| Fluent ORM | [fluent/overview](https://docs.vapor.codes/fluent/overview/) |
| Middleware | [advanced/middleware](https://docs.vapor.codes/advanced/middleware/) |
| Authentication | [security/authentication](https://docs.vapor.codes/security/authentication/) |
| Testing | [advanced/testing](https://docs.vapor.codes/advanced/testing/) |

## Generation Workflow (greenfield)

1. `Package.swift` — vapor, fluent, driver
2. `configure.swift` — DB, middleware, migrations
3. `entrypoint.swift` — `@main`, `Application.make`
4. `routes.swift` — route registration
5. Controllers, DTOs, Models, Migrations as needed
6. Deploy → `swift-server-ci` skill (Docker)

## Swift 6 Concurrency

```swift
app.get("users") { req async throws -> [UserDTO] in
    try await User.query(on: req.db).all().map { $0.toDTO() }
}
```

DTOs shared across actors must be `Sendable`:

```swift
struct UserDTO: Content, Sendable {
    let id: UUID?
    let name: String
}
```

## ml-backoffice-api Quick Reference

```
Sources/MLBackofficeAPI/
├── Controllers/     # RouteCollection
├── DTOs/            # Content, camelCase
├── Infrastructure/Database/{Models,Repositories}/
├── Migrations/      # Fluent only (see ADR-002)
└── configure.swift, routes.swift, entrypoint.swift
```

Canonical example: `FilamentoController` + `FilamentoDTO` + `FilamentoRepository` + `Filamento` model.

Run locally: `./run.sh` or `swift run MLBackofficeAPI serve`

## References

- **ml-backoffice-patterns.md** — project-specific conventions (read first in this repo)
- **vapor-patterns.md** — routing, controllers, middleware, configuration
- **database-patterns.md** — Fluent ORM, queries, relationships
- **auth-patterns.md** — JWT, sessions, Bearer, Sign in with Apple
- **deployment-patterns.md** — generic Docker/Fly.io (project deploy → swift-server-ci)
- **hummingbird-patterns.md** — only when user requests Hummingbird
- **shared-code-patterns.md** — SharedModels, APNSwift
- **testing-patterns.md** — VaporTesting, Swift Testing
