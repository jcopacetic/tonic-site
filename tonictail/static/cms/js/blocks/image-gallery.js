/*
 * File: module.js
 * Module: Image Gallery
 * Description: Handles the lightbox overlay — open, close, next/prev navigation,
 *              keyboard (arrow keys + Escape), focus trap, touch/swipe, and image
 *              preloading. Scoped to each .module-image-gallery instance independently.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  'use strict';

  // ─── Init all gallery instances on the page ──────────────────────
  function initAllGalleries() {
    document.querySelectorAll('.module-image-gallery').forEach(initGallery);
  }

  // ─── Single gallery instance ─────────────────────────────────────
  function initGallery(root) {
    const lightbox = root.querySelector('.module-image-gallery__lightbox');
    if (!lightbox) return; // lightbox disabled in fields

    // ── Collect all lightbox-enabled triggers in DOM order ──
    const triggers = Array.from(
      root.querySelectorAll('.module-image-gallery__item-inner--lightbox')
    );
    if (triggers.length === 0) return;

    // Build an ordered list of slide data from the trigger data-attributes
    const slides = triggers.map(function (btn) {
      return {
        src:     btn.dataset.lightboxSrc,
        alt:     btn.dataset.lightboxAlt     || '',
        caption: btn.dataset.lightboxCaption || ''
      };
    });

    // ── DOM refs inside the lightbox ──
    const lbImg     = lightbox.querySelector('.module-image-gallery__lightbox-img');
    const lbCaption = lightbox.querySelector('.module-image-gallery__lightbox-caption');
    const lbCounter = lightbox.querySelector('.module-image-gallery__lightbox-counter');
    const lbClose   = lightbox.querySelector('.module-image-gallery__lightbox-close');
    const lbPrev    = lightbox.querySelector('.module-image-gallery__lightbox-prev');
    const lbNext    = lightbox.querySelector('.module-image-gallery__lightbox-next');

    // ── State ──
    let currentIndex  = 0;
    let isOpen        = false;
    let lastFocused   = null; // element that triggered open — restored on close
    let touchStartX   = null;
    let touchStartY   = null;
    let touchDragging = false;

    // ─── Open ────────────────────────────────────────────────────
    function open(index) {
      lastFocused  = document.activeElement;
      currentIndex = clamp(index, 0, slides.length - 1);
      isOpen       = true;

      lightbox.setAttribute('aria-hidden', 'false');
      lightbox.classList.add('module-image-gallery__lightbox--open');
      document.body.style.overflow = 'hidden';

      loadSlide(currentIndex);
      lightbox.focus();
    }

    // ─── Close ───────────────────────────────────────────────────
    function close() {
      isOpen = false;
      lightbox.classList.remove('module-image-gallery__lightbox--open');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (lastFocused) lastFocused.focus();
    }

    // ─── Navigate ────────────────────────────────────────────────
    function goTo(index) {
      currentIndex = clamp(index, 0, slides.length - 1);
      loadSlide(currentIndex);
    }

    function next() { goTo(currentIndex + 1); }
    function prev() { goTo(currentIndex - 1); }

    // ─── Load a slide into the lightbox ──────────────────────────
    function loadSlide(index) {
      const slide = slides[index];

      // Show loading state
      lbImg.classList.add('module-image-gallery__lightbox-img--loading');

      // Preload
      const preload = new Image();
      preload.onload = function () {
        lbImg.src = slide.src;
        lbImg.alt = slide.alt;
        lbImg.classList.remove('module-image-gallery__lightbox-img--loading');
      };
      preload.onerror = function () {
        // Still set the src even if preload fails — browser will show broken image
        lbImg.src = slide.src;
        lbImg.alt = slide.alt;
        lbImg.classList.remove('module-image-gallery__lightbox-img--loading');
      };
      preload.src = slide.src;

      // Caption
      if (lbCaption) lbCaption.textContent = slide.caption;

      // Counter: "3 / 9"
      if (lbCounter) lbCounter.textContent = (index + 1) + ' / ' + slides.length;

      // Arrow disabled states
      if (lbPrev) lbPrev.disabled = index === 0;
      if (lbNext) lbNext.disabled = index === slides.length - 1;

      // Preload adjacent images for snappier navigation
      preloadAdjacent(index);
    }

    // ─── Preload neighbours ───────────────────────────────────────
    function preloadAdjacent(index) {
      [-1, 1].forEach(function (offset) {
        const adj = index + offset;
        if (adj >= 0 && adj < slides.length) {
          var img = new Image();
          img.src = slides[adj].src;
        }
      });
    }

    // ─── Wire up triggers ─────────────────────────────────────────
    triggers.forEach(function (btn, i) {
      btn.addEventListener('click', function () { open(i); });
    });

    // ─── Lightbox controls ────────────────────────────────────────
    if (lbClose) lbClose.addEventListener('click', close);
    if (lbPrev)  lbPrev.addEventListener('click',  prev);
    if (lbNext)  lbNext.addEventListener('click',  next);

    // Click on backdrop (outside stage) closes lightbox
    lightbox.addEventListener('click', function (e) {
      if (e.target === lightbox) close();
    });

    // ─── Keyboard ────────────────────────────────────────────────
    lightbox.addEventListener('keydown', function (e) {
      if (!isOpen) return;
      switch (e.key) {
        case 'Escape':     close();            break;
        case 'ArrowLeft':  prev();             break;
        case 'ArrowRight': next();             break;
        case 'Tab':        trapFocus(e);       break;
      }
    });

    // ─── Focus trap ───────────────────────────────────────────────
    function trapFocus(e) {
      const focusable = Array.from(
        lightbox.querySelectorAll(
          'button:not([disabled]), [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
      ).filter(function (el) { return !el.hidden; });

      if (focusable.length === 0) { e.preventDefault(); return; }

      const first = focusable[0];
      const last  = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          last.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === last) {
          first.focus();
          e.preventDefault();
        }
      }
    }

    // ─── Touch / swipe ────────────────────────────────────────────
    lightbox.addEventListener('touchstart', function (e) {
      if (e.touches.length !== 1) return;
      touchStartX   = e.touches[0].clientX;
      touchStartY   = e.touches[0].clientY;
      touchDragging = false;
    }, { passive: true });

    lightbox.addEventListener('touchmove', function (e) {
      if (touchStartX === null) return;
      var dx = e.touches[0].clientX - touchStartX;
      var dy = e.touches[0].clientY - touchStartY;
      if (!touchDragging && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 8) {
        touchDragging = true;
      }
      if (touchDragging) e.preventDefault();
    }, { passive: false });

    lightbox.addEventListener('touchend', function (e) {
      if (!touchDragging || touchStartX === null) {
        touchStartX = null;
        return;
      }
      var dx = e.changedTouches[0].clientX - touchStartX;
      if (dx < -50) next();
      else if (dx > 50) prev();
      touchStartX   = null;
      touchDragging = false;
    }, { passive: true });
  }

  // ─── Utility ────────────────────────────────────────────────────
  function clamp(val, min, max) {
    return Math.min(Math.max(val, min), max);
  }

  // ─── Entry point ────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllGalleries);
  } else {
    initAllGalleries();
  }

})();