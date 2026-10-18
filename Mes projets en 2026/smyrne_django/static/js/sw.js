/**
 * =========================================================
 * SERVICE WORKER — Eglise Smyrne
 * =========================================================
 * Stratégie :
 *  - Cache First pour les ressources statiques (CSS, JS, images)
 *  - Network First pour les pages HTML (contenu frais)
 *  - Offline fallback pour les pages non cachées
 *
 * SECURITE : On ne cache JAMAIS :
 *  - /admin/ (interface d'administration)
 *  - /connexion/ (page de connexion)
 *  - /deconnexion/ (déconnexion)
 *  - /inscription/ (création de compte)
 *  - /ckeditor/ (uploads)
 *  - Requêtes POST (formulaires)
 *  - Sessions ou cookies sensibles
 */

const CACHE_NAME = 'smyrne-v13';
const OFFLINE_PAGE = '/offline/';

// Ressources statiques à pré-cacher au démarrage
const STATIC_ASSETS = [
  '/',
  '/offline/',
  '/static/css/app-shell.css',
  '/static/css/home.css',
  '/static/css/verset-widget.css',
  '/static/css/search-modal.css',
  '/static/css/invite-modal.css',
  '/static/css/actualites.css',
  '/static/css/predications.css',
  '/static/css/evenements.css',
  '/static/css/galerie.css',
  '/static/css/cultes.css',
  '/static/css/priere.css',
  '/static/css/histoire.css',
  '/static/css/ministeres.css',
  '/static/css/biographie.css',
  '/static/css/search.css',
  '/static/js/search.js',
  '/static/js/home-widgets.js',
  '/static/js/app-navigation.js',
  '/static/images/pwa/icon-192x192.png',
  '/static/images/pwa/icon-512x512.png',
  '/static/manifest.json',
];

// URLs à ne JAMAIS mettre en cache (sécurité critique)
const NEVER_CACHE = [
  '/admin',
  '/connexion',
  '/deconnexion',
  '/inscription',
  '/ckeditor',
  '/profil',
];

/**
 * Vérifie si une URL ne doit jamais être mise en cache
 */
function isNeverCache(url) {
  const pathname = new URL(url).pathname;
  return NEVER_CACHE.some(path => pathname.startsWith(path));
}

/**
 * Vérifie si c'est une ressource statique
 */
function isStaticAsset(url) {
  const pathname = new URL(url).pathname;
  return pathname.startsWith('/static/') || pathname.startsWith('/media/');
}

/** Les médias vidéo peuvent être volumineux : les laisser transiter sans stockage PWA. */
function isVideoMedia(url) {
  return /\.(?:mp4|webm|mov|m4v|ogv)$/i.test(new URL(url).pathname);
}

/**
 * Vérifie si la requête est navigable (HTML)
 */
function isNavigationRequest(request) {
  return request.mode === 'navigate';
}

// ─────────────────────────────────────────
// INSTALL — Pré-cache des ressources statiques
// ─────────────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[SW] Installation du service worker Smyrne...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Mise en cache des ressources statiques');
      // Recharger les ressources pour éviter de recopier une ancienne réponse HTTP en cache.
      return Promise.allSettled(
        STATIC_ASSETS.map(url => {
          const request = new Request(new URL(url, self.location.origin), { cache: 'reload' });
          return fetch(request).then(response => {
            if (!response || !response.ok) throw new Error('Réponse HTTP ' + (response && response.status));
            return cache.put(request, response);
          }).catch(err => {
            console.warn(`[SW] Impossible de mettre en cache: ${url}`, err);
          });
        })
      );
    }).then(() => {
      console.log('[SW] Installation terminée');
      return self.skipWaiting();
    })
  );
});

// ─────────────────────────────────────────
// ACTIVATE — Nettoyage des anciens caches
// ─────────────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[SW] Activation du service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => {
            console.log(`[SW] Suppression de l'ancien cache: ${name}`);
            return caches.delete(name);
          })
      );
    }).then(() => {
      console.log('[SW] Service worker actif et à jour');
      return self.clients.claim();
    })
  );
});

// ─────────────────────────────────────────
// FETCH — Stratégies de cache
// ─────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = request.url;

  // Ignorer les requêtes non HTTP/HTTPS
  if (!url.startsWith('http')) return;

  // Ignorer les requêtes POST/PUT/DELETE/PATCH (formulaires, API)
  if (request.method !== 'GET') return;

  // Les fragments AJAX du fil ne doivent pas remplacer la page HTML complète
  // dans le cache de la même URL.
  if (request.headers.get('X-Requested-With') === 'XMLHttpRequest') {
    event.respondWith(fetch(request));
    return;
  }

  // Ne jamais mettre en cache les URLs sensibles
  if (isNeverCache(url)) return;

  // Ressources statiques : Cache First
  if (isStaticAsset(url)) {
    if (isVideoMedia(url)) {
      event.respondWith(fetch(request));
      return;
    }
    event.respondWith(cacheFirst(request));
    return;
  }

  // Pages HTML : Network First avec fallback offline
  if (isNavigationRequest(request)) {
    event.respondWith(networkFirstWithOfflineFallback(request));
    return;
  }

  // Autres requêtes : Network First simple
  event.respondWith(networkFirst(request));
});

/**
 * CACHE FIRST — Retourne le cache, sinon réseau, sinon placeholder
 */
async function cacheFirst(request) {
  try {
    const cached = await caches.match(request);
    if (cached) return cached;

    const response = await fetch(request);
    if (response && response.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    console.warn('[SW] Cache first failed:', err);
    // Pour les images, retourner une réponse vide plutôt que d'erreur
    return new Response('', { status: 503 });
  }
}

/**
 * NETWORK FIRST — Réseau d'abord, cache ensuite
 */
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    const cached = await caches.match(request);
    return cached || new Response('Ressource indisponible hors ligne', { status: 503 });
  }
}

/**
 * NETWORK FIRST avec fallback page offline personnalisée
 */
async function networkFirstWithOfflineFallback(request) {
  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      // Mettre à jour le cache uniquement pour les pages principales
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    // Chercher dans le cache
    const cached = await caches.match(request);
    if (cached) return cached;

    // Afficher la page offline
    const offlinePage = await caches.match(OFFLINE_PAGE);
    if (offlinePage) return offlinePage;

    // Fallback ultime
    return new Response(
      '<html><body><h1>Hors ligne</h1><p>Verifiez votre connexion Internet.</p></body></html>',
      { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    );
  }
}

// ─────────────────────────────────────────
// MESSAGE — Communication avec le client
// ─────────────────────────────────────────
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});
