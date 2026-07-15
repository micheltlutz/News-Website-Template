#!/usr/bin/env python3
"""Aplica patches de a11y por camada (NM-13..NM-16)."""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("patch_a11y", ROOT / "scripts" / "patch_a11y.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)

LAYERS = {
    "nm13": [
        "patch_search",
        "patch_offcanvas",
        "patch_login_modal",
        "patch_newsletter",
        "patch_contact",
        "patch_archive",
        "patch_comments",
    ],
    "nm14": [
        "patch_breadcrumb",
        "patch_article_h1",
        "patch_home_h1",
        "patch_social_aria",
        "patch_decorative_alts",
    ],
    "nm15": [
        "patch_ticker_pause_slot",
    ],
    "nm16": [
        "patch_pages_menu_a11y",
        "patch_footer_a11y_link",
        "patch_footer_a11y_fallback",
    ],
}


def patch_footer_a11y_fallback(text: str, changes: list[str]) -> str:
    """Upstream footers without CMP wrap."""
    if "acessibilidade.html" in text:
        return text
    # Common copyright / footer link lists
    needles = [
        ('<a href="privacy.html">Privacy</a>', '<a href="acessibilidade.html">Acessibilidade</a> · <a href="privacy.html">Privacy</a>'),
        ('<a href="contact.html">Contact</a>', '<a href="acessibilidade.html">Acessibilidade</a> · <a href="contact.html">Contact</a>'),
    ]
    for old, new in needles:
        if old in text:
            text = text.replace(old, new, 1)
            changes.append("footer-a11y-fallback")
            break
    return text


def patch_main_shell(text: str, changes: list[str]) -> str:
    """NM-14 homes/articles need <main> for H1 insertion; keep minimal."""
    return mod.patch_main(text, changes)


def transform_layer(path: Path, layer: str) -> list[str]:
    name = path.name
    text = path.read_text(encoding="utf-8")
    changes: list[str] = []

    # home-h1 depends on main landmark
    if layer == "nm14":
        text = mod.patch_skip(text, changes)
        text = mod.patch_nav(text, changes)
        text = mod.patch_main(text, changes)
        text = mod.patch_sidebar(text, changes)

    for fn_name in LAYERS[layer]:
        if fn_name == "patch_footer_a11y_fallback":
            text = patch_footer_a11y_fallback(text, changes)
            continue
        fn = getattr(mod, fn_name)
        if fn_name in {"patch_breadcrumb", "patch_article_h1", "patch_home_h1", "patch_contact", "patch_archive", "patch_comments"}:
            text = fn(text, name, changes)
        else:
            text = fn(text, changes)

    path.write_text(text, encoding="utf-8")
    return changes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("layer", choices=sorted(LAYERS))
    args = ap.parse_args()
    for f in sorted(ROOT.glob("*.html")):
        ch = transform_layer(f, args.layer)
        print(f"{f.name}: {', '.join(ch) if ch else '(no changes)'}")


if __name__ == "__main__":
    main()
