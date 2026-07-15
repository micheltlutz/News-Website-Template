#!/usr/bin/env python3
"""Annotate News Edge HTML pages with widget id / data-widget-id / data-widget-type."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = json.loads((ROOT / "screen-map.json").read_text(encoding="utf-8"))


def html_id(widget_id: str) -> str:
    page, _, slot = widget_id.partition(".")
    return f"{page}__{slot.replace('.', '-')}"


def attr_string(widget_id: str, widget_type: str) -> str:
    return (
        f'id="{html_id(widget_id)}" '
        f'data-widget-id="{widget_id}" '
        f'data-widget-type="{widget_type}"'
    )


def already_annotated(tag: str, widget_id: str) -> bool:
    return f'data-widget-id="{widget_id}"' in tag or "data-widget-id=" in tag


def inject_into_tag(tag: str, widget_id: str, widget_type: str) -> str:
    if already_annotated(tag, widget_id):
        return tag
    attrs = attr_string(widget_id, widget_type)
    if tag.endswith("/>"):
        return tag[:-2].rstrip() + f" {attrs} />"
    if tag.endswith(">"):
        return tag[:-1].rstrip() + f" {attrs}>"
    return tag


TAG_OPEN = re.compile(r"<(header|section|footer|div|aside|article|ul|form)(\s[^>]*)?>", re.I)


def find_next_tag(html: str, pos: int, allowed: tuple[str, ...] | None = None) -> re.Match | None:
    for m in TAG_OPEN.finditer(html, pos):
        name = m.group(1).lower()
        if allowed and name not in allowed:
            continue
        return m
    return None


def annotate_after_comment(
    html: str,
    comment_substr: str,
    widget_id: str,
    widget_type: str,
    allowed: tuple[str, ...] = ("section", "header", "footer", "div"),
) -> str:
    idx = html.find(comment_substr)
    if idx < 0:
        print(f"  WARN missing comment: {comment_substr!r} for {widget_id}")
        return html
    m = find_next_tag(html, idx + len(comment_substr), allowed)
    if not m:
        print(f"  WARN no tag after {comment_substr!r} for {widget_id}")
        return html
    new_tag = inject_into_tag(m.group(0), widget_id, widget_type)
    return html[: m.start()] + new_tag + html[m.end() :]


def annotate_nth_class(
    html: str,
    class_token: str,
    n: int,
    widget_id: str,
    widget_type: str,
    tag: str = "div",
) -> str:
    """Annotate the n-th (1-based) opening tag that contains class_token."""
    pattern = re.compile(rf"<{tag}\b([^>]*)>", re.I)
    count = 0
    for m in pattern.finditer(html):
        if class_token not in m.group(0):
            continue
        count += 1
        if count != n:
            continue
        new_tag = inject_into_tag(m.group(0), widget_id, widget_type)
        return html[: m.start()] + new_tag + html[m.end() :]
    print(f"  WARN class #{n} not found: {class_token!r} for {widget_id}")
    return html


def annotate_near_topic(
    html: str,
    topic_html_snippet: str,
    widget_id: str,
    widget_type: str,
    walk_back_classes: tuple[str, ...] = (
        "ne-isotope",
        "mb-20-r ne-isotope",
        "row tab-space1",
        "sidebar-box",
        "ne-carousel",
        "newsletter-area",
        "category-box-layout1",
        "news-details-layout",
        "gallery-layout",
        "item-box-dark",
    ),
    fallback_tag: str = "div",
) -> str:
    """Find topic-box label snippet, walk back to a parent opening tag with known class, annotate it."""
    pos = html.find(topic_html_snippet)
    if pos < 0:
        # try once more with non-breaking spaces / amp variants already in snippet
        print(f"  WARN topic not found: {topic_html_snippet[:60]!r} for {widget_id}")
        return html

    # Search backwards for opening tags
    window_start = max(0, pos - 1200)
    window = html[window_start:pos]
    candidates = list(TAG_OPEN.finditer(window))
    chosen = None
    for m in reversed(candidates):
        tag = m.group(0)
        if any(c in tag for c in walk_back_classes) or (
            fallback_tag and m.group(1).lower() == fallback_tag and "class=" in tag
        ):
            # Prefer more specific containers
            if any(c in tag for c in walk_back_classes):
                chosen = m
                break
            if chosen is None:
                chosen = m
    if not chosen:
        # annotate the nearest preceding <div class=...>
        for m in reversed(candidates):
            if m.group(1).lower() == "div" and "class=" in m.group(0):
                chosen = m
                break
    if not chosen:
        print(f"  WARN parent not found near topic for {widget_id}")
        return html
    abs_start = window_start + chosen.start()
    abs_end = window_start + chosen.end()
    new_tag = inject_into_tag(chosen.group(0), widget_id, widget_type)
    return html[:abs_start] + new_tag + html[abs_end:]


def annotate_sidebar_boxes_in_order(html: str, widgets: list[dict]) -> str:
    """Annotate each <div class=\"sidebar-box...\"> in document order with sidebar widgets."""
    sidebar = [w for w in widgets if w["region"] == "sidebar"]
    if not sidebar:
        return html
    pattern = re.compile(r'<div\b([^>]*\bclass="[^"]*\bsidebar-box\b[^"]*"[^>]*)>', re.I)
    matches = list(pattern.finditer(html))
    if len(matches) < len(sidebar):
        print(f"  WARN sidebar-box count {len(matches)} < widgets {len(sidebar)}")
    # Apply from end to start to keep offsets stable
    for m, w in zip(reversed(matches[: len(sidebar)]), reversed(sidebar)):
        new_tag = inject_into_tag(m.group(0), w["id"], w["type"])
        html = html[: m.start()] + new_tag + html[m.end() :]
    return html


def annotate_first_banner_after(html: str, after_substr: str, widget_id: str, widget_type: str) -> str:
    idx = html.find(after_substr)
    if idx < 0:
        print(f"  WARN after-substr missing for banner {widget_id}")
        return html
    pattern = re.compile(r'<div\b([^>]*\bne-banner-layout\d[^>]*)>', re.I)
    m = pattern.search(html, idx)
    if not m:
        print(f"  WARN banner not found for {widget_id}")
        return html
    # skip if already a sidebar-box annotated parent — annotate the banner div itself
    new_tag = inject_into_tag(m.group(0), widget_id, widget_type)
    return html[: m.start()] + new_tag + html[m.end() :]


def by_id(page: dict) -> dict[str, dict]:
    return {w["id"]: w for w in page["widgets"]}


# ---------------------------------------------------------------------------
# Per-page annotation
# ---------------------------------------------------------------------------

AREA_SHELL = {
    "Header Area Start Here": ("header", ("header",)),
    "News Feed Area Start Here": ("ticker", ("section",)),
    "News Info List Area Start Here": ("meta-bar", ("section",)),
    "Breadcrumb Area Start Here": ("breadcrumbs", ("section",)),
    "Footer Area Start Here": ("footer", ("footer",)),
}


def annotate_shell(html: str, page_id: str, wmap: dict[str, dict]) -> str:
    for comment, (slot, tags) in AREA_SHELL.items():
        wid = f"{page_id}.{slot}"
        if wid not in wmap:
            continue
        html = annotate_after_comment(
            html, f"<!-- {comment} -->", wid, wmap[wid]["type"], allowed=tags
        )
    return html


def annotate_home_1(html: str, page: dict) -> str:
    pid, wmap = page["pageId"], by_id(page)
    html = annotate_shell(html, pid, wmap)
    html = annotate_after_comment(
        html, "<!-- News Slider Area Start Here -->", "home-1.hero", wmap["home-1.hero"]["type"]
    )
    html = annotate_near_topic(
        html, 'topic-box-lg color-primary">Top Stories', "home-1.top-stories", "isotope-section",
        walk_back_classes=("ne-isotope", "mb-20-r ne-isotope"),
    )
    html = annotate_near_topic(
        html, 'topic-box-lg color-apple">Life Style', "home-1.lifestyle", "overlay-list",
        walk_back_classes=("row tab-space1 mb-25", "row tab-space1"),
    )
    html = annotate_after_comment(
        html, "<!-- Video Area Start Here -->", "home-1.video", "video-section"
    )
    html = annotate_near_topic(
        html, 'topic-box-lg color-cutty-sark">Tech World', "home-1.tech-world", "media-list",
        walk_back_classes=("topic-border", "col-lg-4"),
    )
    # Second tech world — find remaining occurrence without widget id
    html = annotate_second_tech_world(html)
    html = annotate_near_topic(
        html, 'topic-box-lg color-pomegranate">Health', "home-1.health-fitness", "media-list",
        walk_back_classes=("topic-border", "col-lg-4"),
    )
    html = annotate_near_topic(
        html, 'topic-box-lg color-azure-radiance">Sports', "home-1.sports", "isotope-section",
        walk_back_classes=("ne-isotope",),
    )
    html = annotate_near_topic(
        html, 'topic-box-lg color-scampi">More News', "home-1.more-news", "isotope-section",
        walk_back_classes=("ne-isotope",),
    )
    html = annotate_after_comment(
        html, "<!-- Category Area Start Here -->", "home-1.categories", "category-boxes"
    )
    # Main ads (non-sidebar): after top story banner, latest banner
    html = annotate_main_ads_home1(html)
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_second_tech_world(html: str) -> str:
    snippet = 'topic-box-lg color-web-orange">Tech World'
    pos = html.find(snippet)
    if pos < 0:
        print("  WARN second Tech World not found")
        return html
    window_start = max(0, pos - 800)
    window = html[window_start:pos]
    candidates = list(TAG_OPEN.finditer(window))
    for m in reversed(candidates):
        if "topic-border" in m.group(0) or ("col-lg-4" in m.group(0) and "class=" in m.group(0)):
            abs_start = window_start + m.start()
            abs_end = window_start + m.end()
            if "data-widget-id=" in m.group(0):
                continue
            new_tag = inject_into_tag(m.group(0), "home-1.tech-world-2", "media-list")
            return html[:abs_start] + new_tag + html[abs_end:]
    return html


def annotate_main_ads_home1(html: str) -> str:
    # First ne-banner-layout1 that is NOT inside sidebar-box — after Top Stories section banner
    # Prefer unique context: mt-20-r after top story
    for wid, typ, needle in [
        ("home-1.ad-after-top", "ad-banner", 'class="ne-banner-layout1 mt-20-r text-center"'),
        ("home-1.ad-latest", "ad-banner", 'class="ne-banner-layout1 mb-50 mt-20-r text-center"'),
    ]:
        idx = html.find(needle)
        if idx < 0:
            print(f"  WARN ad needle missing {needle}")
            continue
        # find opening div containing this class
        start = html.rfind("<div", 0, idx + 1)
        end = html.find(">", idx)
        tag = html[start : end + 1]
        new_tag = inject_into_tag(tag, wid, typ)
        html = html[:start] + new_tag + html[end + 1 :]
    return html


def annotate_home_2(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "home-2", wmap)
    html = annotate_after_comment(html, "<!-- News Slider Area Start Here -->", "home-2.hero", "hero-mosaic")
    html = annotate_near_topic(html, 'topic-box-lg color-primary">Top Stories', "home-2.top-stories", "isotope-section", walk_back_classes=("ne-isotope",))
    html = annotate_first_banner_after(html, "<!-- Top Story Area End Here -->", "home-2.ad-after-top", "ad-banner")
    # banner is BEFORE end comment — fix:
    html2 = html
    needle = 'class="ne-banner-layout1 mt-20-r text-center"'
    # only first occurrence in top story
    idx = html.find("<!-- Top Story Area Start Here -->")
    end = html.find("<!-- Top Story Area End Here -->")
    if idx >= 0 and end > idx:
        region = html[idx:end]
        m = re.search(r'<div\b([^>]*ne-banner-layout1 mt-20-r[^>]*)>', region)
        if m:
            abs_start = idx + m.start()
            abs_end = idx + m.end()
            html = html[:abs_start] + inject_into_tag(m.group(0), "home-2.ad-after-top", "ad-banner") + html[abs_end:]
    html = annotate_near_topic(html, 'topic-box-lg color-persian-green">International', "home-2.international", "international-section", walk_back_classes=("topic-border", "col-lg-8", "row"))
    html = annotate_near_topic(html, 'topic-box-lg color-scampi">Editor Picks', "home-2.editor-picks", "news-carousel", walk_back_classes=("ne-carousel", "topic-border", "container"))
    # Prefer the carousel div
    html = annotate_near_topic(html, 'topic-box-lg color-apple">Fashion', "home-2.fashion", "category-news", walk_back_classes=("topic-border", "col-lg-4"))
    html = annotate_near_topic(html, 'topic-box-lg color-cutty-sark">Tech World', "home-2.tech-world", "category-news", walk_back_classes=("topic-border", "col-lg-4"))
    html = annotate_near_topic(html, 'topic-box-lg color-web-orange">Food', "home-2.food-hobbies", "category-news", walk_back_classes=("topic-border", "col-lg-4"))
    # category ad
    cat_start = html.find("<!-- Category News Area Start Here -->")
    cat_end = html.find("<!-- Category News Area End Here -->")
    if cat_start >= 0 and cat_end > cat_start:
        region = html[cat_start:cat_end]
        m = re.search(r'<div\b([^>]*ne-banner-layout1[^>]*)>', region)
        if m:
            abs_start = cat_start + m.start()
            abs_end = cat_start + m.end()
            html = html[:abs_start] + inject_into_tag(m.group(0), "home-2.ad-category", "ad-banner") + html[abs_end:]
    html = annotate_after_comment(html, "<!-- Video Area Start Here -->", "home-2.video", "video-section")
    html = annotate_near_topic(html, 'topic-box-lg color-azure-radiance">More News', "home-2.more-news", "isotope-section", walk_back_classes=("ne-isotope",))
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_home_3(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "home-3", wmap)
    html = annotate_after_comment(html, "<!-- News Slider Area Start Here -->", "home-3.hero", "hero-mosaic")
    html = annotate_near_topic(html, "What", "home-3.whats-new", "isotope-section", walk_back_classes=("ne-isotope", "mb-20-r ne-isotope"))
    # Fix What's New — use exact with curly apostrophe if present
    if 'data-widget-id="home-3.whats-new"' not in html:
        for snip in [
            'topic-box-lg color-azure-radiance">What\u2019s New',
            'topic-box-lg color-azure-radiance">What\'s New',
            "What’s New",
            "What's New",
        ]:
            if snip in html:
                html = annotate_near_topic(html, snip, "home-3.whats-new", "isotope-section", walk_back_classes=("ne-isotope", "mb-20-r ne-isotope"))
                break
    html = annotate_near_topic(html, 'topic-box-lg color-apple">Android', "home-3.android", "media-list", walk_back_classes=("topic-border", "row tab-space1"))
    html = annotate_near_topic(html, 'topic-box-lg color-ecstasy">Accessories', "home-3.accessories", "media-list", walk_back_classes=("topic-border", "row tab-space1"))
    top_start = html.find("<!-- Top Story Area Start Here -->")
    top_end = html.find("<!-- Top Story Area End Here -->")
    if top_start >= 0 and top_end > top_start:
        region = html[top_start:top_end]
        # last ne-banner in top story (ad-after-top); sidebar ads stay on sidebar-box
        banners = list(re.finditer(r'<div\b([^>]*ne-banner-layout1[^>]*)>', region))
        if banners:
            m = banners[-1]
            abs_start = top_start + m.start()
            abs_end = top_start + m.end()
            html = html[:abs_start] + inject_into_tag(m.group(0), "home-3.ad-after-top", "ad-banner") + html[abs_end:]
    html = annotate_after_comment(html, "<!-- Video Area Start Here -->", "home-3.video", "video-section")
    html = annotate_near_topic(html, 'topic-box-lg color-hollywood-cerise">Gadgets', "home-3.gadgets", "card-grid", walk_back_classes=("topic-border", "container", "section"))
    html = annotate_near_topic(html, 'topic-box-lg color-cod-gray">Latest News', "home-3.latest-news", "latest-news", walk_back_classes=("topic-border", "col-lg-8", "row"))
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_home_4(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "home-4", wmap)
    html = annotate_after_comment(html, "<!-- News Slider Area Start Here -->", "home-4.hero", "hero-mosaic")
    html = annotate_near_topic(html, 'topic-box-lg color-white">Popular Games', "home-4.popular-games", "isotope-section", walk_back_classes=("ne-isotope", "item-box-dark"))
    html = annotate_near_topic(html, 'topic-box-lg color-white">Games Reviews', "home-4.games-reviews", "review-section", walk_back_classes=("topic-border", "col-lg-8", "row"))
    html = annotate_after_comment(html, "<!-- Video Area Start Here -->", "home-4.video", "video-section")
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_home_5(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "home-5", wmap)
    html = annotate_after_comment(html, "<!-- News Slider Area Start Here -->", "home-5.hero", "hero-mosaic")
    html = annotate_near_topic(html, 'Popular News', "home-5.popular-news", "isotope-section", walk_back_classes=("ne-isotope",))
    html = annotate_near_topic(html, "Racing World", "home-5.racing-world", "overlay-list", walk_back_classes=("topic-border", "row tab-space1"))
    html = annotate_after_comment(html, "<!-- Video Area Start Here -->", "home-5.video", "video-section")
    html = annotate_near_topic(html, "Latest Article", "home-5.latest-article", "latest-news", walk_back_classes=("topic-border", "col-lg-8", "row"))
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_home_6(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "home-6", wmap)
    html = annotate_after_comment(html, "<!-- News Slider Area Start Here -->", "home-6.hero", "hero-banner")
    html = annotate_after_comment(html, "<!-- Feature News Area Start Here -->", "home-6.featured", "featured-section")
    html = annotate_after_comment(html, "<!-- Latest Articles Area Start Here -->", "home-6.latest-articles", "latest-news")
    html = annotate_after_comment(html, "<!-- Trending News Area Start Here -->", "home-6.trending", "trending-section")
    html = annotate_after_comment(html, "<!-- Category Area Start Here -->", "home-6.categories", "category-boxes")
    html = annotate_after_comment(html, "<!-- More News Area Start Here -->", "home-6.more-news", "more-news")
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_home_7(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "home-7", wmap)
    html = annotate_after_comment(html, "<!-- Slider Area Start Here -->", "home-7.hero", "hero-nivo")
    # side stories near slider — look for media list beside nivo
    html = annotate_near_topic(html, "Popular Recipes", "home-7.popular-recipes", "isotope-section", walk_back_classes=("ne-isotope",))
    html = annotate_near_topic(html, "Food Reviews", "home-7.food-reviews", "review-section", walk_back_classes=("topic-border", "col-lg-8", "row"))
    html = annotate_after_comment(html, "<!-- Videos Area Start Here -->", "home-7.video", "video-carousel")
    html = annotate_after_comment(html, "<!-- Category Area Start Here -->", "home-7.categories", "category-boxes")
    slider_start = html.find("<!-- Slider Area Start Here -->")
    slider_end = html.find("<!-- Slider Area End Here -->")
    if slider_start >= 0 and slider_end > slider_start:
        region = html[slider_start:slider_end]
        m = re.search(r'<div\b([^>]*col-xl-4 col-lg-12[^>]*)>', region)
        if m and "data-widget-id=" not in m.group(0):
            abs_start = slider_start + m.start()
            abs_end = slider_start + m.end()
            html = html[:abs_start] + inject_into_tag(m.group(0), "home-7.hero-side", "media-list") + html[abs_end:]
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_listing(html: str, page: dict, list_slot: str = "list") -> str:
    pid = page["pageId"]
    wmap = by_id(page)
    html = annotate_shell(html, pid, wmap)
    # main page area
    for comment in [
        "Post Style 1 Page Area Start Here",
        "Post Style 2 Page Area Start Here",
        "Post Style 3 Page Area Start Here",
        "Post Style 4 Page Area Start Here",
        "Archive Page Area Start Here",
        "Author Post Page Area Start Here",
        "Gallery Page Area Start Here",
        "Contact Page Area Start Here",
        "404 Error Page Area Start Here",
        "News Details Page Area Start Here",
    ]:
        if f"<!-- {comment} -->" in html:
            # For article/list pages the main section is annotated specially below
            break
    return html


def annotate_post(html: str, page: dict) -> str:
    pid = page["pageId"]
    wmap = by_id(page)
    html = annotate_shell(html, pid, wmap)
    style_n = pid.split("-")[1]
    comment = f"<!-- Post Style {style_n} Page Area Start Here -->"
    list_id = f"{pid}.list"
    html = annotate_after_comment(html, comment, list_id, wmap[list_id]["type"], allowed=("section",))
    # For post pages, main content is col-lg-8 inside section — refine if section got the id (OK)
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_archive(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "archive", wmap)
    html = annotate_after_comment(html, "<!-- Archive Page Area Start Here -->", "archive.filters", "archive-filters")
    # also annotate list — find media list region; use second major block if filters on same section
    # Prefer annotating filters form and list column separately
    if "archive-search" in html or "Archive" in html:
        # try form
        m = re.search(r'<form\b([^>]*)>', html)
        if m and "data-widget-id=" not in m.group(0):
            # only if we want filters on form — already put on section
            pass
    # list: first col-lg-8 with media inside archive area
    start = html.find("<!-- Archive Page Area Start Here -->")
    end = html.find("<!-- Archive Page Area End Here -->")
    if start >= 0 and end > start:
        region = html[start:end]
        m = re.search(r'<div\b([^>]*col-lg-8[^>]*)>', region)
        if m:
            abs_start = start + m.start()
            abs_end = start + m.end()
            html = html[:abs_start] + inject_into_tag(m.group(0), "archive.list", "media-list") + html[abs_end:]
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_author(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "author", wmap)
    start = html.find("<!-- Author Post Page Area Start Here -->")
    end = html.find("<!-- Author Post Page Area End Here -->")
    if start >= 0:
        html = annotate_after_comment(html, "<!-- Author Post Page Area Start Here -->", "author.profile", "article-author")
        # list - look for posts after profile
        if end > start:
            region = html[start:end]
            # second media-none or list block — annotate a div containing media list after author box
            medias = list(re.finditer(r'<div\b([^>]*media media-none[^>]*)>', region))
            if medias:
                # annotate parent col containing multiple media: use col-lg-8
                m = re.search(r'<div\b([^>]*col-lg-8[^>]*)>', region)
                if m and "data-widget-id=" not in m.group(0):
                    abs_start = start + m.start()
                    abs_end = start + m.end()
                    html = html[:abs_start] + inject_into_tag(m.group(0), "author.list", "media-list") + html[abs_end:]
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_by_class(html: str, class_token: str, widget_id: str, widget_type: str, tag: str = "div") -> str:
    if f'data-widget-id="{widget_id}"' in html:
        return html
    pattern = re.compile(
        rf"<{tag}\b([^>]*\bclass=\"[^\"]*\b{re.escape(class_token)}\b[^\"]*\"[^>]*)>",
        re.I,
    )
    m = pattern.search(html)
    if not m:
        print(f"  WARN class token missing: {class_token!r} for {widget_id}")
        return html
    return html[: m.start()] + inject_into_tag(m.group(0), widget_id, widget_type) + html[m.end() :]


def annotate_article(html: str, page: dict) -> str:
    pid = page["pageId"]
    wmap = by_id(page)
    html = annotate_shell(html, pid, wmap)

    if pid == "article-3":
        html = annotate_after_comment(
            html, "<!-- Inner Page Banner Area Start Here -->", f"{pid}.hero", "hero-banner"
        )

    start = html.find("<!-- News Details Page Area Start Here -->")
    end = html.find("<!-- News Details Page Area End Here -->")
    if start < 0:
        return html

    region = html[start:end] if end > start else html[start:]
    layout = re.search(r'<div\b([^>]*news-details-layout\d[^>]*)>', region)
    if layout and "data-widget-id=" not in layout.group(0):
        abs_start = start + layout.start()
        abs_end = start + layout.end()
        html = (
            html[:abs_start]
            + inject_into_tag(layout.group(0), f"{pid}.body", "article-body")
            + html[abs_end:]
        )
        start = html.find("<!-- News Details Page Area Start Here -->")
        end = html.find("<!-- News Details Page Area End Here -->")
        region = html[start:end]

    if pid == "article-2":
        m = re.search(r'<div\b([^>]*position-relative[^>]*)>', region)
        if m and "data-widget-id=" not in m.group(0):
            abs_start = start + m.start()
            abs_end = start + m.end()
            html = (
                html[:abs_start]
                + inject_into_tag(m.group(0), f"{pid}.hero", "hero-banner")
                + html[abs_end:]
            )

    html = annotate_by_class(html, "blog-tags", f"{pid}.tags", "article-tags", tag="ul")
    html = annotate_by_class(html, "post-share-area", f"{pid}.share", "article-share")
    html = annotate_by_class(html, "author-info", f"{pid}.author", "article-author")
    html = annotate_by_class(html, "comments-area", f"{pid}.comments", "article-comments")

    if f'data-widget-id="{pid}.nav"' not in html:
        start = html.find("<!-- News Details Page Area Start Here -->")
        end = html.find("<!-- News Details Page Area End Here -->")
        region = html[start:end] if end > start else html[start:]
        pos = region.find("Previous article")
        if pos < 0:
            pos = region.find("previous-article")
        if pos >= 0:
            window = region[max(0, pos - 300) : pos]
            tags = list(TAG_OPEN.finditer(window))
            if tags:
                m = tags[-1]
                abs_start = start + max(0, pos - 300) + m.start()
                abs_end = start + max(0, pos - 300) + m.end()
                html = (
                    html[:abs_start]
                    + inject_into_tag(m.group(0), f"{pid}.nav", "article-nav")
                    + html[abs_end:]
                )

    if pid == "article-2" and f'data-widget-id="{pid}.related"' not in html:
        pos = html.find("Related Posts")
        if pos >= 0:
            window = html[pos : pos + 900]
            m = re.search(r'<div\b([^>]*ne-carousel[^>]*)>', window)
            if m:
                abs_start = pos + m.start()
                abs_end = pos + m.end()
                html = (
                    html[:abs_start]
                    + inject_into_tag(m.group(0), f"{pid}.related", "related-carousel")
                    + html[abs_end:]
                )

    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_gallery(html: str, page: dict) -> str:
    pid = page["pageId"]
    wmap = by_id(page)
    html = annotate_shell(html, pid, wmap)
    html = annotate_after_comment(
        html, "<!-- Gallery Page Area Start Here -->", f"{pid}.grid", "gallery-grid"
    )
    return html


def annotate_contact(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "contact", wmap)
    html = annotate_near_topic(html, "About Us", "contact.about", "featured-section", walk_back_classes=("topic-border", "col-lg-8"))
    html = annotate_near_topic(html, "Location Info", "contact.location", "meta-bar", walk_back_classes=("topic-border", "col-lg"))
    html = annotate_near_topic(html, "Send Us Message", "contact.form", "contact-form", walk_back_classes=("topic-border", "form", "col-lg"))
    # form element
    start = html.find("Send Us Message")
    if start > 0:
        m = re.search(r'<form\b([^>]*)>', html[start : start + 500])
        if m:
            abs_start = start + m.start()
            abs_end = start + m.end()
            tag = html[abs_start:abs_end]
            if "data-widget-id=" not in tag:
                html = html[:abs_start] + inject_into_tag(tag, "contact.form", "contact-form") + html[abs_end:]
    html = annotate_sidebar_boxes_in_order(html, page["widgets"])
    return html


def annotate_404(html: str, page: dict) -> str:
    wmap = by_id(page)
    html = annotate_shell(html, "error-404", wmap)
    html = annotate_after_comment(
        html, "<!-- 404 Error Page Area Start Here -->", "error-404.message", "error-message"
    )
    return html


ANNOTATORS = {
    "home-1": annotate_home_1,
    "home-2": annotate_home_2,
    "home-3": annotate_home_3,
    "home-4": annotate_home_4,
    "home-5": annotate_home_5,
    "home-6": annotate_home_6,
    "home-7": annotate_home_7,
    "post-1": annotate_post,
    "post-2": annotate_post,
    "post-3": annotate_post,
    "post-4": annotate_post,
    "archive": annotate_archive,
    "author": annotate_author,
    "article-1": annotate_article,
    "article-2": annotate_article,
    "article-3": annotate_article,
    "gallery-1": annotate_gallery,
    "gallery-2": annotate_gallery,
    "contact": annotate_contact,
    "error-404": annotate_404,
}


def verify(html: str, page: dict) -> list[str]:
    missing = []
    for w in page["widgets"]:
        if f'data-widget-id="{w["id"]}"' not in html:
            missing.append(w["id"])
    return missing


def process_page(page: dict) -> None:
    files = [page["file"]] + list(page.get("aliases") or [])
    annotator = ANNOTATORS[page["pageId"]]
    for fname in files:
        path = ROOT / fname
        if not path.exists():
            print(f"MISSING FILE {fname}")
            continue
        print(f"Annotating {fname} ({page['pageId']})...")
        html = path.read_text(encoding="utf-8")
        # strip previous annotations if re-run
        html = re.sub(
            r'\s+id="[a-z0-9-]+__[a-z0-9.-]+"\s+data-widget-id="[^"]+"\s+data-widget-type="[^"]+"',
            "",
            html,
        )
        html = annotator(html, page)
        missing = verify(html, page)
        if missing:
            print(f"  MISSING ({len(missing)}): {', '.join(missing)}")
        else:
            print(f"  OK — {len(page['widgets'])} widgets")
        path.write_text(html, encoding="utf-8")


def main() -> None:
    for page in MAP["pages"]:
        process_page(page)


if __name__ == "__main__":
    main()
