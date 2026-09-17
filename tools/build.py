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
CHEVRON_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'
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

# Iconos grandes por capítulo del informe — geometría simple (línea fina,
# formas primitivas: flecha, círculos, barras, triángulo) en vez de una
# forma derivada de datos. Se usan como marca de agua grande en el margen
# de cada capítulo; el trazo fino (1.4) es deliberado para que se vea bien
# ampliado, igual que el -webkit-text-stroke de los numerales outline.
CHAPTER_ICONS = {
    1: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 17l6-6 4 4 6-9"/><path d="M15 6h5v5"/></svg>',
    2: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="9" cy="9" r="6"/><circle cx="15" cy="9" r="6"/><circle cx="12" cy="15.5" r="6"/></svg>',
    3: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="15" width="6" height="6" rx="0.6"/><rect x="9" y="11" width="6" height="10" rx="0.6"/><rect x="16" y="6" width="6" height="15" rx="0.6"/></svg>',
    4: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"><path d="M12 3 22 20 2 20Z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17" r="0.6" fill="currentColor" stroke="none"/></svg>',
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


def load_informe():
    with open(os.path.join(CONTENT, "informe.json"), encoding="utf-8") as f:
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
    # El número de columnas se decide acá según cuántos facts hay de
    # verdad — con un ancho de columna fijo por CSS (repeat(N, 1fr) con N
    # chico), 1-3 facts ya no dejan columnas vacías desperdiciando espacio
    # (bug reportado: el bloque de Panorama con 2 facts en una grilla de 4).
    n = len(facts or [])
    mod = f" facts-grid--{n}" if 1 <= n <= 3 else ""
    return f'<div class="facts-grid{mod} reveal">\n' + "\n".join(items) + "\n    </div>"


def stat_val_html(r):
    """Una fila de stats-list puede llevar un solo valor ("val", texto
    plano) o dos valores de períodos distintos ("periods": [{label,
    figure}, ...]) — el segundo caso reemplaza el viejo formato "X / Y" o
    "X → Y", que no dejaba claro a qué año correspondía cada cifra sin leer
    el ctx. Con `periods` cada número lleva su propia etiqueta de año al
    lado, sin depender del texto de contexto para entenderse."""
    if r.get("periods"):
        items = "".join(
            f'<span class="stat-row__period">'
            f'<span class="stat-row__period-label">{esc(p["label"])}</span>'
            f'<span class="stat-row__period-figure">{esc(p["figure"])}</span>'
            f'</span>'
            for p in r["periods"]
        )
        return f'<div class="stat-row__val stat-row__val--split">{items}</div>'
    return f'<p class="stat-row__val">{esc(r["val"])}</p>'


def stats_list_html(rows):
    if not rows:
        return ""
    items = []
    for r in rows:
        items.append(
            f'    <div class="stat-row">\n'
            f'      <p class="stat-row__key">{esc(r["key"])}</p>\n'
            f'      {stat_val_html(r)}\n'
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
    # Sin pie de foto: en un informe AAA la fotografía editorial ilustra,
    # no necesita una leyenda descriptiva de lo que ya se ve o de lo que
    # el propio texto de al lado ya cuenta (créditos completos en README.md).
    if not photo:
        return ""
    return (
        f'<figure class="obj-photo reveal">\n'
        f'  <div class="obj-photo__frame">\n'
        f'    <img src="{base}{esc(photo["src"])}" alt="{esc(photo.get("alt",""))}" loading="lazy" />\n'
        f'  </div>\n'
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


def risk_cards_html(risk, open_default=False):
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
    total = len(risk["alza"]) + len(risk["baja"])
    # La barra de proporción y el desplegable se agrupan en una sola tarjeta
    # (.risk-summary) — sueltos se veían como dos botones iguales (mismo
    # estilo que .drawer-trigger) apretados contra una barra de color, sin
    # que quedara claro qué hacía cada uno.
    # `open_default`: en el capítulo de Riesgos la tabla de los 9 factores
    # ahora es el contenido macro de apertura, no un detalle opcional detrás
    # de un clic — se muestra ya desplegada (sigue siendo un <details>
    # nativo, así que el lector puede colapsarla si quiere). La etiqueta del
    # summary cambia de "Ver el detalle..." a "Detalle de..." porque el
    # detalle ya está a la vista, no es una invitación a revelarlo.
    open_attr = " open" if open_default else ""
    toggle_label = f"Detalle de los {total} factores" if open_default else f"Ver el detalle de los {total} factores"
    return (
        '<div class="risk-summary">\n'
        + risk_ratio_html(risk) + "\n"
        # <details>/<summary> nativo: el balance de riesgos se abre al
        # pinchar en vez de mostrar las 9 tarjetas de entrada — cero JS,
        # el mismo patrón "cero dependencias" del resto del sitio.
        + f'<details class="risk-details"{open_attr}>\n'
        + '  <summary class="risk-details__toggle">\n'
        + f'    <span>{toggle_label}</span>\n'
        + f'    <span class="risk-details__chevron" aria-hidden="true">{CHEVRON_SVG}</span>\n'
        + '  </summary>\n'
        + '  <div class="risk-grid">\n'
        + col("alza", "Factores al alza", risk["alza"], TREND_UP_SVG) + "\n"
        + col("baja", "Factores a la baja", risk["baja"], TREND_DOWN_SVG) + "\n"
        + '  </div>\n'
        + '</details>\n'
        + '</div>'
    )


def scenario_table_html(data):
    """Tabla real (Escenario / cifra) para comparar el mismo indicador bajo
    dos intensidades de un evento (p.ej. moderado/fuerte de El Niño). No usa
    el patrón `periods` de `stats_list` porque esas etiquetas ("Escenario
    moderado"/"Escenario fuerte") son más largas que las que ese componente
    espera (años cortos) — no cabían en su columna angosta y partían el
    número de su unidad al ajustar línea, además de no leerse como tabla al
    ser una sola fila. Acá cada escenario es una fila real de un `<table>`."""
    if not data:
        return ""
    rows = "".join(
        f'      <tr><td class="scenario-table__scenario">{esc(r["scenario"])}</td>'
        f'<td class="scenario-table__figure">{esc(r["figure"])}</td></tr>\n'
        for r in data["rows"]
    )
    ctx_html = f'  <p class="scenario-table__ctx">{rich(data["ctx"])}</p>\n' if data.get("ctx") else ""
    return (
        '<div class="scenario-table reveal">\n'
        f'  <p class="scenario-table__key">{esc(data["key"])}</p>\n'
        '  <table class="scenario-table__grid">\n'
        f'    <thead><tr><th>Escenario</th><th>{esc(data.get("col_label", "Valor"))}</th></tr></thead>\n'
        '    <tbody>\n' + rows + '    </tbody>\n'
        '  </table>\n'
        + ctx_html
        + '</div>'
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
    if sec.get("scenario_table"):
        body.append("      " + scenario_table_html(sec["scenario_table"]).replace("\n", "\n      "))
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

def masthead_html(chapters):
    items = []
    for i, block in enumerate(chapters):
        active = " is-active" if i == 0 else ""
        items.append(
            f'      <li class="chapter-rail__item{active}" data-chapter="{block["num"]}">'
            f'<a href="#{block["id"]}"><span class="dot">{block["num"]:02d}</span>'
            f'<span class="chapter-rail__label">{esc(block["title"])}</span></a></li>'
        )
    return f'''<header class="masthead">
  <div class="wrap masthead__inner">
    <a href="#top" class="brand" aria-label="Keyword — inicio">
      <img src="img/logo-keyword-white.svg" alt="Keyword" class="brand__logo masthead__logo" />
    </a>
    <nav class="chapter-rail" aria-label="Progreso del informe">
      <ol>
{chr(10).join(items)}
      </ol>
    </nav>
  </div>
</header>'''


def cover_html(data):
    # Foto editorial real a sangre (mismo tratamiento validado del hero
    # anterior: degradado de abajo hacia arriba, el titular siempre asienta
    # sobre índigo sólido, el cielo de la foto respira arriba). Reemplaza la
    # textura de barras de datos en este lugar específico — con una foto
    # real de fondo, la textura abstracta quedaba compitiendo de más; la
    # textura de datos se conserva en el riel de cada capítulo, donde no
    # hay foto.
    return f'''<section class="cover" id="top">
  <div class="cover__media">
    <img src="img/hero-guayaquil.webp" alt="" loading="eager" />
  </div>
  <div class="wrap cover__inner">
    <div class="cover__content">
      <p class="kicker">{PRODUCT_TITLE} &middot; Banco Central del Ecuador</p>
      <h1>{rich(data["title"])}</h1>
    </div>
  </div>
</section>'''


def divider_html(next_block):
    # Sin el numeral gigante: repetía, idéntico en tamaño, el mismo numeral
    # que aparece un segundo después en el riel del capítulo — se leía como
    # el mismo elemento duplicado, no como "viene esto". El ícono chico acá
    # es un adelanto del ícono grande del riel, no una repetición literal.
    icon_svg = CHAPTER_ICONS.get(next_block["num"], "")
    return f'''<section class="divider">
  <div class="wrap divider__inner">
    <p class="divider__eyebrow">Capítulo siguiente</p>
    <div class="divider__icon" aria-hidden="true">{icon_svg}</div>
    <p class="divider__title">{esc(next_block["title"])}</p>
  </div>
</section>'''


def lead_note_html(text):
    """Frase corta separada del párrafo principal (p.ej. una precisión o un
    dato de cierre) tratada como un punto destacado en vez de una cláusula
    más dentro del mismo bloque de texto — le da variación de ritmo visual
    a un párrafo que si no se leería todo parejo."""
    if not text:
        return ""
    return (
        f'<div class="lead-note reveal">\n'
        f'  <span class="lead-note__marker" aria-hidden="true"></span>\n'
        f'  <p>{rich(text)}</p>\n'
        f'</div>'
    )


def chapter_html(block):
    num = block["num"]
    bid = block["id"]
    headline = block["headline"]

    chart_html = charts.render_chart(load_chart(headline["chart"])) if headline.get("chart") else ""
    stat_tiles = stats_hero_html(headline.get("stats_hero")) if headline.get("stats_hero") else ""
    note_html = lead_note_html(headline.get("intro_note"))

    extra = []
    if headline.get("facts") or headline.get("highlight"):
        extra.append(facts_grid_html(headline.get("facts"), headline.get("highlight")))
    # stats_list normalmente es una elaboración adicional y va después del
    # gráfico (orden por defecto). Cuando es el desglose de los componentes
    # que explican la cifra del párrafo (p.ej. los tres motores del
    # crecimiento) — flag `stats_list_top` — va arriba de todo, justo
    # después del párrafo, para que se lea como el sustento de esa cifra en
    # vez de una nota suelta pegada a un gráfico de un tema relacionado
    # pero distinto (mismo criterio que ya usa el Notion de referencia).
    stats_list_html_block = stats_list_html(headline["stats_list"]) if headline.get("stats_list") else ""
    top_stats = stats_list_html_block if headline.get("stats_list_top") else ""
    if headline.get("stats_list") and not headline.get("stats_list_top"):
        extra.append(stats_list_html_block)
    extra_html = ("\n\n        " + "\n\n        ".join(extra)) if extra else ""

    photo = photo_html(block.get("photo"))
    photo_block = ("\n        " + photo.replace("\n", "\n        ") + "\n") if photo else ""
    icon_svg = CHAPTER_ICONS.get(num, "")
    drawer_trigger = (
        f'<a href="#drawer-{bid}" class="drawer-trigger" data-drawer-open="{bid}">'
        f'<span>{esc(block["drawer"]["trigger_label"])}</span>'
        f'<span class="drawer-trigger__icon" aria-hidden="true">{ARROW_SVG}</span></a>'
    )

    if bid == "riesgos":
        # De lo macro a lo micro: el balance de los 9 factores del BCE
        # (mostrado ya desplegado, no detrás de un clic) se lee primero,
        # completo; El Niño es una cuantificación aparte (no uno de los
        # nueve, ver headline.intro_note) y cierra el capítulo con su propio
        # detalle y el chip hacia el panel ampliado. Antes el orden era
        # 9 factores (mención) → El Niño (foto+gráfico+chip) → 9 factores
        # (tabla) — el mismo número aparecía dos veces con el detalle de un
        # tema distinto en medio, lo que leía como confuso/circular.
        # La foto va justo después del párrafo de apertura, igual que en los
        # otros 3 capítulos (imagen de cabecera del capítulo, no una
        # ilustración pegada al gráfico de El Niño) — antes quedaba
        # encajonada entre la nota de transición y el gráfico, una posición
        # que no sigue el mismo patrón que el resto del informe.
        risk = load("riesgos")["sections"][0]["risk_cards"]
        risk_table = f'<div class="reveal">{risk_cards_html(risk, open_default=True)}</div>'
        body = f'''<p class="lead reveal">{rich(headline["intro"])}</p>
{photo_block}
      {risk_table}

      {note_html}
      {chart_html}
      {extra_html}

      {drawer_trigger}'''
    else:
        closing = ""
        if bid == "crecimiento-general":
            home = load("home")
            closing = f'\n\n        <div class="quote-panel--inset">{quote_panel_html(home.get("quote_closing"))}</div>'
        body = f'''<p class="lead reveal">{rich(headline["intro"])}</p>
      {note_html}
      {top_stats}
{photo_block}
      {stat_tiles}

      {chart_html}
      {extra_html}

      {drawer_trigger}
      {closing}'''

    return f'''<section class="chapter chapter--paper" id="{bid}" data-chapter-section="{num}" aria-labelledby="titulo-{bid}">
  <div class="chapter__grid">
    <aside class="chapter__rail">
      <div class="chapter__rail-icon" aria-hidden="true">{icon_svg}</div>
      <div class="chapter__rail-sticky">
        <span class="chapter__num">{num:02d}</span>
        <span class="chapter__label" id="titulo-{bid}">{esc(block["title"])}</span>
      </div>
    </aside>

    <div class="chapter__body">
      {body}
    </div>
  </div>
</section>

{drawer_html(block)}'''


def drawer_html(block):
    """Panel lateral con el detalle completo del bloque — mismo contenido
    que antes vivía en la página aparte del tema, ahora detrás de un
    'Ver más'. Base funcional en CSS puro (:target, ver .detail-drawer en
    styles.css) para que abrir/cerrar funcione incluso sin JS; main.js
    solo suma cierre con Escape y el bloqueo de scroll del body."""
    drawer = block["drawer"]
    bid = block["id"]
    sections_html = "\n\n".join(section_html(s) for s in drawer["sections"])
    photo = photo_html(drawer.get("photo"))
    # Frase puente: retoma la afirmación del capítulo antes de entrar en el
    # detalle, para que el panel se sienta la continuación de la misma
    # historia y no una lista de datos sueltos sin relación con lo de arriba.
    lead_html = f'<p class="detail-drawer__lead">{rich(drawer["lead"])}</p>' if drawer.get("lead") else ""
    body = (photo + "\n\n    " if photo else "") + '<div class="roadmap">\n' + sections_html + '\n    </div>'
    # El panel tiene su propio título narrativo — nunca repite el título
    # del capítulo (que ya se ve en el riel de fondo), describe qué
    # historia cuenta específicamente este detalle.
    title = drawer.get("title", block["title"])
    return f'''<div class="detail-drawer" id="drawer-{bid}" role="dialog" aria-modal="true" aria-labelledby="drawer-{bid}-title" tabindex="-1">
  <div class="wrap detail-drawer__inner">
    <div class="detail-drawer__head">
      <p class="detail-drawer__eyebrow">Detalle completo</p>
      <p class="detail-drawer__title" id="drawer-{bid}-title">{esc(title)}</p>
      <a href="#_" class="detail-drawer__close" aria-label="Cerrar detalle">&times;</a>
      {lead_html}
    </div>
    <div class="detail-drawer__body">
    {body}
    </div>
  </div>
</div>'''


def quote_panel_html(qc):
    """Bloque de cierre con cita presidencial. Tratamiento formal/editorial
    deliberadamente contenido: un retrato pequeño junto al nombre y cargo
    (como una atribución de prensa), no una foto a gran escala — un
    retrato grande ahí se leía como propaganda, no como reporte."""
    if not qc:
        return ""
    photo = qc.get("photo") or {}
    portrait_html = (
        f'<img class="quote-panel__portrait" src="img/{esc(photo.get("src",""))}" '
        f'alt="{esc(photo.get("alt",""))}" loading="lazy" />'
        if photo.get("src") else ""
    )
    # Cuando hay una segunda cita (quote2), va en su propio blockquote en
    # vez de quedar cosida dentro del párrafo de "text" — una cita citada
    # de corrido dentro de una oración larga es exactamente el párrafo
    # denso que el resto del sitio evita.
    quote2_html = f'<blockquote class="quote-panel__quote">&ldquo;{rich(qc["quote2"])}&rdquo;</blockquote>' if qc.get("quote2") else ""
    return f'''<div class="quote-panel reveal">
    <div class="quote-panel__head">
      {portrait_html}
      <div>
        <p class="quote-panel__name">{esc(qc.get("name",""))}</p>
        <p class="quote-panel__role">{esc(qc.get("role",""))}</p>
      </div>
    </div>
    <p class="quote-panel__intro">{rich(qc["intro"])}</p>
    <blockquote class="quote-panel__quote">&ldquo;{rich(qc["quote"])}&rdquo;</blockquote>
    <p class="quote-panel__text">{rich(qc["text"])}</p>
    {quote2_html}
  </div>'''


REPORT_TPL = """<!doctype html>
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

{masthead}

<main>

{cover}

{chapters}

</main>

<footer class="site-footer" id="cierre">
  <div class="wrap site-footer__inner">
    <img src="img/logo-keyword-white.svg" alt="Keyword" class="site-footer__logo" />
    <p class="site-footer__copy">&copy; Todos los derechos reservados</p>
    <p class="site-footer__contact">Contacto: <a href="mailto:{email}">{email}</a></p>
  </div>
</footer>

<a href="#_" class="drawer-backdrop" aria-hidden="true" tabindex="-1"></a>

<script src="js/main.js"></script>
</body>
</html>
"""


def build_report():
    data = load("home")
    chapters_data = load_informe()

    pieces = []
    for i, block in enumerate(chapters_data):
        pieces.append(chapter_html(block))
        if i < len(chapters_data) - 1:
            pieces.append(divider_html(chapters_data[i + 1]))
    chapters_html = "\n\n".join(pieces)

    page = REPORT_TPL.format(
        title=esc(data["title"]), meta_desc=esc(data["meta_desc"]),
        font=FONT_LINKS,
        masthead=masthead_html(chapters_data),
        cover=cover_html(data),
        chapters=chapters_html,
        email=EMAIL,
    )
    with open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote index.html")


def main():
    os.makedirs(PAGES, exist_ok=True)
    build_report()
    for theme in THEMES:
        build_tema(theme)
    print(f"\nListo: index.html + {N} páginas de tema generadas.")


if __name__ == "__main__":
    main()
