# AGENTS.md — server-side-swift

Skill para desenvolvimento backend em **Swift com Vapor 4 e Fluent**. Leia este arquivo antes de criar ou alterar código da API.

## Quando usar esta skill

- Novos endpoints, controllers, models, DTOs, repositories
- Autenticação (JWT, sessions), validation, middleware
- Queries Fluent, relacionamentos, migrations Swift
- Dúvidas sobre routing, Content, errors

**Não use para CI/deploy** — veja `../swift-server-ci/AGENTS.md`.

## Setup commands

```bash
cp .env.example .env
./run.sh                                    # API local com .env
swift run MLBackofficeAPI serve --hostname 0.0.0.0 --port 8080
swift package resolve                       # após mudar Package.swift
./clean-run.sh                              # limpar .build (conflito de versão Swift)
```

## Dev environment tips

- Target do projeto: `MLBackofficeAPI` — **não** scaffold `Sources/App/`
- Leia `ml-backoffice-patterns.md` e os ADRs em `docs/adr/` antes de codar
- Exemplo canônico CRUD: `FilamentoController` + `FilamentoDTO` + `DatabaseFilamentoRepository` + model `Filamento`
- Lógica complexa: `Application/Services/` (ex.: `ProdutoService`); cálculos puros: `Services/`
- Rotas mais específicas registradas **antes** em `routes.swift`
- Hummingbird só se o usuário pedir explicitamente — ver `hummingbird-patterns.md`

## Code style

- **Vapor 4**, Swift 6, **async/await apenas** (sem EventLoopFuture)
- Controller: `RouteCollection`, handlers `@Sendable async throws`
- Rotas: `api/<recurso>`, IDs `UUID`
- DTO: struct `Content`, camelCase, `toDTO()` / `toModel()` no mesmo arquivo
- Model: `Infrastructure/Database/Models/`, colunas snake_case (`@Field(key:)`)
- Repository: protocol `Sendable` + `DatabaseXxxRepository`
- Erros: `Abort(.badRequest)`, `Abort(.notFound)`, `Abort(.conflict)`
- JSON: camelCase na API; datas ISO8601 na saída (ver `configure.swift`)

## Testing instructions

```bash
swift test
swift build -c release --product MLBackofficeAPI
```

- Framework: **Swift Testing** (`@Suite`, `@Test`)
- Testes de integração HTTP: `VaporTesting` — ver `testing-patterns.md`
- Após alterar lógica de preço/orçamento: rodar testes em `Tests/MLBackofficeAPITests/`
- Corrija erros de compilação e testes antes de finalizar a tarefa

## Migrations

Decida **antes** de criar arquivos (ADR-002):

| Mudança | Onde |
|---------|------|
| Tabela/coluna do schema principal | `database/migrations/NNN_*.sql` |
| Tabela gerenciada só pela API | `Sources/MLBackofficeAPI/Migrations/` (Fluent) |

SQL: `./database/run-migrations-ml-backoffice.sh` — tabela deve existir antes do Model Fluent.

## Security

- Credenciais via env (`DATABASE_URL` ou `DATABASE_*`) — nunca commitar `.env`
- Sem auth na API ainda — não assumir endpoints protegidos
- Validar parâmetros de rota e body (decode em DTO)
- Ver ADR-004 em `docs/adr/004-seguranca-cors-env-erros.md`

## Referências nesta skill

| Arquivo | Uso |
|---------|-----|
| `SKILL.md` | Entry point e detecção de projeto |
| `ml-backoffice-patterns.md` | **Padrões deste repo** (ler primeiro) |
| `vapor-patterns.md` | Routing, middleware, configure |
| `database-patterns.md` | Fluent ORM, queries, relations |
| `auth-patterns.md` | JWT, sessions |
| `testing-patterns.md` | VaporTesting, Swift Testing |

## Documentação oficial

- [Vapor Routing](https://docs.vapor.codes/basics/routing/)
- [Fluent](https://docs.vapor.codes/fluent/overview/)
- [Validation](https://docs.vapor.codes/basics/validation/)
- [Errors](https://docs.vapor.codes/basics/errors/)
