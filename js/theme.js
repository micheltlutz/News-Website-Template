/**
 * Notícias Mobile — Light / Dark theme controller
 * Persists choice in localStorage (`noticiasmobile-theme`).
 * System preference applies only when no saved choice exists.
 * Also injects/syncs toggle into offcanvas (header already exposes one on mobile).
 */
(function (window, document) {
  'use strict';

  var KEY = 'noticiasmobile-theme';
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  function systemTheme() {
    return mq.matches ? 'dark' : 'light';
  }

  function getSaved() {
    try {
      var saved = localStorage.getItem(KEY);
      if (saved === 'light' || saved === 'dark') {
        return saved;
      }
    } catch (e) {
      /* private mode / blocked storage */
    }
    return null;
  }

  function resolveTheme() {
    return getSaved() || systemTheme();
  }

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') || resolveTheme();
  }

  function syncToggle(theme) {
    var buttons = document.querySelectorAll('.theme-toggle');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      btn.setAttribute(
        'title',
        theme === 'dark' ? 'Mudar para tema claro' : 'Mudar para tema escuro'
      );
    }
  }

  function setTheme(theme, persist) {
    if (theme !== 'light' && theme !== 'dark') {
      return;
    }
    document.documentElement.setAttribute('data-theme', theme);
    if (persist) {
      try {
        localStorage.setItem(KEY, theme);
      } catch (e) {
        /* ignore */
      }
    }
    syncToggle(theme);
  }

  function toggleTheme() {
    setTheme(currentTheme() === 'dark' ? 'light' : 'dark', true);
  }

  function onSystemChange() {
    if (getSaved()) {
      return;
    }
    setTheme(systemTheme(), false);
  }

  function createToggleButton(extraClass) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = extraClass ? 'theme-toggle ' + extraClass : 'theme-toggle';
    btn.setAttribute('aria-label', 'Alternar tema claro/escuro');
    btn.setAttribute('title', 'Tema');
    btn.setAttribute('aria-pressed', 'false');

    var moon = document.createElement('i');
    moon.className = 'fa fa-moon-o theme-icon-dark';
    moon.setAttribute('aria-hidden', 'true');

    var sun = document.createElement('i');
    sun.className = 'fa fa-sun-o theme-icon-light';
    sun.setAttribute('aria-hidden', 'true');

    btn.appendChild(moon);
    btn.appendChild(sun);
    return btn;
  }

  /** Offcanvas receives a theme toggle when mounted (header already has one on mobile). */
  function ensureMobileToggles() {
    var changed = false;

    var offcanvas = document.getElementById('offcanvas-body-wrapper');
    if (offcanvas && !offcanvas.querySelector('.theme-toggle')) {
      var slot = document.createElement('div');
      slot.className = 'offcanvas-theme-bar';

      var label = document.createElement('span');
      label.className = 'offcanvas-theme-label';
      label.textContent = 'Tema';

      slot.appendChild(label);
      slot.appendChild(createToggleButton());

      var close = document.getElementById('offcanvas-nav-close');
      if (close && close.parentNode === offcanvas) {
        offcanvas.insertBefore(slot, close.nextSibling);
      } else if (offcanvas.firstChild) {
        offcanvas.insertBefore(slot, offcanvas.firstChild);
      } else {
        offcanvas.appendChild(slot);
      }
      changed = true;
    }

    if (changed) {
      syncToggle(currentTheme());
    }
  }

  function bind() {
    document.addEventListener('click', function (event) {
      var target = event.target;
      if (!target) {
        return;
      }
      var btn = target.closest ? target.closest('.theme-toggle') : null;
      if (!btn && target.classList && target.classList.contains('theme-toggle')) {
        btn = target;
      }
      if (
        !btn &&
        target.parentElement &&
        target.parentElement.classList &&
        target.parentElement.classList.contains('theme-toggle')
      ) {
        btn = target.parentElement;
      }
      if (btn) {
        event.preventDefault();
        toggleTheme();
      }
    });

    if (typeof mq.addEventListener === 'function') {
      mq.addEventListener('change', onSystemChange);
    } else if (typeof mq.addListener === 'function') {
      mq.addListener(onSystemChange);
    }

    ensureMobileToggles();
    syncToggle(currentTheme());

    var tries = 0;
    var timer = window.setInterval(function () {
      ensureMobileToggles();
      tries += 1;
      if (tries >= 20 || document.querySelector('#offcanvas-body-wrapper .theme-toggle')) {
        window.clearInterval(timer);
      }
    }, 150);

    if (typeof MutationObserver === 'function') {
      var obs = new MutationObserver(function () {
        ensureMobileToggles();
      });
      obs.observe(document.body, { childList: true, subtree: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }

  window.NoticiasMobileTheme = {
    KEY: KEY,
    get: resolveTheme,
    set: function (theme) {
      setTheme(theme, true);
    },
    clear: function () {
      try {
        localStorage.removeItem(KEY);
      } catch (e) {
        /* ignore */
      }
      setTheme(systemTheme(), false);
    },
    toggle: toggleTheme,
    ensureMobileToggles: ensureMobileToggles
  };
})(window, document);
