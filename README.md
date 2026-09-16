# Previsiones Económicas 2026-2030 · Septiembre 2026

Lectura empresarial de Keyword sobre la Programación Macroeconómica 2026-2030
del Banco Central del Ecuador (septiembre de 2026): crecimiento, riesgos y el
primer impacto cuantificado del Fenómeno de El Niño.

## Estructura

```
sitio/
├── index.html                 # Home (cifras clave + muro de temas + El Niño + balance de riesgos como cierre)
├── 404.html
├── css/styles.css             # Base heredada de ace2040/ley-transporte-impacto + adiciones propias
├── js/main.js                 # Scroll-reveal, contadores animados, tooltips interactivos de charts
├── img/
│   ├── logo-keyword-white.svg
│   ├── hero-guayaquil.webp    # Hero del home
│   ├── hero-puerto.webp       # Banner de "Por industria" + su tarjeta en el home
│   └── card-*.webp            # Tarjetas de tema restantes en el muro del home
│                               # (ver créditos en "Fotografía" más abajo)
├── content/
│   ├── home.json
│   ├── riesgos.json            # Balance de riesgos — contenido del cierre del home (no es un tema aparte)
│   ├── tema-01-panorama.json … tema-07-el-nino.json
│   └── charts/*.json          # Series de datos de cada gráfico
├── pages/                     # Generado por tools/build.py
│   └── tema-01-panorama.html … tema-07-el-nino.html
└── tools/
    ├── build.py                # Generador de index.html y pages/*.html
    └── charts.py                # Genera cada <svg> inline desde content/charts/*.json
```

## Regenerar el sitio

```
cd sitio
python3 tools/build.py
```

Salida: `index.html` + 7 páginas en `pages/`.

## Contenido

- **7 temas:** Panorama y cifras clave · El pulso de la economía ecuatoriana ·
  Los motores del crecimiento 2026-2030 · El crecimiento por industria
  (ranking de 20 industrias) · Petróleo, sector externo y reservas · Fiscal,
  crédito e inflación · Fenómeno de El Niño.
- **Balance de riesgos** no es un tema aparte: vive como la sección de
  cierre del home (barra de proporción + tarjetas completas por factor),
  justo antes del pie de página.
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

Todas las fotos son de Unsplash (licencia Unsplash — uso comercial libre, sin
atribución obligatoria, atribución dada de todas formas por buena práctica).
Las tarjetas del muro de temas llevan un velo de color de marca (`mix-blend-mode:
multiply` con el acento `--obj-N` de cada tema) sobre la foto — ver
`.obj-cover__photo` en `css/styles.css`.

- Hero del home (`hero-guayaquil.webp`): Andres Medina, ["Vista aérea de los
  edificios de la ciudad durante la puesta del
  sol"](https://unsplash.com/photos/49_PpVFXbGg) (Guayaquil).
- Banner + tarjeta de "Por industria" (`hero-puerto.webp`): Andrés López
  Maldonado, puerto de exportación en Guayaquil
  (https://unsplash.com/photos/HesD2oWQD-c).
- Tarjeta de "Panorama" (`card-panorama.webp`): Andres Medina, centro
  histórico de Quito (https://unsplash.com/photos/l0TziH9PJiM).
- Tarjeta de "Pulso doméstico" (`card-pulso.webp`): Jonathan Monck-Mason,
  mercado local (https://unsplash.com/photos/jb6CdUUAR4g).
- Tarjeta de "Motores del crecimiento" (`card-motores.webp`): Tomas, grúa de
  construcción (https://unsplash.com/photos/Mcn1Ky7jzZU).
- Tarjeta de "Sector externo" (`card-externo.webp`): Josep M Bové, complejo
  industrial/refinería (https://unsplash.com/photos/ArdlHSiX44s).
- Tarjeta de "Fiscal y monetario" (`card-fiscal.webp`): Giorgio Trovato,
  billetes de dólar (https://unsplash.com/photos/WyxqQpyFNk8).
- Tarjeta de "El Niño" (`card-el-nino.webp`): Daniel Lerman, tormenta sobre
  el mar (https://unsplash.com/photos/GBkssTODNT0).

## Publicación

GitHub Pages sirve el sitio desde la raíz de la rama `main`.
