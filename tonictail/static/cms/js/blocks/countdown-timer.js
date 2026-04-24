/*
 * File: module.js
 * Module: Countdown Timer
 * Description: Countdown timer logic — reads target date/time/timezone from data attributes,
 *   updates the display every second, triggers flip animations on digit changes, and shows
 *   the expired state when the deadline passes.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  'use strict';

  // ── Scope to this module instance ──────────────────────────────────────
  // document.currentScript is null when scripts run deferred/async (common in HubSpot).
  // Instead we find every display element on the page — each carries all the config
  // it needs, and its closest .module-countdown-timer ancestor is the root.
  document.querySelectorAll('.module-countdown-timer__display').forEach(initTimer);

  function initTimer (display) {
    const root = display.closest('.module-countdown-timer');
    if (!root) return;

    const expiredEl = root.querySelector('.module-countdown-timer__expired');
    const daysEl    = root.querySelector('[id$="-days"]');
    const hoursEl   = root.querySelector('[id$="-hours"]');
    const minutesEl = root.querySelector('[id$="-minutes"]');
    const secondsEl = root.querySelector('[id$="-seconds"]');

    // ── Read config from data attributes ─────────────────────────────────
    const targetDateRaw = (display.dataset.targetDate || '').trim();
    const targetTimeStr = (display.dataset.targetTime || '17:00').trim();
    const timezone      = (display.dataset.timezone   || 'America/Chicago').trim();

    // ── State for flip animation ──────────────────────────────────────────
    const prev = { days: null, hours: null, minutes: null, seconds: null };

    // ── Build target Date ─────────────────────────────────────────────────
    // HubSpot date fields output a Unix timestamp in milliseconds (13 digits)
    // representing midnight UTC on the chosen date.
    function buildTargetDate () {
      if (!targetDateRaw) return null;

      // 1. Resolve YYYY-MM-DD
      let datePart;
      if (/^\d{10,}$/.test(targetDateRaw)) {
        const ms = targetDateRaw.length >= 13
          ? parseInt(targetDateRaw, 10)
          : parseInt(targetDateRaw, 10) * 1000;
        const d  = new Date(ms);
        datePart = [
          d.getUTCFullYear(),
          String(d.getUTCMonth() + 1).padStart(2, '0'),
          String(d.getUTCDate()).padStart(2, '0')
        ].join('-');
      } else if (/^\d{4}-\d{2}-\d{2}/.test(targetDateRaw)) {
        datePart = targetDateRaw.slice(0, 10);
      } else {
        return null;
      }

      // 2. Parse time
      const tp     = targetTimeStr.split(':').map(Number);
      const hour   = isNaN(tp[0]) ? 17 : tp[0];
      const minute = isNaN(tp[1]) ? 0  : tp[1];
      const hStr   = String(hour).padStart(2, '0');
      const mStr   = String(minute).padStart(2, '0');

      // 3. Convert wall-clock time in <timezone> → UTC
      //
      // Treat the desired local time as if it were UTC (naiveUTC), then ask Intl
      // what wall-clock time the target tz displays for that UTC moment.
      // The gap between what we asked for and what the tz shows IS the offset.
      // Subtract it to get the true UTC instant.
      try {
        const naiveUTC = new Date(`${datePart}T${hStr}:${mStr}:00Z`);

        const parts = {};
        new Intl.DateTimeFormat('en-US', {
          timeZone: timezone,
          year: 'numeric', month: '2-digit', day: '2-digit',
          hour: '2-digit', minute: '2-digit', second: '2-digit',
          hour12: false
        }).formatToParts(naiveUTC).forEach(function (p) { parts[p.type] = p.value; });

        // Intl can return '24' for midnight on some engines
        const h = parts.hour === '24' ? '00' : parts.hour;

        // UTC instant that corresponds to the tz wall-clock reading
        const tzWallAsUTC = new Date(
          `${parts.year}-${parts.month}-${parts.day}T${h}:${parts.minute}:${parts.second}Z`
        );

        const offsetMs = naiveUTC.getTime() - tzWallAsUTC.getTime();
        return new Date(naiveUTC.getTime() + offsetMs);

      } catch (e) {
        // Fallback: browser local time
        return new Date(`${datePart}T${hStr}:${mStr}:00`);
      }
    }

    const targetDate = buildTargetDate();

    // ── Helpers ───────────────────────────────────────────────────────────
    function pad (n) {
      return String(Math.max(0, Math.floor(n))).padStart(2, '0');
    }

    function flip (wrapper) {
      wrapper.classList.remove('is-flipping');
      void wrapper.offsetWidth;
      wrapper.classList.add('is-flipping');
    }

    function updateDigit (el, value, key) {
      if (!el) return;
      const padded = pad(value);
      if (prev[key] !== padded) {
        el.textContent = padded;
        const wrapper = el.closest('.module-countdown-timer__digit-wrapper');
        if (wrapper) flip(wrapper);
        prev[key] = padded;
      }
    }

    function showExpired () {
      display.setAttribute('hidden', '');
      if (expiredEl) expiredEl.removeAttribute('hidden');
    }

    // ── Tick ──────────────────────────────────────────────────────────────
    function tick () {
      if (!targetDate) {
        // No date set — freeze at 00:00:00:00
        updateDigit(daysEl,    0, 'days');
        updateDigit(hoursEl,   0, 'hours');
        updateDigit(minutesEl, 0, 'minutes');
        updateDigit(secondsEl, 0, 'seconds');
        return false;
      }

      const remaining = targetDate.getTime() - Date.now();

      if (remaining <= 0) {
        showExpired();
        return false;
      }

      const total = Math.floor(remaining / 1000);
      updateDigit(daysEl,    Math.floor(total / 86400),           'days');
      updateDigit(hoursEl,   Math.floor((total % 86400) / 3600),  'hours');
      updateDigit(minutesEl, Math.floor((total % 3600)  / 60),    'minutes');
      updateDigit(secondsEl, total % 60,                           'seconds');
      return true;
    }

    // Run once immediately; only open the interval if date is valid + future
    if (tick()) {
      const interval = setInterval(function () {
        if (!tick()) clearInterval(interval);
      }, 1000);

      // Cleanup if module is removed from DOM
      if (typeof MutationObserver !== 'undefined' && root.parentNode) {
        new MutationObserver(function (mutations, obs) {
          for (const m of mutations) {
            for (const node of m.removedNodes) {
              if (node === root || (node.contains && node.contains(root))) {
                clearInterval(interval);
                obs.disconnect();
                return;
              }
            }
          }
        }).observe(root.parentNode, { childList: true });
      }
    }
  }

})();