#!/usr/bin/env python3
"""Apply SEO head, CMP markup, analytics/consent scripts, and image SEO hints to all template HTML pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_NAME = "NewsEdge"
SITE_BASE = "https://www.newsedge.example"
DEFAULT_OG_IMAGE = f"{SITE_BASE}/img/logo.png"

PAGE_META = {
    "index.html": {
        "title": "Home 1",
        "description": "Portal de notícias NewsEdge: destaques do dia, política, esportes, tecnologia e lifestyle em pt-BR.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index-2.html": {
        "title": "Home 1",
        "description": "Portal de notícias NewsEdge: destaques do dia, política, esportes, tecnologia e lifestyle em pt-BR.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index2.html": {
        "title": "Home 2",
        "description": "Home alternativa do NewsEdge com mosaico de destaques, ticker e seções por categoria.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index3.html": {
        "title": "Home 3",
        "description": "Layout home 3 do NewsEdge com hero, categorias e blocos de vídeo.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index4.html": {
        "title": "Home 4",
        "description": "Home 4 NewsEdge: notícias em carrossel, trending e sidebar editorial.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index5.html": {
        "title": "Home 5",
        "description": "Home 5 NewsEdge com isotope highlights e widgets de redes sociais.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index6.html": {
        "title": "Home 6",
        "description": "Home 6 NewsEdge: featured section, reviews e últimos artigos.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "index7.html": {
        "title": "Home 7",
        "description": "Home 7 NewsEdge com slider Nivo e cobertura internacional.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "post-style-1.html": {
        "title": "Listagem de posts — estilo 1",
        "description": "Arquivo de notícias no estilo 1: cards, categorias e filtros editoriais do NewsEdge.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "post-style-2.html": {
        "title": "Listagem de posts — estilo 2",
        "description": "Listagem estilo 2 com media list e destaques por categoria.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "post-style-3.html": {
        "title": "Listagem de posts — estilo 3",
        "description": "Listagem estilo 3 do NewsEdge com overlay cards e sidebar.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "post-style-4.html": {
        "title": "Listagem de posts — estilo 4",
        "description": "Listagem estilo 4: grade de notícias e banners editoriais.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "single-news-1.html": {
        "title": "Detalhe da notícia — estilo 1",
        "description": "Página de artigo NewsEdge com corpo da matéria, tags, compartilhamento e comentários.",
        "type": "article",
        "schema": "article",
        "robots": "index,follow",
    },
    "single-news-2.html": {
        "title": "Detalhe da notícia — estilo 2",
        "description": "Artigo estilo 2: hero, autor, posts relacionados e sidebar do portal.",
        "type": "article",
        "schema": "article",
        "robots": "index,follow",
    },
    "single-news-3.html": {
        "title": "Detalhe da notícia — estilo 3",
        "description": "Artigo estilo 3 NewsEdge com navegação anterior/próximo e share.",
        "type": "article",
        "schema": "article",
        "robots": "index,follow",
    },
    "single-news-4.html": {
        "title": "Detalhe da notícia — estilo 4",
        "description": "Artigo estilo 4 com layout alternativo de matéria e widgets laterais.",
        "type": "article",
        "schema": "article",
        "robots": "index,follow",
    },
    "archive.html": {
        "title": "Arquivo de notícias",
        "description": "Arquivo filtrável por ano, mês e categoria no portal NewsEdge.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "author-post.html": {
        "title": "Posts do autor",
        "description": "Página de autor NewsEdge com bio, redes sociais e artigos publicados.",
        "type": "profile",
        "schema": "collection",
        "robots": "index,follow",
    },
    "gallery-style-1.html": {
        "title": "Galeria — estilo 1",
        "description": "Galeria de imagens estilo 1 do NewsEdge com lightbox e categorias.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "gallery-style-2.html": {
        "title": "Galeria — estilo 2",
        "description": "Galeria estilo 2 com grade de fotos e filtros editoriais.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "gallery-style1.html": {
        "title": "Galeria — estilo 1 (alt)",
        "description": "Variante de galeria estilo 1 do template NewsEdge.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "gallery-style2.html": {
        "title": "Galeria — estilo 2 (alt)",
        "description": "Variante de galeria estilo 2 do template NewsEdge.",
        "type": "website",
        "schema": "collection",
        "robots": "index,follow",
    },
    "contact.html": {
        "title": "Contato",
        "description": "Fale com a redação NewsEdge: formulário de contato e informações do portal.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
    "404.html": {
        "title": "Página não encontrada",
        "description": "Erro 404 — a página solicitada não existe no portal NewsEdge.",
        "type": "website",
        "schema": "home",
        "robots": "noindex,follow",
    },
    "privacy.html": {
        "title": "Política de Privacidade",
        "description": "Política de privacidade e cookies do NewsEdge: LGPD, preferências e Consent Mode.",
        "type": "website",
        "schema": "home",
        "robots": "index,follow",
    },
}

CMP_MARKUP = """
        <!-- NewsEdge CMP Start -->
        <div id="newsedge-cmp-banner" class="ne-cmp-banner" role="dialog" aria-modal="true" aria-labelledby="ne-cmp-title" aria-describedby="ne-cmp-desc">
            <div class="ne-cmp-inner">
                <div class="ne-cmp-copy">
                    <h2 id="ne-cmp-title">Preferências de cookies e privacidade</h2>
                    <p id="ne-cmp-desc">Usamos cookies essenciais e, com seu consentimento, cookies de analytics e publicidade. Você pode aceitar tudo, manter apenas o básico ou recusar cookies não essenciais. Consulte a <a href="privacy.html">Política de Privacidade</a>.</p>
                </div>
                <div class="ne-cmp-actions">
                    <button type="button" class="ne-cmp-btn ne-cmp-btn-ghost" data-cmp-action="open-preferences">Gerenciar preferências</button>
                    <button type="button" class="ne-cmp-btn" data-cmp-action="deny">Recusar</button>
                    <button type="button" class="ne-cmp-btn" data-cmp-action="accept-basic">Básico</button>
                    <button type="button" class="ne-cmp-btn ne-cmp-btn-primary" data-cmp-action="accept-all">Aceitar tudo</button>
                </div>
            </div>
        </div>
        <div id="newsedge-cmp-modal" class="ne-cmp-modal" role="dialog" aria-modal="true" aria-labelledby="ne-cmp-modal-title" hidden>
            <div class="ne-cmp-dialog">
                <h2 id="ne-cmp-modal-title">Gerenciar preferências</h2>
                <fieldset>
                    <label><input type="checkbox" checked disabled> <span>Essenciais <small>Necessários para segurança, tema e lembrar sua escolha.</small></span></label>
                    <label><input type="checkbox" name="cmp-analytics"> <span>Analytics <small>Google Analytics (GA4) para medir audiência.</small></span></label>
                    <label><input type="checkbox" name="cmp-advertising"> <span>Publicidade <small>Google Ads / banners personalizados.</small></span></label>
                    <label><input type="checkbox" name="cmp-personalization"> <span>Preferências <small>Personalização leve de experiência (ex.: tema).</small></span></label>
                </fieldset>
                <div class="ne-cmp-dialog-actions">
                    <button type="button" class="ne-cmp-btn ne-cmp-close" data-cmp-action="close-preferences">Fechar</button>
                    <button type="button" class="ne-cmp-btn ne-cmp-btn-primary" data-cmp-action="save-preferences">Salvar preferências</button>
                </div>
            </div>
        </div>
        <!-- NewsEdge CMP End -->
"""

CONSENT_DEFAULT_SCRIPT = """
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('consent', 'default', {
          ad_storage: 'denied',
          ad_user_data: 'denied',
          ad_personalization: 'denied',
          analytics_storage: 'denied',
          functionality_storage: 'granted',
          personalization_storage: 'denied',
          security_storage: 'granted',
          wait_for_update: 500
        });
        window.NewsEdgeAnalyticsConfig = window.NewsEdgeAnalyticsConfig || { measurementId: 'G-XXXXXXXXXX' };
        </script>
"""


def strip_existing_seo_blocks(html: str) -> str:
    html = re.sub(
        r"\n?\s*<!-- NewsEdge SEO Start -->.*?<!-- NewsEdge SEO End -->\n?",
        "\n",
        html,
        flags=re.S,
    )
    html = re.sub(
        r"\n?\s*<!-- NewsEdge CMP Start -->.*?<!-- NewsEdge CMP End -->\n?",
        "\n",
        html,
        flags=re.S,
    )
    html = re.sub(
        r'\s*<link rel="stylesheet" href="css/consent\.css">\s*',
        "\n",
        html,
    )
    html = re.sub(
        r"\s*<script>\s*window\.dataLayer = window\.dataLayer \|\| \[\];.*?</script>\s*",
        "\n",
        html,
        flags=re.S,
    )
    html = re.sub(r'\s*<script src="js/consent\.js"[^>]*>\s*</script>\s*', "\n", html)
    html = re.sub(r'\s*<script src="js/analytics\.js"[^>]*>\s*</script>\s*', "\n", html)
    html = re.sub(
        r'\s*<p class="ne-cmp-footer-link-wrap">.*?</p>\s*',
        "\n",
        html,
        flags=re.S,
    )
    return html


def build_json_ld(meta: dict, page: str, title: str, description: str, canonical: str) -> str:
    org = {
        "@type": "NewsMediaOrganization",
        "name": SITE_NAME,
        "url": SITE_BASE,
        "logo": DEFAULT_OG_IMAGE,
    }
    if meta["schema"] == "article":
        data = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": title,
            "description": description,
            "image": [DEFAULT_OG_IMAGE],
            "datePublished": "2026-07-14",
            "dateModified": "2026-07-14",
            "author": {"@type": "Person", "name": "Redação NewsEdge"},
            "publisher": org,
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "inLanguage": "pt-BR",
        }
        breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_BASE}/"},
                {"@type": "ListItem", "position": 2, "name": title, "item": canonical},
            ],
        }
        return (
            f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'
            f'        <script type="application/ld+json">{json.dumps(breadcrumb, ensure_ascii=False)}</script>'
        )
    if meta["schema"] == "collection":
        data = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": description,
            "url": canonical,
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_BASE},
            "inLanguage": "pt-BR",
        }
        return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": SITE_BASE,
                "inLanguage": "pt-BR",
                "potentialAction": {
                    "@type": "SearchAction",
                    "target": f"{SITE_BASE}/?s={{search_term_string}}",
                    "query-input": "required name=search_term_string",
                },
            },
            org,
        ],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def build_seo_block(page: str, meta: dict) -> str:
    page_title = meta["title"]
    full_title = f"{SITE_NAME} | {page_title}"
    description = meta["description"]
    canonical = f"{SITE_BASE}/{page}"
    og_type = meta["type"]
    robots = meta["robots"]
    json_ld = build_json_ld(meta, page, full_title, description, canonical)
    return f"""        <!-- NewsEdge SEO Start -->
        <meta name="description" content="{description}">
        <meta name="robots" content="{robots}">
        <link rel="canonical" href="{canonical}">
        <meta property="og:type" content="{og_type}">
        <meta property="og:site_name" content="{SITE_NAME}">
        <meta property="og:locale" content="pt_BR">
        <meta property="og:title" content="{full_title}">
        <meta property="og:description" content="{description}">
        <meta property="og:url" content="{canonical}">
        <meta property="og:image" content="{DEFAULT_OG_IMAGE}">
        <meta property="og:image:width" content="1200">
        <meta property="og:image:height" content="630">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{full_title}">
        <meta name="twitter:description" content="{description}">
        <meta name="twitter:image" content="{DEFAULT_OG_IMAGE}">
        <link rel="apple-touch-icon" href="img/favicon.png">
        <meta name="theme-color" content="#99cc00">
        {json_ld}
        <!-- NewsEdge SEO End -->
"""


def enhance_images(html: str) -> str:
    # Ad banners: ensure alt="Publicidade"
    def fix_ad_img(m: re.Match) -> str:
        tag = m.group(0)
        if re.search(r'alt=["\']\s*["\']', tag) or "alt=" not in tag:
            tag = re.sub(r'\s*alt=["\'][^"\']*["\']', "", tag)
            tag = tag.replace("<img", '<img alt="Publicidade"', 1)
        if "loading=" not in tag:
            tag = tag.replace("<img", '<img loading="lazy" decoding="async"', 1)
        return tag

    html = re.sub(
        r'<div[^>]*data-widget-type="ad-banner"[^>]*>[\s\S]*?</div>',
        lambda m: re.sub(r"<img\b[^>]*>", fix_ad_img, m.group(0)),
        html,
    )

    # Generic empty alt -> descriptive fallback for news images
    def fix_img(m: re.Match) -> str:
        tag = m.group(0)
        # Skip if already processed with loading/fetchpriority
        if 'alt=""' in tag or "alt=''" in tag:
            src = re.search(r'src=["\']([^"\']+)["\']', tag)
            name = Path(src.group(1)).stem.replace("-", " ").replace("_", " ") if src else "imagem"
            tag = re.sub(r'alt=["\']["\']', f'alt="{name}"', tag)
        if re.search(r'data-widget-id="[^"]*\.hero"', tag) or "hero" in tag.lower():
            if "fetchpriority=" not in tag:
                tag = tag.replace("<img", '<img fetchpriority="high"', 1)
            return tag
        # Add lazy to content images without loading attr (skip logo/favicon-like in head is N/A)
        if "loading=" not in tag and "fetchpriority=" not in tag:
            # Avoid lazy on logo in header roughly
            if "logo" in tag.lower():
                return tag
            tag = tag.replace("<img", '<img loading="lazy" decoding="async"', 1)
        return tag

    html = re.sub(r"<img\b[^>]*>", fix_img, html)
    return html


def enhance_tags(html: str) -> str:
    # Add rel="tag" to links inside article-tags widget
    def tag_block(m: re.Match) -> str:
        block = m.group(0)

        def add_rel(am: re.Match) -> str:
            a = am.group(0)
            if "rel=" in a:
                return a
            return a.replace("<a ", '<a rel="tag" ', 1)

        return re.sub(r"<a\b[^>]*>", add_rel, block)

    html = re.sub(
        r'<ul[^>]*data-widget-type="article-tags"[^>]*>[\s\S]*?</ul>',
        tag_block,
        html,
        flags=re.I,
    )
    # Also blog-tags without data-widget on some pages
    html = re.sub(
        r'<ul[^>]*class="[^"]*blog-tags[^"]*"[^>]*>[\s\S]*?</ul>',
        tag_block,
        html,
        flags=re.I,
    )
    return html


def inject_footer_cookie_link(html: str) -> str:
    if "ne-cmp-footer-link" in html:
        return html
    link = (
        '<p class="ne-cmp-footer-link-wrap">'
        '<a href="privacy.html" class="ne-cmp-footer-link">Política de Privacidade</a>'
        " · "
        '<button type="button" class="ne-cmp-btn ne-cmp-btn-ghost ne-cmp-footer-link" data-cmp-action="open-preferences">Preferências de cookies</button>'
        "</p>"
    )
    # Insert before copyright paragraph if present
    html2, n = re.subn(
        r"(<p>©[^<]*</p>)",
        link + r"\n                                \1",
        html,
        count=1,
    )
    if n:
        return html2
    # Else before </footer>
    return html.replace("</footer>", link + "\n            </footer>", 1)


def process_file(path: Path) -> bool:
    name = path.name
    meta = PAGE_META.get(name)
    if not meta:
        print(f"skip (no meta): {name}")
        return False

    html = path.read_text(encoding="utf-8")
    html = strip_existing_seo_blocks(html)

    # lang
    html = re.sub(r"<html([^>]*)>", r'<html\1 lang="pt-BR">', html, count=1)
    html = html.replace('lang="" lang="pt-BR"', 'lang="pt-BR"')
    html = re.sub(r'lang="[^"]*"\s+lang="pt-BR"', 'lang="pt-BR"', html)

    full_title = f"{SITE_NAME} | {meta['title']}"
    html = re.sub(r"<title>[^<]*</title>", f"<title>{full_title}</title>", html, count=1)

    # Remove old empty meta description (we'll inject in SEO block)
    html = re.sub(
        r'\s*<meta name="description" content="[^"]*">\s*',
        "\n",
        html,
        count=1,
    )

    seo = build_seo_block(name, meta)
    # Insert after viewport meta
    html = re.sub(
        r'(<meta name="viewport"[^>]*>)',
        r"\1\n" + seo,
        html,
        count=1,
    )

    # consent.css after variables.css or style.css
    if 'href="css/consent.css"' not in html:
        html = html.replace(
            '<link rel="stylesheet" href="style.css">',
            '<link rel="stylesheet" href="style.css">\n        <link rel="stylesheet" href="css/consent.css">',
            1,
        )

    # Consent defaults early in head (after anti-FOUC or before modernizr)
    if "NewsEdgeAnalyticsConfig" not in html:
        html = html.replace(
            '<script src="js/modernizr-2.8.3.min.js"></script>',
            CONSENT_DEFAULT_SCRIPT + '\n        <script src="js/modernizr-2.8.3.min.js"></script>',
            1,
        )

    html = enhance_images(html)
    html = enhance_tags(html)
    html = inject_footer_cookie_link(html)

    if "newsedge-cmp-banner" not in html:
        html = html.replace("</body>", CMP_MARKUP + "\n    </body>", 1)

    # Scripts before </body>
    if 'src="js/consent.js"' not in html:
        html = html.replace(
            "</body>",
            '        <script src="js/consent.js" type="text/javascript"></script>\n'
            '        <script src="js/analytics.js" type="text/javascript"></script>\n'
            "    </body>",
            1,
        )

    path.write_text(html, encoding="utf-8")
    print(f"updated: {name}")
    return True


def main() -> None:
    count = 0
    for path in sorted(ROOT.glob("*.html")):
        if process_file(path):
            count += 1
    print(f"done: {count} pages")


if __name__ == "__main__":
    main()
