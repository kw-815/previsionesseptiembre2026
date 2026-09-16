#!/usr/bin/env python3
"""Genera index.html y pages/tema-NN-*.html a partir de content/*.json.

Patrón heredado de ace2040 / ley-transporte-impacto: sitio estático
pre-renderizado (sin hidratación cliente), CSS compartido, contenido en
JSON separado del layout. Lo nuevo en este producto: cada tema puede
llevar gráficos SVG (tools/charts.py) y todo el markup se apoya en la
clase .reveal para el scroll-reveal de js/main.js.
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

# (num, slug, nombre, corto, headline_figure, headline_label, in_grid)
# in_grid=False => la página existe y aparece en la navegación entre temas,
# pero no se repite como tarjeta en el muro del home (ver "Balance de
# riesgos": vive como sección propia en el home, no como tarjeta más).
THEMES = [
    (1, "tema-01-panorama", "Panorama y cifras clave", "Panorama", "2,7%", "PIB 2026", True),
    (2, "tema-02-pulso-domestico", "El pulso de la economía ecuatoriana", "Pulso doméstico", "+2,2%", "IMAEc jun-26", True),
    (3, "tema-03-motores", "Los motores del crecimiento 2026-2030", "Motores del crecimiento", "+5,8%", "Inversión (FBKF) 2026", True),
    (4, "tema-04-industrias", "Cómo crecerá tu sector", "Cómo crecerá tu sector", "+6,8%", "Minería, la industria líder en 2026", True),
    (5, "tema-05-externo", "Petróleo, sector externo y reservas", "Sector externo", "USD 4.587M", "Cuenta corriente 2026", True),
    (6, "tema-06-fiscal-monetario", "Fiscal, crédito e inflación", "Fiscal y monetario", "2,1%", "Inflación 2026", True),
    (7, "tema-07-riesgos", "Balance de riesgos", "Balance de riesgos", "6 vs 3", "Riesgos a la baja vs. al alza", False),
    (8, "tema-08-el-nino", "Fenómeno de El Niño", "El Niño: el riesgo climático", "-1,4 p.p.", "PIB 2027, escenario fuerte", True),
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
# Bloques reutilizables
# ----------------------------------------------------------------------

def facts_grid_html(facts, highlight=None):
    if not facts and not highlight:
        return ""
    items = []
    for f in facts or []:
        items.append(
            f'      <div class="fact reveal">\n'
            f'        <p class="fact__label">{esc(f["label"])}</p>\n'
            f'        <p class="fact__text">{rich(f["text"])}</p>\n'
            f'      </div>'
        )
    if highlight:
        items.append(
            f'      <div class="fact fact--highlight reveal">\n'
            f'        <span class="fact__icon" aria-hidden="true">{ARROW_SVG}</span>\n'
            f'        <div>\n'
            f'          <p class="fact__label">{esc(highlight["label"])}</p>\n'
            f'          <p class="fact__text">{rich(highlight["text"])}</p>\n'
            f'        </div>\n'
            f'      </div>'
        )
    return '<div class="facts-grid">\n' + "\n".join(items) + "\n    </div>"


def stats_list_html(rows):
    if not rows:
        return ""
    items = []
    for r in rows:
        items.append(
            f'    <div class="stat-row reveal">\n'
            f'      <p class="stat-row__key">{esc(r["key"])}</p>\n'
            f'      <p class="stat-row__val">{esc(r["val"])}</p>\n'
            f'      <p class="stat-row__ctx">{rich(r["ctx"])}</p>\n'
            f'    </div>'
        )
    return '<div class="stats-list">\n' + "\n".join(items) + "\n  </div>"


def stats_hero_html(items):
    if not items:
        return ""
    cards = []
    for it in items:
        decimals = 1 if "," in it["figure"] else 0
        count_to = it["figure"].replace(".", "").replace(",", ".")
        cards.append(
            f'    <div class="stat-hero reveal">\n'
            f'      <p class="stat-hero__label">{esc(it["label"])}</p>\n'
            f'      <p class="stat-hero__figure"><span class="counter" data-count-to="{count_to}" '
            f'data-decimals="{decimals}">{esc(it["figure"])}</span><span>{esc(it["unit"])}</span></p>\n'
            f'      <p class="stat-hero__note">{rich(it["note"])}</p>\n'
            f'    </div>'
        )
    return '<div class="stats-hero-row">\n' + "\n".join(cards) + "\n  </div>"


# --- Balance de riesgos: componentes visuales compartidos entre el home
# (versión compacta) y la página propia del tema (versión completa). ------

def risk_ratio_html(risk):
    n_alza, n_baja = len(risk["alza"]), len(risk["baja"])
    return f'''<div class="risk-ratio reveal">
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
            f'      <article class="risk-card reveal">\n'
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


def risk_chips_html(risk):
    """Versión compacta (solo títulos) para el panel del home."""
    def col(kind, label, items, icon):
        chips = "\n".join(
            f'        <li class="risk-chip risk-chip--{kind}"><span class="risk-chip__icon" aria-hidden="true">{icon}</span>{esc(it["title"])}</li>'
            for it in items
        )
        return (
            f'    <div class="risk-chip-col">\n'
            f'      <p class="risk-chip-col__label">{label}</p>\n'
            f'      <ul class="risk-chip-list">\n{chips}\n      </ul>\n'
            f'    </div>'
        )
    return (
        '<div class="risk-chip-cols">\n'
        + col("alza", "Al alza", risk["alza"], TREND_UP_SVG) + "\n"
        + col("baja", "A la baja", risk["baja"], TREND_DOWN_SVG) + "\n"
        + "</div>"
    )


def section_html(sec):
    head = (
        f'      <header class="fact-section__head reveal">\n'
        f'        <p class="fact-section__eyebrow">{esc(sec["eyebrow"])}</p>\n'
        f'        <h2 class="fact-section__title">{esc(sec["title"])}</h2>\n'
        + (f'        <p class="fact-section__lead">{rich(sec["lead"])}</p>\n' if sec.get("lead") else "")
        + '      </header>'
    )
    body = []
    if sec.get("chart"):
        body.append("      " + charts.render_chart(load_chart(sec["chart"])).replace("\n", "\n      "))
    if sec.get("facts") or sec.get("highlight"):
        body.append("      " + facts_grid_html(sec.get("facts"), sec.get("highlight")).replace("\n", "\n      "))
    if sec.get("stats_list"):
        body.append("      " + stats_list_html(sec["stats_list"]).replace("\n", "\n      "))
    if sec.get("risk_cards"):
        body.append("      " + risk_cards_html(sec["risk_cards"]).replace("\n", "\n      "))
    return f'    <div class="fact-section reveal">\n{head}\n' + "\n\n".join(body) + "\n    </div>"


def nav_top_html(current):
    items = []
    for num, slug, nombre, corto, _fig, _lab, _grid in THEMES:
        cur = ' aria-current="page"' if num == current else ""
        items.append(
            f'    <a class="obj-nav-top__item obj-nav-top__item--{num}" href="{slug}.html"{cur}>\n'
            f'      <small>{num:02d}</small><span>{esc(corto)}</span>\n'
            f'    </a>'
        )
    return '<nav class="wrap obj-nav-top" aria-label="Temas del reporte">\n  <div class="obj-nav-top__grid">\n' + "\n".join(items) + "\n  </div>\n</nav>"


def pager_html(num):
    if num > 1:
        pn, pslug, pnombre, _pc, _pf, _pl, _pg = THEMES[num - 2]
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
        nn, nslug, nnombre, _nc, _nf, _nl, _ng = THEMES[num]
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
    <p class="obj-hero__kicker">Tema {num:02d} de {n:02d}</p>
    <div class="obj-hero__row">
      <h1 class="obj-hero__name" id="titulo-tema">{nombre}</h1>
      <span class="obj-hero__num" aria-hidden="true">{num:02d}</span>
    </div>

    <div class="obj-lead{lead_solo}">
      <div class="obj-lead__card reveal">
        <p class="obj-lead__label">En síntesis</p>
        <p class="obj-lead__text">{en_sintesis}</p>
      </div>
      {chart_lead}
    </div>

    <div class="roadmap" style="margin-top: clamp(2.5rem, 6vw, 4rem);">
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
    num, slug, nombre, corto, fig, lab, _grid = theme
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
    num, slug, nombre, corto, fig, lab, _grid = theme
    return f'''  <a class="obj-cover obj-cover--{num} obj-cover--data reveal" href="pages/{slug}.html">
    <div class="obj-cover__top">
      <span class="obj-cover__num" aria-hidden="true">{num:02d}</span>
      <p class="obj-cover__title">{esc(corto)}</p>
      <div class="obj-cover__cta">
        <span class="obj-cover__cta-pill">Explorar tema {ARROW_SVG}</span>
        <span class="obj-cover__meta">Tema {num:02d} de {N:02d}</span>
      </div>
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
    <a href="#riesgos">Balance de riesgos</a>
    <a href="#el-nino">Fenómeno de El Niño</a>
    <a href="#cierre">Sobre este reporte</a>
  </div>
</nav>

<main>

<section class="hero hero--data" aria-labelledby="titulo-principal">
  <div class="wrap hero__inner">
    <h1 class="hero__title" id="titulo-principal">{title}</h1>
    <p class="hero__subtitle">{subtitle}</p>
  </div>
</section>

<section class="section" id="cifras" aria-labelledby="titulo-cifras">
  <div class="wrap">
    <header class="section-mark">
      <span class="section-mark__num" aria-hidden="true">01</span>
      <p class="section-mark__eyebrow">En cifras</p>
      <h2 class="section-mark__title" id="titulo-cifras">El escenario en diez datos</h2>
      <p class="section-mark__lead">Lo esencial de la Programación Macroeconómica 2026-2030 del Banco Central.</p>
    </header>

    {stats_hero}

    {stats_list}
  </div>
</section>

<section class="section" id="temas" aria-labelledby="titulo-temas">
  <div class="wrap">
    <header class="section-mark">
      <span class="section-mark__num" aria-hidden="true">02</span>
      <p class="section-mark__eyebrow">{intro_eyebrow}</p>
      <h2 class="section-mark__title" id="titulo-temas">{intro_title}</h2>
      <p class="section-mark__lead">{intro_lead}</p>
    </header>

    <div class="objectives__grid">
{cards}
    </div>
  </div>
</section>

<section class="section" id="riesgos" aria-labelledby="titulo-riesgos">
  <div class="wrap">
    <div class="risk-panel reveal">
      <p class="risk-panel__eyebrow">{risks_eyebrow}</p>
      <h2 class="risk-panel__title" id="titulo-riesgos">{risks_title}</h2>
      <p class="risk-panel__lead">{risks_lead}</p>

      {risk_ratio}
      {risk_chips}

      <a class="risk-panel__cta" href="{risks_href}">{risks_label} {arrow}</a>
    </div>
  </div>
</section>

<section class="section" id="el-nino" aria-labelledby="titulo-el-nino">
  <div class="wrap">
    <div class="closing-panel reveal">
      <p class="closing-panel__eyebrow">{closing_eyebrow}</p>
      <h2 class="closing-panel__title" id="titulo-el-nino">{closing_title}</h2>
      <p class="closing-panel__text">{closing_text}</p>
      <a class="closing-panel__cta" href="{closing_href}">{closing_label} {arrow}</a>
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
    risks_data = load("tema-07-riesgos")
    risk = risks_data["sections"][0]["risk_cards"]
    cards = "\n".join(obj_cover_html(t) for t in THEMES if t[6])
    page = HOME_TPL.format(
        title=esc(data["title"]), meta_desc=esc(data["meta_desc"]),
        font=FONT_LINKS, product=PRODUCT_TITLE,
        subtitle=rich(data["subtitle"]),
        stats_hero=stats_hero_html(data["stats_hero"]),
        stats_list=stats_list_html(data["stats_list"]),
        intro_eyebrow=esc(data["intro_nav"]["eyebrow"]),
        intro_title=esc(data["intro_nav"]["title"]),
        intro_lead=rich(data["intro_nav"]["lead"]),
        cards=cards,
        risks_eyebrow=esc(data["risks"]["eyebrow"]),
        risks_title=esc(data["risks"]["title"]),
        risks_lead=rich(data["risks"]["lead"]),
        risk_ratio=risk_ratio_html(risk),
        risk_chips=risk_chips_html(risk),
        risks_href=data["risks"]["cta_href"],
        risks_label=esc(data["risks"]["cta_label"]),
        closing_eyebrow=esc(data["closing"]["eyebrow"]),
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
