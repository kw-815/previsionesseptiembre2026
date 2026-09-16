#!/usr/bin/env python3
"""Genera <svg> inline a partir de content/charts/*.json — sin librerías de
charting, coherente con la filosofía "cero dependencias" del sitio.

Tipos soportados:
  - line              : trayectoria multi-serie (líneas + puntos)
  - bars              : barras verticales agrupadas por categoría
  - hbars             : ranking horizontal, una serie (admite signo y una
                         segunda cifra de referencia por fila, p.ej. 2027)
  - diverging-hbars    : barras horizontales agrupadas a ambos lados de 0
                         (para comparar escenarios, p.ej. El Niño moderado/fuerte)

Cada gráfico se envuelve en un <figure class="chart-card"> con título, nota
y fuente. El trazo de las líneas usa stroke-dasharray/-dashoffset calculado
aquí mismo (largo real del polyline) para que js/main.js sólo tenga que
quitar el offset cuando la card entra en viewport — cero cálculo de layout
en el cliente.

Interactividad real (no solo :hover de CSS): cada gráfico lleva
  1) un <script type="application/json" class="chart-data"> con todas las
     series y categorías, y
  2) en el <svg>, atributos data-orient/data-x0/data-step/... que describen
     su geometría (dónde cae cada categoría en coordenadas SVG),
de modo que js/main.js pueda, al mover el mouse, ubicar la categoría más
cercana y mostrar un tooltip con el valor de TODAS las series en ese punto
(p.ej. crédito Y captaciones del mismo año, o 2026 Y 2027 de una industria)
— no solo el valor de la marca puntual bajo el cursor. Un <rect
class="chart-hitzone"> transparente cubre toda el área de trazado para que
el hover funcione en cualquier punto, no solo sobre el trazo/barra exacta.
"""
import html
import json
import math

W, H = 640, 300
PAD_L, PAD_R, PAD_T, PAD_B = 8, 8, 20, 28


def esc(s):
    return html.escape(str(s), quote=True)


def _fmt(v):
    if abs(v - round(v)) < 0.001:
        return f"{round(v):,}".replace(",", ".")
    return f"{v:,.1f}".replace(",", "§").replace(".", ",").replace("§", ".")


def _title(label, v, unit=""):
    return f'<title>{esc(label)}: {_fmt(v)}{esc(unit)}</title>'


def _poly_len(pts):
    length = 0.0
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        length += math.hypot(x1 - x0, y1 - y0)
    return length


def _data_script(chart):
    """Bloque JSON que consume js/main.js para armar el tooltip enriquecido
    (todas las series de la categoría bajo el cursor, no solo una)."""
    payload = {
        "categories": chart["categories"],
        "series": [{"name": s["name"], "accent": s.get("accent", "orange"), "values": s["values"]} for s in chart["series"]],
        "unit": chart.get("unit", ""),
    }
    if chart.get("series2"):
        s2 = chart["series2"]
        payload["series2"] = {"name": s2.get("shortLabel", s2.get("name", "")), "values": s2["values"]}
    return f'<script type="application/json" class="chart-data">{json.dumps(payload, ensure_ascii=False)}</script>'


def _hitzone(x, y, w, h):
    return f'<rect class="chart-hitzone" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="transparent"/>'


def _wrap_figure(inner, chart, extra_class=""):
    title = esc(chart.get("title", ""))
    unit = esc(chart.get("unit", ""))
    note = chart.get("note", "")
    source = chart.get("source", "Fuente: Banco Central del Ecuador, Programación Macroeconómica 2026-2030, septiembre 2026.")
    note_html = f'<figcaption class="chart-card__note">{esc(note)}</figcaption>' if note else ""
    unit_html = f'<span class="chart-card__unit">{unit}</span>' if unit else ""
    return f'''<figure class="chart-card reveal {extra_class}">
  <div class="chart-card__head">
    <p class="chart-card__title">{title}</p>
    {unit_html}
  </div>
  {inner}
  {_data_script(chart)}
  {note_html}
  <p class="chart-card__source">{esc(source)}</p>
</figure>'''


def chart_line(chart):
    categories = chart["categories"]
    series = chart["series"]
    unit = chart.get("unit", "")
    n = len(categories)
    all_vals = [v for s in series for v in s["values"]]
    vmin, vmax = min(0, min(all_vals)), max(all_vals)
    if vmax == vmin:
        vmax = vmin + 1
    pad = (vmax - vmin) * 0.18
    vmin -= pad
    vmax += pad

    x0, x1 = PAD_L + 4, W - PAD_R - 4
    y0, y1 = H - PAD_B, PAD_T
    step = (x1 - x0) / (n - 1) if n > 1 else 0

    def xy(i, v):
        x = x0 + step * i
        y = y0 - (v - vmin) / (vmax - vmin) * (y0 - y1)
        return x, y

    zero_y = y0 - (0 - vmin) / (vmax - vmin) * (y0 - y1)
    parts = [f'<line class="chart-grid0" x1="{x0}" y1="{zero_y:.1f}" x2="{x1}" y2="{zero_y:.1f}"/>']

    labels_x = [f'<text class="chart-axis" x="{x0 + step * i:.1f}" y="{H - 8}" text-anchor="middle">{esc(c)}</text>'
                for i, c in enumerate(categories)]

    for si, s in enumerate(series):
        pts = [xy(i, v) for i, v in enumerate(s["values"])]
        length = _poly_len(pts)
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        accent = s.get("accent", "orange")
        parts.append(
            f'<polyline class="chart-line chart-draw" data-len="{length:.1f}" '
            f'style="stroke:var(--{accent});stroke-dasharray:{length:.1f};stroke-dashoffset:{length:.1f}" '
            f'points="{pts_str}"/>'
        )
        for i, (x, y) in enumerate(pts):
            r = 4.5 if i in (0, n - 1) else 3
            label = f'{s["name"]} · {categories[i]}'
            parts.append(
                f'<circle class="chart-dot" data-idx="{i}" style="fill:var(--{accent})" cx="{x:.1f}" cy="{y:.1f}" r="{r}">'
                f'{_title(label, s["values"][i], unit)}</circle>'
            )
        lx, ly = pts[-1]
        label_dy = -10 if s["values"][-1] >= s["values"][-2 if n > 1 else -1] else 16
        parts.append(
            f'<text class="chart-label" style="fill:var(--{accent})" x="{lx:.1f}" y="{ly + label_dy:.1f}" '
            f'text-anchor="end">{esc(s["name"])} {_fmt(s["values"][-1])}{esc(unit)}</text>'
        )

    parts.append(_hitzone(x0, y1 - 6, x1 - x0, y0 - y1 + 6))

    svg = (
        f'<svg class="chart chart--line" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{esc(chart.get("title",""))}" '
        f'data-orient="x" data-x0="{x0}" data-step="{step:.2f}" data-n="{n}" '
        f'data-plot-top="{y1}" data-plot-bottom="{y0}">'
        + "".join(parts) + "".join(labels_x) +
        '</svg>'
    )
    return _wrap_figure(svg, chart)


def chart_bars(chart, stacked=False):
    categories = chart["categories"]
    series = chart["series"]
    unit = chart.get("unit", "")
    n = len(categories)
    if stacked:
        totals = [sum(s["values"][i] for s in series) for i in range(n)]
        vmax = max(totals) if totals else 1
        vmin = min(0, min(totals))
    else:
        all_vals = [v for s in series for v in s["values"]]
        vmax = max(all_vals) if all_vals else 1
        vmin = min(0, min(all_vals)) if all_vals else 0
    if vmax == vmin:
        vmax = vmin + 1
    vmax *= 1.18

    x0, x1 = PAD_L + 4, W - PAD_R - 4
    y0, y1 = H - PAD_B, PAD_T
    group_w = (x1 - x0) / n
    n_series = len(series)
    bar_gap = group_w * 0.14
    bar_w = (group_w - bar_gap * 2) / (1 if stacked else n_series)

    def yv(v):
        return y0 - (v - vmin) / (vmax - vmin) * (y0 - y1)

    parts = [f'<line class="chart-grid0" x1="{x0}" y1="{y0:.1f}" x2="{x1}" y2="{y0:.1f}"/>']
    labels_x = []
    for i, c in enumerate(categories):
        gx = x0 + group_w * i
        labels_x.append(f'<text class="chart-axis" x="{gx + group_w/2:.1f}" y="{H - 8}" text-anchor="middle">{esc(c)}</text>')
        if stacked:
            cum = 0
            bx = gx + bar_gap
            for s in series:
                v = s["values"][i]
                accent = s.get("accent", "orange")
                by0, by1 = yv(cum), yv(cum + v)
                h = max(0, by0 - by1)
                parts.append(
                    f'<rect class="chart-bar chart-draw-v" data-idx="{i}" style="fill:var(--{accent})" '
                    f'x="{bx:.1f}" y="{by1:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
                    f'data-final-h="{h:.1f}" data-final-y="{by1:.1f}">{_title(s["name"] + " · " + str(c), v, unit)}</rect>'
                )
                cum += v
            total_y = yv(cum)
            parts.append(f'<text class="chart-val" x="{bx + bar_w/2:.1f}" y="{total_y - 6:.1f}" text-anchor="middle">{_fmt(cum)}</text>')
        else:
            for si, s in enumerate(series):
                v = s["values"][i]
                accent = s.get("accent", "orange")
                bx = gx + bar_gap + bar_w * si
                if v >= 0:
                    top = yv(v)
                    h = max(0.5, yv(0) - yv(v))
                else:
                    top = yv(0)
                    h = max(0.5, yv(v) - yv(0))
                parts.append(
                    f'<rect class="chart-bar chart-draw-v" data-idx="{i}" style="fill:var(--{accent})" '
                    f'x="{bx:.1f}" y="{top:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
                    f'data-final-h="{h:.1f}" data-final-y="{top:.1f}">{_title(str(c), v, unit)}</rect>'
                )
                lbl_y = top - 6 if v >= 0 else top + h + 12
                parts.append(f'<text class="chart-val" x="{bx + bar_w/2:.1f}" y="{lbl_y:.1f}" text-anchor="middle">{_fmt(v)}</text>')

    legend = ""
    if n_series > 1:
        items = []
        for s in series:
            accent = s.get("accent", "orange")
            items.append(
                f'<span class="chart-legend__item"><i style="background:var(--{accent})"></i>{esc(s["name"])}</span>'
            )
        legend = f'<div class="chart-legend">{"".join(items)}</div>'

    parts.append(_hitzone(x0, y1 - 6, x1 - x0, y0 - y1 + 6))

    svg = (
        f'<svg class="chart chart--bars" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{esc(chart.get("title",""))}" '
        f'data-orient="x" data-x0="{x0}" data-step="{group_w:.2f}" data-n="{n}" '
        f'data-plot-top="{y1}" data-plot-bottom="{y0}">'
        + "".join(parts) + "".join(labels_x) +
        '</svg>'
    )
    return _wrap_figure(legend + svg, chart)


def chart_hbars(chart):
    """Ranking horizontal de una serie. Admite valores con signo (barra
    sale de una línea de cero, no siempre del borde izquierdo) y, si el
    chart trae `series2`, agrega una cifra secundaria más tenue junto al
    valor principal (p.ej. crecimiento 2026 grande + 2027 secundario)."""
    categories = chart["categories"]
    series = chart["series"][0]
    values = series["values"]
    unit = chart.get("unit", "")
    series2 = chart.get("series2")
    accent = series.get("accent", "orange")
    n = len(categories)
    row_h = 30
    height = PAD_T + n * row_h + 10

    vmin = min(0, min(values))
    vmax = max(values + [0])
    span = max(vmax - vmin, 0.001)

    x_label_w = 172
    x0 = x_label_w
    x1 = W - 96
    zero_x = x0 + (0 - vmin) / span * (x1 - x0)

    parts = [f'<line class="chart-grid0" x1="{zero_x:.1f}" y1="{PAD_T - 4}" x2="{zero_x:.1f}" y2="{PAD_T + n*row_h}"/>']
    for i, (c, v) in enumerate(zip(categories, values)):
        y = PAD_T + i * row_h
        bw = abs(v) / span * (x1 - x0)
        bx = zero_x - bw if v < 0 else zero_x
        highlight = " chart-hbar--on" if chart.get("highlight") == c else ""
        parts.append(f'<text class="chart-axis chart-axis--row" x="{x0 - 12}" y="{y + row_h*0.64:.1f}" text-anchor="end">{esc(c)}</text>')
        parts.append(
            f'<rect class="chart-bar chart-draw-h{highlight}" data-idx="{i}" style="fill:var(--{accent})" '
            f'x="{bx:.1f}" y="{y + 5}" width="{max(bw,1.2):.1f}" height="{row_h - 11}" '
            f'data-final-w="{bw:.1f}" data-dir="{"l" if v < 0 else "r"}">{_title(c, v, unit)}</rect>'
        )
        # El valor de una barra negativa se ancla junto a la línea de cero
        # (lado derecho, siempre libre), no en la punta de la barra: con
        # valores muy negativos la barra puede llegar hasta el borde de la
        # columna de nombres, y anclar el texto ahí lo haría chocar con esa
        # etiqueta. Las barras positivas sí usan su propia punta, porque a
        # la derecha de la punta siempre hay margen libre hasta x1.
        val_x = bx + bw + 8 if v >= 0 else zero_x + 8
        val_anchor = "start"
        sign = "+" if v > 0 else ""
        val_text = f'{sign}{_fmt(v)}'
        if series2 and i < len(series2.get("values", [])):
            v2 = series2["values"][i]
            sign2 = "+" if v2 > 0 else ""
            val_text += f'<tspan class="chart-val__sub"> · {esc(series2.get("shortLabel", series2.get("name","")))} {sign2}{_fmt(v2)}</tspan>'
        parts.append(f'<text class="chart-val" x="{val_x:.1f}" y="{y + row_h*0.64:.1f}" text-anchor="{val_anchor}">{val_text}</text>')

    parts.append(_hitzone(0, PAD_T, W, n * row_h))

    svg = (
        f'<svg class="chart chart--hbars" viewBox="0 0 {W} {height}" role="img" '
        f'aria-label="{esc(chart.get("title",""))}" '
        f'data-orient="y" data-y0="{PAD_T}" data-step="{row_h}" data-n="{n}" '
        f'data-plot-left="0" data-plot-right="{W}">'
        + "".join(parts) +
        '</svg>'
    )
    return _wrap_figure(svg, chart)


def chart_diverging(chart):
    categories = chart["categories"]
    series = chart["series"]
    unit = chart.get("unit", "")
    n = len(categories)
    n_series = len(series)
    row_h = 46
    height = PAD_T + n * row_h + 26
    all_vals = [v for s in series for v in s["values"]]
    vmax = max(abs(min(all_vals)), abs(max(all_vals)), 0.5) * 1.25

    x_mid = W / 2 + 30
    x_left = 96
    x_right = W - 20
    half = min(x_mid - x_left, x_right - x_mid)
    bar_h = (row_h - 16) / n_series

    parts = [f'<line class="chart-grid0" x1="{x_mid}" y1="{PAD_T - 6}" x2="{x_mid}" y2="{PAD_T + n*row_h}"/>']
    for i, c in enumerate(categories):
        y = PAD_T + i * row_h
        parts.append(f'<text class="chart-axis chart-axis--row" x="{x_left - 10}" y="{y + row_h/2 + 4:.1f}" text-anchor="end">{esc(c)}</text>')
        for si, s in enumerate(series):
            v = s["values"][i]
            accent = s.get("accent", "orange")
            bw = abs(v) / vmax * half
            by = y + 8 + si * bar_h
            bx = x_mid - bw if v < 0 else x_mid
            parts.append(
                f'<rect class="chart-bar chart-draw-h" data-idx="{i}" style="fill:var(--{accent})" '
                f'x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bar_h - 4:.1f}" '
                f'data-final-w="{bw:.1f}" data-dir="{"l" if v < 0 else "r"}" data-mid="{x_mid}">'
                f'{_title(s["name"] + " · " + str(c), v, unit)}</rect>'
            )
            lx = bx - 6 if v < 0 else bx + bw + 6
            anchor = "end" if v < 0 else "start"
            sign = "+" if v > 0 else ""
            parts.append(f'<text class="chart-val" x="{lx:.1f}" y="{by + bar_h/2 + 3:.1f}" text-anchor="{anchor}">{sign}{_fmt(v)}</text>')

    legend = ""
    if n_series > 1:
        items = [f'<span class="chart-legend__item"><i style="background:var(--{s.get("accent","orange")})"></i>{esc(s["name"])}</span>' for s in series]
        legend = f'<div class="chart-legend">{"".join(items)}</div>'

    parts.append(_hitzone(x_left, PAD_T, x_right - x_left, n * row_h))

    svg = (
        f'<svg class="chart chart--diverging" viewBox="0 0 {W} {height}" role="img" '
        f'aria-label="{esc(chart.get("title",""))}" '
        f'data-orient="y" data-y0="{PAD_T}" data-step="{row_h}" data-n="{n}" '
        f'data-plot-left="{x_left}" data-plot-right="{x_right}">'
        + "".join(parts) +
        '</svg>'
    )
    return _wrap_figure(legend + svg, chart)


def render_chart(chart):
    kind = chart.get("kind")
    if kind == "line":
        return chart_line(chart)
    if kind == "bars":
        return chart_bars(chart, stacked=False)
    if kind == "stacked-bars":
        return chart_bars(chart, stacked=True)
    if kind == "hbars":
        return chart_hbars(chart)
    if kind == "diverging-hbars":
        return chart_diverging(chart)
    raise ValueError(f"Tipo de gráfico desconocido: {kind}")
