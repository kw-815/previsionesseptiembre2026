# Previsiones Económicas 2026-2030 · Septiembre 2026

Lectura empresarial de Keyword sobre la Programación Macroeconómica 2026-2030
del Banco Central del Ecuador (septiembre de 2026): crecimiento, riesgos y el
primer impacto cuantificado del Fenómeno de El Niño.

## Estructura

```
sitio/
├── index.html                 # Home (cifras clave + muro de temas + balance de riesgos + cierre)
├── 404.html
├── css/styles.css             # Base heredada de ace2040/ley-transporte-impacto + adiciones propias
├── js/main.js                 # Scroll-reveal, contadores animados, tooltips interactivos de charts
├── img/
│   ├── logo-keyword-white.svg
│   ├── hero-guayaquil.webp    # Foto: Andres Medina / Unsplash (licencia Unsplash, uso libre)
│   └── hero-puerto.webp       # Foto: Andrés López Maldonado / Unsplash (licencia Unsplash, uso libre)
├── content/
│   ├── home.json
│   ├── tema-01-panorama.json … tema-08-el-nino.json
│   └── charts/*.json          # Series de datos de cada gráfico
├── pages/                     # Generado por tools/build.py
│   └── tema-01-panorama.html … tema-08-el-nino.html
└── tools/
    ├── build.py                # Generador de index.html y pages/*.html
    └── charts.py                # Genera cada <svg> inline desde content/charts/*.json
```

## Regenerar el sitio

```
cd sitio
python3 tools/build.py
```

Salida: `index.html` + 8 páginas en `pages/`.

## Contenido

- **8 temas:** Panorama y cifras clave · El pulso de la economía ecuatoriana ·
  Los motores del crecimiento 2026-2030 · Cómo crecerá tu sector (ranking de
  20 industrias) · Petróleo, sector externo y reservas · Fiscal, crédito e
  inflación · Balance de riesgos · Fenómeno de El Niño.
- **Balance de riesgos** vive como sección propia del home (barra de
  proporción + chips), no como una tarjeta más del muro de temas.
- **7 gráficos** en SVG inline (sin librería de charting), generados en
  build-time desde `content/charts/*.json`. Cada uno lleva tooltip
  interactivo: al pasar el cursor por el área de trazado, muestra el valor
  de todas las series de esa categoría (js/main.js).
- Tono informativo: el sitio no incluye lecturas valorativas tipo "qué
  implica para tu empresa" — solo lo que dice el Banco Central.

Todas las cifras citadas provienen de la Programación Macroeconómica
2026-2030 del Banco Central del Ecuador (septiembre de 2026). Los datos por
industria (`tema-04-industrias`) vienen del Excel de referencia del BCE
(`REFERENCIAS/PrevEcon.xlsx`, fuera de este repo).

## Fotografía

Ambas fotos son de Unsplash (licencia Unsplash — uso comercial libre, sin
atribución obligatoria, atribución dada de todas formas por buena práctica):

- Hero del home: Andres Medina, ["Vista aérea de los edificios de la ciudad
  durante la puesta del sol"](https://unsplash.com/photos/49_PpVFXbGg)
  (Guayaquil).
- Banner de "Cómo crecerá tu sector": Andrés López Maldonado, puerto de
  exportación en Guayaquil (https://unsplash.com/photos/HesD2oWQD-c).

## Publicación

GitHub Pages sirve el sitio desde la raíz de la rama `main`.
