# GitHub Actions — Swift Server CI

Suggested workflow for SPM Vapor projects like ml-backoffice-api.

## Workflow Overview

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Swift
        uses: swift-actions/setup-swift@v2
        with:
          swift-version: "6.1"

      - name: Resolve dependencies
        run: swift package resolve

      - name: Build
        run: swift build -c release --product MLBackofficeAPI

      - name: Test
        run: swift test

  docker:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t ml-backoffice-api:ci .

      - name: Verify image starts
        run: |
          docker run -d --name api-test -p 8080:8080 \
            -e DATABASE_HOST=localhost \
            -e DATABASE_USERNAME=test \
            -e DATABASE_PASSWORD=test \
            -e DATABASE_NAME=test \
            ml-backoffice-api:ci || true
          # Full integration requires PostgreSQL service — see below
```

## PostgreSQL Service (integration tests)

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: ml-backoffice-teste
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5

steps:
  - name: Test with database
    env:
      DATABASE_HOST: localhost
      DATABASE_PORT: 5432
      DATABASE_USERNAME: test
      DATABASE_PASSWORD: test
      DATABASE_NAME: ml-backoffice-teste
    run: swift test
```

## Caching

```yaml
- name: Cache .build
  uses: actions/cache@v4
  with:
    path: .build
    key: ${{ runner.os }}-swift-${{ hashFiles('Package.resolved') }}
    restore-keys: |
      ${{ runner.os }}-swift-
```

## SQL Migrations in CI/CD

For deploy pipelines, run SQL migrations before starting the API:

```yaml
- name: Run SQL migrations
  env:
    PGHOST: ${{ secrets.DATABASE_HOST }}
    PGUSER: ${{ secrets.DATABASE_USERNAME }}
    PGPASSWORD: ${{ secrets.DATABASE_PASSWORD }}
    PGDATABASE: ${{ secrets.DATABASE_NAME }}
  run: ./database/run-migrations-ml-backoffice.sh
```

Fluent migrations run automatically via `autoMigrate()` on boot.

## Deploy Job (example)

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: [test, docker]
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4
    - name: Build and push image
      run: |
        docker build -t ${{ secrets.REGISTRY }}/ml-backoffice-api:${{ github.sha }} .
        # docker push ...
```

## Secrets

Store in GitHub repository secrets:

- `DATABASE_HOST`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_NAME`
- Container registry credentials if pushing images

Never hardcode credentials in workflow files.

## ml-backoffice-api Notes

- Product name: `MLBackofficeAPI` (not `App`)
- Test DB name in testing env: `ml-backoffice-teste` (see `configure.swift`)
- No `.xcodeproj` — use `swift build`, not `xcodebuild`
