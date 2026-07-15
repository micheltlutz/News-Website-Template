#!/usr/bin/env python3
"""Batch a11y patches for News-Website-Template HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PAGES = {
    "single-news-1.html",
    "single-news-2.html",
    "single-news-3.html",
    "single-news-4.html",
}
HOME_PAGES = {
    "index.html",
    "index-2.html",
    "index2.html",
    "index3.html",
    "index4.html",
    "index5.html",
    "index6.html",
    "index7.html",
}
SKIP = '        <a class="skip-link visuallyhidden focusable" href="#conteudo">Ir para o conteúdo</a>'

TITLE_MAP = {
    "fa-facebook": "Facebook",
    "fa-twitter": "Twitter",
    "fa-google-plus": "Google Plus",
    "fa-linkedin": "LinkedIn",
    "fa-pinterest": "Pinterest",
    "fa-rss": "RSS",
    "fa-vimeo": "Vimeo",
    "fa-youtube": "YouTube",
    "fa-instagram": "Instagram",
}


def replace_once(text: str, pattern: str, repl: str, flags=0) -> tuple[str, bool]:
    out, n = re.subn(pattern, repl, text, count=1, flags=flags)
    return out, n > 0


def patch_skip(text: str, changes: list[str]) -> str:
    if 'class="skip-link' in text:
        return text
    text, ok = replace_once(text, r"<body>", "<body>\n" + SKIP)
    if ok:
        changes.append("skip")
    return text


def patch_nav(text: str, changes: list[str]) -> str:
    if 'aria-label="Menu principal"' in text:
        return text
    text, ok = replace_once(
        text,
        r'(<nav id="dropdown")(\s*>)',
        r'\1 aria-label="Menu principal"\2',
    )
    if ok:
        changes.append("nav")
    return text


def patch_search(text: str, changes: list[str]) -> str:
    if 'id="top-search-input"' in text:
        return text
    text, ok = replace_once(
        text,
        r'<form id="top-search-form" class="header-search-light">\s*'
        r'<input type="text" class="search-input"[^>]*>\s*'
        r'<button class="search-button">\s*'
        r'<i class="fa fa-search" aria-hidden="true"></i>\s*'
        r"</button>\s*</form>",
        """<form id="top-search-form" class="header-search-light" role="search">
                                                    <label class="visuallyhidden" for="top-search-input">Buscar no site</label>
                                                    <input type="search" id="top-search-input" class="search-input" name="s" placeholder="Buscar...." required="" style="display: none;" aria-label="Buscar no site">
                                                    <button type="button" class="search-button" aria-label="Abrir busca" aria-expanded="false" aria-controls="top-search-input">
                                                        <i class="fa fa-search" aria-hidden="true"></i>
                                                    </button>
                                                </form>""",
        flags=re.S,
    )
    if ok:
        changes.append("search")
    return text


def patch_offcanvas(text: str, changes: list[str]) -> str:
    if 'aria-controls="offcanvas-body-wrapper"' not in text and "side-menu-trigger" in text:
        text, ok = replace_once(
            text,
            r'<div id="side-menu-trigger" class="offcanvas-menu-btn">\s*'
            r'<a href="#" class="menu-bar">\s*'
            r"<span></span>\s*<span></span>\s*<span></span>\s*"
            r"</a>\s*"
            r'<a href="#" class="menu-times close">\s*'
            r"<span></span>\s*<span></span>\s*"
            r"</a>\s*</div>",
            """<div id="side-menu-trigger" class="offcanvas-menu-btn">
                                                    <button type="button" class="menu-bar" aria-label="Abrir menu lateral" aria-expanded="false" aria-controls="offcanvas-body-wrapper">
                                                        <span></span>
                                                        <span></span>
                                                        <span></span>
                                                    </button>
                                                    <button type="button" class="menu-times close" aria-label="Fechar menu lateral" hidden>
                                                        <span></span>
                                                        <span></span>
                                                    </button>
                                                </div>""",
            flags=re.S,
        )
        if ok:
            changes.append("oc-trig")

    if 'class="menu-times re-point"' in text and "<button type=\"button\" class=\"menu-times re-point\"" not in text:
        text, ok = replace_once(
            text,
            r'<div id="offcanvas-nav-close" class="offcanvas-nav-close offcanvas-menu-btn">\s*'
            r'<a href="#" class="menu-times re-point">\s*'
            r"<span></span>\s*<span></span>\s*"
            r"</a>\s*</div>",
            """<div id="offcanvas-nav-close" class="offcanvas-nav-close offcanvas-menu-btn">
                    <button type="button" class="menu-times re-point" aria-label="Fechar menu lateral">
                        <span></span>
                        <span></span>
                    </button>
                </div>""",
            flags=re.S,
        )
        if ok:
            changes.append("oc-close")
    return text


def patch_main(text: str, changes: list[str]) -> str:
    if 'id="conteudo"' in text:
        return text
    if "<!-- Header Area End Here -->" not in text:
        return text
    text = text.replace(
        "<!-- Header Area End Here -->",
        '<!-- Header Area End Here -->\n            <main id="conteudo">',
        1,
    )
    if "<!-- Footer Area Start Here -->" in text:
        text = text.replace(
            "<!-- Footer Area Start Here -->",
            '</main>\n            <!-- Footer Area Start Here -->',
            1,
        )
    else:
        text, _ = replace_once(text, r"(\n[ \t]*<footer\b)", r"\n            </main>\1")
    changes.append("main")
    return text


def patch_sidebar(text: str, changes: list[str]) -> str:
    if 'aria-label="Barra lateral"' in text:
        return text
    text2, n = re.subn(
        r'<div class="ne-sidebar([^"]*)">',
        r'<div class="ne-sidebar\1" role="complementary" aria-label="Barra lateral">',
        text,
    )
    if n:
        changes.append(f"sidebar:{n}")
        return text2
    return text


def patch_breadcrumb(text: str, name: str, changes: list[str]) -> str:
    if 'aria-label="Breadcrumb"' in text:
        return text
    if "breadcrumbs-content" not in text:
        return text

    def repl(m: re.Match) -> str:
        inner = m.group(1)
        # demote h1 to p for articles so article headline can be the H1
        if name in ARTICLE_PAGES:
            inner = re.sub(
                r"<h1>(.*?)</h1>",
                r'<p class="breadcrumbs-heading">\1</p>',
                inner,
                count=1,
                flags=re.S,
            )
        # wrap list as nav semantics; keep ul for CSS, mark last item
        def fix_ul(um: re.Match) -> str:
            items = um.group(0)
            # strip trailing " -" from li text noise is OK for SR with aria-hidden separators later
            # mark last li without link as current
            parts = re.split(r"(</li>)", items)
            # find last <li>...</li> that has no <a>
            lis = list(re.finditer(r"<li>(.*?)</li>", items, flags=re.S))
            if not lis:
                return items
            last = lis[-1]
            last_inner = last.group(1)
            if "<a " not in last_inner and "aria-current" not in last_inner:
                new_last = f'<li aria-current="page">{last_inner}</li>'
                items = items[: last.start()] + new_last + items[last.end() :]
            return items

        inner = re.sub(r"<ul>.*?</ul>", fix_ul, inner, count=1, flags=re.S)
        return f'<nav class="breadcrumbs-content" aria-label="Breadcrumb">{inner}</nav>'

    text2, n = re.subn(
        r'<div class="breadcrumbs-content">(.*?)</div>',
        repl,
        text,
        count=1,
        flags=re.S,
    )
    if n:
        changes.append("breadcrumb")
        return text2
    return text


def patch_article_h1(text: str, name: str, changes: list[str]) -> str:
    if name not in ARTICLE_PAGES:
        return text
    m = re.search(
        r'(class="news-details-layout\d+"[^>]*>[\s\S]*?)(<h2 class="title-semibold-dark[^"]*">)([\s\S]*?)(</h2>)',
        text,
    )
    if m:
        text = (
            text[: m.start(2)]
            + m.group(2).replace("<h2", "<h1", 1)
            + m.group(3)
            + "</h1>"
            + text[m.end(4) :]
        )
        changes.append("article-h1")
    return text


def patch_home_h1(text: str, name: str, changes: list[str]) -> str:
    if name not in HOME_PAGES:
        return text
    if 'class="visuallyhidden site-page-title"' in text:
        return text
    # Ensure a single clear page H1 for SR if missing meaningful one (index7 has 0)
    h1s = re.findall(r"<h1\b", text, flags=re.I)
    if name == "index7.html" or not h1s:
        text = text.replace(
            '<main id="conteudo">',
            '<main id="conteudo">\n                <h1 class="visuallyhidden site-page-title">NewsEdge — Início</h1>',
            1,
        )
        changes.append("home-h1")
    return text


def patch_footer_a11y_link(text: str, changes: list[str]) -> str:
    if "acessibilidade.html" in text and 'ne-cmp-footer-link">Acessibilidade' in text:
        return text
    old = (
        '<p class="ne-cmp-footer-link-wrap"><a href="privacy.html" class="ne-cmp-footer-link">'
        "Política de Privacidade</a>"
    )
    new = (
        '<p class="ne-cmp-footer-link-wrap">'
        '<a href="acessibilidade.html" class="ne-cmp-footer-link">Acessibilidade</a> · '
        '<a href="privacy.html" class="ne-cmp-footer-link">Política de Privacidade</a>'
    )
    if old in text:
        text = text.replace(old, new)
        changes.append("footer-a11y")
    return text


def patch_login_modal(text: str, changes: list[str]) -> str:
    if 'id="login-username"' in text:
        return text
    if 'id="myModal"' not in text:
        return text
    text, ok = replace_once(
        text,
        r'<div class="modal fade" id="myModal" role="dialog">\s*'
        r'<div class="modal-dialog">\s*'
        r'<div class="modal-content">\s*'
        r'<div class="modal-header">\s*'
        r'<button type="button" class="close" data-dismiss="modal">&times;</button>\s*'
        r'<div class="title-login-form">Login</div>\s*'
        r"</div>\s*"
        r'<div class="modal-body">\s*'
        r'<div class="login-form">\s*'
        r"<form>\s*"
        r"<label>Username or email address \*</label>\s*"
        r'<input type="text" placeholder="Name or E-mail" />\s*'
        r"<label>Password \*</label>\s*"
        r'<input type="password" placeholder="Password" />\s*'
        r'<div class="checkbox checkbox-primary">\s*'
        r'<input id="checkbox" type="checkbox" checked>\s*'
        r'<label for="checkbox">Remember Me</label>\s*'
        r"</div>\s*"
        r'<button type="submit" value="Login">Login</button>\s*'
        r'<button class="form-cancel" type="submit" value="">Cancel</button>\s*'
        r'<label class="lost-password">\s*'
        r'<a href="#">Lost your password\?</a>\s*'
        r"</label>\s*"
        r"</form>",
        """<div class="modal fade" id="myModal" role="dialog" aria-modal="true" aria-labelledby="login-modal-title">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Fechar">&times;</button>
                            <div class="title-login-form" id="login-modal-title">Login</div>
                        </div>
                        <div class="modal-body">
                            <div class="login-form">
                                <form>
                                    <label for="login-username">Username or email address *</label>
                                    <input id="login-username" type="text" name="username" placeholder="Name or E-mail" autocomplete="username" required />
                                    <label for="login-password">Password *</label>
                                    <input id="login-password" type="password" name="password" placeholder="Password" autocomplete="current-password" required />
                                    <div class="checkbox checkbox-primary">
                                        <input id="checkbox" type="checkbox" checked>
                                        <label for="checkbox">Remember Me</label>
                                    </div>
                                    <button type="submit" value="Login">Login</button>
                                    <button class="form-cancel" type="button" data-dismiss="modal" value="">Cancel</button>
                                    <label class="lost-password">
                                        <a href="#">Lost your password?</a>
                                    </label>
                                </form>""",
        flags=re.S,
    )
    if ok:
        changes.append("login")
    return text


def patch_newsletter(text: str, changes: list[str]) -> str:
    if 'aria-label="E-mail para newsletter"' in text:
        return text
    text2, n = re.subn(
        r'(<div class="input-group stylish-input-group">\s*)'
        r'<input type="text" placeholder="Enter your mail" class="form-control">\s*'
        r'<span class="input-group-addon">\s*'
        r'<button type="submit">\s*'
        r'<i class="fa fa-angle-right" aria-hidden="true"></i>\s*'
        r"</button>",
        r'\1<input type="email" placeholder="Enter your mail" class="form-control" aria-label="E-mail para newsletter" name="email" autocomplete="email">\n'
        r'                                        <span class="input-group-addon">\n'
        r'                                            <button type="submit" aria-label="Assinar newsletter">\n'
        r'                                                <i class="fa fa-angle-right" aria-hidden="true"></i>\n'
        r"                                            </button>",
        text,
        flags=re.S,
    )
    if n:
        changes.append(f"newsletter:{n}")
        return text2
    return text


def patch_social_aria(text: str, changes: list[str]) -> str:
    n_total = 0

    def repl_title(m: re.Match) -> str:
        nonlocal n_total
        title = m.group(1)
        label = TITLE_MAP.get(
            next((k for k in TITLE_MAP if k.split("-")[-1] in title.lower() or title.lower() in k), ""),
            title.replace("-", " ").title(),
        )
        # map common title attrs
        mapping = {
            "facebook": "Facebook",
            "twitter": "Twitter",
            "google-plus": "Google Plus",
            "linkedin": "LinkedIn",
            "pinterest": "Pinterest",
            "rss": "RSS",
            "vimeo": "Vimeo",
            "youtube": "YouTube",
            "instagram": "Instagram",
        }
        label = mapping.get(title.lower(), title.replace("-", " ").title())
        n_total += 1
        return f'aria-label="{label}" title="{title}"'

    text2, n = re.subn(
        r'<a href="#" title="([^"]+)">(\s*<i class="fa fa-[^"]+" aria-hidden="true"></i>)',
        lambda m: f'<a href="#" aria-label="{ {"facebook":"Facebook","twitter":"Twitter","google-plus":"Google Plus","linkedin":"LinkedIn","pinterest":"Pinterest","rss":"RSS","vimeo":"Vimeo","youtube":"YouTube","instagram":"Instagram"}.get(m.group(1).lower(), m.group(1).replace("-"," ").title()) }" title="{m.group(1)}">{m.group(2)}',
        text,
    )
    if n:
        changes.append(f"social-title:{n}")
        text = text2

    # share links with class only
    for cls, label in {
        "facebook": "Facebook",
        "twitter": "Twitter",
        "google-plus": "Google Plus",
        "linkedin": "LinkedIn",
        "pinterest": "Pinterest",
        "rss": "RSS",
    }.items():
        text2, n = re.subn(
            rf'(<a href="#" class="{cls}")(?![^>]*aria-label)',
            rf'\1 aria-label="{label}"',
            text,
        )
        if n:
            text = text2
            n_total += n
    if n_total and "social-class" not in "".join(changes):
        changes.append(f"social-class:{n_total}")
    return text


def patch_decorative_alts(text: str, changes: list[str]) -> str:
    # Card thumbnails next to linked titles: generic alts -> empty
    text2, n1 = re.subn(
        r'(<a class="img-opacity-hover"[^>]*>\s*<img[^>]*\salt=")(?:news|post|ad)(")',
        r"\1\2",
        text,
        flags=re.S,
    )
    text2, n2 = re.subn(
        r'(<a href="[^"]*"[^>]*>\s*<img[^>]*\salt=")(?:news|post)(")',
        r"\1\2",
        text2,
        flags=re.S,
    )
    # logo already has alt=logo — improve once
    text2, n3 = re.subn(r'alt="logo"', 'alt="NewsEdge"', text2)
    if n1 or n2 or n3:
        changes.append(f"alts:{n1+n2+n3}")
        return text2
    return text


def patch_contact(text: str, name: str, changes: list[str]) -> str:
    if name != "contact.html":
        return text
    if 'for="form-name"' in text:
        return text
    text, ok = replace_once(
        text,
        r'<div class="form-group">\s*'
        r'<input type="text" placeholder="Name" class="form-control" name="name" id="form-subject"[^>]*>',
        """<div class="form-group">
                                                <label class="visuallyhidden" for="form-name">Nome</label>
                                                <input type="text" placeholder="Name" class="form-control" name="name" id="form-name" data-error="Name field is required"
                                                    required="" aria-label="Nome">""",
        flags=re.S,
    )
    if ok:
        text, _ = replace_once(
            text,
            r'(id="form-email"[^>]*)(>)',
            r'\1 aria-label="E-mail">',
        )
        # insert label before email if missing
        if 'for="form-email"' not in text:
            text = text.replace(
                '<input type="email" placeholder="Your E-mail"',
                '<label class="visuallyhidden" for="form-email">E-mail</label>\n                                                <input type="email" placeholder="Your E-mail"',
                1,
            )
        if 'for="form-message"' not in text:
            text = text.replace(
                '<textarea placeholder="Message"',
                '<label class="visuallyhidden" for="form-message">Mensagem</label>\n                                                <textarea placeholder="Message" aria-label="Mensagem"',
                1,
            )
        changes.append("contact-form")
    return text


def patch_archive(text: str, name: str, changes: list[str]) -> str:
    if name != "archive.html":
        return text
    if 'for="ne-year"' in text:
        return text
    for sel, label in (
        ("ne-year", "Ano"),
        ("ne-month", "Mês"),
        ("ne-date", "Dia"),
        ("ne-category", "Categoria"),
    ):
        if f'id="{sel}"' in text and f'for="{sel}"' not in text:
            text = text.replace(
                f'<select id="{sel}"',
                f'<label class="visuallyhidden" for="{sel}">{label}</label>\n                                                <select id="{sel}" aria-label="{label}"',
                1,
            )
            changes.append(f"archive-{sel}")
    return text


def patch_comments(text: str, name: str, changes: list[str]) -> str:
    if name not in ARTICLE_PAGES:
        return text
    if 'id="comment-name"' in text:
        return text
    if 'id="leave-comments"' not in text:
        return text
    text, ok = replace_once(
        text,
        r'<form id="leave-comments">\s*'
        r'<div class="row">\s*'
        r'<div class="col-md-4 col-sm-12">\s*'
        r'<div class="form-group">\s*'
        r'<input placeholder="Name\*" class="form-control" type="text">',
        """<form id="leave-comments">
                                        <div class="row">
                                            <div class="col-md-4 col-sm-12">
                                                <div class="form-group">
                                                    <label class="visuallyhidden" for="comment-name">Nome</label>
                                                    <input id="comment-name" name="name" placeholder="Name*" class="form-control" type="text" required aria-label="Nome">""",
        flags=re.S,
    )
    if not ok:
        return text
    text, _ = replace_once(
        text,
        r'<input placeholder="Email\*" class="form-control" type="email">',
        '<label class="visuallyhidden" for="comment-email">E-mail</label>\n                                                    <input id="comment-email" name="email" placeholder="Email*" class="form-control" type="email" required aria-label="E-mail">',
    )
    text, _ = replace_once(
        text,
        r'<input placeholder="Web Address" class="form-control" type="text">',
        '<label class="visuallyhidden" for="comment-website">Website</label>\n                                                    <input id="comment-website" name="website" placeholder="Web Address" class="form-control" type="url" aria-label="Website">',
    )
    text, _ = replace_once(
        text,
        r'<textarea placeholder="Message\*" class="textarea form-control" id="form-message"',
        '<label class="visuallyhidden" for="form-message">Mensagem</label>\n                                                    <textarea placeholder="Message*" class="textarea form-control" id="form-message" name="message" aria-label="Mensagem"',
    )
    changes.append("comments")
    return text


def patch_ticker_pause_slot(text: str, changes: list[str]) -> str:
    if 'class="ne-ticker-controls"' in text:
        return text
    if 'class="feeding-text-dark"' not in text and 'class="feeding-text"' not in text:
        return text
    # insert pause control before feeding-text
    text2, n = re.subn(
        r'(<div class="feeding-text(?:-dark)?">)',
        r'<div class="ne-ticker-controls">'
        r'<button type="button" class="ne-ticker-pause" aria-label="Pausar destaques" aria-pressed="false">'
        r'<i class="fa fa-pause" aria-hidden="true"></i><span class="visuallyhidden">Pausar</span>'
        r"</button></div>\n                            \1",
        text,
        count=1,
    )
    if n:
        changes.append("ticker-btn")
        return text2
    return text


def patch_pages_menu_a11y(text: str, changes: list[str]) -> str:
    # Only insert in primary nav Pages dropdown (before Politics / after Contact)
    if re.search(
        r'href="contact\.html">Contact Page</a>\s*</li>\s*<li>\s*<a href="acessibilidade\.html">',
        text,
    ):
        return text
    needle = '<a href="contact.html">Contact Page</a>'
    if needle not in text:
        return text
    text = text.replace(
        needle,
        needle
        + "\n                                                        </li>\n"
        + "                                                        <li>\n"
        + '                                                            <a href="acessibilidade.html">Acessibilidade</a>',
        1,
    )
    changes.append("menu-a11y")
    return text


def transform(path: Path) -> list[str]:
    name = path.name
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []
    text = patch_skip(text, changes)
    text = patch_nav(text, changes)
    text = patch_search(text, changes)
    text = patch_offcanvas(text, changes)
    text = patch_main(text, changes)
    text = patch_sidebar(text, changes)
    text = patch_breadcrumb(text, name, changes)
    text = patch_article_h1(text, name, changes)
    text = patch_home_h1(text, name, changes)
    text = patch_pages_menu_a11y(text, changes)
    text = patch_footer_a11y_link(text, changes)
    text = patch_login_modal(text, changes)
    text = patch_newsletter(text, changes)
    text = patch_social_aria(text, changes)
    text = patch_decorative_alts(text, changes)
    text = patch_contact(text, name, changes)
    text = patch_archive(text, name, changes)
    text = patch_comments(text, name, changes)
    text = patch_ticker_pause_slot(text, changes)
    path.write_text(text, encoding="utf-8")
    return changes


def main() -> None:
    files = sorted(ROOT.glob("*.html"))
    for f in files:
        ch = transform(f)
        print(f"{f.name}: {', '.join(ch) if ch else '(no changes / already)'}")


if __name__ == "__main__":
    main()
