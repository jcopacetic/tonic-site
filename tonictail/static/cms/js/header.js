/* Module: Global Header | Author: Jonathan Sumner | jonathan@khaoticdigital.com */

(function () {
  'use strict';

  function initHeader(header) {
    if (!header) return;

    const sentinel       = document.getElementById(header.id + '-sentinel');
    const mobileNav      = document.getElementById(header.id + '-mobile-nav');
    const mobileToggle   = header.querySelector('.header__mobile-toggle');
    const navItems       = header.querySelectorAll('.nav__item--has-dropdown');
    const mobileSubItems = header.querySelectorAll('.mobile-nav__item--has-sub');
    const isTransparent  = header.dataset.transparent === 'true';

    // ── Active page highlighting ────────────────────────────────────────────
    const currentPath = window.location.pathname.replace(/\/$/, '') || '/';

    function markActive(links) {
      links.forEach(function (link) {
        if (!link.href) return;
        try {
          const linkPath = new URL(link.href).pathname.replace(/\/$/, '') || '/';
          if (linkPath === currentPath) {
            link.classList.add('is-active');
            // If this is a dropdown child, also mark the parent trigger
            const parentItem = link.closest('.nav__item--has-dropdown');
            if (parentItem) {
              const parentTrigger = parentItem.querySelector(':scope > .nav__link');
              if (parentTrigger) parentTrigger.classList.add('is-active');
            }
          }
        } catch (e) { /* external link — skip */ }
      });
    }

    markActive(header.querySelectorAll('.nav__link[href], .nav__dropdown-link'));
    markActive(header.querySelectorAll('.mobile-nav__link[href], .mobile-nav__sub-link'));

    // ── Smart sticky scroll ─────────────────────────────────────────────────
    let lastScrollY   = window.scrollY;
    let ticking       = false;
    let isSticky      = false;

    function onScroll() {
      if (!ticking) {
        window.requestAnimationFrame(updateSticky);
        ticking = true;
      }
    }

    function updateSticky() {
      const scrollY      = window.scrollY;
      const headerHeight = header.offsetHeight;
      const scrollingDown = scrollY > lastScrollY;

      if (scrollY > headerHeight) {
        // Past the header's natural position — activate sticky
        if (!isSticky) {
          header.classList.add('is-sticky');
          // Add a padding-top spacer to the body to prevent layout jump
          document.body.style.paddingTop = headerHeight + 'px';
          isSticky = true;
        }
        // Smart hide/show
        if (scrollingDown && scrollY > lastScrollY + 4) {
          header.classList.add('is-hidden');
          closeMobileMenu(); // close mobile menu if open when hiding
        } else if (!scrollingDown && lastScrollY > scrollY + 4) {
          header.classList.remove('is-hidden');
        }
      } else {
        // Back near the top — deactivate sticky
        if (isSticky) {
          header.classList.remove('is-sticky', 'is-hidden');
          document.body.style.paddingTop = '';
          isSticky = false;
        }
        // Restore transparency if applicable
        if (isTransparent && scrollY < 10) {
          header.classList.add('is-transparent');
        }
      }

      // Remove transparency once scrolled
      if (isTransparent && scrollY > 10) {
        header.classList.remove('is-transparent');
      }

      lastScrollY = scrollY;
      ticking = false;
    }

    window.addEventListener('scroll', onScroll, { passive: true });

    // ── Desktop dropdown keyboard nav ───────────────────────────────────────
    navItems.forEach(function (item) {
      const trigger  = item.querySelector(':scope > .nav__link');
      const dropdown = item.querySelector('.nav__dropdown');
      const links    = dropdown ? dropdown.querySelectorAll('.nav__dropdown-link') : [];

      if (!trigger || !dropdown) return;

      // Open/close on trigger click (for keyboard users — hover handles mouse)
      trigger.addEventListener('click', function () {
        const isOpen = item.classList.contains('is-open');
        closeAllDropdowns();
        if (!isOpen) openDropdown(item, trigger);
      });

      // Arrow key nav within dropdown
      dropdown.addEventListener('keydown', function (e) {
        const focusable = Array.from(links);
        const idx       = focusable.indexOf(document.activeElement);
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          focusable[Math.min(idx + 1, focusable.length - 1)].focus();
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          if (idx === 0) { trigger.focus(); closeDropdown(item, trigger); }
          else focusable[Math.max(idx - 1, 0)].focus();
        } else if (e.key === 'Escape') {
          trigger.focus();
          closeDropdown(item, trigger);
        } else if (e.key === 'Tab') {
          // Close dropdown when tabbing out
          closeDropdown(item, trigger);
        }
      });

      // Close when trigger loses focus to something outside
      trigger.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const isOpen = item.classList.contains('is-open');
          closeAllDropdowns();
          if (!isOpen) openDropdown(item, trigger);
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          openDropdown(item, trigger);
          if (links.length) links[0].focus();
        } else if (e.key === 'Escape') {
          closeDropdown(item, trigger);
        }
      });
    });

    function openDropdown(item, trigger) {
      item.classList.add('is-open');
      trigger.setAttribute('aria-expanded', 'true');
    }

    function closeDropdown(item, trigger) {
      item.classList.remove('is-open');
      trigger.setAttribute('aria-expanded', 'false');
    }

    function closeAllDropdowns() {
      navItems.forEach(function (item) {
        const trigger = item.querySelector(':scope > .nav__link');
        closeDropdown(item, trigger);
      });
    }

    // Click outside closes dropdowns
    document.addEventListener('click', function (e) {
      if (!header.contains(e.target)) closeAllDropdowns();
    });

    // ── Mobile menu toggle ──────────────────────────────────────────────────
    function openMobileMenu() {
      header.classList.add('is-menu-open');
      mobileToggle.setAttribute('aria-expanded', 'true');
      mobileToggle.setAttribute('aria-label', 'Close navigation menu');
      document.body.style.overflow = 'hidden';
    }

    function closeMobileMenu() {
      header.classList.remove('is-menu-open');
      mobileToggle.setAttribute('aria-expanded', 'false');
      mobileToggle.setAttribute('aria-label', 'Open navigation menu');
      document.body.style.overflow = '';
      // Collapse all open mobile sub-menus
      mobileSubItems.forEach(function (item) {
        const btn = item.querySelector('.mobile-nav__link');
        item.classList.remove('is-open');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }

    if (mobileToggle) {
      mobileToggle.addEventListener('click', function () {
        if (header.classList.contains('is-menu-open')) {
          closeMobileMenu();
        } else {
          openMobileMenu();
        }
      });
    }

    // ── Mobile sub-menu accordions ──────────────────────────────────────────
    mobileSubItems.forEach(function (item) {
      const btn = item.querySelector('.mobile-nav__link');
      if (!btn) return;

      btn.addEventListener('click', function () {
        const isOpen = item.classList.contains('is-open');
        // Close other open sub-menus
        mobileSubItems.forEach(function (other) {
          if (other !== item) {
            const otherBtn = other.querySelector('.mobile-nav__link');
            other.classList.remove('is-open');
            if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
          }
        });
        item.classList.toggle('is-open', !isOpen);
        btn.setAttribute('aria-expanded', String(!isOpen));
      });
    });

    // ── Escape key — close everything ──────────────────────────────────────
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        closeAllDropdowns();
        if (header.classList.contains('is-menu-open')) {
          closeMobileMenu();
          mobileToggle.focus();
        }
      }
    });

    // ── Resize — close mobile menu if resizing to desktop ──────────────────
    const mql = window.matchMedia('(min-width: 1024px)');
    function onBreakpoint(e) {
      if (e.matches) {
        closeMobileMenu();
        closeAllDropdowns();
      }
    }
    if (mql.addEventListener) {
      mql.addEventListener('change', onBreakpoint);
    } else {
      mql.addListener(onBreakpoint); // Safari <14 fallback
    }

  }

  // ── Init on DOM ready ─────────────────────────────────────────────────────
  function ready(fn) {
    if (document.readyState !== 'loading') { fn(); }
    else { document.addEventListener('DOMContentLoaded', fn); }
  }

  ready(function () {
    // HubSpot global modules render with a unique id="/* [hubl-value] */" on the root element.
    // We find the header by its BEM class so this script works regardless of the
    // dynamic name value, and supports multiple instances (e.g. in the editor).
    document.querySelectorAll('.module-global-header').forEach(initHeader);
  });

})();