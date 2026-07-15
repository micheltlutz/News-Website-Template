#!/usr/bin/env python3
"""Auditoria estrutural NM-17 — 4 jornadas a11y."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

Journey = tuple[str, str, list[tuple[str, callable]]]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8", errors="replace")


def ok(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def main() -> int:
    errors: list[str] = []

    # 1 Home
    home = read("index.html")
    ok("skip-link" in home and 'href="#conteudo"' in home, "home: skip-link", errors)
    ok('id="conteudo"' in home, "home: main#conteudo", errors)
    ok('aria-label="Menu principal"' in home, "home: nav label", errors)
    ok("ne-ticker-pause" in home, "home: ticker pause", errors)
    ok('id="top-search-input"' in home, "home: search input", errors)

    # 2 Artigo
    for name in ("single-news-1.html", "single-news-2.html", "single-news-3.html"):
        t = read(name)
        h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", t, flags=re.S | re.I)
        ok(len(h1s) == 1, f"{name}: exatamente 1 H1 (tem {len(h1s)})", errors)
        if h1s:
            title = re.sub(r"\s+", " ", h1s[0]).strip().lower()
            ok("comment" not in title, f"{name}: H1 não deve ser Comments", errors)
        ok('id="comment-name"' in t or 'aria-label="Nome"' in t, f"{name}: comment labels", errors)

    # 3 Busca
    ok('aria-label="Abrir busca"' in home or 'aria-label="Buscar no site"' in home, "busca: botão/input nomeados", errors)

    # 4 Contato
    contact = read("contact.html")
    ok('for="form-name"' in contact or 'aria-label="Nome"' in contact, "contato: nome", errors)
    ok("form-email" in contact, "contato: email", errors)
    ok("form-message" in contact, "contato: mensagem", errors)

    # CMP / declaração
    ok(Path(ROOT / "acessibilidade.html").exists(), "acessibilidade.html existe", errors)
    ok("trapFocus" in read("js/consent.js"), "CMP focus trap", errors)
    ok("prefers-reduced-motion" in read("style.css"), "reduced-motion CSS", errors)
    ok("Slide anterior" in read("js/main.js"), "owl aria-labels", errors)

    # Coverage sample
    pages = [p for p in ROOT.glob("*.html") if "<body" in p.read_text(encoding="utf-8", errors="replace")]
    missing_skip = [p.name for p in pages if "skip-link" not in p.read_text(encoding="utf-8", errors="replace")]
    ok(not missing_skip, f"skip-link ausente em: {missing_skip}", errors)

    if errors:
        print("FAIL NM-17 audit:")
        for e in errors:
            print(" -", e)
        return 1
    print(f"PASS NM-17 audit ({len(pages)} páginas com <body>)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
