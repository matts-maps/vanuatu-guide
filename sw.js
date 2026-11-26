/* Offline support for the Vanuatu guide.
   - Pages: network first, so a new version arrives as soon as you are online; the saved copy is used when you are not.
   - Weather: network first, falling back to the last saved forecast.
   - Map data: saved the first time an area is viewed, then served at once and refreshed quietly in the background.
   - Fonts and icons: saved on first use.
   Bump VERSION if the list of precached files below changes. */
const VERSION = 'v1';
const SHELL = 'vanuatu-shell-' + VERSION;
const DATA = 'vanuatu-data-' + VERSION;
const PRECACHE = [
  './', 'index.html', 'data-sources.html', 'manifest.webmanifest',
  'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png',
  'fonts/caveat-brush-latin-400-normal.woff2', 'fonts/caveat-latin-500-normal.woff2', 'fonts/caveat-latin-700-normal.woff2',
  'fonts/patrick-hand-latin-400-normal.woff2', 'fonts/space-mono-latin-400-normal.woff2', 'fonts/space-mono-latin-700-normal.woff2'
];
const CORE_DATA = ['data/land.json', 'data/decor.json', 'data/places.json', 'data/bcells.json', 'data/weather.json'];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    await (await caches.open(SHELL)).addAll(PRECACHE);
    const d = await caches.open(DATA);
    await Promise.all(CORE_DATA.map(u => d.add(u).catch(() => {})));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== SHELL && k !== DATA) await caches.delete(k);
    await self.clients.claim();
  })());
});

const keyFor = url => new Request(url.origin + url.pathname); // ignore ?t=... cache-busting

async function networkFirst(req, cacheName, key) {
  const cache = await caches.open(cacheName);
  try {
    const res = await fetch(req);
    if (res && res.ok) cache.put(key, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(key);
    if (hit) return hit;
    throw err;
  }
}

async function staleWhileRevalidate(req, cacheName, key) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(key);
  const refresh = fetch(req).then(res => { if (res && res.ok) cache.put(key, res.clone()); return res; }).catch(() => null);
  return hit || (await refresh) || Response.error();
}

async function cacheFirst(req, cacheName, key) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(key);
  if (hit) return hit;
  const res = await fetch(req);
  if (res && res.ok) cache.put(key, res.clone());
  return res;
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  const path = url.pathname;
  if (req.mode === 'navigate' || path.endsWith('.html') || path.endsWith('/')) {
    e.respondWith(networkFirst(req, SHELL, keyFor(url)).catch(async () => (await caches.match('index.html')) || Response.error()));
  } else if (path.endsWith('/data/weather.json')) {
    e.respondWith(networkFirst(req, DATA, keyFor(url)));
  } else if (path.includes('/data/')) {
    e.respondWith(staleWhileRevalidate(req, DATA, keyFor(url)));
  } else if (path.includes('/fonts/') || path.includes('/icons/') || path.endsWith('.webmanifest')) {
    e.respondWith(cacheFirst(req, SHELL, keyFor(url)));
  }
});
