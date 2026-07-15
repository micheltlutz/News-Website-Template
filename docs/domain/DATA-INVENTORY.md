# Inventário de estruturas de dados (template → domínio)

Fonte: HTML Notícias Mobile + [`screen-map.json`](../../screen-map.json) + [`CATEGORIES.md`](../CATEGORIES.md) + [`TAGS.md`](../TAGS.md).  
Schema completo: [`DATABASE-SCHEMA.md`](DATABASE-SCHEMA.md) · DDL: [`../schema/001_portal_noticias.sql`](../schema/001_portal_noticias.sql).  
Jira: [NM-7](https://mlcreativehub.atlassian.net/browse/NM-7) / épico [NM-1](https://mlcreativehub.atlassian.net/browse/NM-1).

## Artigos (cadastro)

| Campo | Evidência template | Tabela / coluna |
|-------|-------------------|-----------------|
| title | h1/h2/h3 | `articles.title` |
| slug | URL single-news | `articles.slug` |
| excerpt | `<p>` em cards | `articles.excerpt` |
| body | `.news-details-layout1` | `articles.body_html` |
| status | backoffice | `articles.status` (`draft`…`published`) |
| featured / hero image | `img/news/*` | `media_assets` + FKs |
| category | `.topic-box*` / slug | `categories` |
| author | "By …" | `authors` |
| publishedAt | ícone calendário | `articles.published_at` |
| viewCount / commentCount | fa-eye / fa-comments | colunas cache |
| tags | `.blog-tags` + `rel=tag` | `tags` / `article_tags` |
| SEO | head OG/JSON-LD | `seo_metadata` |
| video | blocos video-* | `articles.video_url` |

Exemplo de payload: [`../seeds/articles.example.seed.json`](../seeds/articles.example.seed.json).

## Widgets / destaques

| Tipo | Comportamento | Tabelas |
|------|---------------|---------|
| hero-*, isotope, trending, carousel, ticker | Lista de artigos | `widget_bindings`, `widget_binding_articles` |
| ad-banner | Banner / Ads | `ad_slots`, `ad_creatives` |
| sidebar-social | Contagens + links | `social_links` |
| sidebar-tags | Nuvem | `tags` |
| site-header / footer | Chrome | `menu_items`, `site_settings` |
| article-* | Derivados do artigo | `articles` / `comments` / `article_tags` |
| privacy.body | Texto legal | `privacy_policy` |

Matriz completa: [`widget-id-matrix.json`](widget-id-matrix.json) (21 páginas, 256 widgets).

## Site / tagueamento / analytics

| Conceito | Template | Schema / seed |
|----------|----------|---------------|
| Nome, logo, tema, locale | header/footer, theme.js | `site_settings` · [`site_settings.seed.json`](../seeds/site_settings.seed.json) |
| Menus | nav header/footer | `menu_items` · [`menu_items.seed.json`](../seeds/menu_items.seed.json) |
| Tags | TAGS.md | `tags` · [`tags.seed.json`](../seeds/tags.seed.json) |
| GA4 + Consent Mode | `js/analytics.js`, `js/consent.js` | `analytics_config` · seed homônimo |
| CMP Aceitar/Básico/Recusar | banner CMP | client storage + `privacy_policy` |
| Google Ads | ad slots | `google_ads_config`, `ad_creatives` |
| Redes | Stay Connected / share | `social_links` |

## Contagens (2026-07-14)

| Seed | Count aproximado |
|------|------------------|
| pages | 21 (incl. `privacy`) |
| widget_slots | 256 |
| ad_slots | 24 |
| categories | 81 |
| tags | 11 |

## Status do inventário

Completo para configuração, tagueamento, Analytics/CMP e cadastro editorial (DDL + seeds; Fluent ainda não implementado).
