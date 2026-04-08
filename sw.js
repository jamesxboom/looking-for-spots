const CACHE_NAME = 'lfs-v1';
const urlsToCache = ['/'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Network-first with cache fallback for API calls
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const cache = caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, response.clone());
              return response;
            });
            return cache;
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
  }
  // Stale-while-revalidate for HTML
  else if (request.destination === 'document' || url.pathname.endsWith('.html') || url.pathname === '/') {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request).then((response) => {
          if (response.ok) {
            const cache = caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, response.clone());
              return response;
            });
            return cache;
          }
          return response;
        });
        return cachedResponse || fetchPromise;
      })
    );
  }
  // Default: network-first
  else {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const cache = caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, response.clone());
              return response;
            });
            return cache;
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
  }
});
