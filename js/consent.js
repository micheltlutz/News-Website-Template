/**
 * Notícias Mobile CMP — Consent Mode v2 (2026)
 * Choices: all | basic | denied
 * Storage key: noticiasmobile-consent
 */
(function (window, document) {
  'use strict';

  var STORAGE_KEY = 'noticiasmobile-consent';
  var POLICY_VERSION = '2026-07-14';
  var BANNER_ID = 'noticiasmobile-cmp-banner';
  var MODAL_ID = 'noticiasmobile-cmp-modal';

  function gtag() {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(arguments);
  }

  function defaultDenied() {
    gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied',
      functionality_storage: 'granted',
      personalization_storage: 'denied',
      security_storage: 'granted',
      wait_for_update: 500
    });
  }

  function levelsToConsent(level) {
    if (level === 'all') {
      return {
        ad_storage: 'granted',
        ad_user_data: 'granted',
        ad_personalization: 'granted',
        analytics_storage: 'granted',
        functionality_storage: 'granted',
        personalization_storage: 'granted',
        security_storage: 'granted'
      };
    }
    if (level === 'basic') {
      return {
        ad_storage: 'denied',
        ad_user_data: 'denied',
        ad_personalization: 'denied',
        analytics_storage: 'denied',
        functionality_storage: 'granted',
        personalization_storage: 'granted',
        security_storage: 'granted'
      };
    }
    return {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'denied',
      functionality_storage: 'granted',
      personalization_storage: 'denied',
      security_storage: 'granted'
    };
  }

  function readConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || data.policyVersion !== POLICY_VERSION) return null;
      return data;
    } catch (e) {
      return null;
    }
  }

  function writeConsent(level, categories) {
    var payload = {
      level: level,
      policyVersion: POLICY_VERSION,
      timestamp: new Date().toISOString(),
      categories: categories || {
        essential: true,
        analytics: level === 'all',
        advertising: level === 'all',
        personalization: level === 'all' || level === 'basic'
      }
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch (e) { /* ignore */ }
    return payload;
  }

  function applyConsent(level) {
    var consent = levelsToConsent(level);
    gtag('consent', 'update', consent);
    document.documentElement.setAttribute('data-consent', level);
    document.documentElement.classList.toggle('consent-ads-allowed', consent.ad_storage === 'granted');
    document.documentElement.classList.toggle('consent-analytics-allowed', consent.analytics_storage === 'granted');

    if (window.NoticiasMobileAnalytics && typeof window.NoticiasMobileAnalytics.onConsentUpdate === 'function') {
      window.NoticiasMobileAnalytics.onConsentUpdate(level, consent);
    }

    gtag('event', 'cookie_consent_update', {
      consent_level: level === 'denied' ? 'denied' : level,
      event_category: 'consent'
    });
  }

  function hideBanner() {
    var banner = document.getElementById(BANNER_ID);
    if (banner) {
      banner.hidden = true;
      banner.setAttribute('aria-hidden', 'true');
    }
  }

  function showBanner() {
    var banner = document.getElementById(BANNER_ID);
    if (banner) {
      banner.hidden = false;
      banner.setAttribute('aria-hidden', 'false');
      var firstBtn = banner.querySelector('button');
      if (firstBtn) firstBtn.focus();
    }
  }


  var lastFocus = null;
  var trapHandler = null;

  function getFocusable(root) {
    if (!root) return [];
    return Array.prototype.slice.call(root.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter(function (el) {
      return el.offsetParent !== null || el === document.activeElement;
    });
  }

  function releaseFocusTrap() {
    if (trapHandler) {
      document.removeEventListener('keydown', trapHandler, true);
      trapHandler = null;
    }
    if (lastFocus && typeof lastFocus.focus === 'function') {
      try { lastFocus.focus(); } catch (e) {}
    }
    lastFocus = null;
  }

  function trapFocus(container) {
    releaseFocusTrap();
    lastFocus = document.activeElement;
    trapHandler = function (ev) {
      if (ev.key !== 'Tab' || !container || container.hidden) return;
      var nodes = getFocusable(container);
      if (!nodes.length) return;
      var first = nodes[0];
      var last = nodes[nodes.length - 1];
      if (ev.shiftKey && document.activeElement === first) {
        ev.preventDefault();
        last.focus();
      } else if (!ev.shiftKey && document.activeElement === last) {
        ev.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', trapHandler, true);
  }

  function openModal() {
    var modal = document.getElementById(MODAL_ID);
    if (!modal) return;
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    trapFocus(modal);
    var saved = readConsent();
    if (saved && saved.categories) {
      var a = modal.querySelector('[name="cmp-analytics"]');
      var d = modal.querySelector('[name="cmp-advertising"]');
      var p = modal.querySelector('[name="cmp-personalization"]');
      if (a) a.checked = !!saved.categories.analytics;
      if (d) d.checked = !!saved.categories.advertising;
      if (p) p.checked = !!saved.categories.personalization;
    }
    var closeBtn = modal.querySelector('.ne-cmp-close');
    if (closeBtn) closeBtn.focus();
  }

  function closeModal() {
    var modal = document.getElementById(MODAL_ID);
    if (!modal) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    releaseFocusTrap();
  }

  function acceptAll() {
    writeConsent('all');
    applyConsent('all');
    hideBanner();
    closeModal();
  }

  function acceptBasic() {
    writeConsent('basic');
    applyConsent('basic');
    hideBanner();
    closeModal();
  }

  function denyAll() {
    writeConsent('denied');
    applyConsent('denied');
    hideBanner();
    closeModal();
  }

  function savePreferences() {
    var modal = document.getElementById(MODAL_ID);
    if (!modal) return;
    var analyticsEl = modal.querySelector('[name="cmp-analytics"]');
    var advertisingEl = modal.querySelector('[name="cmp-advertising"]');
    var personalizationEl = modal.querySelector('[name="cmp-personalization"]');
    var analytics = !!(analyticsEl && analyticsEl.checked);
    var advertising = !!(advertisingEl && advertisingEl.checked);
    var personalization = !!(personalizationEl && personalizationEl.checked);

    var level = 'denied';
    if (analytics && advertising) level = 'all';
    else if (analytics && !advertising) level = 'all';
    else if (!analytics && !advertising && personalization) level = 'basic';
    else if (!analytics && !advertising) level = 'denied';

    var categories = {
      essential: true,
      analytics: analytics,
      advertising: advertising,
      personalization: personalization
    };
    writeConsent(level, categories);

    var consent = {
      ad_storage: advertising ? 'granted' : 'denied',
      ad_user_data: advertising ? 'granted' : 'denied',
      ad_personalization: advertising ? 'granted' : 'denied',
      analytics_storage: analytics ? 'granted' : 'denied',
      functionality_storage: 'granted',
      personalization_storage: personalization ? 'granted' : 'denied',
      security_storage: 'granted'
    };
    gtag('consent', 'update', consent);
    document.documentElement.setAttribute('data-consent', level);
    document.documentElement.classList.toggle('consent-ads-allowed', advertising);
    document.documentElement.classList.toggle('consent-analytics-allowed', analytics);
    if (window.NoticiasMobileAnalytics && typeof window.NoticiasMobileAnalytics.onConsentUpdate === 'function') {
      window.NoticiasMobileAnalytics.onConsentUpdate(level, consent);
    }
    gtag('event', 'cookie_consent_update', { consent_level: level, event_category: 'consent' });
    hideBanner();
    closeModal();
  }

  function bindUI() {
    document.addEventListener('click', function (ev) {
      var t = ev.target.closest('[data-cmp-action]');
      if (!t) return;
      var action = t.getAttribute('data-cmp-action');
      if (action === 'accept-all') acceptAll();
      else if (action === 'accept-basic') acceptBasic();
      else if (action === 'deny') denyAll();
      else if (action === 'open-preferences') openModal();
      else if (action === 'close-preferences') closeModal();
      else if (action === 'save-preferences') savePreferences();
    });

    document.addEventListener('keydown', function (ev) {
      if (ev.key !== 'Escape') return;
      var modal = document.getElementById(MODAL_ID);
      if (modal && !modal.hidden) closeModal();
    });
  }

  function init() {
    defaultDenied();
    bindUI();
    var saved = readConsent();
    if (saved && saved.level) {
      applyConsent(saved.level);
      if (saved.categories) {
        var consent = levelsToConsent(saved.level);
        consent.analytics_storage = saved.categories.analytics ? 'granted' : 'denied';
        consent.ad_storage = saved.categories.advertising ? 'granted' : 'denied';
        consent.ad_user_data = saved.categories.advertising ? 'granted' : 'denied';
        consent.ad_personalization = saved.categories.advertising ? 'granted' : 'denied';
        consent.personalization_storage = saved.categories.personalization ? 'granted' : 'denied';
        gtag('consent', 'update', consent);
        document.documentElement.classList.toggle('consent-ads-allowed', !!saved.categories.advertising);
        document.documentElement.classList.toggle('consent-analytics-allowed', !!saved.categories.analytics);
      }
      hideBanner();
    } else {
      showBanner();
    }
  }

  window.NoticiasMobileConsent = {
    acceptAll: acceptAll,
    acceptBasic: acceptBasic,
    denyAll: denyAll,
    openPreferences: openModal,
    get: readConsent,
    POLICY_VERSION: POLICY_VERSION
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window, document);
