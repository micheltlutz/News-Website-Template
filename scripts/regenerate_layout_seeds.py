#!/usr/bin/env python3
"""Regenera seeds de layout a partir de screen-map.json."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SM_PATH = ROOT / "screen-map.json"
SEED_DIR = ROOT / "docs" / "seeds"
DOMAIN_DIR = ROOT / "docs" / "domain"

EDITORIAL = {
    "ticker",
    "hero-mosaic",
    "hero-banner",
    "hero-nivo",
    "isotope-section",
    "media-list",
    "card-grid",
    "overlay-list",
    "video-section",
    "video-carousel",
    "category-news",
    "news-carousel",
    "featured-section",
    "trending-section",
    "international-section",
    "more-news",
    "latest-news",
    "review-section",
    "related-carousel",
    "archive-filters",
    "sidebar-recent",
    "sidebar-reviews",
}

TYPE_TABLE = {
    "site-header": "site_settings",
    "site-footer": "site_settings",
    "meta-bar": "site_settings",
    "breadcrumbs": "seo_metadata",
    "sidebar-social": "social_links",
    "sidebar-tags": "tags",
    "sidebar-newsletter": "site_settings",
    "article-tags": "article_tags",
    "article-share": "social_links",
    "article-body": "articles",
    "article-nav": "articles",
    "article-author": "authors",
    "article-comments": "comments",
    "ad-banner": "ad_slots",
    "category-boxes": "categories",
    "contact-form": "site_settings",
    "error-message": "site_settings",
    "gallery-grid": "media_assets",
}


def primary_table(widget_id: str, wtype: str) -> str:
    if widget_id == "privacy.body":
        return "privacy_policy"
    if wtype in TYPE_TABLE:
        return TYPE_TABLE[wtype]
    if wtype in EDITORIAL:
        return "widget_bindings"
    return "widget_bindings"


def notes_for(table: str) -> str:
    return {
        "widget_bindings": "Curadoria via widget_bindings + widget_binding_articles",
        "ad_slots": "Creatives em ad_creatives; gated por Consent Mode",
        "site_settings": "Config global do site / chrome",
        "social_links": "Links e contagens de redes",
        "tags": "Nuvem de tags (frequência / uso)",
        "article_tags": "Tags do artigo corrente",
        "articles": "Campos / navegação do artigo",
        "authors": "Perfil do autor",
        "comments": "Lista e formulário de comentários",
        "categories": "Caixas de categoria (CATEGORIES.md)",
        "seo_metadata": "SEO / breadcrumbs da página",
        "media_assets": "Mídia da galeria",
        "privacy_policy": "Conteúdo da política + versão CMP",
    }.get(table, table)


def page_kind(page_id: str) -> str:
    if page_id.startswith("home-"):
        return "home"
    if page_id.startswith("article-"):
        return "article"
    if page_id.startswith("post-") or page_id in {"archive", "author"}:
        return "listing"
    if page_id.startswith("gallery-"):
        return "gallery"
    if page_id in {"contact", "error-404", "privacy"}:
        return "system"
    return "other"


def main() -> None:
    sm = json.loads(SM_PATH.read_text(encoding="utf-8"))
    SEED_DIR.mkdir(parents=True, exist_ok=True)
    DOMAIN_DIR.mkdir(parents=True, exist_ok=True)

    pages_seed = {
        "version": 1,
        "source": "screen-map.json",
        "pages": [
            {
                "pageId": p["pageId"],
                "file": p["file"],
                "title": p["title"],
                "aliases": p.get("aliases", []),
                "isActiveHome": p["pageId"] == "home-1",
                "pageKind": page_kind(p["pageId"]),
            }
            for p in sm["pages"]
        ],
    }
    (SEED_DIR / "pages.seed.json").write_text(
        json.dumps(pages_seed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    slots = []
    ads = []
    matrix = []
    for p in sm["pages"]:
        for order, w in enumerate(p["widgets"]):
            table = primary_table(w["id"], w["type"])
            slots.append(
                {
                    "widgetId": w["id"],
                    "pageId": p["pageId"],
                    "widgetType": w["type"],
                    "label": w.get("label", ""),
                    "region": w.get("region", "main"),
                    "sortOrder": order,
                    "table": table,
                }
            )
            matrix.append(
                {
                    "widgetId": w["id"],
                    "widgetType": w["type"],
                    "pageId": p["pageId"],
                    "region": w.get("region", "main"),
                    "primaryTable": table,
                    "notes": notes_for(table),
                }
            )
            if w["type"] == "ad-banner":
                ads.append(
                    {
                        "widgetId": w["id"],
                        "pageId": p["pageId"],
                        "label": w.get("label", ""),
                        "region": w.get("region", "sidebar"),
                        "slotKey": w["id"].replace(".", "_"),
                    }
                )

    (SEED_DIR / "widget_slots.seed.json").write_text(
        json.dumps(
            {
                "version": 1,
                "source": "screen-map.json",
                "count": len(slots),
                "widgetSlots": slots,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (SEED_DIR / "ad_slots.seed.json").write_text(
        json.dumps(
            {
                "version": 1,
                "source": "screen-map.json widgets type=ad-banner",
                "count": len(ads),
                "adSlots": ads,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (DOMAIN_DIR / "widget-id-matrix.json").write_text(
        json.dumps(
            {
                "version": 2,
                "jiraEpic": "NM-1",
                "naming": sm.get("naming"),
                "count": len(matrix),
                "primaryTableCounts": dict(Counter(m["primaryTable"] for m in matrix)),
                "mapping": matrix,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"pages={len(pages_seed['pages'])} widgets={len(slots)} ads={len(ads)}")


if __name__ == "__main__":
    main()
