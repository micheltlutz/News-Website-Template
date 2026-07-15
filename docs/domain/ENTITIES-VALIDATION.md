# Validação de entidades propostas

Jira: [NM-1](https://mlcreativehub.atlassian.net/browse/NM-1).  
Escopo: **validação de proposta** + schema DDL em [`../schema/001_portal_noticias.sql`](../schema/001_portal_noticias.sql).

## Resultado

| Entidade | Necessária? | Observação |
|----------|-------------|------------|
| `articles` | Sim | Núcleo — cadastro de notícias |
| `categories` | Sim | Hierarquia `sports.*` / CATEGORIES.md |
| `tags` / `article_tags` | Sim | UI de tags + TAGS.md |
| `authors` | Sim | Página author + byline |
| `comments` | Sim (v1 simples) | Moderação futura |
| `media_assets` | Sim | alt/width/height para SEO |
| `seo_metadata` | Sim | Polymorphic |
| `pages` / `widget_slots` | Sim | Espelha screen-map (21 páginas) |
| `widget_bindings` / `widget_binding_articles` | Sim | Destaques |
| `menu_items` | Sim | Header/footer |
| `social_links` | Sim | Sidebar + footer + share |
| `site_settings` | Sim | Singleton lógico key/value |
| `analytics_config` | Sim | GA4/GTM + eventos |
| `ad_slots` / `ad_creatives` | Sim | Banners + Ads |
| `google_ads_config` | Sim | Consent Mode on |
| `privacy_policy` | Sim | Versão legal alinhada ao CMP |
| `consent_preferences` (tabela server) | **Não no v1** | Preferência fica no browser |

## Contagem

**19 tabelas** no v1 de schema (sem tabela server de consentimento por visitante).

## Riscos aceitos

- Reviews sem score no template → sem coluna `rating` no v1
- Newsletter → fora do v1 (só `site_settings` / tracking `generate_lead`)
- Multi-tenant → fora (decisão explícita site único)
- `page_chrome` como tabela → **rejeitado**; meta-bar usa `site_settings` / `seo_metadata`
