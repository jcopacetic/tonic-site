/**
 * File: module.js
 * Module: Slider / Carousel
 * Description: Transform-based carousel controller. Clones first/last slides to
 *              create a seamless infinite loop. No scroll APIs used — avoids the
 *              scroll-snap / scrollTo conflict that causes bounce and glitching.
 *              All config read from data-* attributes on [data-slider].
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  'use strict';

  function initSlider(root) {

    // ── Config ───────────────────────────────────────────────────────────────
    const slidesToShow   = Math.max(1, parseInt(root.dataset.slidesToShow,   10) || 1);
    const slidesToScroll = Math.max(1, parseInt(root.dataset.slidesToScroll, 10) || 1);
    const loop           = root.dataset.loop      !== 'false';
    const autoplay       = root.dataset.autoplay  === 'true';
    const autoplaySpeed  = parseInt(root.dataset.autoplaySpeed,   10) || 4000;
    const transSpeed     = parseInt(root.dataset.transitionSpeed, 10) || 400;

    // ── DOM ──────────────────────────────────────────────────────────────────
    const track   = root.querySelector('.module-slider__track');
    const btnsPrev = Array.from(root.querySelectorAll('.module-slider__btn--prev'));
    const btnsNext = Array.from(root.querySelectorAll('.module-slider__btn--next'));
    const dots     = Array.from(root.querySelectorAll('.module-slider__dot'));

    if (!track) return;

    // ── Clone slides for infinite loop ───────────────────────────────────────
    // We clone enough slides at each end to cover the slidesToShow count.
    // Real slides are indexed from `clonesBefore` to `clonesBefore + realCount - 1`
    // in the DOM; our JS `currentIndex` always refers to real-slide positions (0-based).

    const realSlides = Array.from(track.children);
    const realCount  = realSlides.length;
    if (realCount === 0) return;

    let clonesBefore = 0;

    if (loop && realCount > 1) {
      // Clone last N real slides and prepend
      const prependCount = Math.min(slidesToShow, realCount);
      for (let i = realCount - prependCount; i < realCount; i++) {
        const clone = realSlides[i].cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.classList.add('module-slider__slide--clone');
        track.insertBefore(clone, track.firstChild);
      }
      clonesBefore = prependCount;

      // Clone first N real slides and append
      const appendCount = Math.min(slidesToShow + slidesToScroll, realCount);
      for (let i = 0; i < appendCount; i++) {
        const clone = realSlides[i].cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        clone.classList.add('module-slider__slide--clone');
        track.appendChild(clone);
      }
    }

    // All slides (including clones)
    const allSlides = Array.from(track.children);

    // ── State ────────────────────────────────────────────────────────────────
    let currentIndex  = 0; // 0-based index into REAL slides
    let isAnimating   = false;
    let autoplayTimer = null;

    // ── Layout helpers ───────────────────────────────────────────────────────

    function getSlideWidth() {
      if (!allSlides[0]) return 0;
      const trackStyle = window.getComputedStyle(track);
      const gap = parseFloat(trackStyle.gap || trackStyle.columnGap) || 0;
      return allSlides[0].offsetWidth + gap;
    }

    // DOM index of a real slide
    function domIndex(realIdx) {
      return realIdx + clonesBefore;
    }

    // Translate track to show realIdx at the left
    function setTranslate(realIdx, animate) {
      const sw   = getSlideWidth();
      const di   = domIndex(realIdx);
      const x    = -(di * sw);

      track.style.transition = animate
        ? `transform ${transSpeed}ms ease`
        : 'none';
      track.style.transform = `translateX(${x}px)`;
    }

    // ── Navigation ───────────────────────────────────────────────────────────

    function go(delta) {
      if (isAnimating) return;

      let next = currentIndex + (delta * slidesToScroll);

      if (loop) {
        // Allow going out of bounds — we'll snap-correct after animation
        // (clones cover the overshoot visually)
      } else {
        next = Math.max(0, Math.min(next, realCount - slidesToShow));
      }

      currentIndex = next;
      isAnimating  = true;
      setTranslate(currentIndex, true);
      updateDots();
      updateArrows();

      // After animation, silently jump if we've gone into clone territory
      setTimeout(() => {
        if (loop) {
          if (currentIndex < 0) {
            currentIndex = realCount - slidesToScroll;
            setTranslate(currentIndex, false);
          } else if (currentIndex > realCount - slidesToShow) {
            currentIndex = 0;
            setTranslate(currentIndex, false);
          }
        }
        isAnimating = false;
      }, transSpeed + 20);
    }

    function goTo(realIdx) {
      if (isAnimating) return;
      currentIndex = Math.max(0, Math.min(realIdx * slidesToScroll, realCount - 1));
      isAnimating  = true;
      setTranslate(currentIndex, true);
      updateDots();
      updateArrows();
      setTimeout(() => { isAnimating = false; }, transSpeed + 20);
    }

    // ── UI updates ───────────────────────────────────────────────────────────

    function updateDots() {
      const activePage = Math.floor(
        Math.max(0, Math.min(currentIndex, realCount - 1)) / slidesToScroll
      );
      dots.forEach((dot, i) => {
        const active = i === activePage;
        dot.classList.toggle('is-active', active);
        dot.setAttribute('aria-selected', active ? 'true' : 'false');
      });
    }

    function updateArrows() {
      if (loop) {
        btnsPrev.forEach(b => b.classList.remove('is-disabled'));
        btnsNext.forEach(b => b.classList.remove('is-disabled'));
        return;
      }
      btnsPrev.forEach(b => b.classList.toggle('is-disabled', currentIndex <= 0));
      btnsNext.forEach(b => b.classList.toggle('is-disabled', currentIndex >= realCount - slidesToShow));
    }

    // ── Autoplay ─────────────────────────────────────────────────────────────

    function startAutoplay() {
      if (!autoplay) return;
      autoplayTimer = setInterval(() => go(1), autoplaySpeed);
    }

    function stopAutoplay() {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }

    // ── Touch / drag ─────────────────────────────────────────────────────────

    let dragStartX  = null;
    let dragCurrentX = null;

    function onDragStart(e) {
      dragStartX   = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
      dragCurrentX = dragStartX;
      root.classList.add('module-slider--dragging');
      stopAutoplay();
    }

    function onDragMove(e) {
      if (dragStartX === null) return;
      dragCurrentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
      const diff = dragCurrentX - dragStartX;
      const sw   = getSlideWidth();
      const base = -(domIndex(currentIndex) * sw);
      track.style.transition = 'none';
      track.style.transform  = `translateX(${base + diff}px)`;
    }

    function onDragEnd() {
      if (dragStartX === null) return;
      const diff = dragCurrentX - dragStartX;
      const threshold = getSlideWidth() * 0.2; // 20% of slide width triggers advance

      root.classList.remove('module-slider--dragging');

      if (Math.abs(diff) > threshold) {
        go(diff < 0 ? 1 : -1);
      } else {
        // Snap back to current
        setTranslate(currentIndex, true);
      }

      dragStartX   = null;
      dragCurrentX = null;
      startAutoplay();
    }

    track.addEventListener('touchstart',  onDragStart, { passive: true });
    track.addEventListener('touchmove',   onDragMove,  { passive: true });
    track.addEventListener('touchend',    onDragEnd);
    track.addEventListener('mousedown',   onDragStart);
    track.addEventListener('mousemove',   onDragMove);
    track.addEventListener('mouseup',     onDragEnd);
    track.addEventListener('mouseleave',  onDragEnd);

    // ── Event listeners ──────────────────────────────────────────────────────

    btnsPrev.forEach(btn => btn.addEventListener('click', () => {
      stopAutoplay(); go(-1); startAutoplay();
    }));

    btnsNext.forEach(btn => btn.addEventListener('click', () => {
      stopAutoplay(); go(1); startAutoplay();
    }));

    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        stopAutoplay(); goTo(i); startAutoplay();
      });
    });

    root.addEventListener('mouseenter', stopAutoplay);
    root.addEventListener('mouseleave', startAutoplay);
    root.addEventListener('focusin',    stopAutoplay);
    root.addEventListener('focusout',   startAutoplay);

    root.addEventListener('keydown', e => {
      if (e.key === 'ArrowLeft')  { e.preventDefault(); stopAutoplay(); go(-1); startAutoplay(); }
      if (e.key === 'ArrowRight') { e.preventDefault(); stopAutoplay(); go(1);  startAutoplay(); }
    });

    // ── Resize: recalculate position without animation ────────────────────────
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => setTranslate(currentIndex, false), 100);
    });

    // ── Init ─────────────────────────────────────────────────────────────────
    setTranslate(0, false);
    updateDots();
    updateArrows();
    startAutoplay();
  }

  // Boot
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-slider]').forEach(initSlider);
  });

})();