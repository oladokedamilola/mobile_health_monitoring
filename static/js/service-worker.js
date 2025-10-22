/* static/service-worker.js */
const CACHE_NAME = 'auralis-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png',
  '/static/js/analytics.js',
];

self.addEventListener('install', (evt) => {
  evt.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (evt) => {
  evt.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (evt) => {
  const req = evt.request;
  const url = new URL(req.url);

  // Network-first for API calls
  if (url.pathname.startsWith('/api/')) {
    evt.respondWith(
      fetch(req)
        .then((res) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, res.clone());
            return res;
          });
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // Cache-first for static resources
  evt.respondWith(
    caches.match(req).then((cached) => cached || fetch(req))
  );
});

/* Background sync placeholder — real sync handled by app logic or background sync API */
const CACHE_NAME = "auralis-cache-v1";
const OFFLINE_URLS = [
  "/",
  "/dashboard/",
  "/monitoring/live/",
  "/static/css/style.css",
  "/static/js/main.js",
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS))
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request))
  );
});
