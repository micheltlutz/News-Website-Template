# Formatos e tamanhos de banner — News-Website-Template

Guia para orientar criativos de publicidade (e futuro ad-server) conforme os slots reais do template.

Fontes: assets em [`img/banner/`](../img/banner/) · slots `data-widget-type="ad-banner"` em [`SCREEN-MAP.md`](SCREEN-MAP.md) / [`screen-map.json`](../screen-map.json) · markup `.ne-banner-layout*`.

Última medição dos arquivos de exemplo: 2026-07-14.

---

## Como o template exibe anúncios

1. O criativo é um `<img class="img-fluid">` (largura máx. 100% do slot; altura proporcional).
2. Layouts CSS: `.ne-banner-layout1` (padrão) e `.ne-banner-layout2` (variante sidebar em home-6).
3. Largura útil depende da coluna Bootstrap no **container** (~1140 px em desktop XL):
   - **Full / in-content** (`col-12`): ~1110 px úteis — banners largos centralizados.
   - **Header ao lado do logo** (`col-lg-8`): ~730–750 px úteis — leaderboard clássico.
   - **Sidebar** (`col-lg-4` / `ne-sidebar`): ~330–370 px úteis — retângulos médios / verticais.

**Regra prática:** entregar no tamanho canônico da tabela abaixo; o CSS reduz sem crop se a arte for maior (respeitando a proporção). Evitar arte mais estreita que o slot em desktop — haverá espaço vazio nas laterais.

---

## Catálogo canônico (para o time comercial)

| Código interno | Nome comercial (IAB-like) | Tamanho (px) | Proporção | Uso tipico | Asset de referência |
|----------------|--------------------------|--------------|-----------|------------|---------------------|
| `LB-728x90` | Leaderboard | **728 × 90** | ~8,1∶1 | Header (ao lado do logo); faixa full width entre seções | `banner2.jpg` |
| `MR-370x278` | Medium Rectangle / MPU | **370 × 278** | ~4∶3 | Sidebar principal (maioria das páginas) | `banner3.jpg` |
| `SQ-340x340` | Half-page / Square | **341 × 346** ≈ **300 × 300** ou **336 × 280** | ~1∶1 | Sidebar secundária / artigo | `banner6.jpg` |
| `LS-370x200` | Large Mobile / Landscape box | **370 × 207** | ~16∶9 | Sidebar (home-2) | `banner11.jpg` |
| `LS-370x180` | Landscape box compacto | **370 × 182** | ~2∶1 | Sidebar (home-6) | `banner12.jpg` |
| `LS-370x190` | Landscape box (layout2) | **370 × 189** | ~2∶1 | Sidebar home-6 (`.ne-banner-layout2`) | `banner5.jpg` |

### Tamanhos IAB aceitos como equivalente

Quando o anunciante não tiver o pixel exacto do template, use o equivalente IAB mais próximo **sem esticar**:

| Slot template | Aceitar também | Não recomendado |
|---------------|----------------|-----------------|
| Leaderboard 728×90 | 970×90 (Billboard, vai ser reduzido), 320×50 / 320×100 (só mobile) | 300×250 no header |
| Sidebar 370×278 | **300×250**, 336×280 | 728×90 (fica baixo e largo demais) |
| Sidebar ~1∶1 | 300×300, 336×280, 300×600 (com crop/letterbox consciente) | 728×90 |
| Landscape ~370×190–207 | 320×100, 300×100, 320×150 | arte vertical |

### Entrega de arquivo (sugestão operacional)

| Item | Recomendação |
|------|----------------|
| Formato | JPG (fotos) ou PNG (logo/texto nítido); WebP opcional se o pipeline servir fallback |
| Peso | ≤ **150 KB** leaderboard; ≤ **200 KB** retângulos sidebar |
| Fundo | Não contar com transparência em JPG; PNG só se necessário |
| Safe area | Manter texto/logo a ≥ **16 px** das bordas (redução em mobile corta o miolo) |
| Alt text | Sempre descritivo curto (não `alt="ad"`) — a11y |
| Animação | GIF/HTML5 fora do escopo atual do template estático (só `<img>`) |

---

## Inventário de slots por seção

Legenda de região:

- **header** — ao lado do logo (largura ~col-8)
- **in-content** — faixa full width entre blocos editoriais (`col-12`)
- **sidebar** — coluna lateral (~col-4)

### Formato A — Leaderboard 728×90 (`LB-728x90`)

| Slot / local | Página(s) | `data-widget-id` | Região |
|--------------|-----------|------------------|--------|
| Header (ao lado do logo) | `index2.html`, `index3.html`, `index4.html`, `index5.html` | *(sem widget-id hoje — markup `.ne-banner-layout1.pull-right`)* | header |
| Após bloco de destaques / top story | Home 1 · `index.html` / `index-2.html` | `home-1.ad-after-top` | in-content |
| Após / junto a “últimas” | Home 1 | `home-1.ad-latest` | in-content |
| Após destaques | Home 2 · `index2.html` | `home-2.ad-after-top` | in-content |
| Faixa categorias | Home 2 | `home-2.ad-category` | in-content |
| Após destaques | Home 3 · `index3.html` | `home-3.ad-after-top` | in-content |

Homes **4** e **5** usam o mesmo leaderboard no header; **não** têm faixa in-content tipada no screen-map. Home **7** não tem slot `ad-banner` no markup atual.

### Formato B — Medium rectangle ~370×278 (`MR-370x278`)

| Slot | Página(s) | `data-widget-id` |
|------|-----------|------------------|
| Sidebar ad 1 | Home 1 | `home-1.sidebar.ad-1` |
| Sidebar | Home 5 (×2) | `home-5.sidebar.ad-1`, `home-5.sidebar.ad-2` |
| Sidebar | Posts 1–4 | `post-1.sidebar.ad` … `post-4.sidebar.ad` |
| Sidebar | Archive, Author, Contact, Privacy, Acessibilidade | `archive.sidebar.ad`, `author.sidebar.ad`, `contact.sidebar.ad`, `privacy.sidebar.ad`, `a11y.sidebar.ad` |
| Sidebar | Artigos 1 / 3 / 4 | `article-1.sidebar.ad`, `article-3.sidebar.ad` |

### Formato C — Quase quadrado ~341×346 (`SQ-340x340`)

| Slot | Página(s) | `data-widget-id` |
|------|-----------|------------------|
| Sidebar ad 2 | Home 1 | `home-1.sidebar.ad-2` |
| Sidebar | Home 3 | `home-3.sidebar.ad-1` |
| Sidebar | Artigo 2 | `article-2.sidebar.ad` |

### Formato D — Landscape sidebar (~370×180–207)

| Slot | Página | `data-widget-id` | Asset / px |
|------|--------|------------------|------------|
| Sidebar | Home 2 | `home-2.sidebar.ad-1` | `banner11.jpg` 370×207 |
| Sidebar ad 1 | Home 6 | `home-6.sidebar.ad-1` | `banner12.jpg` 370×182 |
| Sidebar ad 2 | Home 6 | `home-6.sidebar.ad-2` | `banner5.jpg` 370×189 (`.ne-banner-layout2`) |

---

## Resumo por página (orientação rápida)

| Página | Arquivo | Leaderboard header | Faixa in-content | Sidebar |
|--------|---------|--------------------|------------------|---------|
| Home 1 | `index.html` (+ alias `index-2.html`) | — | 2× 728×90 | 370×278 + 341×346 |
| Home 2 | `index2.html` | 728×90 | 2× 728×90 | 370×207 |
| Home 3 | `index3.html` | 728×90 | 1× 728×90 | 341×346 |
| Home 4 | `index4.html` | 728×90 | — | — |
| Home 5 | `index5.html` | 728×90 | — | 2× 370×278 |
| Home 6 | `index6.html` | — | — | 370×182 + 370×189 |
| Home 7 | `index7.html` | — | — | — |
| Post styles 1–4 | `post-style-*.html` | — | — | 370×278 |
| Artigos 1 / 3 / 4 | `single-news-*.html` | — | — | 370×278 |
| Artigo 2 | `single-news-2.html` | — | — | 341×346 |
| Archive / Author / Contact / Privacy / A11y | respectivos HTML | — | — | 370×278 |
| Galerias / 404 | — | — | — | sem ad tipado |

---

## Assets em `img/banner/` (não são todos “ad vendável”)

| Arquivo | Px | Papel |
|---------|----|--------|
| `banner2.jpg` | 728×90 | Criativo leaderboard (ad) |
| `banner3.jpg` | 370×278 | Criativo sidebar MPU (ad) |
| `banner5.jpg` | 370×189 | Criativo sidebar landscape (ad) |
| `banner6.jpg` | 341×346 | Criativo sidebar square (ad) |
| `banner11.jpg` | 370×207 | Criativo sidebar landscape (ad) |
| `banner12.jpg` | 370×182 | Criativo sidebar landscape (ad) |
| `banner1.jpg` | 1920×695 | Fundo/hero amplo — **não** slot `ad-banner` |
| `breadcrumbs-banner.jpg` | 1920×134 | Fundo de breadcrumb — **não** ad |
| `section-background.png` | 1920×966 | Fundo de seção — **não** ad |
| `slide1–3.jpg` | 1200×814 | Slider Nivo / editorial — **não** ad |
| `video-back*.jpg` | 1920×555 / 1169×540 | Fundo de bloco de vídeo — **não** ad |
| `newsletter.png` | 79×81 | Ícone decorativo newsletter — **não** ad |
| `play.png` | 60×60 | Ícone play — **não** ad |

---

## Checklist para briefing de mídia

1. Informar o **código interno** (`LB-728x90`, `MR-370x278`, …) + páginas-alvo.
2. Pedir arte no **tamanho canônico**; aceitar equivalente IAB da tabela.
3. Confirmar se o creativo precisa funcionar só desktop, só mobile, ou ambos (no mobile tudo vira full-bleed da coluna).
4. Lembrar: template atual é **imagem estática** (`<img>`); rich media / VAST exige integração futura.
5. Preferir `data-widget-id` do [`SCREEN-MAP.md`](SCREEN-MAP.md) no ad-server para targeting por slot.

---

## Evolução sugerida (não implementado)

- Tipar o leaderboard do header (`home-2.header.ad`, etc.) com `data-widget-id` faltante.
- Definir breakpoint mobile explícito (ex.: servir `320×50` via `<picture>` / `srcset`).
- Padronizar sidebar em um único tamanho comercial (**300×250**) e ajustar placeholders.
