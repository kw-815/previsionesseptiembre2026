/* Previsiones Económicas 2026-2030 — Keyword
 * Vanilla JS, sin dependencias. Tres responsabilidades:
 *   1) scroll-reveal (.reveal -> .in-view) vía IntersectionObserver
 *   2) contador animado en cifras hero ([data-count-to])
 *   3) el trazo de líneas/barras de los charts ya vive en CSS y se
 *      dispara con la misma clase .in-view (ver styles.css)
 * Todo respeta prefers-reduced-motion: si el usuario lo pide, se
 * muestra el estado final de una vez, sin animar nada.
 */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
    return;
  }

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
})();
