/* Service Worker: App offline verfügbar machen.
   App-Dateien: zuerst Cache, im Hintergrund aktualisieren.
   Fragen (data/fragen.json): zuerst Netzwerk, damit Updates sofort ankommen. */
var CACHE = "lerntool-v1";
var DATEIEN = ["./", "index.html", "style.css", "app.js", "manifest.webmanifest", "data/fragen.json",
  "icons/icon.svg", "icons/icon-180.png", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(DATEIEN); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  var istDaten = e.request.url.indexOf("/data/") >= 0;
  var netz = fetch(e.request).then(function (r) {
    if (r && r.ok) { var kopie = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, kopie); }); }
    return r;
  });
  if (istDaten) {
    e.respondWith(netz.catch(function () { return caches.match(e.request, { ignoreSearch: true }); }));
  } else {
    e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(function (c) {
      if (c) { netz.catch(function () {}); return c; }
      return netz;
    }));
  }
});
