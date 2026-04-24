// Module: Accordion FAQ
// Description: Accessible accordion expand/collapse with animated height transitions.
//              Reads behavior flags (allow-multi, animate) from data attributes on
//              the section wrapper. Scoped to module instance via data-module-id.
// Author: Jonathan Sumner | jonathan@khaoticdigital.com

(function () {
  'use strict';

  /**
   * Initialize all accordion FAQ modules on the page.
   * Runs on DOMContentLoaded. Safe to call multiple times — each instance
   * is identified by [data-module-id] and initialized once.
   */
  function initAllFAQModules() {
    document.querySelectorAll('[data-module-id]').forEach(function (section) {
      if (!section.classList.contains('module-accordion-faq')) return;
      if (section.dataset.faqInit) return; // already initialized
      section.dataset.faqInit = 'true';
      initFAQModule(section);
    });
  }

  /**
   * Initialize a single accordion FAQ module.
   * @param {HTMLElement} section - The .module-accordion-faq wrapper element.
   */
  function initFAQModule(section) {
    var allowMulti = section.dataset.allowMulti === 'true';
    var animate    = section.dataset.animate !== 'false';
    var triggers   = section.querySelectorAll('[data-faq-trigger]');

    triggers.forEach(function (trigger) {
      trigger.addEventListener('click', function () {
        var item  = trigger.closest('[data-faq-item]');
        var panel = item.querySelector('[data-faq-panel]');
        var isOpen = item.classList.contains('is-open');

        // Close other items unless multi-open is allowed
        if (!allowMulti) {
          closeAllExcept(section, item, animate);
        }

        // Toggle clicked item
        if (isOpen) {
          closeItem(item, panel, trigger, animate);
        } else {
          openItem(item, panel, trigger, animate);
        }
      });
    });
  }

  /**
   * Open a single accordion item.
   */
  function openItem(item, panel, trigger, animate) {
    item.classList.add('is-open');
    trigger.setAttribute('aria-expanded', 'true');

    if (animate) {
      animateOpen(panel);
    } else {
      panel.removeAttribute('hidden');
    }
  }

  /**
   * Close a single accordion item.
   */
  function closeItem(item, panel, trigger, animate) {
    item.classList.remove('is-open');
    trigger.setAttribute('aria-expanded', 'false');

    if (animate) {
      animateClose(panel);
    } else {
      panel.setAttribute('hidden', '');
    }
  }

  /**
   * Close all items in a module except the specified one.
   */
  function closeAllExcept(section, excludeItem, animate) {
    section.querySelectorAll('[data-faq-item].is-open').forEach(function (openItem) {
      if (openItem === excludeItem) return;
      var openPanel   = openItem.querySelector('[data-faq-panel]');
      var openTrigger = openItem.querySelector('[data-faq-trigger]');
      closeItem(openItem, openPanel, openTrigger, animate);
    });
  }

  /**
   * Animate panel open: measure scrollHeight, transition from 0 to full height.
   */
  function animateOpen(panel) {
    // Remove hidden so we can measure
    panel.removeAttribute('hidden');
    panel.dataset.animating = 'true';

    // Start from 0
    panel.style.height = '0px';
    panel.style.overflow = 'hidden';

    // Force reflow
    panel.getBoundingClientRect();

    var targetHeight = panel.scrollHeight;
    panel.style.height = targetHeight + 'px';

    panel.addEventListener('transitionend', function onEnd() {
      panel.removeEventListener('transitionend', onEnd);
      panel.style.height = '';
      panel.style.overflow = '';
      delete panel.dataset.animating;
    }, { once: true });
  }

  /**
   * Animate panel close: transition from current height to 0, then hide.
   */
  function animateClose(panel) {
    if (panel.hasAttribute('hidden')) return;

    panel.dataset.animating = 'true';
    panel.style.height = panel.scrollHeight + 'px';
    panel.style.overflow = 'hidden';

    // Force reflow
    panel.getBoundingClientRect();

    panel.style.height = '0px';

    panel.addEventListener('transitionend', function onEnd() {
      panel.removeEventListener('transitionend', onEnd);
      panel.setAttribute('hidden', '');
      panel.style.height = '';
      panel.style.overflow = '';
      delete panel.dataset.animating;
    }, { once: true });
  }

  /**
   * Keyboard navigation: allow arrow keys to move between triggers,
   * Home/End to jump to first/last.
   */
  function initKeyboardNav(section) {
    section.addEventListener('keydown', function (e) {
      var trigger = e.target.closest('[data-faq-trigger]');
      if (!trigger) return;

      var triggers = Array.from(section.querySelectorAll('[data-faq-trigger]'));
      var idx      = triggers.indexOf(trigger);

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        var next = triggers[idx + 1] || triggers[0];
        next.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        var prev = triggers[idx - 1] || triggers[triggers.length - 1];
        prev.focus();
      } else if (e.key === 'Home') {
        e.preventDefault();
        triggers[0].focus();
      } else if (e.key === 'End') {
        e.preventDefault();
        triggers[triggers.length - 1].focus();
      }
    });
  }

  /**
   * Extended init: keyboard nav per module.
   */
  function initAllFAQModulesFull() {
    document.querySelectorAll('[data-module-id]').forEach(function (section) {
      if (!section.classList.contains('module-accordion-faq')) return;
      if (section.dataset.faqKeyInit) return;
      section.dataset.faqKeyInit = 'true';
      initKeyboardNav(section);
    });
  }

  // ── Boot ──────────────────────────────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initAllFAQModules();
      initAllFAQModulesFull();
    });
  } else {
    initAllFAQModules();
    initAllFAQModulesFull();
  }

})();