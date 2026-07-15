# Seeds — portal de notícias

Artefatos gerados a partir do template (não aplicam migration Fluent ainda).  
Schema: [`../schema/001_portal_noticias.sql`](../schema/001_portal_noticias.sql) · docs: [`../domain/DATABASE-SCHEMA.md`](../domain/DATABASE-SCHEMA.md).

## Layout (regeneráveis)

| Arquivo | Fonte | Destino futuro |
|---------|-------|----------------|
| `pages.seed.json` | `screen-map.json` | `pages` |
| `widget_slots.seed.json` | widgets do screen-map | `widget_slots` |
| `ad_slots.seed.json` | widgets `ad-banner` | `ad_slots` |

```bash
python3 News-Website-Template/scripts/regenerate_layout_seeds.py
```

## Domínio / configuração

| Arquivo | Fonte | Destino futuro |
|---------|-------|----------------|
| `categories.seed.json` | [`CATEGORIES.md`](../CATEGORIES.md) | `categories` |
| `tags.seed.json` | [`TAGS.md`](../TAGS.md) / HTML | `tags` |
| `site_settings.seed.json` | brand / theme / CMP | `site_settings` |
| `analytics_config.seed.json` | `js/analytics.js` | `analytics_config` |
| `google_ads_config.seed.json` | Consent Mode / ads | `google_ads_config` |
| `social_links.seed.json` | sidebar / share | `social_links` |
| `menu_items.seed.json` | nav header/footer | `menu_items` |
| `privacy_policy.seed.json` | `privacy.html` + CMP | `privacy_policy` |
| `articles.example.seed.json` | modelo de cadastro | referência (não seed massivo) |

## Contagens (2026-07-14)

~21 pages · ~256 widget slots · ~24 ad slots · ~81 categories · 11 tags.
