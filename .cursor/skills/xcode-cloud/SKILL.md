---
name: xcode-cloud
description: Xcode Cloud CI/CD for Apple platform apps (.xcodeproj, .xcworkspace). Covers workflows, ci_scripts, TestFlight, App Store deployment, and signing. Use when setting up or troubleshooting Xcode Cloud for iOS, macOS, watchOS, or tvOS apps. Not for SPM-only server projects — use swift-server-ci instead.
---

# Xcode Cloud CI/CD

Guides **Apple platform apps** with `.xcodeproj` or `.xcworkspace`. Workflows, custom scripts, TestFlight, and App Store distribution.

## Early Exit — SPM Server Projects

Before proceeding, detect project type:

```
Glob: **/*.xcodeproj, **/*.xcworkspace, **/Package.swift, **/Dockerfile
```

| Detection | Action |
|-----------|--------|
| `Package.swift` + `Dockerfile`, no `.xcodeproj` | **Stop.** Use `skills/swift-server-ci/SKILL.md` |
| **ml-backoffice-api** | **Stop.** This repo is Vapor/Docker — use `swift-server-ci` |
| `.xcodeproj` or `.xcworkspace` present | Continue with this skill |

## When This Skill Activates

- Set up Xcode Cloud or configure CI/CD for an **Apple app**
- Xcode Cloud workflows, build pipelines
- TestFlight or App Store distribution
- Custom build scripts (`ci_scripts/`)
- Xcode Cloud build failures, signing issues
- Test plans, cloud signing, compute hours optimization

## Pre-Configuration Checks

### 1. Project Detection

- [ ] `.xcodeproj` or `.xcworkspace` exists
- [ ] Project type (app, framework, multi-platform)
- [ ] Git source control configured

```
Glob: **/*.xcodeproj, **/*.xcworkspace, **/ci_scripts/*.sh
```

### 2. Existing CI/CD

```
Glob: **/.github/workflows/*.yml, **/bitrise.yml, **/fastlane/Fastfile
```

If found, ask (via AskQuestion or conversation): replace or run alongside?

### 3. Signing

```
Glob: **/*.entitlements, **/*.xcodeproj/project.pbxproj
Grep: "CODE_SIGN_STYLE" or "PROVISIONING_PROFILE"
```

## Configuration Questions (greenfield only)

Ask only when setting up a new Apple app CI:

1. **Automate what?** Build+Test on PR, TestFlight on merge, App Store on tag
2. **Triggers?** Push, PR, tag, schedule
3. **Tests?** Unit, UI, performance, build-only
4. **Platforms?** iOS, macOS, watchOS, all

## Workflow Components

Configured in Xcode UI or App Store Connect API — not YAML.

1. **Start Conditions** — triggers
2. **Environment** — Xcode/macOS version
3. **Build Actions** — build, test, analyze, archive
4. **Post-Actions** — TestFlight, App Store, notifications

## Custom Scripts (`ci_scripts/`)

```
ci_scripts/
├── ci_post_clone.sh         # After clone (deps)
├── ci_pre_xcodebuild.sh     # Before build
└── ci_post_xcodebuild.sh    # After build
```

**Order:** post_clone → pre_xcodebuild → build/test/archive → post_xcodebuild

## Key Environment Variables

| Variable | Description |
|----------|-------------|
| `CI` | Always `TRUE` |
| `CI_XCODEBUILD_ACTION` | `build`, `test`, `archive` |
| `CI_WORKFLOW` | Workflow name |
| `CI_BRANCH` | Branch being built |
| `CI_COMMIT` | Full commit SHA |
| `CI_BUILD_NUMBER` | Auto-incrementing |
| `CI_XCODE_SCHEME` | Scheme being built |
| `CI_DERIVED_DATA_PATH` | Derived data location |

## References

- **workflow-patterns.md** — PR, TestFlight, App Store workflows
- **scripts-reference.md** — ci_scripts patterns
- **testing-patterns.md** — Test plans, parallel testing
- **deployment-patterns.md** — TestFlight, App Store, notarization
- **troubleshooting.md** — Signing, SPM, timeouts
- **optimization.md** — Build time, compute hours
- [Xcode Cloud Documentation](https://developer.apple.com/documentation/xcode/xcode-cloud)

## Server Swift Alternative

For Vapor/Hummingbird SPM backends without Xcode project:

→ `skills/swift-server-ci/SKILL.md` (Docker, GitHub Actions)
