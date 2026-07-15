# AGENTS.md — xcode-cloud

Skill para **CI/CD de apps Apple** com `.xcodeproj` ou `.xcworkspace` via Xcode Cloud.

## Early exit — não usar neste repo

Se o projeto tem `Package.swift` + `Dockerfile` **sem** `.xcodeproj`:

→ Pare. Use `../swift-server-ci/AGENTS.md` (**ml-backoffice-api** é Vapor/Docker).

## Quando usar esta skill

- Configurar Xcode Cloud para app iOS, macOS, watchOS ou tvOS
- Workflows: build, test, archive, TestFlight, App Store
- Scripts `ci_scripts/` (post_clone, pre_xcodebuild, post_xcodebuild)
- Falhas de signing, certificados, SPM no Xcode Cloud
- Otimização de compute hours e tempo de build

## Setup commands

Workflows são configurados no **Xcode** (Product → Xcode Cloud → Create Workflow), não em YAML.

Scripts customizados na raiz do app:

```bash
mkdir -p ci_scripts
chmod +x ci_scripts/*.sh
```

Ordem de execução: `ci_post_clone.sh` → `ci_pre_xcodebuild.sh` → build/test/archive → `ci_post_xcodebuild.sh`

## Dev environment tips

- Exige `.xcodeproj` ou `.xcworkspace` e repositório Git
- Verifique `CODE_SIGN_STYLE` e `DEVELOPMENT_TEAM` no `project.pbxproj`
- Test plans para paralelizar testes — ver `testing-patterns.md`
- Variável `CI=TRUE` disponível em todos os scripts Xcode Cloud
- Se já existe GitHub Actions/Fastlane: decidir substituir ou rodar em paralelo

## Code style (ci_scripts)

- Scripts em bash, `set -euo pipefail` recomendado
- Usar `$CI_WORKSPACE` / paths documentados em `scripts-reference.md`
- `ci_post_clone.sh`: instalar deps, `xcodebuild -resolvePackageDependencies`
- Não commitar certificados — usar cloud signing da Apple

## Testing instructions

- Definir test plan no workflow Xcode Cloud
- UI tests: simuladores disponíveis no ambiente cloud
- Cobertura mínima: configurar threshold no workflow se necessário
- Ver `testing-patterns.md` para padrões PR vs nightly

## PR / release instructions

- **PR workflow**: build + unit tests em cada push/PR
- **Merge to main**: archive + TestFlight internal
- **Tag**: App Store submission — ver `deployment-patterns.md`
- Build number: `CI_BUILD_NUMBER` auto-incrementado

## Security

- Não logar tokens ou provisioning profiles
- Secrets via App Store Connect / ambiente Xcode Cloud
- Notarização macOS: ver `deployment-patterns.md`

## Referências nesta skill

| Arquivo | Uso |
|---------|-----|
| `SKILL.md` | Entry point e early exit SPM |
| `workflow-patterns.md` | PR, TestFlight, App Store |
| `scripts-reference.md` | Hooks e variáveis `CI_*` |
| `testing-patterns.md` | Test plans, UI tests |
| `deployment-patterns.md` | TestFlight, App Store, notarization |
| `troubleshooting.md` | Signing, timeouts, SPM |
| `optimization.md` | Compute hours, cache |

## Documentação oficial

- [Xcode Cloud](https://developer.apple.com/documentation/xcode/xcode-cloud)
- [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi)

## Alternativa server-side

Projetos Vapor/Hummingbird SPM sem Xcode → `../swift-server-ci/AGENTS.md`
