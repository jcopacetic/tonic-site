/*
 * File: module.js
 * Description: Handles thumbnail click-to-play behavior for YouTube and Vimeo embeds. When a custom thumbnail is set, clicking it replaces the thumbnail with the actual iframe embed.
 * Author: Jonathan Sumner | jonathan@khaoticdigital.com
 */

(function () {
  const root = document.getElementById('/* [hubl-value] */');
  if (!root) return;

  const thumbnails = root.querySelectorAll('.video-embed__thumbnail-play');
  if (!thumbnails.length) return;

  thumbnails.forEach(function (thumb) {
    function activatePlayer() {
      const platform = thumb.dataset.platform;
      const videoId = thumb.dataset.videoId;
      if (!platform || !videoId) return;

      let src = '';
      if (platform === 'youtube') {
        src = 'https://www.youtube-nocookie.com/embed/' + videoId + '?autoplay=1&rel=0';
      } else if (platform === 'vimeo') {
        src = 'https://player.vimeo.com/video/' + videoId + '?autoplay=1';
      }

      if (!src) return;

      const iframe = document.createElement('iframe');
      iframe.setAttribute('src', src);
      iframe.setAttribute('frameborder', '0');
      iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
      iframe.setAttribute('allowfullscreen', '');
      iframe.setAttribute('title', thumb.getAttribute('aria-label') || 'Video');
      iframe.className = 'video-embed__iframe';

      thumb.parentNode.replaceChild(iframe, thumb);
      iframe.focus();
    }

    thumb.addEventListener('click', activatePlayer);
    thumb.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activatePlayer();
      }
    });
  });
})();