# Documentação — News-Website-Template

Índice da documentação do template HTML [Notícias Mobile](https://www.noticiasmobile.com.br). Comece pelos guias de template; use domínio/schema/seeds para o contrato de dados.

## Template e UI

| Documento | Conteúdo |
|-----------|----------|
| [STYLE-GUIDE.md](STYLE-GUIDE.md) | Identidade visual, tokens, light/dark, SEO/CMP, checklist de novas páginas |
| [SCREEN-MAP.md](SCREEN-MAP.md) | Mapa de telas, `data-widget-id` / `data-widget-type`, slots editoriais |
| [BANNER-FORMATS.md](BANNER-FORMATS.md) | Formatos e tamanhos de banner (publicidade / ad slots) |

JSON máquina do screen map (fora de `docs/`): [`../screen-map.json`](../screen-map.json).

## Taxonomia editorial

| Documento | Conteúdo |
|-----------|----------|
| [CATEGORIES.md](CATEGORIES.md) | Slugs canônicos, rótulos pt-BR, classes `color-*`, filtros Isotope |
| [TAGS.md](TAGS.md) | Catálogo de tags (`rel=tag` / nuvem / `sidebar-tags`) |

## Domínio e dados

| Documento / pasta | Conteúdo |
|-------------------|----------|
| [domain/DATABASE-SCHEMA.md](domain/DATABASE-SCHEMA.md) | Schema PostgreSQL (tabelas, relações, notas) |
| [domain/DATA-INVENTORY.md](domain/DATA-INVENTORY.md) | Inventário template → entidades |
| [domain/ENTITIES-VALIDATION.md](domain/ENTITIES-VALIDATION.md) | Checklist de validação das entidades |
| [domain/widget-id-matrix.json](domain/widget-id-matrix.json) | Matriz máquina page → widget |
| [schema/001_portal_noticias.sql](schema/001_portal_noticias.sql) | DDL canônico |
| [seeds/](seeds/) | Seeds JSON + [README dos seeds](seeds/README.md) |

## Decisões de arquitetura

| Documento | Conteúdo |
|-----------|----------|
| [adr/001-dominio-portal-noticias.md](adr/001-dominio-portal-noticias.md) | ADR-001 — domínio do portal de notícias |

## Leitura sugerida

1. **Novo layout / página HTML** → [STYLE-GUIDE.md](STYLE-GUIDE.md) → [SCREEN-MAP.md](SCREEN-MAP.md)
2. **Categoria ou tag no UI** → [CATEGORIES.md](CATEGORIES.md) / [TAGS.md](TAGS.md)
3. **Banner / anúncio** → [BANNER-FORMATS.md](BANNER-FORMATS.md)
4. **Backend / CMS / Fluent** → [adr/001](adr/001-dominio-portal-noticias.md) → [domain/DATABASE-SCHEMA.md](domain/DATABASE-SCHEMA.md) → [seeds/](seeds/)

Voltar ao [README do projeto](../README.md).
