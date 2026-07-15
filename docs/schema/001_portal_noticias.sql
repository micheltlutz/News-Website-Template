-- Portal Notícias Mobile / News Edge — schema PostgreSQL v1
-- Fonte: screen-map.json + CATEGORIES.md + STYLE-GUIDE §11 + ADR-001
-- PKs UUID, colunas snake_case. API JSON futura: camelCase.
-- Soft delete apenas em articles. Consentimento do visitante: client-side (não há tabela).

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- Mídia
-- =============================================================================

CREATE TABLE media_assets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url             TEXT NOT NULL,
    alt_text        TEXT NOT NULL DEFAULT '',
    mime_type       VARCHAR(100),
    width           INT,
    height          INT,
    blurhash        VARCHAR(64),
    credit          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- Editorial
-- =============================================================================

CREATE TABLE authors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(120) NOT NULL UNIQUE,
    display_name    VARCHAR(200) NOT NULL,
    bio             TEXT,
    avatar_media_id UUID REFERENCES media_assets(id) ON DELETE SET NULL,
    email           VARCHAR(255),
    twitter_handle  VARCHAR(80),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(120) NOT NULL UNIQUE,
    label_pt_br     VARCHAR(160) NOT NULL,
    label_en        VARCHAR(160),
    parent_id       UUID REFERENCES categories(id) ON DELETE SET NULL,
    kind            VARCHAR(32) NOT NULL DEFAULT 'category'
                    CHECK (kind IN ('category', 'subcategory', 'brand', 'section_label')),
    color_class     VARCHAR(64),
    isotope_filter  VARCHAR(64),
    sort_order      INT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_categories_parent ON categories(parent_id);

CREATE TABLE tags (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(120) NOT NULL UNIQUE,
    label           VARCHAR(160) NOT NULL,
    usage_count     INT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE articles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug                VARCHAR(220) NOT NULL UNIQUE,
    title               VARCHAR(300) NOT NULL,
    excerpt             TEXT,
    body_html           TEXT,
    body_markdown       TEXT,
    status              VARCHAR(32) NOT NULL DEFAULT 'draft'
                        CHECK (status IN ('draft', 'scheduled', 'published', 'archived')),
    category_id         UUID REFERENCES categories(id) ON DELETE SET NULL,
    author_id           UUID REFERENCES authors(id) ON DELETE SET NULL,
    featured_media_id   UUID REFERENCES media_assets(id) ON DELETE SET NULL,
    hero_media_id       UUID REFERENCES media_assets(id) ON DELETE SET NULL,
    video_url           TEXT,
    is_featured         BOOLEAN NOT NULL DEFAULT FALSE,
    allow_comments      BOOLEAN NOT NULL DEFAULT TRUE,
    reading_time_min    INT,
    view_count          INT NOT NULL DEFAULT 0,
    comment_count       INT NOT NULL DEFAULT 0,
    published_at        TIMESTAMPTZ,
    scheduled_at        TIMESTAMPTZ,
    source_url          TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE INDEX idx_articles_status_published ON articles(status, published_at DESC)
    WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_category ON articles(category_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_author ON articles(author_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_articles_featured ON articles(is_featured) WHERE deleted_at IS NULL AND status = 'published';

CREATE TABLE article_tags (
    article_id  UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    tag_id      UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    sort_order  INT NOT NULL DEFAULT 0,
    PRIMARY KEY (article_id, tag_id)
);

CREATE INDEX idx_article_tags_tag ON article_tags(tag_id);

CREATE TABLE comments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id      UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    parent_id       UUID REFERENCES comments(id) ON DELETE CASCADE,
    author_name     VARCHAR(160) NOT NULL,
    author_email    VARCHAR(255),
    body            TEXT NOT NULL,
    status          VARCHAR(32) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'spam', 'rejected')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_comments_article ON comments(article_id, status);

-- =============================================================================
-- SEO (polimórfico)
-- =============================================================================

CREATE TABLE seo_metadata (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type         VARCHAR(32) NOT NULL
                        CHECK (entity_type IN ('article', 'category', 'page', 'site', 'author', 'tag')),
    entity_id           UUID,
    meta_title          VARCHAR(300),
    meta_description    TEXT,
    canonical_url       TEXT,
    og_title            VARCHAR(300),
    og_description      TEXT,
    og_image_media_id   UUID REFERENCES media_assets(id) ON DELETE SET NULL,
    og_type             VARCHAR(64),
    twitter_card        VARCHAR(64) DEFAULT 'summary_large_image',
    robots              VARCHAR(64) DEFAULT 'index,follow',
    json_ld             JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_seo_entity UNIQUE (entity_type, entity_id)
);

-- Defaults do site: entity_type = 'site' AND entity_id IS NULL
CREATE UNIQUE INDEX uq_seo_site_defaults
    ON seo_metadata (entity_type)
    WHERE entity_type = 'site' AND entity_id IS NULL;

-- =============================================================================
-- Layout (screen-map)
-- =============================================================================

CREATE TABLE pages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id         VARCHAR(64) NOT NULL UNIQUE,
    file_name       VARCHAR(160) NOT NULL,
    title           VARCHAR(200) NOT NULL,
    aliases         JSONB NOT NULL DEFAULT '[]'::jsonb,
    page_kind       VARCHAR(32) NOT NULL DEFAULT 'other'
                    CHECK (page_kind IN ('home', 'article', 'listing', 'gallery', 'system', 'other')),
    is_active_home  BOOLEAN NOT NULL DEFAULT FALSE,
    is_published    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE widget_slots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id         UUID NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    widget_id       VARCHAR(120) NOT NULL UNIQUE,
    widget_type     VARCHAR(64) NOT NULL,
    label           VARCHAR(200) NOT NULL,
    region          VARCHAR(32) NOT NULL DEFAULT 'main'
                    CHECK (region IN ('main', 'sidebar')),
    sort_order      INT NOT NULL DEFAULT 0,
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_widget_slots_page ON widget_slots(page_id);

CREATE TABLE widget_bindings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_slot_id      UUID NOT NULL UNIQUE REFERENCES widget_slots(id) ON DELETE CASCADE,
    source_type         VARCHAR(32) NOT NULL DEFAULT 'manual'
                        CHECK (source_type IN (
                            'manual', 'category', 'tag', 'trending',
                            'recent', 'popular', 'author', 'static'
                        )),
    category_id         UUID REFERENCES categories(id) ON DELETE SET NULL,
    tag_id              UUID REFERENCES tags(id) ON DELETE SET NULL,
    author_id           UUID REFERENCES authors(id) ON DELETE SET NULL,
    limit_count         INT NOT NULL DEFAULT 10,
    start_at            TIMESTAMPTZ,
    end_at              TIMESTAMPTZ,
    config_json         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE widget_binding_articles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_binding_id   UUID NOT NULL REFERENCES widget_bindings(id) ON DELETE CASCADE,
    article_id          UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    sort_order          INT NOT NULL DEFAULT 0,
    pinned_until        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (widget_binding_id, article_id)
);

-- =============================================================================
-- Navegação e site
-- =============================================================================

CREATE TABLE menu_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_key        VARCHAR(64) NOT NULL
                    CHECK (menu_key IN ('header', 'footer', 'offcanvas', 'mobile')),
    parent_id       UUID REFERENCES menu_items(id) ON DELETE CASCADE,
    label           VARCHAR(160) NOT NULL,
    href            TEXT,
    page_id         UUID REFERENCES pages(id) ON DELETE SET NULL,
    target          VARCHAR(16) NOT NULL DEFAULT '_self',
    sort_order      INT NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_menu_items_key ON menu_items(menu_key, sort_order);

CREATE TABLE site_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key             VARCHAR(120) NOT NULL UNIQUE,
    value_json      JSONB NOT NULL,
    description     TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE social_links (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    network         VARCHAR(64) NOT NULL UNIQUE,
    label           VARCHAR(120) NOT NULL,
    url             TEXT NOT NULL,
    icon_class      VARCHAR(80),
    follower_count  INT NOT NULL DEFAULT 0,
    sort_order      INT NOT NULL DEFAULT 0,
    show_in_sidebar BOOLEAN NOT NULL DEFAULT TRUE,
    show_in_footer  BOOLEAN NOT NULL DEFAULT TRUE,
    show_in_share   BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE analytics_config (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider                VARCHAR(32) NOT NULL DEFAULT 'ga4'
                            CHECK (provider IN ('ga4', 'gtm', 'none')),
    measurement_id          VARCHAR(64),
    gtm_container_id        VARCHAR(64),
    anonymize_ip            BOOLEAN NOT NULL DEFAULT TRUE,
    send_page_view          BOOLEAN NOT NULL DEFAULT FALSE,
    consent_mode_v2         BOOLEAN NOT NULL DEFAULT TRUE,
    enabled                 BOOLEAN NOT NULL DEFAULT FALSE,
    events_enabled          JSONB NOT NULL DEFAULT '[
        "page_view","select_content","view_item","share",
        "click_ad","generate_lead","search","cookie_consent_update"
    ]'::jsonb,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Singleton lógico: no máximo 1 linha ativa
CREATE UNIQUE INDEX uq_analytics_singleton ON analytics_config ((TRUE));

-- =============================================================================
-- Ads + privacidade
-- =============================================================================

CREATE TABLE ad_slots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    widget_id       VARCHAR(120) NOT NULL UNIQUE,
    page_id         UUID REFERENCES pages(id) ON DELETE SET NULL,
    slot_key        VARCHAR(160) NOT NULL UNIQUE,
    label           VARCHAR(200) NOT NULL,
    region          VARCHAR(32) NOT NULL DEFAULT 'sidebar',
    size_hint       VARCHAR(64),
    is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ad_creatives (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ad_slot_id      UUID NOT NULL REFERENCES ad_slots(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    media_id        UUID REFERENCES media_assets(id) ON DELETE SET NULL,
    click_url       TEXT,
    alt_text        TEXT NOT NULL DEFAULT 'Publicidade',
    weight          INT NOT NULL DEFAULT 1,
    start_at        TIMESTAMPTZ,
    end_at          TIMESTAMPTZ,
    requires_ad_consent BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ad_creatives_slot ON ad_creatives(ad_slot_id);

CREATE TABLE google_ads_config (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    publisher_id            VARCHAR(64),
    consent_mode_enabled    BOOLEAN NOT NULL DEFAULT TRUE,
    default_ad_storage      VARCHAR(16) NOT NULL DEFAULT 'denied'
                            CHECK (default_ad_storage IN ('denied', 'granted')),
    enabled                 BOOLEAN NOT NULL DEFAULT FALSE,
    notes                   TEXT,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_google_ads_singleton ON google_ads_config ((TRUE));

CREATE TABLE privacy_policy (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version             VARCHAR(32) NOT NULL UNIQUE,
    title               VARCHAR(300) NOT NULL,
    body_html           TEXT NOT NULL,
    effective_at        DATE NOT NULL,
    cmp_enabled         BOOLEAN NOT NULL DEFAULT TRUE,
    policy_storage_key  VARCHAR(64) NOT NULL DEFAULT 'newsedge-consent',
    is_current          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX uq_privacy_current ON privacy_policy ((TRUE)) WHERE is_current;
