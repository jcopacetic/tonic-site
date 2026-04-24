/* File: module.js | Module: Video Background Banner | Author: Jonathan Sumner | jonathan@khaoticdigital.com */

(function () {
  'use strict';

  function initVideoBackground(wrapper) {
    const video = wrapper.querySelector('.module-video-background__video');
    const fallback = wrapper.querySelector('.module-video-background__fallback');
    const playBtn = wrapper.querySelector('.module-video-background__play-btn');

    const respectReducedMotion = wrapper.dataset.respectReducedMotion === 'True';
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ── Reduced motion: skip video entirely ──────────────────
    if (respectReducedMotion && prefersReducedMotion) {
      if (video) video.remove();
      if (fallback) fallback.classList.add('is-visible');
      return;
    }

    // ── MP4 video handling ────────────────────────────────────
    if (video) {
      // Show fallback while video loads
      if (fallback) fallback.classList.add('is-visible');

      video.addEventListener('canplay', function () {
        if (fallback) fallback.classList.remove('is-visible');
      });

      video.addEventListener('error', function () {
        // Video failed — keep fallback visible
        if (fallback) fallback.classList.add('is-visible');
        if (video) video.remove();
      });

      // ── Play button ─────────────────────────────────────────
      if (playBtn) {
        playBtn.addEventListener('click', function () {
          video.muted = false;
          video.currentTime = 0;
          video.play().then(function () {
            playBtn.classList.add('is-playing');
            playBtn.setAttribute('aria-label', 'Video playing');
          }).catch(function () {
            // Autoplay with sound blocked — keep button visible
          });
        });
      }
    }

    // ── Intersection Observer: pause when off-screen ──────────
    if (video && 'IntersectionObserver' in window) {
      const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            if (video.paused) video.play().catch(function () {});
          } else {
            if (!video.paused) video.pause();
          }
        });
      }, { threshold: 0.1 });

      observer.observe(wrapper);
    }
  }

  // ── Init all instances on page ───────────────────────────────
  document.querySelectorAll('.module-video-background').forEach(initVideoBackground);

})();