/*
 * File: module.js
 * Module: Stats / Numbers
 * Description: Count-up animation triggered when the stats section scrolls into view.
 *              Uses IntersectionObserver for performance. Respects prefers-reduced-motion.
 *              Scoped to the module instance via id="/* [hubl-value] */".
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  'use strict';

  // ─── Locate this module instance ───────────────────────────────
  var root = (document.currentScript && document.currentScript.closest('section[id]'))
    || document.querySelector('.module-stats-numbers');

  if (!root) return;

  // ─── Respect prefers-reduced-motion ────────────────────────────
  var prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ─── Collect all count-up targets in this instance ─────────────
  var targets = root.querySelectorAll('[data-countup="true"]');
  if (!targets.length) return;

  // ─── Easing: easeOutQuart ──────────────────────────────────────
  function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
  }

  // ─── Animate a single number element ───────────────────────────
  function animateCount(el) {
    var target   = parseFloat(el.dataset.target) || 0;
    var duration = parseInt(el.dataset.duration, 10) || 1800;
    var prefix   = el.dataset.prefix || '';
    var suffix   = el.dataset.suffix || '';
    var countEl  = el.querySelector('.module-stats-numbers__count');

    if (!countEl) return;

    // If motion is reduced, just set the final value immediately
    if (prefersReduced) {
      countEl.textContent = formatNumber(target);
      return;
    }

    var startTime = null;
    var isDecimal = target % 1 !== 0;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var elapsed  = timestamp - startTime;
      var progress = Math.min(elapsed / duration, 1);
      var eased    = easeOutQuart(progress);
      var current  = target * eased;

      countEl.textContent = isDecimal
        ? current.toFixed(1)
        : Math.round(current).toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        // Ensure we land exactly on the target
        countEl.textContent = isDecimal
          ? target.toFixed(1)
          : formatNumber(target);
      }
    }

    requestAnimationFrame(step);
  }

  // ─── Format final number with locale commas ─────────────────────
  function formatNumber(n) {
    return n % 1 !== 0
      ? n.toFixed(1)
      : Math.round(n).toLocaleString();
  }

  // ─── Set initial display value before animation ─────────────────
  targets.forEach(function (el) {
    var countEl = el.querySelector('.module-stats-numbers__count');
    if (countEl) countEl.textContent = '0';
  });

  // ─── IntersectionObserver — trigger once when 20% visible ───────
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    targets.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback: no IntersectionObserver (legacy) — just set values
    targets.forEach(function (el) {
      var countEl = el.querySelector('.module-stats-numbers__count');
      var target  = parseFloat(el.dataset.target) || 0;
      if (countEl) countEl.textContent = formatNumber(target);
    });
  }

})();