/*
 * File: theme.js
 * Description: Theme-level JavaScript entry point. Handles global UI behaviors
 *              that are not owned by any individual module: scroll-to-top button
 *              visibility and smooth scroll, and JS feature detection class.
 *              Module-specific behaviors (navigation, accordions, sliders, etc.)
 *              live in their respective module.js files.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 * Theme: Tonic — Khaotic Digital, LLC
 */

(function () {
  'use strict';

  // ── Scroll-to-top button ─────────────────────────────────────────────────
  // Shows after 400px of scroll. Smooth-scrolls to top on click.
  // Button is hardcoded in base.html; CSS handles the visibility transition.

  var SCROLL_THRESHOLD = 400;
  var btn = document.getElementById('scroll-top-btn');

  if (btn) {
    var ticking = false;

    function onScroll() {
      if (!ticking) {
        window.requestAnimationFrame(updateBtn);
        ticking = true;
      }
    }

    function updateBtn() {
      if (window.scrollY > SCROLL_THRESHOLD) {
        btn.classList.add('is-visible');
      } else {
        btn.classList.remove('is-visible');
      }
      ticking = false;
    }

    window.addEventListener('scroll', onScroll, { passive: true });

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Keyboard: Enter and Space both trigger scroll
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

})();