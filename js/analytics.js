/**
 * Notícias Mobile Analytics — GA4 stub + Consent Mode aware events
 * Configure: window.NoticiasMobileAnalyticsConfig = { measurementId: 'G-XXXX' }
 */
(function (window, document) {
  'use strict';

  var loaded = false;
  var config = window.NoticiasMobileAnalyticsConfig || { measurementId: 'G-XXXXXXXXXX' };

  function gtag() {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(arguments);
  }

  function hasAnalyticsConsent() {
    return document.documentElement.classList.contains('consent-analytics-allowed');
  }

  function loadGtag() {
    if (loaded || !hasAnalyticsConsent()) return;
    var id = config.measurementId;
    if (!id || id.indexOf('G-XXXX') === 0) {
      // Stub mode: keep dataLayer events only until a real ID is configured
      loaded = true;
      gtag('js', new Date());
      gtag('config', id, { anonymize_ip: true, send_page_view: false });
      trackPageView();
      return;
    }
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    s.setAttribute('data-consent-script', 'analytics');
    document.head.appendChild(s);
    gtag('js', new Date());
    gtag('config', id, { anonymize_ip: true, send_page_view: false });
    loaded = true;
    trackPageView();
  }

  function track(name, params) {
    if (!hasAnalyticsConsent()) return;
    gtag('event', name, params || {});
  }

  function trackPageView() {
    track('page_view', {
      page_title: document.title,
      page_location: window.location.href,
      page_path: window.location.pathname
    });
  }

  function parseParams(el) {
    var raw = el.getAttribute('data-ga-params');
    if (!raw) return {};
    try {
      return JSON.parse(raw);
    } catch (e) {
      return {};
    }
  }

  function bindDelegatedEvents() {
    document.addEventListener('click', function (ev) {
      var ad = ev.target.closest('[data-widget-type="ad-banner"] a, .ne-banner-layout1 a');
      if (ad) {
        var slot = (ad.closest('[data-widget-id]') || {}).getAttribute
          ? ad.closest('[data-widget-id]').getAttribute('data-widget-id')
          : '';
        track('click_ad', { ad_slot_id: slot || 'unknown' });
      }

      var share = ev.target.closest('[data-widget-type="article-share"] a, .blog-social a');
      if (share) {
        var method = share.getAttribute('title') || share.getAttribute('aria-label') || 'share';
        track('share', { method: method, content_type: 'article' });
      }

      var card = ev.target.closest('[data-ga-event]');
      if (card) {
        var name = card.getAttribute('data-ga-event');
        track(name, parseParams(card));
        return;
      }

      var articleLink = ev.target.closest('a[href*="single-news"]');
      if (articleLink && !articleLink.closest('[data-widget-type="ad-banner"]')) {
        track('select_content', {
          content_type: 'article',
          item_id: articleLink.getAttribute('href') || '',
          item_name: (articleLink.textContent || '').trim().slice(0, 120)
        });
      }
    });

    document.addEventListener('submit', function (ev) {
      var form = ev.target;
      if (!(form instanceof HTMLFormElement)) return;
      if (form.id === 'top-search-form' || form.querySelector('input[type="search"], input[name="search"]')) {
        var input = form.querySelector('input[type="search"], input[type="text"], input[name="search"]');
        track('search', { search_term: input ? input.value : '' });
      }
      if (form.closest('[data-widget-type="sidebar-newsletter"]') || form.id === 'newsletter' || /newsletter/i.test(form.id || '')) {
        track('generate_lead', { form_id: form.id || 'newsletter' });
      }
    });
  }

  function maybeViewItem() {
    if (!/single-news/i.test(window.location.pathname + window.location.href)) return;
    var h1 = document.querySelector('h1, .news-details-layout1 h2, .title-medium-dark');
    track('view_item', {
      item_id: window.location.pathname.split('/').pop() || 'article',
      item_name: h1 ? h1.textContent.trim().slice(0, 120) : document.title,
      item_category: 'news'
    });
  }

  function onConsentUpdate(level, consent) {
    if (consent && consent.analytics_storage === 'granted') {
      loadGtag();
      maybeViewItem();
    }
  }

  window.NoticiasMobileAnalytics = {
    track: track,
    trackPageView: trackPageView,
    onConsentUpdate: onConsentUpdate,
    load: loadGtag,
    config: config
  };

  function init() {
    bindDelegatedEvents();
    if (hasAnalyticsConsent()) {
      loadGtag();
      maybeViewItem();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window, document);
