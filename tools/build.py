#!/usr/bin/env python3
"""Genera index.html y pages/tema-NN-*.html a partir de content/*.json.

Patrón heredado de ace2040 / ley-transporte-impacto: sitio estático
pre-renderizado (sin hidratación cliente), CSS compartido, contenido en
JSON separado del layout. Lo nuevo en este producto: cada tema puede
llevar gráficos SVG (tools/charts.py), fotografía editorial donde el
tema tiene un sujeto real y fotografiable, y el motion vive a nivel de
sección (no ítem por ítem) — un solo momento coreografiado por bloque,
con stagger por nth-child, en vez de N entradas idénticas repetidas.
"""
import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(SITE, "content")
CHARTS_DIR = os.path.join(CONTENT, "charts")
PAGES = os.path.join(SITE, "pages")

BRAND = "Keyword"
EMAIL = "info@keyword.com.ec"
PRODUCT_TITLE = "Previsiones Económicas 2026-2030"

# (num, slug, nombre, corto, headline_figure, headline_label, card_photo)
# El Balance de riesgos ya no es un tema propio: vive como sección de
# cierre del home (ver build_home), justo antes del pie. card_photo es el
# archivo en img/ que ilustra la tarjeta del tema en el muro del home.
THEMES = [
    (1, "tema-01-panorama", "Panorama y cifras clave", "Panorama", "2,7%", "PIB 2026", "card-panorama.webp"),
    (2, "tema-02-pulso-domestico", "El pulso de la economía ecuatoriana", "Pulso doméstico", "+2,2%", "IMAEc jun-26", "card-pulso.webp"),
    (3, "tema-03-motores", "Los motores del crecimiento 2026-2030", "Motores del crecimiento", "+5,8%", "Inversión (FBKF) 2026", "card-motores.webp"),
    (4, "tema-04-industrias", "El crecimiento por industria", "Por industria", "+6,8%", "Minería lidera en 2026", "hero-puerto.webp"),
    (5, "tema-05-externo", "Petróleo, sector externo y reservas", "Sector externo", "USD 4.587M", "Cuenta corriente 2026", "card-externo.webp"),
    (6, "tema-06-fiscal-monetario", "Sector fiscal, crédito e inflación", "Sector fiscal y monetario", "2,1%", "Inflación 2026", "card-fiscal.webp"),
    (7, "tema-07-el-nino", "Fenómeno de El Niño", "El Niño: el riesgo climático", "-1,4 p.p.", "PIB 2027, escenario fuerte", "card-el-nino.webp"),
]
N = len(THEMES)

FONT_LINKS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" />'
)

ARROW_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
TREND_UP_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 17l6-6 4 4 6-9"/><path d="M15 6h5v5"/></svg>'
TREND_DOWN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 7l6 6 4-4 6 9"/><path d="M15 18h5v-5"/></svg>'

# Iconos pequeños opcionales para .fact (p.ej. el desglose de industrias en
# tema-04) — mismo estilo trazo/round que ARROW_SVG, un icono por sector.
FACT_ICONS = {
    "mining": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 20l6-11 4 6 2-3 6 8z"/></svg>',
    "bolt": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 3 4 14h6l-1 7 9-11h-6z"/></svg>',
    "construction": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 21V9l8-5v5h8v12"/><path d="M12 9v12"/><path d="M4 21h16"/></svg>',
    "food": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21V9"/><path d="M12 9c-2.2 0-4-1.8-4-4 2.2 0 4 1.8 4 4z"/><path d="M12 9c2.2 0 4-1.8 4-4-2.2 0-4 1.8-4 4z"/><path d="M12 15c-2.2 0-4-1.8-4-4 2.2 0 4 1.8 4 4z"/><path d="M12 15c2.2 0 4-1.8 4-4-2.2 0-4 1.8-4 4z"/></svg>',
    "art": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9c0-1.1-.9-2-2-2h-2.2a2 2 0 0 1-1.9-2.7c.2-.5.1-1-.3-1.4A2 2 0 0 0 13 5.3c0-.9-.4-1.7-1-2.1-.6-.2-1.3-.2-2 0"/><circle cx="7.5" cy="10.5" r="1"/><circle cx="9" cy="7" r="1"/><circle cx="14.5" cy="6.2" r="1"/></svg>',
    "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 21c8 0 14-6 14-14V5h-2C9 5 3 11 3 19v2z"/><path d="M3 21c4-6 8-9 13-11"/></svg>',
}


def esc(s):
    return html.escape(str(s), quote=True)


def rich(s):
    """Texto ya autorado con HTML de confianza (<strong>...</strong>),
    escrito a mano en content/*.json — no llega input externo, se
    renderiza tal cual."""
    return s


def load(name):
    with open(os.path.join(CONTENT, f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def load_chart(slug):
    with open(os.path.join(CHARTS_DIR, f"{slug}.json"), encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------------
# Bloques reutilizables — el contenedor lleva .reveal (un solo momento
# coreografiado); los ítems dentro se escalonan por nth-child en CSS,
# no repiten cada uno su propia entrada idéntica.
# ----------------------------------------------------------------------

def facts_grid_html(facts, highlight=None):
    if not facts and not highlight:
        return ""
    items = []
    for f in facts or []:
        icon_svg = FACT_ICONS.get(f.get("icon"))
        icon_html = f'        <span class="fact__icon" aria-hidden="true">{icon_svg}</span>\n' if icon_svg else ""
        items.append(
            f'      <div class="fact">\n'
            f'{icon_html}'
            f'        <p class="fact__label">{esc(f["label"])}</p>\n'
            f'        <p class="fact__text">{rich(f["text"])}</p>\n'
            f'      </div>'
        )
    if highlight:
        items.append(
            f'      <div class="fact fact--highlight">\n'
            f'        <span class="fact__icon" aria-hidden="true">{ARROW_SVG}</span>\n'
            f'        <div>\n'
            f'          <p class="fact__label">{esc(highlight["label"])}</p>\n'
            f'          <p class="fact__text">{rich(highlight["text"])}</p>\n'
            f'        </div>\n'
            f'      </div>'
        )
    return '<div class="facts-grid reveal">\n' + "\n".join(items) + "\n    </div>"


def stats_list_html(rows):
    if not rows:
        return ""
    items = []
    for r in rows:
        items.append(
            f'    <div class="stat-row">\n'
            f'      <p class="stat-row__key">{esc(r["key"])}</p>\n'
            f'      <p class="stat-row__val">{esc(r["val"])}</p>\n'
            f'      <p class="stat-row__ctx">{rich(r["ctx"])}</p>\n'
            f'    </div>'
        )
    return '<div class="stats-list reveal">\n' + "\n".join(items) + "\n  </div>"


def stats_hero_html(items):
    if not items:
        return ""
    cards = []
    for it in items:
        decimals = 1 if "," in it["figure"] else 0
        count_to = it["figure"].replace(".", "").replace(",", ".")
        cards.append(
            f'    <div class="stat-hero">\n'
            f'      <p class="stat-hero__label">{esc(it["label"])}</p>\n'
            f'      <p class="stat-hero__figure"><span class="counter" data-count-to="{count_to}" '
            f'data-decimals="{decimals}">{esc(it["figure"])}</span><span class="stat-hero__unit">{esc(it["unit"])}</span></p>\n'
            f'      <p class="stat-hero__note">{rich(it["note"])}</p>\n'
            f'    </div>'
        )
    return '<div class="stats-hero-row reveal">\n' + "\n".join(cards) + "\n  </div>"


def photo_html(photo, base="img/"):
    if not photo:
        return ""
    return (
        f'<figure class="obj-photo reveal">\n'
        f'  <div class="obj-photo__frame">\n'
        f'    <img src="{base}{esc(photo["src"])}" alt="{esc(photo.get("alt",""))}" loading="lazy" />\n'
        f'  </div>\n'
        f'  <figcaption>{rich(photo["caption"])}</figcaption>\n'
        f'</figure>'
    )


# --- Balance de riesgos: componentes visuales compartidos entre el home
# (versión compacta) y la página propia del tema (versión completa). ------

def risk_ratio_html(risk):
    n_alza, n_baja = len(risk["alza"]), len(risk["baja"])
    return f'''<div class="risk-ratio">
  <div class="risk-ratio__seg risk-ratio__seg--alza" style="flex:{n_alza}">
    <span class="risk-ratio__n">{n_alza}</span>
    <span class="risk-ratio__label">factor{"es" if n_alza != 1 else ""} al alza</span>
  </div>
  <div class="risk-ratio__seg risk-ratio__seg--baja" style="flex:{n_baja}">
    <span class="risk-ratio__n">{n_baja}</span>
    <span class="risk-ratio__label">factor{"es" if n_baja != 1 else ""} a la baja</span>
  </div>
</div>'''


def risk_cards_html(risk):
    def col(kind, label, items, icon):
        cards = "\n".join(
            f'      <article class="risk-card">\n'
            f'        <span class="risk-card__icon" aria-hidden="true">{icon}</span>\n'
            f'        <p class="risk-card__title">{esc(it["title"])}</p>\n'
            f'        <p class="risk-card__text">{rich(it["text"])}</p>\n'
            f'      </article>'
            for it in items
        )
        return (
            f'  <div class="risk-col risk-col--{kind}">\n'
            f'    <div class="risk-col__head">\n'
            f'      <span class="risk-col__dot" aria-hidden="true"></span>\n'
            f'      <p class="risk-col__title">{label} ({len(items)})</p>\n'
            f'    </div>\n{cards}\n  </div>'
        )
    return (
        risk_ratio_html(risk) + "\n"
        + '<div class="risk-grid">\n'
        + col("alza", "Factores al alza", risk["alza"], TREND_UP_SVG) + "\n"
        + col("baja", "Factores a la baja", risk["baja"], TREND_DOWN_SVG) + "\n"
        + "</div>"
    )


def section_html(sec):
    head = (
        f'      <header class="fact-section__head">\n'
        f'        <h2 class="fact-section__title">{esc(sec["title"])}</h2>\n'
        + (f'        <p class="fact-section__lead">{rich(sec["lead"])}</p>\n' if sec.get("lead") else "")
        + '      </header>'
    )
    body = []
    if sec.get("chart"):
        chart_html = charts.render_chart(load_chart(sec["chart"]))
        # Un gráfico embebido a nivel de sección ocupa el ancho completo por
        # defecto (necesario para rankings largos como industrias). Cuando
        # el gráfico es simple (pocas categorías) eso lo hace ver
        # desproporcionadamente grande frente al resto — chart_compact lo
        # acota al ancho de una columna de obj-lead; chart_cap lo acota a un
        # ancho generoso pero no de borde a borde.
        if sec.get("chart_compact"):
            chart_html = f'<div class="fact-section__chart--compact">{chart_html}</div>'
        elif sec.get("chart_cap"):
            chart_html = f'<div class="fact-section__chart--cap">{chart_html}</div>'
        body.append("      " + chart_html.replace("\n", "\n      "))
    if sec.get("facts") or sec.get("highlight"):
        body.append("      " + facts_grid_html(sec.get("facts"), sec.get("highlight")).replace("\n", "\n      "))
    if sec.get("stats_list"):
        body.append("      " + stats_list_html(sec["stats_list"]).replace("\n", "\n      "))
    if sec.get("risk_cards"):
        body.append("      " + risk_cards_html(sec["risk_cards"]).replace("\n", "\n      "))
    return f'    <div class="fact-section reveal">\n{head}\n' + "\n\n".join(body) + "\n    </div>"


def nav_top_html(current):
    items = []
    for num, slug, nombre, corto, _fig, _lab, _photo in THEMES:
        cur = ' aria-current="page"' if num == current else ""
        items.append(
            f'    <a class="obj-nav-top__item obj-nav-top__item--{num}" href="{slug}.html"{cur}>\n'
            f'      <small>{num:02d}</small><span>{esc(corto)}</span>\n'
            f'    </a>'
        )
    return '<nav class="wrap obj-nav-top" aria-label="Temas del reporte">\n  <div class="obj-nav-top__grid">\n' + "\n".join(items) + "\n  </div>\n</nav>"


def pager_html(num):
    if num > 1:
        pn, pslug, pnombre, _pc, _pf, _pl, _pp = THEMES[num - 2]
        prev_link = f'''    <a class="obj-pager__link" href="{pslug}.html">
      <small>&larr; Tema {pn:02d}</small>
      <strong>{esc(pnombre)}</strong>
    </a>'''
    else:
        prev_link = '''    <a class="obj-pager__link" href="../index.html#temas">
      <small>&larr; Volver</small>
      <strong>Los temas del reporte</strong>
    </a>'''
    if num < N:
        nn, nslug, nnombre, _nc, _nf, _nl, _np = THEMES[num]
        next_link = f'''    <a class="obj-pager__link obj-pager__link--next" href="{nslug}.html">
      <small>Tema {nn:02d} &rarr;</small>
      <strong>{esc(nnombre)}</strong>
    </a>'''
    else:
        next_link = '''    <a class="obj-pager__link obj-pager__link--next" href="../index.html#cierre">
      <small>Volver al inicio &rarr;</small>
      <strong>Sobre este reporte</strong>
    </a>'''
    return prev_link + "\n" + next_link


TEMA_TPL = """<!doctype html>
<html lang="es" class="no-js">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{nombre} — {product} — Keyword</title>
  <meta name="description" content="{meta_desc}" />
  {font}
  <link rel="stylesheet" href="../css/styles.css" />
</head>
<body class="obj-page--{num}">

<header class="site-header">
  <div class="wrap site-header__inner">
    <a href="../index.html" class="brand" aria-label="Keyword — inicio">
      <img src="../img/logo-keyword-white.svg" alt="Keyword" class="brand__logo" />
    </a>
    <nav class="nav-crumbs" aria-label="Ruta de navegación">
      <a href="../index.html">{product}</a> &middot; <span>{corto}</span>
    </nav>
  </div>
</header>

<main>

{nav}

<section class="obj-hero obj-hero--{num}" aria-labelledby="titulo-tema">
  <div class="wrap">
    <div class="obj-hero__row">
      <span class="obj-hero__num" aria-hidden="true">{num:02d}<small>/{n:02d}</small></span>
      <h1 class="obj-hero__name" id="titulo-tema">{nombre}</h1>
    </div>

    <div class="obj-lead{lead_solo}">
      <div class="obj-lead__card reveal">
        <p class="obj-lead__text">{en_sintesis}</p>
      </div>
      {chart_lead}
    </div>

    {photo}

    <div class="roadmap">
{sections}
    </div>

    <nav class="obj-pager" aria-label="Navegación entre temas">
{pager}
    </nav>
  </div>
</section>

</main>

<footer class="site-footer">
  <div class="wrap site-footer__inner">
    <img src="../img/logo-keyword-white.svg" alt="Keyword" class="site-footer__logo" />
    <p class="site-footer__copy">&copy; Todos los derechos reservados</p>
    <p class="site-footer__contact">Contacto: <a href="mailto:{email}">{email}</a></p>
  </div>
</footer>

<script src="../js/main.js"></script>
</body>
</html>
"""


def build_tema(theme):
    num, slug, nombre, corto, fig, lab, _photo = theme
    data = load(slug)
    chart_lead = ""
    lead_solo = ""
    if data.get("chart"):
        chart_lead = charts.render_chart(load_chart(data["chart"]))
    else:
        lead_solo = " obj-lead--solo"

    sections_html = "\n\n".join(section_html(s) for s in data["sections"])

    page = TEMA_TPL.format(
        num=num, n=N, nombre=esc(nombre), corto=esc(corto),
        product=PRODUCT_TITLE, meta_desc=esc(data["meta_desc"]),
        font=FONT_LINKS, nav=nav_top_html(num),
        en_sintesis=rich(data["en_sintesis"]),
        lead_solo=lead_solo, chart_lead=chart_lead,
        photo=photo_html(data.get("photo"), base="../img/"),
        sections=sections_html,
        pager=pager_html(num),
        email=EMAIL,
    )
    out_path = os.path.join(PAGES, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote pages/{slug}.html")


# ----------------------------------------------------------------------
# Home
# ----------------------------------------------------------------------

def obj_cover_html(theme):
    num, slug, nombre, corto, fig, lab, photo = theme
    photo_html = (
        f'<div class="obj-cover__photo"><img src="img/{esc(photo)}" alt="" loading="lazy" /></div>'
        if photo else ""
    )
    return f'''  <a class="obj-cover obj-cover--{num} obj-cover--data" href="pages/{slug}.html">
    <div class="obj-cover__top">
      {photo_html}
      <span class="obj-cover__num" aria-hidden="true">{num:02d}</span>
      <p class="obj-cover__title">{esc(corto)}</p>
      <span class="obj-cover__cta-pill">Explorar tema {ARROW_SVG}</span>
    </div>
    <div class="obj-cover__data">
      <span class="obj-cover__data-figure">{esc(fig)}</span>
      <span class="obj-cover__data-label">{esc(lab)}</span>
    </div>
  </a>'''


HOME_TPL = """<!doctype html>
<html lang="es" class="no-js">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — Keyword</title>
  <meta name="description" content="{meta_desc}" />
  {font}
  <link rel="stylesheet" href="css/styles.css" />
</head>
<body>

<header class="site-header">
  <div class="wrap site-header__inner">
    <a href="index.html" class="brand" aria-label="Keyword — inicio">
      <img src="img/logo-keyword-white.svg" alt="Keyword" class="brand__logo" />
    </a>
    <nav class="nav-crumbs" aria-label="Ruta de navegación">
      <span>{product}</span>
    </nav>
  </div>
</header>

<nav class="home-nav" aria-label="Índice del análisis">
  <div class="wrap home-nav__inner">
    <a href="#cifras">En cifras</a>
    <a href="#temas">Los temas</a>
    <a href="#el-nino">Fenómeno de El Niño</a>
    <a href="#riesgos">Balance de riesgos</a>
    <a href="#cierre">Sobre este reporte</a>
  </div>
</nav>

<main>

<section class="hero" aria-labelledby="titulo-principal">
  <div class="hero__media">
    <img src="img/hero-guayaquil.webp" alt="" loading="eager" />
  </div>
  <div class="wrap hero__inner">
    <h1 class="hero__title" id="titulo-principal">{title}</h1>
    <p class="hero__subtitle">{subtitle}</p>
  </div>
</section>

<section class="section" id="cifras" aria-labelledby="titulo-cifras">
  <div class="wrap">
    <header class="section-mark">
      <h2 class="section-mark__title" id="titulo-cifras">El escenario en diez datos</h2>
    </header>

    {stats_hero}

    {stats_list}
  </div>
</section>

<section class="section" id="temas" aria-labelledby="titulo-temas">
  <div class="wrap">
    <header class="section-mark">
      <h2 class="section-mark__title" id="titulo-temas">{intro_title}</h2>
    </header>

    <div class="objectives__grid reveal">
{cards}
    </div>
  </div>
</section>

<section class="section" id="el-nino" aria-labelledby="titulo-el-nino">
  <div class="wrap">
    <div class="closing-panel reveal">
      <h2 class="closing-panel__title" id="titulo-el-nino">{closing_title}</h2>
      <p class="closing-panel__text">{closing_text}</p>
      <a class="closing-panel__cta" href="{closing_href}">{closing_label} {arrow}</a>
    </div>
  </div>
</section>

<section class="section" id="riesgos" aria-labelledby="titulo-riesgos">
  <div class="wrap">
    <div class="risk-panel reveal">
      <h2 class="risk-panel__title" id="titulo-riesgos">{risks_title}</h2>
      <p class="risk-panel__lead">{risks_lead}</p>

      {risk_cards}
    </div>
  </div>
</section>

</main>

<footer class="site-footer" id="cierre">
  <div class="wrap">
    <p class="about-note">{final_text}</p>
  </div>
  <div class="wrap site-footer__inner">
    <img src="img/logo-keyword-white.svg" alt="Keyword" class="site-footer__logo" />
    <p class="site-footer__copy">&copy; Todos los derechos reservados</p>
    <p class="site-footer__contact">Contacto: <a href="mailto:{email}">{email}</a></p>
  </div>
</footer>

<script src="js/main.js"></script>
</body>
</html>
"""


def build_home():
    data = load("home")
    risks_data = load("riesgos")
    risk = risks_data["sections"][0]["risk_cards"]
    cards = "\n".join(obj_cover_html(t) for t in THEMES)
    page = HOME_TPL.format(
        title=esc(data["title"]), meta_desc=esc(data["meta_desc"]),
        font=FONT_LINKS, product=PRODUCT_TITLE,
        subtitle=rich(data["subtitle"]),
        stats_hero=stats_hero_html(data["stats_hero"]),
        stats_list=stats_list_html(data["stats_list"]),
        intro_title=esc(data["intro_nav"]["title"]),
        cards=cards,
        risks_title=esc(data["risks"]["title"]),
        risks_lead=rich(data["risks"]["lead"]),
        risk_cards=risk_cards_html(risk),
        closing_title=esc(data["closing"]["title"]),
        closing_text=rich(data["closing"]["text"]),
        closing_href=data["closing"]["cta_href"],
        closing_label=esc(data["closing"]["cta_label"]),
        arrow=ARROW_SVG,
        final_text=rich(data["final"]["text"]),
        email=EMAIL,
    )
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote index.html")


def main():
    os.makedirs(PAGES, exist_ok=True)
    build_home()
    for theme in THEMES:
        build_tema(theme)
    print(f"\nListo: index.html + {N} páginas de tema generadas.")


if __name__ == "__main__":
    main()
