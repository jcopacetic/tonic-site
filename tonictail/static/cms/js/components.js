/**
 * File: components.js
 * Description: Module loader — imports all block-level JS for the Tonic theme.
 *              Load this file in base.html after theme.js.
 *              Each block's JS is self-contained and initializes on DOMContentLoaded.
 *
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 * Theme: Tonic — Khaotic Digital, LLC
 *
 * Usage in base.html:
 *   <script src="{% static 'cms/js/theme.js' %}" defer></script>
 *   <script src="{% static 'cms/js/components.js' %}" defer></script>
 *
 * Or load only the blocks you need per-page using individual script tags.
 */

/* Block JS files (only loaded if the block is present on the page):
 *
 * blocks/faq.js               — FAQ accordion
 * blocks/countdown-timer.js   — Countdown timer
 * blocks/image-gallery.js     — Image gallery + lightbox
 * blocks/slider.js            — Image/content carousel
 * blocks/tabs-panels.js       — Tabbed content
 * blocks/testimonials-slider.js — Testimonials carousel
 * blocks/stats.js             — Count-up animation
 * blocks/map-embed.js         — Google Maps
 * blocks/code-block.js        — Prism syntax highlighting
 * blocks/video-banner.js      — Background video
 * blocks/video-embed.js       — Video embed play button
 * blocks/testimonials-grid.js — Testimonials (no JS needed at runtime)
 * blocks/announcements.js     — Announcement bar
 * header.js                   — Sticky header, mobile nav
 * theme.js                    — Scroll-to-top, global utilities
 */

(function () {
  'use strict';

  /**
   * Conditionally load a block JS file only if the block's
   * root element exists on the current page.
   */
  function loadIfPresent(selector, src) {
    if (!document.querySelector(selector)) return;
    var s = document.createElement('script');
    s.src = src;
    s.defer = true;
    document.head.appendChild(s);
  }

  var base = document.currentScript
    ? document.currentScript.src.replace('components.js', 'blocks/')
    : '/static/cms/js/blocks/';

  loadIfPresent('.module-accordion-faq',          base + 'faq.js');
  loadIfPresent('.module-countdown-timer',         base + 'countdown-timer.js');
  loadIfPresent('.module-image-gallery',           base + 'image-gallery.js');
  loadIfPresent('.module-slider',                  base + 'slider.js');
  loadIfPresent('.module-tabbed-content',          base + 'tabs-panels.js');
  loadIfPresent('.module-testimonials-slider',     base + 'testimonials-slider.js');
  loadIfPresent('.module-stats-numbers',           base + 'stats.js');
  loadIfPresent('.module-map-embed',               base + 'map-embed.js');
  loadIfPresent('.module-code-block',              base + 'code-block.js');
  loadIfPresent('.module-video-background',        base + 'video-banner.js');
  loadIfPresent('.module-video-embed',             base + 'video-embed.js');

})();
