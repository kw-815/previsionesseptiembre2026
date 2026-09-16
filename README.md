# Previsiones Económicas 2026-2030 · Septiembre 2026

Lectura empresarial de Keyword sobre la Programación Macroeconómica 2026-2030
del Banco Central del Ecuador (septiembre de 2026): crecimiento, riesgos y el
primer impacto cuantificado del Fenómeno de El Niño.

## Estructura

```
sitio/
├── index.html                 # Home (cifras clave + muro de 9 temas + cierre)
├── 404.html
├── css/styles.css             # Base heredada de ace2040/ley-transporte-impacto + adiciones propias
├── js/main.js                 # Scroll-reveal, contadores animados, trazo de gráficos
├── img/logo-keyword-white.svg
├── content/
│   ├── home.json
│   ├── tema-01-panorama.json … tema-09-empresas.json
│   └── charts/*.json          # Series de datos de cada gráfico
├── pages/                     # Generado por tools/build.py
│   └── tema-01-panorama.html … tema-09-empresas.html
└── tools/
    ├── build.py                # Generador de index.html y pages/*.html
    └── charts.py                # Genera cada <svg> inline desde content/charts/*.json
```

## Regenerar el sitio

```
cd sitio
python3 tools/build.py
```

Salida: `index.html` + 9 páginas en `pages/`.

## Contenido

- **9 temas:** Panorama y cifras clave · Entorno internacional · El pulso de
  la economía ecuatoriana · Los motores del crecimiento 2026-2030 · Petróleo,
  sector externo y reservas · Fiscal, crédito e inflación · Balance de
  riesgos · Fenómeno de El Niño · Qué significa para tu empresa.
- **7 gráficos** en SVG inline (sin librería de charting), generados en
  build-time desde `content/charts/*.json`.
- Cada tema cierra con un bloque "Qué implica para tu empresa" — lectura
  propia de Keyword, no una cita del Banco Central.

Todas las cifras citadas provienen de la Programación Macroeconómica
2026-2030 del Banco Central del Ecuador (septiembre de 2026).

## Publicación

GitHub Pages sirve el sitio desde la raíz de la rama `main`.
