#!/usr/bin/env python3
"""Traduz textos de topic-box / filtros visíveis / ctg-title para pt-BR."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# rótulo EN (ou typo) → PT-BR
LABELS: dict[str, str] = {
    # seções / UI
    "Top Stories": "Destaques",
    "Stay Connected": "Redes Sociais",
    "Newsletter": "Newsletter",
    "Tags": "Tags",
    "Recent News": "Notícias Recentes",
    "More News": "Mais Notícias",
    "Most Reviews": "Mais Avaliados",
    "Latest Reviews": "Últimas Avaliações",
    "Related Posts": "Posts Relacionados",
    "Watch Videos": "Assistir Vídeos",
    "Editor Picks": "Escolha do Editor",
    "Latest News": "Últimas Notícias",
    "Latest Article": "Último Artigo",
    "Latest Articles": "Últimos Artigos",
    "Trending Posts": "Em Alta",
    "Popular News": "Notícias Populares",
    "Popular Games": "Games Populares",
    "Popular Recipes": "Receitas Populares",
    "Games Reviews": "Reviews de Games",
    "Food Reviews": "Reviews Gastronômicos",
    "Racing World": "Mundo das Corridas",
    "What’s New": "Novidades",
    "What's New": "Novidades",
    "International": "Internacional",
    "Categories": "Categorias",
    "Archives": "Arquivo",
    "About Us": "Sobre Nós",
    "Location Info": "Localização",
    "Send Us Message": "Envie uma Mensagem",
    "All": "Todos",
    # categorias editoriais
    "Politics": "Política",
    "Fashion": "Moda",
    "Travel": "Viagem",
    "Gadget": "Gadget",
    "Gadgets": "Gadgets",
    "Fadgets": "Gadgets",
    "Sports": "Esportes",
    "Business": "Negócios",
    "Nature": "Natureza",
    "Technology": "Tecnologia",
    "Tech": "Tech",
    "Tech World": "Mundo Tech",
    "Life Style": "Lifestyle",
    "Lifestyle": "Lifestyle",
    "Food": "Gastronomia",
    "Food & Hobbbies": "Gastronomia & Hobbies",
    "Food & Hobbies": "Gastronomia & Hobbies",
    "Health & Fitness": "Saúde & Fitness",
    "Fitness": "Fitness",
    "Music": "Música",
    "Education": "Educação",
    "Accessories": "Acessórios",
    "Android": "Android",
    "Application": "Aplicativos",
    "Model": "Modelo",
    "Public": "Público",
    "Adventure": "Aventura",
    "Adventue": "Aventura",
    "Ventura": "Aventura",
    "Flower": "Flores",
    "Picture": "Foto",
    "Game": "Game",
    "Games": "Games",
    "Play": "Play",
    "Animation": "Animação",
    "cartoon": "Cartoon",
    "Action": "Ação",
    "Electronics": "Eletrônicos",
    "Electronic": "Eletrônicos",
    "Software": "Software",
    "Apple": "Apple",
    "Ipad": "iPad",
    "Camera": "Câmera",
    "World": "Mundo",
    "People": "Pessoas",
    "Corporate": "Corporativo",
    "Style Zone": "Style Zone",
    "Style zone": "Style Zone",
    "Style ZOne": "Style Zone",
    "Fashion Today": "Moda Hoje",
    "Daily Wear": "Dia a Dia",
    "Daily wear": "Dia a Dia",
    # esportes
    "Football": "Futebol",
    "Fotball": "Futebol",
    "Boxing": "Boxe",
    "Cycling": "Ciclismo",
    "Diving": "Mergulho",
    "Racing": "Corrida",
    "Race": "Corrida",
    "Riding": "Hipismo",
    "Rorse Rider": "Hipismo",
    "Horse Racing": "Turfe",
    "Bike Racing": "Motovelocidade",
    "Bike Riding": "Ciclismo",
    "Car Racing": "Automobilismo",
    "Ragbe": "Rúgbi",
    "Rugby": "Rúgbi",
    "Cricket": "Críquete",
    "Golf": "Golf",
    "Baseball": "Beisebol",
    "Tenis": "Tênis",
    "Tennies": "Tênis",
    "Tenies": "Tênis",
    "Swiming": "Natação",
    "Swimming": "Natação",
    "Boat": "Náutica",
    "Desert": "Deserto",
    # gastronomia
    "Drinks": "Bebidas",
    "Fast Food": "Fast Food",
    "Fastfood": "Fast Food",
    "Burger": "Hambúrguer",
    "Pizza": "Pizza",
    "Fruits": "Frutas",
    "Chines": "Chinesa",
    "Chinese": "Chinesa",
    "Beef Pizza": "Pizza de Carne",
    "Chicken Pizza": "Pizza de Frango",
    "Vegetable Roll": "Rolinho Vegetal",
    # outros
    "MaxRocket": "MaxRocket",
    "Maxrocket": "MaxRocket",
    "Maxrocke": "MaxRocket",
    "Sprts": "Esportes",
}

# screen-map.json label overrides (widget titles)
WIDGET_LABELS: dict[str, str] = {
    "Header": "Cabeçalho",
    "News Feed": "Ticker de Notícias",
    "Top Stories Ticker": "Ticker de Destaques",
    "News Info List": "Barra de Infos",
    "News Slider": "Slider de Notícias",
    "Top Stories": "Destaques",
    "Life Style": "Lifestyle",
    "Stay Connected": "Redes Sociais",
    "Sidebar Ad": "Anúncio Sidebar",
    "Sidebar Ad (2)": "Anúncio Sidebar (2)",
    "Recent News": "Notícias Recentes",
    "Banner After Top Story": "Banner Após Destaques",
    "Banner After Top Stories": "Banner Após Destaques",
    "Video Area": "Área de Vídeos",
    "Watch Videos": "Assistir Vídeos",
    "Tech World": "Mundo Tech",
    "Tech World (2)": "Mundo Tech (2)",
    "Health & Fitness": "Saúde & Fitness",
    "Banner Latest News": "Banner Últimas Notícias",
    "Sports": "Esportes",
    "More News": "Mais Notícias",
    "Newsletter": "Newsletter",
    "Category Area": "Área de Categorias",
    "Footer": "Rodapé",
    "International": "Internacional",
    "Editor Picks": "Escolha do Editor",
    "Fashion": "Moda",
    "Food & Hobbies": "Gastronomia & Hobbies",
    "Banner Category News": "Banner Categorias",
    "Latest Reviews": "Últimas Avaliações",
    "What's New": "Novidades",
    "Android": "Android",
    "Accessories": "Acessórios",
    "Gadgets": "Gadgets",
    "Latest News": "Últimas Notícias",
    "Most Reviews": "Mais Avaliados",
    "Popular Games": "Games Populares",
    "Games Reviews": "Reviews de Games",
    "Recent / Popular List": "Recentes / Populares",
    "Popular News": "Notícias Populares",
    "Racing World": "Mundo das Corridas",
    "Latest Article": "Último Artigo",
    "Categories": "Categorias",
    "Feature News": "Notícias em Destaque",
    "Latest Articles": "Últimos Artigos",
    "Trending Posts": "Em Alta",
    "Nivo Slider": "Slider Nivo",
    "Slider Side Stories": "Laterais do Slider",
    "Popular Recipes": "Receitas Populares",
    "Food Reviews": "Reviews Gastronômicos",
    "Recent / Popular / Common Tabs": "Abas Recentes / Populares",
    "Breadcrumb": "Breadcrumb",
    "Post Style 1 List": "Lista Post Style 1",
    "Post Style 2 Grid": "Grade Post Style 2",
    "Post Style 3 List": "Lista Post Style 3",
    "Post Style 4 Video List": "Lista Post Style 4",
    "Archive Search Filters": "Filtros de Arquivo",
    "Archive Posts": "Posts do Arquivo",
    "Archives": "Arquivo",
    "Author Profile": "Perfil do Autor",
    "Author Posts": "Posts do Autor",
    "Article Body": "Corpo do Artigo",
    "Article Tags": "Tags do Artigo",
    "Share Post": "Compartilhar",
    "Previous / Next Article": "Artigo Anterior / Próximo",
    "Author Box": "Box do Autor",
    "Comments + Leave Comment": "Comentários",
    "Article Hero Image": "Hero do Artigo",
    "Related Posts": "Posts Relacionados",
    "Inner Page Banner": "Banner Interno",
    "Gallery Layout 1": "Galeria Layout 1",
    "Gallery Layout 2 Masonry": "Galeria Layout 2",
    "About Us": "Sobre Nós",
    "Location Info": "Localização",
    "Send Us Message": "Envie uma Mensagem",
    "404 Error Message": "Mensagem 404",
}


def translate_topic_boxes(html: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        prefix, label, suffix = m.group(1), m.group(2), m.group(3)
        raw = label.replace("&amp;", "&")
        key = re.sub(r"\s+", " ", raw).strip()
        if key not in LABELS:
            return m.group(0)
        new = LABELS[key]
        if "&" in new:
            new = new.replace("&", "&amp;")
        if new == label or new == raw:
            # still count typo fixes where display equals after amp normalize
            if key != LABELS[key] and LABELS[key] == raw:
                return m.group(0)
        count += 1
        out_label = LABELS[key]
        if "&" in out_label and "&amp;" not in html[m.start() : m.end()]:
            # keep amp encoding if original used it for Health & Fitness etc.
            pass
        encoded = out_label.replace("&", "&amp;") if ("&amp;" in label or "&" in out_label) else out_label
        # Prefer &amp; in HTML when label contains &
        if "&" in out_label:
            encoded = out_label.replace("&", "&amp;")
        else:
            encoded = out_label
        return f"{prefix}{encoded}{suffix}"

    pattern = re.compile(
        r'(class="[^"]*\btopic-box(?:-sm|-lg)?\b[^"]*"[^>]*>\s*)([^<]+?)(\s*<)',
        re.I,
    )
    return pattern.sub(repl, html), count


def translate_filter_links(html: str) -> tuple[str, int]:
    """Traduz texto visível de links data-filter (mantém o valor do filtro)."""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        before, label, after = m.group(1), m.group(2), m.group(3)
        key = re.sub(r"\s+", " ", label.replace("&amp;", "&")).strip()
        if key not in LABELS:
            return m.group(0)
        new = LABELS[key]
        encoded = new.replace("&", "&amp;") if "&" in new else new
        if encoded == label:
            return m.group(0)
        count += 1
        return f"{before}{encoded}{after}"

    pattern = re.compile(
        r'(data-filter="[^"]*"[^>]*>)([^<]+)(</a>)',
        re.I,
    )
    return pattern.sub(repl, html), count


def translate_ctg_titles(html: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        before, label, after = m.group(1), m.group(2), m.group(3)
        key = re.sub(r"\s+", " ", label.replace("&amp;", "&")).strip()
        if key not in LABELS:
            return m.group(0)
        new = LABELS[key]
        encoded = new.replace("&", "&amp;") if "&" in new else new
        if encoded == label:
            return m.group(0)
        count += 1
        return f"{before}{encoded}{after}"

    pattern = re.compile(
        r'(class="ctg-title[^"]*"[^>]*>)([^<]+)(<)',
        re.I,
    )
    return pattern.sub(repl, html), count


def main() -> None:
    total = 0
    for path in sorted(ROOT.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        html, c1 = translate_topic_boxes(html)
        html, c2 = translate_filter_links(html)
        html, c3 = translate_ctg_titles(html)
        n = c1 + c2 + c3
        if n:
            path.write_text(html, encoding="utf-8")
            print(f"{path.name}: {c1} topic-box, {c2} filters, {c3} ctg")
            total += n
    print(f"Total replacements: {total}")

    # Update screen-map.json widget labels
    map_path = ROOT / "screen-map.json"
    data = json.loads(map_path.read_text(encoding="utf-8"))
    changed = 0
    for page in data["pages"]:
        for w in page["widgets"]:
            if w["label"] in WIDGET_LABELS:
                w["label"] = WIDGET_LABELS[w["label"]]
                changed += 1
            elif w["label"] in LABELS:
                w["label"] = LABELS[w["label"]]
                changed += 1
    map_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"screen-map.json labels updated: {changed}")


if __name__ == "__main__":
    main()
