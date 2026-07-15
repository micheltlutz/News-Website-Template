# Tags do template Notícias Mobile

Catálogo de **tags** (não confundir com [categorias](CATEGORIES.md)).  
Usado em `article-tags` (`.blog-tags` + `rel=tag`) e nuvem `sidebar-tags`.

Fontes: HTML demo · schema `tags` / `article_tags` · [`domain/DATABASE-SCHEMA.md`](domain/DATABASE-SCHEMA.md).

## Convenção

| Campo | Regra | Exemplo |
|-------|--------|---------|
| `slug` | kebab-case, sem `#` | `business` |
| `label` | pt-BR ou EN estável do template | `Business` |
| UI artigo | `#` + label | `#Business` |
| URL futura | `/tag/{slug}` | `/tag/business` |

Tags ≠ categorias: um artigo tem **1 categoria** principal e **N tags**.

## Catálogo (seed do template)

| slug | label | Onde aparece |
|------|-------|--------------|
| `business` | Business | `article-*.tags`, sidebars |
| `magazine` | Magazine | `article-*.tags` |
| `lifestyle` | Lifestyle | `article-*.tags` |
| `apple` | Apple | `sidebar-tags` |
| `architecture` | Architecture | `sidebar-tags` |
| `gadgets` | Gadgets | `sidebar-tags` |
| `software` | Software | `sidebar-tags` |
| `microsoft` | Microsoft | `sidebar-tags` |
| `robotic` | Robotic | `sidebar-tags` |
| `technology` | Technology | `sidebar-tags` |
| `others` | Others | `sidebar-tags` |

Seed JSON: [`seeds/tags.seed.json`](seeds/tags.seed.json).

## Backoffice

1. Ao cadastrar notícia, escolher tags existentes ou criar novo `slug`.
2. Persistir em `article_tags` com `sort_order`.
3. Atualizar `tags.usage_count` na publicação.
4. Widget `sidebar-tags` lista top N por `usage_count`.
