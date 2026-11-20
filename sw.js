const CACHE = 'utro7-static-v18';
const PRECACHE = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png', './src/motion/motion-policy.js'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  // Let the browser handle byte-range video requests; do not corrupt Safari MP4 seeking.
  if (event.request.destination === 'video' || event.request.headers.has('range') || new URL(event.request.url).pathname.endsWith('.mp4')) return;
  if (event.request.mode === 'navigate') {
    // Review pages are not the app shell; never overwrite cached index.html with them.
    const path = new URL(event.request.url).pathname;
    const rootPath = new URL(self.registration.scope).pathname;
    if (path !== rootPath && path !== rootPath + 'index.html') return;
    event.respondWith(fetch(event.request).then(response => {
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE).then(cache => cache.put('./index.html', copy));
      }
      return response;
    }).catch(() => caches.match('./index.html')));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => cached || fetch(event.request)));
});
