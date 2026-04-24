/*
 * File: module.js
 * Module: Testimonials Slider
 * Description: Vanilla ES6 slider. Handles arrow navigation, dot indicators,
 *              keyboard (arrow keys), touch/swipe, and optional autoplay.
 *              Fully scoped to the module instance via #/* [hubl-value] */.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  'use strict';

  // ─── Bootstrap every slider instance on the page ────────────────
  function initAllSliders() {
    const sliders = document.querySelectorAll('.module-testimonials-slider');
    sliders.forEach(initSlider);
  }

  // ─── Single slider instance ──────────────────────────────────────
  function initSlider(root) {
    // ── Read config from data attributes set by HubL ──
    const slidesToShow  = parseInt(root.dataset.slidesToShow, 10)  || 1;
    const autoplay      = root.dataset.autoplay === 'true';
    const autoplayDelay = parseInt(root.dataset.autoplayDelay, 10) || 5000;

    // ── DOM references ──
    const track    = root.querySelector('.module-testimonials-slider__track');
    const viewport = root.querySelector('.module-testimonials-slider__viewport');
    const slides   = Array.from(root.querySelectorAll('.module-testimonials-slider__slide'));
    const btnPrev  = root.querySelector('.module-testimonials-slider__arrow--prev');
    const btnNext  = root.querySelector('.module-testimonials-slider__arrow--next');
    const dotsWrap = root.querySelector('.module-testimonials-slider__dots');

    if (!track || slides.length === 0) return;

    // ── State ──
    const totalSlides   = slides.length;
    // Number of "pages" (steps) in the slider.
    // When showing N slides, advance by N slides per step.
    const totalSteps    = Math.ceil(totalSlides / slidesToShow);
    let   currentStep   = 0;
    let   autoplayTimer = null;
    let   isHovered     = false;
    let   isFocused     = false;

    // ── Gap between slides (read from computed style after render) ──
    // We defer this to the first goTo() call so the DOM is painted.
    let slideGap = null;

    function getSlideGap() {
      if (slideGap !== null) return slideGap;
      const trackStyle = window.getComputedStyle(track);
      slideGap = parseFloat(trackStyle.columnGap) || 0;
      return slideGap;
    }

    // ── Slide width (one slide's flex basis width in px) ──
    function getSlideWidth() {
      return slides[0] ? slides[0].getBoundingClientRect().width : 0;
    }

    // ── Calculate translateX for a given step ──
    // Each step advances by (slidesToShow) slides.
    // translateX = step * slidesToShow * (slideWidth + gap)
    // On the last step, we clamp so we don't over-scroll past the last slide.
    function getTranslateX(step) {
      const gap        = getSlideGap();
      const slideWidth = getSlideWidth();
      const unit       = slideWidth + gap;

      // Last step: align the last slide(s) to the right edge of the viewport
      if (step === totalSteps - 1) {
        const maxTranslate = (totalSlides - slidesToShow) * unit;
        return Math.max(0, maxTranslate);
      }

      return step * slidesToShow * unit;
    }

    // ── Apply position ──
    function applyPosition(animate) {
      if (!animate) track.classList.add('module-testimonials-slider__track--no-transition');
      track.style.transform = 'translateX(-' + getTranslateX(currentStep) + 'px)';
      if (!animate) {
        // Force reflow so the no-transition class takes effect before removal
        void track.offsetHeight;
        track.classList.remove('module-testimonials-slider__track--no-transition');
      }
    }

    // ── Go to step ──
    function goTo(step, animate) {
      animate = animate !== false;
      currentStep = Math.max(0, Math.min(step, totalSteps - 1));
      applyPosition(animate);
      updateArrows();
      updateDots();
      updateAriaLive();
    }

    // ── Next / Prev ──
    function next() { goTo(currentStep + 1); }
    function prev() { goTo(currentStep - 1); }

    // ── Arrow disabled state ──
    function updateArrows() {
      if (btnPrev) {
        const disabled = currentStep === 0;
        btnPrev.disabled = disabled;
        btnPrev.setAttribute('aria-disabled', String(disabled));
      }
      if (btnNext) {
        const disabled = currentStep === totalSteps - 1;
        btnNext.disabled = disabled;
        btnNext.setAttribute('aria-disabled', String(disabled));
      }
    }

    // ── Build dots ──
    function buildDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = '';
      for (let i = 0; i < totalSteps; i++) {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'module-testimonials-slider__dot';
        dot.setAttribute('role', 'tab');
        dot.setAttribute('aria-label', 'Go to slide group ' + (i + 1));
        dot.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
        dot.addEventListener('click', function () { goTo(i); });
        dotsWrap.appendChild(dot);
      }
    }

    // ── Update dots ──
    function updateDots() {
      if (!dotsWrap) return;
      const dots = dotsWrap.querySelectorAll('.module-testimonials-slider__dot');
      dots.forEach(function (dot, i) {
        const active = i === currentStep;
        dot.classList.toggle('module-testimonials-slider__dot--active', active);
        dot.setAttribute('aria-selected', String(active));
      });
    }

    // ── ARIA live region update ──
    // Announce the current slide range to screen readers.
    function updateAriaLive() {
      const start = currentStep * slidesToShow + 1;
      const end   = Math.min(start + slidesToShow - 1, totalSlides);
      const msg   = end > start
        ? 'Showing testimonials ' + start + ' to ' + end + ' of ' + totalSlides
        : 'Showing testimonial ' + start + ' of ' + totalSlides;
      if (viewport) {
        viewport.setAttribute('aria-label', msg);
      }
    }

    // ── Autoplay ──
    function startAutoplay() {
      if (!autoplay) return;
      stopAutoplay();
      autoplayTimer = setInterval(function () {
        if (isHovered || isFocused) return;
        if (currentStep === totalSteps - 1) {
          goTo(0);
        } else {
          next();
        }
      }, autoplayDelay);
    }

    function stopAutoplay() {
      if (autoplayTimer) {
        clearInterval(autoplayTimer);
        autoplayTimer = null;
      }
    }

    // ── Touch / swipe ──
    let touchStartX   = null;
    let touchStartY   = null;
    let touchDragging = false;

    function onTouchStart(e) {
      if (e.touches.length !== 1) return;
      touchStartX   = e.touches[0].clientX;
      touchStartY   = e.touches[0].clientY;
      touchDragging = false;
    }

    function onTouchMove(e) {
      if (touchStartX === null) return;
      const dx = e.touches[0].clientX - touchStartX;
      const dy = e.touches[0].clientY - touchStartY;
      // Only lock to horizontal if clearly swiping sideways
      if (!touchDragging && Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 8) {
        touchDragging = true;
      }
      if (touchDragging) e.preventDefault();
    }

    function onTouchEnd(e) {
      if (!touchDragging || touchStartX === null) {
        touchStartX = null;
        return;
      }
      const dx = e.changedTouches[0].clientX - touchStartX;
      const threshold = 50;
      if (dx < -threshold) next();
      else if (dx > threshold) prev();
      touchStartX   = null;
      touchDragging = false;
    }

    // ── Keyboard navigation ──
    function onKeyDown(e) {
      if (e.key === 'ArrowLeft')  { prev(); e.preventDefault(); }
      if (e.key === 'ArrowRight') { next(); e.preventDefault(); }
    }

    // ── Reflow on resize ──
    // When the viewport width changes, slide widths change. Recalculate translateX.
    let resizeTimer = null;
    function onResize() {
      slideGap = null; // clear cached gap
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        applyPosition(false); // snap without animation
      }, 100);
    }

    // ── Wire up events ──
    if (btnPrev) btnPrev.addEventListener('click', prev);
    if (btnNext) btnNext.addEventListener('click', next);

    root.addEventListener('keydown', onKeyDown);

    root.addEventListener('mouseenter', function () { isHovered = true; });
    root.addEventListener('mouseleave', function () { isHovered = false; });
    root.addEventListener('focusin',    function () { isFocused = true; });
    root.addEventListener('focusout',   function () { isFocused = false; });

    viewport.addEventListener('touchstart', onTouchStart, { passive: true });
    viewport.addEventListener('touchmove',  onTouchMove,  { passive: false });
    viewport.addEventListener('touchend',   onTouchEnd,   { passive: true });

    window.addEventListener('resize', onResize);

    // ── Init ──
    buildDots();
    goTo(0, false);
    startAutoplay();
  }

  // ─── Entry point ────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllSliders);
  } else {
    initAllSliders();
  }

})();