/* Previsiones Económicas 2026-2030 — Keyword
 * Vanilla JS, sin dependencias. Responsabilidades:
 *   1) scroll-reveal (.reveal -> .in-view) vía IntersectionObserver
 *   2) contador animado en cifras hero ([data-count-to])
 *   3) el trazo de líneas/barras de los charts vive en CSS y se dispara
 *      con la misma clase .in-view (ver styles.css)
 *   4) tooltip interactivo de los gráficos: al mover el mouse sobre el
 *      área de trazado, ubica la categoría más cercana (año, industria...)
 *      y muestra el valor de TODAS las series en ese punto — no solo la
 *      marca puntual bajo el cursor. Esto corre siempre, incluso con
 *      prefers-reduced-motion, porque es información, no animación.
 */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------------------------------------------------------------
  // 1-2) Scroll-reveal + contadores
  // ---------------------------------------------------------------
  function formatCount(value, decimals) {
    return value.toLocaleString("es-EC", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }

  function runCounter(el) {
    var to = parseFloat(el.getAttribute("data-count-to"));
    var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
    if (isNaN(to)) return;
    if (reduced) {
      el.textContent = formatCount(to, decimals);
      return;
    }
    var duration = 1100;
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min(1, (ts - start) / duration);
      var eased = 1 - Math.pow(1 - p, 3); // ease-out-cubic
      el.textContent = formatCount(to * eased, decimals);
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = formatCount(to, decimals);
    }
    requestAnimationFrame(step);
  }

  // Los charts fijan su estado inicial (barras en scaleX/Y(0), líneas con
  // stroke-dashoffset) por atributo `style` inline (tools/charts.py), así
  // que una regla de CSS por clase nunca puede ganarle esa pelea de
  // especificidad — se revierte aquí mismo, también inline, para que
  // siempre gane el último que escribe.
  function revealCharts(root) {
    root.querySelectorAll(".chart-bar").forEach(function (el) { el.style.transform = "none"; });
    root.querySelectorAll(".chart-line.chart-draw").forEach(function (el) { el.style.strokeDashoffset = "0"; });
  }

  var revealTargets = document.querySelectorAll(".reveal");
  var counterTargets = document.querySelectorAll("[data-count-to]");

  if (reduced || !("IntersectionObserver" in window)) {
    revealTargets.forEach(function (el) {
      el.classList.add("in-view");
      revealCharts(el);
    });
    counterTargets.forEach(runCounter);
  } else {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("in-view");
          revealCharts(entry.target);
          if (entry.target.hasAttribute("data-count-to")) runCounter(entry.target);
          entry.target.querySelectorAll("[data-count-to]").forEach(runCounter);
          io.unobserve(entry.target);
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
    );
    revealTargets.forEach(function (el) { io.observe(el); });
    // Contadores que no están dentro de un .reveal (poco probable, pero
    // por si acaso) se observan aparte para no quedar sin animar nunca.
    counterTargets.forEach(function (el) {
      if (!el.closest(".reveal")) io.observe(el);
    });
  }

  // ---------------------------------------------------------------
  // 4) Tooltip interactivo de gráficos
  // ---------------------------------------------------------------
  var SVG_NS = "http://www.w3.org/2000/svg";

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function formatVal(v) {
    var decimals = Math.abs(v - Math.round(v)) < 0.001 ? 0 : 1;
    return v.toLocaleString("es-EC", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  }

  function unitSuffix(unit) {
    if (!unit) return "";
    return unit === "%" ? unit : " " + unit;
  }

  function initChartInteractivity() {
    var cards = document.querySelectorAll(".chart-card");
    if (!cards.length) return;

    var tooltip = document.createElement("div");
    tooltip.className = "chart-tooltip";
    tooltip.setAttribute("aria-hidden", "true");
    document.body.appendChild(tooltip);

    cards.forEach(function (card) {
      var svg = card.querySelector("svg.chart");
      var dataScript = card.querySelector("script.chart-data");
      if (!svg || !dataScript) return;

      var data;
      try {
        data = JSON.parse(dataScript.textContent);
      } catch (e) {
        return;
      }

      var hitzone = svg.querySelector(".chart-hitzone");
      if (!hitzone) return;
      hitzone.style.pointerEvents = "all";

      var orient = svg.getAttribute("data-orient");
      var n = parseInt(svg.getAttribute("data-n"), 10) || data.categories.length;
      var crosshair = null;
      var rowHighlight = null;

      function svgPoint(evt) {
        var ctm = svg.getScreenCTM();
        if (!ctm) return null;
        var pt = svg.createSVGPoint();
        pt.x = evt.clientX;
        pt.y = evt.clientY;
        return pt.matrixTransform(ctm.inverse());
      }

      function indexFromPoint(p) {
        var idx;
        if (orient === "x") {
          var x0 = parseFloat(svg.getAttribute("data-x0"));
          var stepX = parseFloat(svg.getAttribute("data-step"));
          idx = stepX ? Math.round((p.x - x0) / stepX) : 0;
        } else {
          var y0 = parseFloat(svg.getAttribute("data-y0"));
          var stepY = parseFloat(svg.getAttribute("data-step"));
          idx = stepY ? Math.floor((p.y - y0) / stepY) : 0;
        }
        return Math.max(0, Math.min(n - 1, idx));
      }

      function ensureXHelpers() {
        if (orient !== "x" || crosshair) return;
        crosshair = document.createElementNS(SVG_NS, "line");
        crosshair.setAttribute("class", "chart-crosshair");
        crosshair.setAttribute("y1", svg.getAttribute("data-plot-top"));
        crosshair.setAttribute("y2", svg.getAttribute("data-plot-bottom"));
        svg.appendChild(crosshair);
      }

      function ensureRowHighlight() {
        if (orient !== "y" || rowHighlight) return;
        var rowH = parseFloat(svg.getAttribute("data-step"));
        var left = parseFloat(svg.getAttribute("data-plot-left"));
        var right = parseFloat(svg.getAttribute("data-plot-right"));
        rowHighlight = document.createElementNS(SVG_NS, "rect");
        rowHighlight.setAttribute("class", "chart-row-highlight");
        rowHighlight.setAttribute("x", left);
        rowHighlight.setAttribute("width", right - left);
        rowHighlight.setAttribute("height", rowH);
        svg.insertBefore(rowHighlight, svg.firstChild);
      }

      function clearActive() {
        svg.querySelectorAll(".chart-mark--active").forEach(function (el) {
          el.classList.remove("chart-mark--active");
        });
      }

      function buildTooltipHtml(idx) {
        var cat = data.categories[idx];
        var html = '<div class="chart-tooltip__cat">' + escapeHtml(cat) + "</div>";
        data.series.forEach(function (s) {
          html +=
            '<div class="chart-tooltip__row"><span class="chart-tooltip__swatch" style="background:var(--' +
            s.accent +
            ')"></span><span class="chart-tooltip__name">' +
            escapeHtml(s.name) +
            '</span><span class="chart-tooltip__val">' +
            formatVal(s.values[idx]) +
            unitSuffix(data.unit) +
            "</span></div>";
        });
        if (data.series2) {
          html +=
            '<div class="chart-tooltip__row"><span class="chart-tooltip__swatch" style="background:var(--t-40)"></span><span class="chart-tooltip__name">' +
            escapeHtml(data.series2.name) +
            '</span><span class="chart-tooltip__val">' +
            formatVal(data.series2.values[idx]) +
            unitSuffix(data.unit) +
            "</span></div>";
        }
        return html;
      }

      function positionTooltip(evt) {
        var pad = 16;
        var tw = tooltip.offsetWidth;
        var th = tooltip.offsetHeight;
        var left = evt.clientX + pad;
        var top = evt.clientY + pad;
        if (left + tw > window.innerWidth - 8) left = evt.clientX - tw - pad;
        if (top + th > window.innerHeight - 8) top = evt.clientY - th - pad;
        tooltip.style.left = Math.max(8, left) + "px";
        tooltip.style.top = Math.max(8, top) + "px";
      }

      function onMove(evt) {
        var p = svgPoint(evt);
        if (!p) return;
        var idx = indexFromPoint(p);

        clearActive();
        svg.querySelectorAll('[data-idx="' + idx + '"]').forEach(function (el) {
          el.classList.add("chart-mark--active");
        });

        if (orient === "x") {
          ensureXHelpers();
          var x0 = parseFloat(svg.getAttribute("data-x0"));
          var stepX = parseFloat(svg.getAttribute("data-step"));
          var x = x0 + stepX * idx;
          crosshair.setAttribute("x1", x);
          crosshair.setAttribute("x2", x);
          crosshair.style.display = "";
        } else {
          ensureRowHighlight();
          var rowH = parseFloat(svg.getAttribute("data-step"));
          var y0 = parseFloat(svg.getAttribute("data-y0"));
          rowHighlight.setAttribute("y", y0 + rowH * idx);
          rowHighlight.style.display = "";
        }

        tooltip.innerHTML = buildTooltipHtml(idx);
        tooltip.classList.add("is-visible");
        positionTooltip(evt);
      }

      function onLeave() {
        clearActive();
        if (crosshair) crosshair.style.display = "none";
        if (rowHighlight) rowHighlight.style.display = "none";
        tooltip.classList.remove("is-visible");
      }

      hitzone.addEventListener("pointermove", onMove);
      hitzone.addEventListener("pointerleave", onLeave);
    });
  }

  initChartInteractivity();

  // ---------------------------------------------------------------
  // 5) Paneles laterales de detalle ("Ver más")
  // El abrir/cerrar en sí es CSS puro (:target, ver .detail-drawer en
  // styles.css) — funciona incluso sin JS. Esto solo suma cierre con
  // Escape y devuelve el foco al botón que abrió el panel, para que la
  // experiencia con teclado/lector de pantalla sea completa.
  // ---------------------------------------------------------------
  function initDrawers() {
    var triggers = document.querySelectorAll("[data-drawer-open]");
    if (!triggers.length) return;
    var lastTrigger = null;

    triggers.forEach(function (t) {
      t.addEventListener("click", function () { lastTrigger = t; });
    });

    function openDrawer() {
      var m = /^#drawer-(.+)/.exec(window.location.hash);
      return m ? document.getElementById("drawer-" + m[1]) : null;
    }

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      var d = openDrawer();
      if (!d) return;
      window.location.hash = "_";
    });

    window.addEventListener("hashchange", function () {
      var d = openDrawer();
      if (d) {
        d.focus();
      } else if (lastTrigger) {
        lastTrigger.focus();
      }
    });
  }

  initDrawers();
})();
