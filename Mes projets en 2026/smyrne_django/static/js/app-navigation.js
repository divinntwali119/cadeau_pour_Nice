/* Navigation interne progressive : les routes Django et formulaires restent la source de vérité. */
(function() {
  'use strict';

  const HISTORY_KEY = '__smyrneAppHistory';
  const POSITION_KEY = 'smyrneAppPositions';
  const HOME_FEED_SNAPSHOT_KEY = 'smyrneHomeFeedSnapshot';
  const tabRoutes = {
    home: /^\/$/,
    sermons: /^\/predications(?:\/|$)/,
    live: /^\/live(?:\/|$)/,
    events: /^\/(?:cultes|evenements|actualites)(?:\/|$)/,
    space: /^\/(?:profil|connexion|inscription)(?:\/|$)/
  };
  const main = document.getElementById('appMain');
  const menuButton = document.getElementById('hamburgerBtn');
  const menu = document.getElementById('appMenuDrawer');
  const scrim = document.getElementById('appMenuScrim');
  const tabbar = document.getElementById('appTabbar');
  const subtabs = document.getElementById('appEventSubtabs');

  if (!main || !tabbar || !menu || !scrim) return;

  try {
    window.history.scrollRestoration = 'manual';
  } catch (error) {
    // Certains navigateurs ne permettent pas de désactiver la restauration native.
  }

  window.__smyrneAppNavigationReady = true;

  try {
    const savedTheme = window.localStorage.getItem('theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      document.documentElement.setAttribute('data-theme', savedTheme);
    }
  } catch (error) {
    // Le mode privé peut désactiver localStorage.
  }

  let currentUrl = window.location.href;
  let historyState = window.history.state || {};
  let menuOpen = false;
  let menuStartX = null;

  if (!historyState[HISTORY_KEY]) {
    historyState = Object.assign({}, historyState, {
      [HISTORY_KEY]: { tab: tabForPath(window.location.pathname), scrollY: window.scrollY }
    });
    window.history.replaceState(historyState, '', window.location.href);
  }

  function normalizePath(path) {
    return path.length > 1 && !path.endsWith('/') && !path.includes('.') ? path + '/' : path;
  }

  function tabForPath(path) {
    const normalized = normalizePath(path);
    for (const [tab, pattern] of Object.entries(tabRoutes)) {
      if (pattern.test(normalized)) return tab;
    }
    return '';
  }

  function isAppPage(url) {
    return url.origin === window.location.origin &&
      !/^\/(?:admin|ckeditor|static|media|sw\.js|manifest\.json|offline|deconnexion|robots\.txt|sitemap\.xml)(?:\/|$)/.test(url.pathname);
  }

  function pageHasShell(doc) {
    return Boolean(doc.querySelector('[data-app-shell-style]') && doc.getElementById('appMain'));
  }

  function readSessionMap(key) {
    try {
      return JSON.parse(window.sessionStorage.getItem(key) || '{}');
    } catch (error) {
      return {};
    }
  }

  function writeSessionMap(key, value) {
    try {
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      // Private browsing modes may disable session storage.
    }
  }

  function saveHomeFeedSnapshot() {
    if (window.location.pathname !== '/') return;
    const feed = main.querySelector('[data-home-feed]');
    const list = feed && feed.querySelector('[data-feed-items]');
    if (!feed || !list) return;
    try {
      window.sessionStorage.setItem(HOME_FEED_SNAPSHOT_KEY, JSON.stringify({
        userKey: feed.dataset.userKey,
        itemsHtml: list.innerHTML
      }));
    } catch (error) {
      // Si le stockage de session est plein, le fil sera rechargé normalement.
    }
  }

  function restoreHomeFeedSnapshot(doc, url) {
    if (url.pathname !== '/') return;
    const incomingFeed = doc.querySelector('[data-home-feed]');
    const incomingList = incomingFeed && incomingFeed.querySelector('[data-feed-items]');
    if (!incomingFeed || !incomingList) return;
    try {
      const snapshot = JSON.parse(window.sessionStorage.getItem(HOME_FEED_SNAPSHOT_KEY) || 'null');
        if (!snapshot || snapshot.userKey !== incomingFeed.dataset.userKey ||
          typeof snapshot.itemsHtml !== 'string') return;
      incomingList.innerHTML = snapshot.itemsHtml;
    } catch (error) {
      // Un snapshot invalide n'empêche pas le chargement normal de l'accueil.
    }
  }

  function routeKey(url) {
    return url.pathname + url.search;
  }

  function subtabForPath(path) {
    if (path.startsWith('/cultes/')) return 'cultes';
    if (path.startsWith('/evenements/')) return 'evenements';
    if (path.startsWith('/actualites/')) return 'actualites';
    return '';
  }

  function saveCurrentPosition() {
    const currentPage = new URL(window.location.href);
    const state = Object.assign({}, window.history.state || {});
    state[HISTORY_KEY] = Object.assign({}, state[HISTORY_KEY] || {}, {
      tab: tabForPath(currentPage.pathname) || (state[HISTORY_KEY] && state[HISTORY_KEY].tab) || '',
      scrollY: window.scrollY
    });
    window.history.replaceState(state, '', window.location.href);

    const positions = readSessionMap(POSITION_KEY);
    positions[routeKey(currentPage)] = window.scrollY;
    writeSessionMap(POSITION_KEY, positions);
  }

  function renderNavigationState(url, state, options) {
    const path = normalizePath(url.pathname);
    const pageTab = tabForPath(path);
    const stateTab = state && state[HISTORY_KEY] ? state[HISTORY_KEY].tab : '';
    const activeTab = pageTab || stateTab;

    if (menuButton) menuButton.hidden = false;
    tabbar.querySelectorAll('[data-app-tab]').forEach(function(tab) {
      const active = tab.dataset.appTab === activeTab;
      if (active) tab.setAttribute('aria-current', 'page');
      else tab.removeAttribute('aria-current');
    });

    if (subtabs) {
      const activeSubtab = subtabForPath(path);
      const isEventsSection = path.startsWith('/evenements/');
      subtabs.hidden = !isEventsSection;
      subtabs.querySelectorAll('[data-app-subtab]').forEach(function(link) {
        const active = link.dataset.appSubtab === activeSubtab;
        if (active) link.setAttribute('aria-current', 'page');
        else link.removeAttribute('aria-current');
      });
    }

    if (options && options.scrollToTop) {
      window.scrollTo({ top: 0, behavior: options.behavior || 'instant' });
    } else if (state && state[HISTORY_KEY] && Number.isFinite(state[HISTORY_KEY].scrollY)) {
      const savedScrollY = state[HISTORY_KEY].scrollY;
      requestAnimationFrame(function() {
        requestAnimationFrame(function() {
          window.scrollTo({ top: savedScrollY, behavior: 'instant' });
        });
      });
    } else {
      const positions = readSessionMap(POSITION_KEY);
      const savedPosition = positions[routeKey(url)];
      if (Number.isFinite(savedPosition)) {
        requestAnimationFrame(function() {
          requestAnimationFrame(function() {
            window.scrollTo({ top: savedPosition, behavior: 'instant' });
          });
        });
      }
    }
  }

  function syncShellStyles(doc) {
    document.head.querySelectorAll('[data-app-route-style]').forEach(function(style) { style.remove(); });
    let insideRouteStyles = false;

    Array.from(doc.head.childNodes).forEach(function(node) {
      if (node.nodeType === Node.COMMENT_NODE && node.nodeValue.includes('APP_ROUTE_STYLES_START')) {
        insideRouteStyles = true;
        return;
      }
      if (node.nodeType === Node.COMMENT_NODE && node.nodeValue.includes('APP_ROUTE_STYLES_END')) {
        insideRouteStyles = false;
        return;
      }
      if (!insideRouteStyles || node.nodeType !== Node.ELEMENT_NODE) return;
      if (node.tagName !== 'STYLE' && !(node.tagName === 'LINK' && node.rel === 'stylesheet')) return;

      const copy = node.cloneNode(true);
      copy.dataset.appRouteStyle = 'true';
      document.head.insertBefore(copy, document.querySelector('[data-app-shell-style]'));
    });
  }

  function replaceRouteScripts(doc) {
    const currentScripts = Array.from(document.querySelectorAll('script[data-route-script]'));
    currentScripts.forEach(function(script) { script.remove(); });

    const scripts = Array.from(doc.querySelectorAll('#appMain script, script[data-route-script]'));
    scripts.forEach(function(oldScript) {
      const script = document.createElement('script');
      Array.from(oldScript.attributes).forEach(function(attribute) {
        script.setAttribute(attribute.name, attribute.value);
      });
      if (oldScript.src) {
        script.src = oldScript.src;
        script.dataset.routeScript = 'true';
      } else {
        script.textContent = oldScript.textContent;
        script.dataset.routeScript = 'true';
      }
      document.body.appendChild(script);
    });
  }

  function prepareImages(container) {
    container.querySelectorAll('img').forEach(function(image) {
      if (!image.hasAttribute('loading')) image.loading = 'lazy';
      if (!image.hasAttribute('decoding')) image.decoding = 'async';
    });
    container.querySelectorAll('.fade-in').forEach(function(element) {
      element.classList.add('appear');
    });
  }

  function replaceMainContent(doc, targetUrl) {
    const nextMain = doc.getElementById('appMain');
    if (!nextMain) return false;

    if (window.__smyrneHomeWidgetsCleanup) window.__smyrneHomeWidgetsCleanup();
    main.classList.remove('app-screen-enter', 'app-screen-detail-enter');
    main.innerHTML = nextMain.innerHTML;
    syncShellStyles(doc);
    replaceRouteScripts(doc);
    prepareImages(main);
    if (window.__smyrneInitHomeWidgets) window.__smyrneInitHomeWidgets();

    const nextTitle = doc.querySelector('title');
    if (nextTitle) document.title = nextTitle.textContent;

    if (targetUrl.hash) {
      requestAnimationFrame(function() {
        const target = document.getElementById(decodeURIComponent(targetUrl.hash.slice(1)));
        if (target) target.scrollIntoView({ behavior: 'instant', block: 'start' });
      });
    }

    const animationClass = /^\/(?:predications|evenements|actualites)\/[^/]+\/$/.test(targetUrl.pathname)
      ? 'app-screen-detail-enter'
      : 'app-screen-enter';
    main.classList.add(animationClass);
    window.setTimeout(function() { main.classList.remove(animationClass); }, 240);
    return true;
  }

  async function navigate(url, options) {
    const targetUrl = url instanceof URL ? url : new URL(url, window.location.href);
    const settings = Object.assign({ push: true, scrollToTop: true }, options || {});

    if (!isAppPage(targetUrl) || targetUrl.origin !== window.location.origin ||
        targetUrl.pathname === '/connexion/' && settings.formNavigation) {
      window.location.assign(targetUrl.href);
      return;
    }

    if (targetUrl.href === currentUrl) {
      if (settings.scrollToTop) window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    closeMenu(true);
    if (!settings.fromPopstate) {
      saveCurrentPosition();
      saveHomeFeedSnapshot();
    }
    main.setAttribute('aria-busy', 'true');

    try {
      const response = await fetch(targetUrl.href, {
        method: 'GET',
        credentials: 'same-origin',
        headers: { 'X-Requested-With': 'Smyrne-App-Navigation' }
      });
      if (!response.ok) throw new Error('Réponse HTTP ' + response.status);

      if (response.redirected) {
        const finalUrl = new URL(response.url, targetUrl.href);
        if (finalUrl.origin !== targetUrl.origin ||
            finalUrl.pathname !== targetUrl.pathname ||
            finalUrl.search !== targetUrl.search) {
          window.location.assign(finalUrl.href);
          return;
        }
      }

      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      restoreHomeFeedSnapshot(doc, targetUrl);
      if (!pageHasShell(doc) || !replaceMainContent(doc, targetUrl)) {
        throw new Error('Gabarit d’application absent');
      }
      updateMessages(doc);

      const nextTab = tabForPath(targetUrl.pathname) ||
        (window.history.state && window.history.state[HISTORY_KEY] && window.history.state[HISTORY_KEY].tab) || '';
      const nextState = Object.assign({}, window.history.state || {});
      delete nextState.smyrneMenu;
      const savedPositions = readSessionMap(POSITION_KEY);
      const restoredScrollY = settings.fromPopstate && window.history.state && window.history.state[HISTORY_KEY]
        ? window.history.state[HISTORY_KEY].scrollY
        : (savedPositions[routeKey(targetUrl)] || 0);
      nextState[HISTORY_KEY] = {
        tab: settings.tab || nextTab,
        scrollY: settings.scrollToTop ? 0 : restoredScrollY
      };
      if (settings.push) window.history.pushState(nextState, '', targetUrl.href);
      else window.history.replaceState(nextState, '', targetUrl.href);

      currentUrl = targetUrl.href;
      renderNavigationState(targetUrl, nextState, { scrollToTop: settings.scrollToTop });
      window.dispatchEvent(new CustomEvent('smyrne:navigate', { detail: { url: targetUrl.href } }));
    } catch (error) {
      console.warn('[App] Navigation interne indisponible, chargement Django normal:', error);
      window.location.assign(targetUrl.href);
    } finally {
      main.removeAttribute('aria-busy');
    }
  }

  function openMenu() {
    if (menuOpen) return;
    menuOpen = true;
    menuOpenState(true);
    window.history.pushState(Object.assign({}, window.history.state || {}, { smyrneMenu: true }), '', window.location.href);
  }

  function menuOpenState(open) {
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', String(!open));
    menu.inert = !open;
    scrim.hidden = !open;
    if (menuButton) {
      menuButton.classList.toggle('is-open', open);
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
    }
    document.body.classList.toggle('menu-open', open);
    if (open) {
      requestAnimationFrame(function() { scrim.classList.add('is-visible'); });
      const firstLink = menu.querySelector('.app-menu-item');
      if (firstLink) firstLink.focus({ preventScroll: true });
    } else {
      scrim.classList.remove('is-visible');
      if (menuButton && !menuButton.hidden) menuButton.focus({ preventScroll: true });
    }
  }

  function closeMenu(forNavigation) {
    if (!menuOpen) return;
    menuOpen = false;
    menuOpenState(false);
    if (window.history.state && window.history.state.smyrneMenu) {
      if (forNavigation === true) {
          const state = Object.assign({}, window.history.state);
        delete state.smyrneMenu;
        window.history.replaceState(state, '', window.location.href);
      } else {
        window.history.back();
      }
    }
  }

  document.addEventListener('click', function(event) {
    const anchor = event.target.closest('a[href]');
    if (!anchor || event.defaultPrevented || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
        anchor.target || anchor.hasAttribute('download') || anchor.dataset.noSpa !== undefined) return;

    const targetUrl = new URL(anchor.href, window.location.href);
    if (!isAppPage(targetUrl) || targetUrl.origin !== window.location.origin) return;

    event.preventDefault();
    navigate(targetUrl);
  });

  document.addEventListener('submit', function(event) {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || form.target || form.dataset.noSpa !== undefined) return;
    const action = new URL(form.action || window.location.href, window.location.href);
    if (!isAppPage(action) || /^\/(?:connexion|inscription)\/?$/.test(action.pathname)) return;

    event.preventDefault();
    if (form.method.toLowerCase() === 'get') {
      const values = new URLSearchParams(new FormData(form));
      action.search = values.toString();
      navigate(action, { formNavigation: true });
      return;
    }

    const formData = new FormData(form);
    main.setAttribute('aria-busy', 'true');
    saveCurrentPosition();
    saveHomeFeedSnapshot();
    fetch(action.href, {
      method: form.method.toUpperCase(),
      body: formData,
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'Smyrne-App-Form' }
    }).then(async function(response) {
      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const finalUrl = new URL(response.url || action.href, window.location.href);
      if (!response.ok || !pageHasShell(doc) || !replaceMainContent(doc, finalUrl)) {
        throw new Error('Le formulaire doit être traité par le chargement Django complet.');
      }

      updateMessages(doc);
      const state = Object.assign({}, window.history.state || {});
      delete state.smyrneMenu;
      state[HISTORY_KEY] = { tab: tabForPath(finalUrl.pathname), scrollY: 0 };
      window.history.pushState(state, '', finalUrl.href);
      currentUrl = finalUrl.href;
      document.title = doc.title || document.title;
      renderNavigationState(finalUrl, state, { scrollToTop: true });
      window.dispatchEvent(new CustomEvent('smyrne:navigate', { detail: { url: finalUrl.href } }));
    }).catch(function(error) {
      console.warn('[App] Soumission interne indisponible, envoi Django normal:', error);
      form.dataset.noSpa = 'true';
      form.submit();
    }).finally(function() {
      main.removeAttribute('aria-busy');
    });
  });

  tabbar.addEventListener('click', function(event) {
    const tab = event.target.closest('[data-app-tab]');
    if (!tab) return;
    if (tab.dataset.appTab === 'live' && tab.dataset.liveActive === 'true') {
      event.preventDefault();
      event.stopImmediatePropagation();
      const liveButton = document.getElementById('openLiveModalBtn');
      if (liveButton) liveButton.click();
      return;
    }
    const destination = new URL(tab.href, window.location.href);
    const currentPage = new URL(window.location.href);
    if (destination.pathname === currentPage.pathname &&
        destination.search === currentPage.search &&
        destination.hash === currentPage.hash) {
      event.preventDefault();
      event.stopImmediatePropagation();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    event.preventDefault();
    event.stopImmediatePropagation();
    navigate(destination, { tab: tab.dataset.appTab, scrollToTop: true });
  }, true);

  if (subtabs) {
    subtabs.addEventListener('click', function(event) {
      const subtab = event.target.closest('[data-app-subtab]');
      if (!subtab) return;
      const destination = new URL(subtab.href, window.location.href);
      const currentPage = new URL(window.location.href);
      if (destination.pathname === currentPage.pathname &&
          destination.search === currentPage.search &&
          destination.hash === currentPage.hash) {
        event.preventDefault();
        event.stopImmediatePropagation();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      event.preventDefault();
      event.stopImmediatePropagation();
      navigate(destination, { tab: 'events', scrollToTop: true });
    }, true);
  }

  if (menuButton) menuButton.addEventListener('click', openMenu);
  scrim.addEventListener('click', closeMenu);
  const inviteMenuItem = menu.querySelector('[data-open-invite]');
  if (inviteMenuItem) inviteMenuItem.addEventListener('click', closeMenu);
  const verseMenuItem = menu.querySelector('[data-open-verse]');
  if (verseMenuItem) verseMenuItem.addEventListener('click', function() {
    closeMenu();
    if (window.openDailyVerseModal) window.openDailyVerseModal(verseMenuItem);
  });
  menu.addEventListener('touchstart', function(event) {
    menuStartX = event.changedTouches[0].clientX;
  }, { passive: true });
  menu.addEventListener('touchend', function(event) {
    if (menuStartX !== null && event.changedTouches[0].clientX - menuStartX > 60) closeMenu();
    menuStartX = null;
  }, { passive: true });

  window.addEventListener('popstate', function(event) {
    if (menuOpen) {
      menuOpen = false;
      menuOpenState(false);
      if (event.state && event.state.smyrneMenu) return;
    }

    const targetUrl = new URL(window.location.href);
    if (targetUrl.href === currentUrl) return;

    if (!isAppPage(targetUrl)) {
      window.location.reload();
      return;
    }

    navigate(targetUrl, { push: false, scrollToTop: false, fromPopstate: true }).then(function() {
      currentUrl = targetUrl.href;
    });
  });

  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && document.querySelector('.invite-modal-backdrop.active, .live-video-modal-backdrop.active, .search-modal-backdrop.active, .verset-modal-backdrop.active, .lightbox-modal.active')) return;
    if (event.key === 'Escape' && menuOpen) {
      event.preventDefault();
      closeMenu();
    }
  }, true);

  window.addEventListener('scroll', saveCurrentPosition, { passive: true });
  window.addEventListener('smyrne:home-feed-updated', saveHomeFeedSnapshot);
  window.addEventListener('pagehide', function() {
    saveCurrentPosition();
    saveHomeFeedSnapshot();
  });

  prepareImages(main);
  renderNavigationState(new URL(window.location.href), window.history.state || {}, { scrollToTop: false });
  saveCurrentPosition();

  function updateMessages(doc) {
    const incoming = doc.querySelector('.messages-container');
    const current = document.querySelector('.messages-container');
    if (incoming && current) {
      current.innerHTML = incoming.innerHTML;
    } else if (incoming) {
      main.parentNode.insertBefore(incoming.cloneNode(true), main);
    } else if (current) {
      current.remove();
    }
  }
})();