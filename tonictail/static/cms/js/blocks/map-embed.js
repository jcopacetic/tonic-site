/*
 * File: module.js
 * Module: Map Embed
 * Description: Initialises Google Maps instances. Exports window.__tonicInitMap
 *              so the per-instance inline script (in module.html) can call it
 *              after the Maps API resolves. Reads location data from a nested
 *              <script type="application/json"> element to avoid HTML attribute
 *              encoding corruption. Uses AdvancedMarkerElement (replaces the
 *              deprecated google.maps.Marker). Handles pins, radius circles,
 *              polygons, info windows, style presets, bounds fitting, and the
 *              optional location list panel.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  'use strict';

  // ─── Stub callback — installed IMMEDIATELY, before anything else ─────
  //
  // module.js is loaded early by HubSpot as a global external file.
  // The Maps API script tag is injected by the per-instance inline <script>
  // which runs later. However, in the HubSpot previewer (and potentially in
  // some page assembly orders) the API can resolve and call its callback
  // before the inline script has had a chance to define __tonicMapsReady.
  //
  // Fix: define __tonicMapsReady here as a stub that records any premature
  // calls into a pending queue. When the inline script installs the real
  // implementation it drains that queue immediately.
  //
  // The stub must be defined unconditionally — do NOT guard with
  // "if (!window.__tonicMapsReady)" here, because if a previous page-load
  // left a stale value we still want the fresh stub in place.

  var pendingReadyCalls = [];

  window.__tonicMapsReady = function () {
    // API fired before the inline script ran — record the call.
    pendingReadyCalls.push(true);
  };

  // Expose the pending queue so the inline script can drain it.
  window.__tonicMapsReadyQueue = pendingReadyCalls;

  // ─── Map style preset JSON ───────────────────────────────────────

  var STYLES = {
    light: [],

    greyscale: [
      { elementType: 'geometry',           stylers: [{ saturation: -100 }] },
      { elementType: 'labels.text.fill',   stylers: [{ color: '#555555' }] },
      { elementType: 'labels.text.stroke', stylers: [{ color: '#f5f5f5' }] },
      { featureType: 'road',    elementType: 'geometry',        stylers: [{ color: '#ffffff' }] },
      { featureType: 'road',    elementType: 'geometry.stroke', stylers: [{ color: '#e0e0e0' }] },
      { featureType: 'water',   elementType: 'geometry',        stylers: [{ color: '#c9d6e3' }] },
      { featureType: 'poi',     elementType: 'geometry',        stylers: [{ color: '#e8e8e8' }] },
      { featureType: 'poi',     elementType: 'labels',          stylers: [{ visibility: 'off' }] },
      { featureType: 'transit',                                  stylers: [{ visibility: 'off' }] }
    ],

    dark: [
      { elementType: 'geometry',           stylers: [{ color: '#1a1a2e' }] },
      { elementType: 'labels.text.fill',   stylers: [{ color: '#8a9bb0' }] },
      { elementType: 'labels.text.stroke', stylers: [{ color: '#1a1a2e' }] },
      { featureType: 'road',         elementType: 'geometry',         stylers: [{ color: '#2c2c54' }] },
      { featureType: 'road',         elementType: 'geometry.stroke',  stylers: [{ color: '#212148' }] },
      { featureType: 'road',         elementType: 'labels.text.fill', stylers: [{ color: '#9ca5b3' }] },
      { featureType: 'road.highway', elementType: 'geometry',         stylers: [{ color: '#3a3a6e' }] },
      { featureType: 'water',        elementType: 'geometry',         stylers: [{ color: '#0d1b2e' }] },
      { featureType: 'water',        elementType: 'labels.text.fill', stylers: [{ color: '#3d5a7a' }] },
      { featureType: 'poi',          elementType: 'geometry',         stylers: [{ color: '#252540' }] },
      { featureType: 'poi',          elementType: 'labels',           stylers: [{ visibility: 'off' }] },
      { featureType: 'transit',                                        stylers: [{ visibility: 'off' }] },
      { featureType: 'administrative', elementType: 'geometry.stroke', stylers: [{ color: '#3a3a6e' }] }
    ]
  };

  var MILES_TO_M = 1609.344;
  var KM_TO_M    = 1000;

  // ─── Map ID constant ─────────────────────────────────────────────
  // AdvancedMarkerElement requires a Map ID. We use the generic
  // "DEMO_MAP_ID" which works for any key without additional setup.
  // For production, clients can create a named Map ID in Google Cloud
  // Console and set it via a future field.
  var MAP_ID = 'DEMO_MAP_ID';

  // ─── Public init — called per instance when API is ready ─────────

  window.__tonicInitMap = function (instanceId) {
    var root = document.getElementById(instanceId);
    if (!root) return;

    var canvas = root.querySelector('.module-map-embed__canvas');
    if (!canvas) { showError(root); return; }

    // Read location JSON from the nested <script type="application/json">
    var dataEl = canvas.querySelector('.module-map-embed__location-data');
    if (!dataEl) { showError(root); return; }

    var locations;
    try {
      locations = JSON.parse(dataEl.textContent);
    } catch (e) {
      console.error('[Map Embed] JSON parse error for "' + instanceId + '":', e);
      showError(root);
      return;
    }

    // Drop unconfigured locations still at the 0,0 default
    locations = locations.filter(function (loc) {
      return !(loc.lat === 0 && loc.lng === 0);
    });

    if (!locations.length) { showError(root); return; }

    var styleKey = canvas.dataset.style || 'light';
    var maxZoom  = parseInt(canvas.dataset.zoom, 10) || 11;
    var showUI   = canvas.dataset.ui !== 'false';

    canvas.classList.remove('module-map-embed__canvas--loading');

    // ── Map ──
    var mapOptions = {
      zoom:              maxZoom,
      center:            { lat: locations[0].lat, lng: locations[0].lng },
      mapId:             MAP_ID,
      disableDefaultUI:  !showUI,
      zoomControl:       showUI,
      streetViewControl: showUI,
      mapTypeControl:    false,
      fullscreenControl: showUI,
      mapTypeId:         styleKey === 'satellite'
                           ? google.maps.MapTypeId.HYBRID
                           : google.maps.MapTypeId.ROADMAP
    };

    // Styles array is not supported with mapId on the new renderer.
    // For light/greyscale/dark we apply it; satellite ignores styles anyway.
    if (styleKey !== 'satellite' && STYLES[styleKey] && STYLES[styleKey].length) {
      mapOptions.styles = STYLES[styleKey];
    }

    var map         = new google.maps.Map(canvas, mapOptions);
    var bounds      = new google.maps.LatLngBounds();
    var markers     = [];
    var infoWindows = [];

    function closeAllInfoWindows() {
      infoWindows.forEach(function (iw) { iw.close(); });
      root.querySelectorAll('.module-map-embed__location-btn').forEach(function (btn) {
        btn.classList.remove('module-map-embed__location-btn--active');
      });
    }

    function buildInfoWindowContent(loc) {
      var html = '<div class="module-map-embed__iw">';
      if (loc.label)   html += '<p class="module-map-embed__iw-name">'    + escHtml(loc.label)   + '</p>';
      if (loc.address) html += '<p class="module-map-embed__iw-address">' + escHtml(loc.address) + '</p>';
      if (loc.extra)   html += '<p class="module-map-embed__iw-extra">'   + escHtml(loc.extra)   + '</p>';
      html += '</div>';
      return html;
    }

    // ── Plot locations ──
    locations.forEach(function (loc, i) {
      var position  = { lat: loc.lat, lng: loc.lng };
      var latLng    = new google.maps.LatLng(loc.lat, loc.lng);
      bounds.extend(latLng);

      // ── AdvancedMarkerElement with a custom coloured pin ──
      var pinEl = new google.maps.marker.PinElement({
        background:  loc.color || '#0057B8',
        borderColor: '#ffffff',
        glyphColor:  '#ffffff',
        scale:       1.1
      });

      var marker = new google.maps.marker.AdvancedMarkerElement({
        position: latLng,
        map:      map,
        title:    loc.label || '',
        content:  pinEl.element
      });
      markers.push(marker);

      // Info window
      var iw = new google.maps.InfoWindow({
        content: buildInfoWindowContent(loc)
      });
      infoWindows.push(iw);

      marker.addListener('click', function () {
        closeAllInfoWindows();
        iw.open({ anchor: marker, map: map });
        activateListItem(root, i);
      });

      // Radius circle
      if (loc.mode === 'radius' && loc.radius > 0) {
        var radiusM = loc.unit === 'km'
          ? loc.radius * KM_TO_M
          : loc.radius * MILES_TO_M;

        var circle = new google.maps.Circle({
          map:           map,
          center:        position,
          radius:        radiusM,
          fillColor:     loc.color || '#0057B8',
          fillOpacity:   0.12,
          strokeColor:   loc.color || '#0057B8',
          strokeOpacity: 0.5,
          strokeWeight:  1.5,
          clickable:     false
        });

        var cb = circle.getBounds();
        if (cb) {
          bounds.extend(cb.getNorthEast());
          bounds.extend(cb.getSouthWest());
        }
      }

      // Polygon
      if (loc.mode === 'polygon' && loc.polygon) {
        var path = parsePolygonCoords(loc.polygon);
        if (path.length >= 3) {
          new google.maps.Polygon({
            paths:         path,
            map:           map,
            fillColor:     loc.color || '#0057B8',
            fillOpacity:   0.14,
            strokeColor:   loc.color || '#0057B8',
            strokeOpacity: 0.6,
            strokeWeight:  2,
            clickable:     false
          });
          path.forEach(function (pt) { bounds.extend(pt); });
        }
      }
    });

    // ── Fit bounds ──
    if (locations.length === 1) {
      map.setCenter({ lat: locations[0].lat, lng: locations[0].lng });
      map.setZoom(maxZoom);
    } else {
      map.fitBounds(bounds);
      google.maps.event.addListenerOnce(map, 'idle', function () {
        if (map.getZoom() > maxZoom) map.setZoom(maxZoom);
      });
    }

    // ── Location list ──
    root.querySelectorAll('.module-map-embed__location-btn').forEach(function (btn) {
      var li  = btn.closest('[data-list-index]');
      var idx = li ? parseInt(li.dataset.listIndex, 10) : NaN;
      btn.addEventListener('click', function () {
        if (isNaN(idx) || !markers[idx]) return;
        closeAllInfoWindows();
        map.panTo(markers[idx].position);
        infoWindows[idx].open({ anchor: markers[idx], map: map });
        btn.classList.add('module-map-embed__location-btn--active');
      });
    });

    map.addListener('click', function () { closeAllInfoWindows(); });
  };

  // ─── Helpers ─────────────────────────────────────────────────────

  function activateListItem(root, index) {
    root.querySelectorAll('[data-list-index]').forEach(function (item) {
      var btn = item.querySelector('.module-map-embed__location-btn');
      if (!btn) return;
      btn.classList.toggle(
        'module-map-embed__location-btn--active',
        parseInt(item.dataset.listIndex, 10) === index
      );
    });
  }

  function parsePolygonCoords(raw) {
    var path = [];
    raw.split(/\n/).forEach(function (line) {
      line = line.trim();
      if (!line) return;
      var parts = line.split(',');
      if (parts.length < 2) return;
      var lat = parseFloat(parts[0]);
      var lng = parseFloat(parts[1]);
      if (!isNaN(lat) && !isNaN(lng)) path.push({ lat: lat, lng: lng });
    });
    return path;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g,  '&amp;')
      .replace(/</g,  '&lt;')
      .replace(/>/g,  '&gt;')
      .replace(/"/g,  '&quot;')
      .replace(/'/g,  '&#39;');
  }

  function showError(root) {
    var msg    = root && root.querySelector('.module-map-embed__no-key-msg');
    var canvas = root && root.querySelector('.module-map-embed__canvas');
    if (msg)    msg.hidden    = false;
    if (canvas) canvas.hidden = true;
  }

  // Shimmer all canvases immediately while the API loads
  document.querySelectorAll('.module-map-embed__canvas').forEach(function (c) {
    c.classList.add('module-map-embed__canvas--loading');
  });

}());