/* Service Worker: App offline verfügbar machen.
   Strategie "zuerst Netzwerk": Online kommt immer die aktuelle Version (Abgleich mit dem
   Server, am HTTP-Cache des Browsers vorbei). Nur offline wird die gespeicherte Kopie genutzt.
   So erreichen Updates alle Nutzer, ohne dass jemand den Cache leeren muss. */
var CACHE = "lerntool-v4";
var DATEIEN = ["./", "index.html", "style.css", "app.js", "manifest.webmanifest", "data/fragen.json", "data/fragen_ki.json", "data/erklaerungen.json",
  "icons/icon.svg", "icons/icon-180.png", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) {
    // cache: "reload" verhindert, dass veraltete Dateien aus dem HTTP-Cache übernommen werden
    return c.addAll(DATEIEN.map(function (u) { return new Request(u, { cache: "reload" }); }));
  }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  // Neue Anfrage nur mit der URL: Navigationsanfragen lassen sich nicht mit Optionen kopieren
  e.respondWith(fetch(new Request(e.request.url, { cache: "no-cache", credentials: "same-origin" })).then(function (r) {
    if (r && r.ok) { var kopie = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, kopie); }); }
    return r;
  }).catch(function () {
    return caches.match(e.request, { ignoreSearch: true }).then(function (c) {
      return c || caches.match("index.html");
    });
  }));
});
