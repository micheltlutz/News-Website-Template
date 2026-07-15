# Schema de banco — portal Notícias Mobile

Contrato PostgreSQL para configuração do site, tagueamento, Analytics/CMP e cadastro de notícias.  
DDL: [`../schema/001_portal_noticias.sql`](../schema/001_portal_noticias.sql) · ADR: [`../adr/001-dominio-portal-noticias.md`](../adr/001-dominio-portal-noticias.md).

## Convenções

| Item | Regra |
|------|--------|
| PK | `UUID` (`gen_random_uuid()`) |
| Colunas DB | `snake_case` |
| API JSON futura | `camelCase` |
| Soft delete | só `articles.deleted_at` |
| Consentimento visitante | **não** persiste no servidor (v1) — `localStorage['noticiasmobile-consent']` |
| Singletons | `analytics_config`, `google_ads_config` (1 linha); `privacy_policy.is_current` |

## Mapa rápido por capacidade

| Capacidade | Tabelas |
|------------|---------|
| Configuração do site | `site_settings`, `menu_items`, `social_links`, `pages`, `widget_slots` |
| Tagueamento | `tags`, `article_tags` (+ nuvem `sidebar-tags`) |
| Analytics / CMP / Ads | `analytics_config`, `privacy_policy`, `google_ads_config`, `ad_slots`, `ad_creatives` |
| Cadastro de notícias | `articles`, `categories`, `authors`, `media_assets`, `seo_metadata`, `comments` |
| Destaques por tela | `widget_bindings`, `widget_binding_articles` |

## Relação com o screen-map

Cada `data-widget-id` vira uma linha em `widget_slots.widget_id`.  
Matriz widget → tabela primária: [`widget-id-matrix.json`](widget-id-matrix.json).

| widget-type (exemplos) | Tabela primária |
|------------------------|-----------------|
| `hero-*`, `isotope-section`, `ticker`, `*-carousel`, `sidebar-recent` | `widget_bindings` |
| `site-header`, `site-footer`, `meta-bar`, `sidebar-newsletter` | `site_settings` |
| `ad-banner` | `ad_slots` |
| `sidebar-social`, `article-share` | `social_links` |
| `sidebar-tags` | `tags` |
| `article-tags` | `article_tags` |
| `article-body` / `article-nav` | `articles` |
| `category-boxes` | `categories` |
| `privacy.body` | `privacy_policy` (conteúdo) + `seo_metadata` (page) |

## Cadastro de notícias (`articles`)

Fluxo mínimo de backoffice:

1. Criar/garantir `authors`, `categories` (slug de [`CATEGORIES.md`](../CATEGORIES.md)), `media_assets`.
2. Inserir `articles` com `status = draft` → opcionalmente `scheduled` → `published` (`published_at`).
3. Anexar tags em `article_tags` (slugs de [`TAGS.md`](../TAGS.md)).
4. Preencher `seo_metadata` com `entity_type = article`.
5. (Opcional) fixar no home via `widget_binding_articles`.

| Coluna | Uso |
|--------|-----|
| `slug` / `title` / `excerpt` / `body_html` | Conteúdo |
| `status` | `draft` \| `scheduled` \| `published` \| `archived` |
| `category_id` / `author_id` | Taxonomia + byline |
| `featured_media_id` / `hero_media_id` | Card / LCP |
| `video_url` | Blocos `video-*` |
| `view_count` / `comment_count` | Cache UI |
| `deleted_at` | Soft delete |

## Tagueamento

| Tabela | Papel |
|--------|-------|
| `tags` | Catálogo (`slug`, `label`, `usage_count`) |
| `article_tags` | N:N artigo↔tag (`sort_order`) |
| Widget `article-tags` | Render das tags do artigo (`rel=tag`) |
| Widget `sidebar-tags` | Nuvem ordenada por `usage_count` |

Ao publicar/despublicar, incrementar/decrementar `tags.usage_count` (serviço de domínio; não trigger no v1).

## Configuração do site

Chaves sugeridas em `site_settings` (ver seed):

| key | Conteúdo (`value_json`) |
|-----|-------------------------|
| `brand.name` | `"Notícias Mobile"` |
| `brand.logoUrl` / `brand.logoDarkUrl` | caminhos/URLs |
| `brand.themeColor` | `#99cc00` |
| `site.baseUrl` | `https://www.noticiasmobile.com.br` |
| `site.locale` | `pt-BR` |
| `site.defaultHomePageId` | `home-1` |
| `theme.default` | `system` \| `light` \| `dark` |
| `cmp.enabled` | `true` |
| `meta.locationLabel` | texto da meta-bar |

Menus: `menu_items` com `menu_key` ∈ `header|footer|offcanvas|mobile`.

## Analytics e consentimento

Alinhado a `js/analytics.js` + `js/consent.js`:

| Artefato | Onde |
|----------|------|
| Measurement ID GA4 | `analytics_config.measurement_id` → `window.NoticiasMobileAnalyticsConfig` |
| Consent Mode v2 | `analytics_config.consent_mode_v2` + defaults denied |
| Versão da política | `privacy_policy.version` (= `POLICY_VERSION` do CMP) |
| Preferência do usuário | browser only |
| Ads | `google_ads_config.consent_mode_enabled`; creatives com `requires_ad_consent` |

Eventos esperados (seed): `page_view`, `select_content`, `view_item`, `share`, `click_ad`, `generate_lead`, `search`, `cookie_consent_update`.

## Contagem v1

**19 tabelas** (sem tabela server de consentimento por visitante).

## Seeds

Ver [`../seeds/`](../seeds/) — regenerar layouts com:

```bash
python3 News-Website-Template/scripts/regenerate_layout_seeds.py
```
