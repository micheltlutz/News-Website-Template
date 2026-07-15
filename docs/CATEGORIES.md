# Categorias do template Notícias Mobile

Documento para agentes e backoffice. Mapeia **rótulos visuais** (`topic-box`), **slugs canônicos**, classes de cor e filtros Isotope.

> Textos de UI estão em **pt-BR**. Classes CSS (`color-*`, `data-filter=".politics"`) e slugs de filtro **não mudam** — só o texto exibido foi traduzido.

Fontes relacionadas: [`SCREEN-MAP.md`](SCREEN-MAP.md) · [`screen-map.json`](../screen-map.json) · [`TAGS.md`](TAGS.md) · [`STYLE-GUIDE.md`](STYLE-GUIDE.md) §4 · schema [`domain/DATABASE-SCHEMA.md`](domain/DATABASE-SCHEMA.md)

---

## Como usar (agentes)

1. Ao categorizar um artigo, preferir o **slug** da tabela canônica (coluna `slug`).
2. No HTML do template, o badge usa `.topic-box*` + **classe de cor** (`color-*`) + texto pt-BR.
3. Em seções Isotope, o valor de `data-filter` continua em inglês (ex.: `.politics`); o link exibe “Política”.
4. Não renomear classes CSS de categoria — quebram layout, JS e este mapa.
5. Subcategorias (esportes, gastronomia) usam `slug` hierárquico `pai.filho` quando fizer sentido no CMS.

```html
<div class="topic-box-sm color-primary mb-20">Política</div>
<a href="#" data-filter=".politics">Política</a>
```

---

## Categorias canônicas (editoriais)

Estas são as categorias principais do portal no template.

| slug | Rótulo pt-BR | Rótulo EN (legado) | Classe de cor recomendada | Filtro Isotope (`data-filter`) |
|------|--------------|--------------------|---------------------------|--------------------------------|
| `politics` | Política | Politics | `color-primary` | `.politics` |
| `fashion` | Moda | Fashion | `color-cod-gray` / theme | `.fashion` |
| `travel` | Viagem | Travel | `color-cod-gray` | `.travel` |
| `gadget` | Gadget / Gadgets | Gadget(s) | `color-cod-gray` | `.gadget` |
| `sports` | Esportes | Sports | `color-azure-radiance` | `.sports` / tabs por esporte |
| `business` | Negócios | Business | `color-primary` | — |
| `technology` | Tecnologia | Technology | `color-cutty-sark` | — |
| `tech-world` | Mundo Tech | Tech World | `color-cutty-sark` / `color-web-orange` | — |
| `lifestyle` | Lifestyle | Life Style | `color-apple` | — |
| `food` | Gastronomia | Food | `color-web-orange` | tabs comida |
| `health-fitness` | Saúde & Fitness | Health & Fitness | `color-pomegranate` | `.health` (quando presente) |
| `fitness` | Fitness | Fitness | `color-cod-gray` | `.fitness` |
| `music` | Música | Music | `color-cod-gray` | — |
| `education` | Educação | Education | — (ctg-title) | — |
| `nature` | Natureza | Nature | `color-cod-gray` | — |
| `android` | Android | Android | `color-apple` | — |
| `accessories` | Acessórios | Accessories | `color-ecstasy` | — |
| `international` | Internacional | International | `color-persian-green` | — |
| `games` | Games | Games / Game | `color-cod-gray` / dark | — |
| `animation` | Animação | Animation | `color-primary` | `.animation` |
| `action` | Ação | Action | `color-primary` | `.action` |
| `racing` | Corrida | Racing | `color-primary` | `.racing` |
| `electronics` | Eletrônicos | Electronics | `color-white` (em fundo escuro) | — |
| `software` | Software | Software | `color-cod-gray` | — |
| `style-zone` | Style Zone | Style Zone | `color-cod-gray` | — |
| `public` | Público | Public | `color-cod-gray` | — |
| `adventure` | Aventura | Adventure / Ventura / Adventue | `color-cod-gray` | — |
| `corporate` | Corporativo | Corporate | `color-cod-gray` | — |
| `people` | Pessoas | People | `color-cod-gray` | — |
| `world` | Mundo | World | `color-cod-gray` | — |
| `camera` | Câmera | Camera | `color-cod-gray` | — |
| `application` | Aplicativos | Application | `color-cod-gray` | — |
| `model` | Modelo | Model | `color-cod-gray` | — |
| `picture` | Foto | Picture | `color-cod-gray` | — |
| `flower` | Flores | Flower | `color-cod-gray` | — |
| `daily-wear` | Dia a Dia | Daily Wear | `color-cod-gray` | — |
| `fashion-today` | Moda Hoje | Fashion Today | `color-cod-gray` | — |

### Marcas / produtos (não são categorias editoriais genéricas)

| slug | Rótulo | Notas |
|------|--------|-------|
| `brand.apple` | Apple | Mantido em inglês |
| `brand.ipad` | iPad | Mantido |
| `brand.maxrocket` | MaxRocket | Demo do template |

---

## Subcategorias — Esportes (`sports.*`)

| slug | Rótulo pt-BR | EN / typo legado | Cor típica |
|------|--------------|------------------|------------|
| `sports.football` | Futebol | Football / Fotball | `color-cod-gray` |
| `sports.boxing` | Boxe | Boxing | `color-primary` / gray |
| `sports.cycling` | Ciclismo | Cycling | `color-cod-gray` |
| `sports.diving` | Mergulho | Diving | `color-cod-gray` |
| `sports.racing` | Corrida | Racing / Race | `color-primary` |
| `sports.riding` | Hipismo | Riding / Rorse Rider | `color-cod-gray` |
| `sports.horse-racing` | Turfe | Horse Racing | `color-cod-gray` |
| `sports.bike-racing` | Motovelocidade | Bike Racing | `color-cod-gray` |
| `sports.bike-riding` | Ciclismo | Bike Riding | `color-cod-gray` |
| `sports.car-racing` | Automobilismo | Car Racing | — |
| `sports.rugby` | Rúgbi | Ragbe / Rugby | `color-cod-gray` |
| `sports.cricket` | Críquete | Cricket | `color-cod-gray` |
| `sports.golf` | Golf | Golf | `color-cod-gray` |
| `sports.baseball` | Beisebol | Baseball | `color-cod-gray` |
| `sports.tennis` | Tênis | Tenis / Tennies / Tenies | `color-cod-gray` |
| `sports.swimming` | Natação | Swiming | `color-cod-gray` |
| `sports.boat` | Náutica | Boat | `color-cod-gray` |
| `sports.desert` | Deserto | Desert | filtro `.desert` |

Filtros Isotope de esportes comuns: `.football`, `.cycling`, `.boxing`, `.racing`, `.cricket` (valores **não** traduzidos).

---

## Subcategorias — Gastronomia (`food.*`)

| slug | Rótulo pt-BR | EN / typo legado |
|------|--------------|------------------|
| `food.drinks` | Bebidas | Drinks |
| `food.fast-food` | Fast Food | Fast Food / Fastfood |
| `food.burger` | Hambúrguer | Burger |
| `food.pizza` | Pizza | Pizza |
| `food.beef-pizza` | Pizza de Carne | Beef Pizza |
| `food.chicken-pizza` | Pizza de Frango | Chicken Pizza |
| `food.vegetable-roll` | Rolinho Vegetal | Vegetable Roll |
| `food.fruits` | Frutas | Fruits |
| `food.chinese` | Chinesa | Chines / Chinese |
| `food.hobbies` | Gastronomia & Hobbies | Food & Hobbbies |

---

## Paleta `color-*` (token visual de categoria)

Cores de categoria do design system (não confundir com primária de marca).

| Classe | Hex (aprox.) | Uso típico no template |
|--------|--------------|------------------------|
| `color-primary` | `#99cc00` | Política, badges da marca, Ação/Animação |
| `color-cod-gray` | `#111` | Padrão sidebar / muitas subcategorias |
| `color-apple` | `#43a047` | Lifestyle, Android |
| `color-azure-radiance` | `#0089ff` | Esportes |
| `color-persian-green` | `#009688` | Internacional |
| `color-web-orange` | `#ffab00` | Gastronomia / Mundo Tech (variante) |
| `color-ecstasy` | `#f57f17` | Acessórios |
| `color-pomegranate` | `#f4511e` | Saúde & Fitness |
| `color-razzmatazz` | `#ed145b` | (disponível) |
| `color-disney-cerise` | `#ec008c` | Gadgets (home-3) |
| `color-scampi` | `#605ca8` | Notícias Recentes / Editor / Mais Notícias |
| `color-cutty-sark` | `#546e7a` | Mundo Tech |
| `color-white` | `#fff` | Badges em fundo escuro (home-4) |

---

## Rótulos de seção (UI) — não são categorias de artigo

Usados em `topic-box-lg` de widgets. Ver também `data-widget-id` em `SCREEN-MAP.md`.

| Rótulo pt-BR | EN legado | Uso |
|--------------|-----------|-----|
| Destaques | Top Stories | Seção / ticker |
| Redes Sociais | Stay Connected | Sidebar |
| Newsletter | Newsletter | Sidebar |
| Tags | Tags | Sidebar / artigo |
| Notícias Recentes | Recent News | Sidebar |
| Mais Notícias | More News | Seção |
| Mais Avaliados | Most Reviews | Sidebar |
| Últimas Avaliações | Latest Reviews | Sidebar |
| Posts Relacionados | Related Posts | Artigo |
| Assistir Vídeos | Watch Videos | Seção vídeo |
| Escolha do Editor | Editor Picks | Carrossel |
| Últimas Notícias | Latest News | Seção |
| Em Alta | Trending Posts | Seção |
| Novidades | What’s New | Seção home-3 |
| Categorias | Categories | Sidebar / área |
| Arquivo | Archives | Archive |
| Sobre Nós | About Us | Contato |
| Localização | Location Info | Contato |
| Envie uma Mensagem | Send Us Message | Contato |

---

## Typos corrigidos na tradução

| Legado (EN/typo) | pt-BR aplicado |
|------------------|----------------|
| Ragbe | Rúgbi |
| Rorse Rider | Hipismo |
| Adventue / Ventura | Aventura |
| Tenies / Tennies / Tenis | Tênis |
| Fotball | Futebol |
| Swiming | Natação |
| Chines | Chinesa |
| Fadgets | Gadgets |
| Hobbbies | Hobbies |
| Sprts (ctg-title) | Esportes |
| Style ZOne | Style Zone |
| Maxrocke / Maxrocket | MaxRocket |

---

## Reaplicar traduções

```bash
cd News-Website-Template
python3 scripts/translate_topic_boxes.py
```

O script atualiza `topic-box*`, texto de links `data-filter`, `ctg-title*` e labels de [`screen-map.json`](../screen-map.json). **Não altera** valores de `data-filter` nem nomes de classes CSS.
