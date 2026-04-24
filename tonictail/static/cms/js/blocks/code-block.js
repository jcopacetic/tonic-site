/*
 * File: module.js
 * Description: Re-triggers Prism highlighting after HubSpot's editor loads module content dynamically. Not needed on the live front end — Prism runs automatically on DOMContentLoaded.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  // In the HubSpot page editor, modules are injected after initial load.
  // Prism's autoloader may have already run before the module was present.
  // This re-highlights just the code blocks within this module instance.
  const moduleEl = document.currentScript
    ? document.currentScript.closest('[id]')
    : null;

  if (!moduleEl) return;

  if (window.Prism) {
    Prism.highlightAllUnder(moduleEl);
  }
})();