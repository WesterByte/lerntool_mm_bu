/* Karteikarten-Lerntool – reines JavaScript, keine Abhängigkeiten.
   Fortschritt wird nur lokal im Browser (localStorage) gespeichert. */
(function () {
  "use strict";

  // ---------- Konfiguration ----------
  // Fragensets: jedes Set hat eigene Fragen, eigenen Speicher und eigene Prüfungsregeln.
  // Der Speicher-Key des Original-Sets bleibt "lerntool.v1", damit bestehender Fortschritt erhalten bleibt.
  var SETS = {
    original: { name: "Original-Fragen", kurz: "Original", datei: "data/fragen.json", speicherKey: "lerntool.v1",
      pruefungFragen: 60, pruefungMinuten: 90 },
    ki: { name: "Übungsfragen (KI-generiert)", kurz: "KI-Übung", datei: "data/fragen_ki.json", speicherKey: "lerntool.ki.v1",
      pruefungFragen: 50, pruefungMinuten: 75, // gleiches Tempo wie das Original: 1,5 Minuten pro Frage
      hinweis: "Diese Fragen wurden von einer KI auf Basis der Lernzusammenfassungen S4500 und S4520 erstellt. Sie dienen zum Üben und sind keine offiziellen Prüfungsfragen." }
  };
  var SET_WAHL_KEY = "lerntool.set";
  var SET_ID = "original";
  var PRUEFUNG_FRAGEN = 60;
  var PRUEFUNG_MINUTEN = 90;
  var GRENZE_BESTANDEN = 55;      // Prozent
  var GRENZE_AUSZEICHNUNG = 75;   // Prozent
  var GELERNT_AB_BOX = 3;         // so oft in Folge richtig = "gelernt"
  var MAX_BOX = 5;
  var WIEDERHOLEN_NACH = 3;       // falsche Karte kommt nach so vielen Karten erneut
  var SPEICHER_KEY = SETS.original.speicherKey;

  // ---------- Hilfsfunktionen ----------
  var $app = document.getElementById("app");
  var $extra = document.getElementById("topbar-extra");
  var $dialog = document.getElementById("dialog");

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function mischen(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function hash(str) {
    // FNV-1a, stabiler Schlüssel aus dem Fragetext (Fortschritt bleibt bei Excel-Updates erhalten)
    var h = 0x811c9dc5;
    for (var i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = Math.imul(h, 0x01000193) >>> 0;
    }
    return ("0000000" + h.toString(16)).slice(-8);
  }
  function gleicheMenge(a, b) {
    if (a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (b.indexOf(a[i]) < 0) return false;
    return true;
  }
  function zeitFormat(ms) {
    var s = Math.max(0, Math.ceil(ms / 1000));
    var h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sek = s % 60;
    var mm = (h ? String(m).padStart(2, "0") : String(m));
    return (h ? h + ":" : "") + mm + ":" + String(sek).padStart(2, "0");
  }
  function datumFormat(ts) {
    var d = new Date(ts);
    return d.toLocaleDateString("de-DE") + ", " + d.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
  }
  function buchstabe(i) { return String.fromCharCode(65 + i); }
  function toast(text) {
    var t = document.createElement("div");
    t.className = "toast"; t.textContent = text;
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2200);
  }

  // ---------- Speicher ----------
  var speicher = null;
  function laden() {
    var leer = { fortschritt: {}, einstellungen: { mischen: true }, pruefungen: [], laufend: null, ergebnis: null };
    try {
      var s = JSON.parse(localStorage.getItem(SPEICHER_KEY));
      if (s && typeof s === "object") {
        for (var k in leer) if (!(k in s)) s[k] = leer[k];
        return s;
      }
    } catch (e) { /* ignorieren */ }
    return leer;
  }
  function speichern() {
    try { localStorage.setItem(SPEICHER_KEY, JSON.stringify(speicher)); }
    catch (e) { /* z. B. privater Modus – App funktioniert trotzdem */ }
  }
  function fp(key) {
    return speicher.fortschritt[key] || { box: 0, richtig: 0, falsch: 0, zuletzt: 0 };
  }
  function fortschrittBuchen(key, korrekt) {
    var f = fp(key);
    if (korrekt) { f.richtig++; f.box = Math.min(MAX_BOX, f.box + 1); }
    else { f.falsch++; f.box = 0; }
    f.zuletzt = Date.now();
    f.letztesErgebnis = korrekt ? "richtig" : "falsch";
    speicher.fortschritt[key] = f;
    speichern();
  }
  function status(key) {
    var f = speicher.fortschritt[key];
    if (!f || (f.richtig + f.falsch) === 0) return "neu";
    if (f.box >= GELERNT_AB_BOX) return "gelernt";
    return "lernend";
  }

  // ---------- Daten ----------
  var FRAGEN = [];          // [{key, nr, frage, antworten:[{id,text,richtig}], anzahlRichtig}]
  var NACH_KEY = {};

  var GELADEN = {};          // setId -> {fragen, nachKey}

  function datenLaden(setId) {
    if (GELADEN[setId]) return Promise.resolve(GELADEN[setId]);
    return fetch(SETS[setId].datei, { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var nachKey = {};
        var fragen = d.fragen.map(function (f) {
          var key = hash(f.frage + "|" + f.antworten.map(function (a) { return a.text; }).join("|"));
          var q = { key: key, nr: f.nr, frage: f.frage, antworten: f.antworten, anzahlRichtig: f.anzahlRichtig, quelle: f.quelle || "" };
          nachKey[key] = q;
          return q;
        });
        return (GELADEN[setId] = { fragen: fragen, nachKey: nachKey });
      });
  }

  // Fragenset laden und aktiv schalten (Fragen, Speicher, Prüfungsregeln)
  function setAktivieren(setId) {
    if (!SETS[setId]) setId = "original";
    return datenLaden(setId).then(function (g) {
      var s = SETS[setId];
      SET_ID = setId;
      SPEICHER_KEY = s.speicherKey;
      PRUEFUNG_FRAGEN = s.pruefungFragen;
      PRUEFUNG_MINUTEN = s.pruefungMinuten;
      FRAGEN = g.fragen;
      NACH_KEY = g.nachKey;
      speicher = laden();
      lern = null;
      seiteErgebnis.filter = null;
      seiteFragen.filter = null;
      seitePruefung.uebersicht = false;
      try { localStorage.setItem(SET_WAHL_KEY, setId); } catch (e) { /* ignorieren */ }
      if (setId === "original") {
        erklaerungenLaden().then(function () {
          // Falls gerade eine aufgelöste Karte oder die Auswertung angezeigt wird: Erklärung nachreichen
          var h = location.hash;
          if (SET_ID === "original" && (h === "#/ergebnis" || (h === "#/lernen" && lern && lern.aktuell && lern.aktuell.geprueft))) route();
        }, function () { /* ohne Erklärungen weiterlernen */ });
      }
    });
  }
  // Erklärungen (nur für die Original-Fragen), Zuordnung über denselben Schlüssel wie der Fortschritt
  var ERKL = null;           // {buecher, nachKey}
  var erklLaeuft = null;
  function erklaerungenLaden() {
    if (ERKL) return Promise.resolve(ERKL);
    if (erklLaeuft) return erklLaeuft;
    erklLaeuft = fetch("data/erklaerungen.json", { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var nachKey = {};
        d.erklaerungen.forEach(function (e) { nachKey[e.key] = e; });
        return (ERKL = { buecher: d.buecher || {}, nachKey: nachKey });
      })
      .catch(function (err) { erklLaeuft = null; throw err; });
    return erklLaeuft;
  }
  function erklaerungZu(q) {
    return SET_ID === "original" && ERKL ? ERKL.nachKey[q.key] || null : null;
  }

  function gespeichertesSet() {
    try { return localStorage.getItem(SET_WAHL_KEY) || "original"; } catch (e) { return "original"; }
  }
  function richtigeIds(q) {
    return q.antworten.filter(function (a) { return a.richtig; }).map(function (a) { return a.id; });
  }

  // ---------- Dialog ----------
  function bestaetigen(titel, text, ja, nein) {
    return new Promise(function (resolve) {
      $dialog.innerHTML =
        '<div class="card dialog" role="dialog" aria-modal="true" aria-labelledby="dlg-t">' +
        '<h2 id="dlg-t">' + esc(titel) + "</h2><p>" + text + "</p>" +
        '<div class="btn-row end"><button class="btn" data-a="0">' + esc(nein || "Abbrechen") + "</button>" +
        '<button class="btn primary" data-a="1">' + esc(ja || "OK") + "</button></div></div>";
      $dialog.hidden = false;
      $dialog.querySelector('[data-a="1"]').focus();
      function fertig(v) { $dialog.hidden = true; $dialog.innerHTML = ""; document.removeEventListener("keydown", esc_); resolve(v); }
      function esc_(e) { if (e.key === "Escape") fertig(false); }
      document.addEventListener("keydown", esc_);
      $dialog.onclick = function (e) {
        var b = e.target.closest("[data-a]");
        if (b) fertig(b.getAttribute("data-a") === "1");
        else if (e.target === $dialog) fertig(false);
      };
    });
  }

  // ---------- Router ----------
  var aufraeumen = null; // Funktion, die beim Seitenwechsel läuft (Timer, Tasten …)
  function route() {
    if (aufraeumen) { aufraeumen(); aufraeumen = null; }
    $extra.innerHTML = "";
    $dialog.hidden = true;
    if (!speicher) return; // Fragen werden noch geladen
    if (pruefungAblaufPruefen()) { if (location.hash === "#/ergebnis") seiteErgebnis(); return; }
    var h = location.hash.replace(/^#\/?/, "");
    var teile = h.split("?");
    var seite = teile[0];
    window.scrollTo(0, 0);
    document.body.classList.toggle("im-test", seite === "pruefung");
    navMarkieren(seite === "erklaerungen" ? "erklaerungen" : "start");
    if (seite === "erklaerungen") return seiteErklaerungen(teile[1] || "");
    if (seite === "lernen") return seiteLernen();
    if (seite === "pruefung") return seitePruefung();
    if (seite === "ergebnis") return seiteErgebnis();
    if (seite === "fragen") return seiteFragen();
    return seiteStart();
  }

  function navMarkieren(aktiv) {
    var links = document.querySelectorAll(".topnav a");
    for (var i = 0; i < links.length; i++) {
      if (links[i].getAttribute("data-nav") === aktiv) links[i].setAttribute("aria-current", "page");
      else links[i].removeAttribute("aria-current");
    }
  }

  // ---------- Startseite ----------
  function zaehlen(keys) {
    var z = { neu: 0, lernend: 0, gelernt: 0 };
    keys.forEach(function (k) { z[status(k)]++; });
    return z;
  }
  function fortschrittsBalken(z, gesamt) {
    function w(n) { return (gesamt ? (n / gesamt) * 100 : 0).toFixed(2) + "%"; }
    return '<div class="bar" role="img" aria-label="' + z.gelernt + " von " + gesamt + ' gelernt">' +
      '<i class="b-ok" style="width:' + w(z.gelernt) + '"></i><i class="b-mid" style="width:' + w(z.lernend) + '"></i></div>';
  }

  function seiteStart() {
    var keys = FRAGEN.map(function (q) { return q.key; });
    var z = zaehlen(keys);
    var schwierig = keys.filter(function (k) { var f = speicher.fortschritt[k]; return f && f.falsch > 0 && f.box < GELERNT_AB_BOX; }).length;
    var laufend = speicher.laufend;
    var letzte = speicher.pruefungen.slice(-5).reverse();

    var html = '<div class="card set-wahl"><div class="tabs" role="group" aria-label="Fragenset wählen">' +
      Object.keys(SETS).map(function (id) {
        return '<button data-set="' + id + '" aria-pressed="' + (id === SET_ID) + '">' + esc(SETS[id].name) + "</button>";
      }).join("") + "</div>" +
      (SETS[SET_ID].hinweis ? '<p class="small muted" style="margin:10px 0 0">' + esc(SETS[SET_ID].hinweis) + "</p>" : "") +
      '<p class="small muted" style="margin:6px 0 0">Lernstand und Prüfungen werden für jedes Fragenset getrennt gespeichert.</p></div>';
    if (laufend) {
      html += '<div class="card" style="border-color:var(--primary)"><h2>Laufende Prüfung</h2>' +
        '<p>Restzeit: <b>' + zeitFormat(laufend.ende - Date.now()) + "</b> · " +
        Object.keys(laufend.antworten).filter(function (k) { return laufend.antworten[k].length; }).length + " von " + laufend.keys.length + " beantwortet</p>" +
        '<a class="btn primary" href="#/pruefung">Prüfung fortsetzen</a></div>';
    }

    html += '<div class="card"><h1>Dein Lernstand · ' + esc(SETS[SET_ID].kurz) + "</h1>" +
      '<div class="stats">' +
      '<div class="stat"><b>' + FRAGEN.length + "</b><span>Fragen</span></div>" +
      '<div class="stat"><b style="color:var(--ok)">' + z.gelernt + "</b><span>gelernt</span></div>" +
      '<div class="stat"><b style="color:var(--warn)">' + z.lernend + "</b><span>in Arbeit</span></div>" +
      '<div class="stat"><b>' + z.neu + "</b><span>neu</span></div></div>" +
      fortschrittsBalken(z, FRAGEN.length) +
      '<p class="small muted" style="margin-top:8px">Eine Frage gilt als gelernt, wenn du sie ' + GELERNT_AB_BOX + "× hintereinander richtig beantwortet hast.</p></div>";

    html += '<div class="mode-grid">' +
      '<div class="card"><h2>Lernmodus</h2><p class="muted">Karten durchgehen mit sofortigem Feedback. Falsch beantwortete Fragen kommen kurz danach und beim nächsten Mal zuerst wieder.</p>' +
      '<label class="small muted" for="filter">Welche Karten?</label>' +
      '<select id="filter" style="width:100%;margin:4px 0 10px">' +
      '<option value="offen">Noch nicht gelernte (' + (z.neu + z.lernend) + ")</option>" +
      '<option value="schwierig">Nur bisher falsch beantwortete (' + schwierig + ")</option>" +
      '<option value="neu">Nur neue (' + z.neu + ")</option>" +
      '<option value="alle">Alle Karten (' + FRAGEN.length + ")</option></select>" +
      '<button class="btn primary" id="start-lernen">Lernen starten</button></div>' +
      '<div class="card"><h2>Prüfungssimulation</h2><p class="muted">' +
      (PRUEFUNG_FRAGEN >= FRAGEN.length ? "Alle " + FRAGEN.length + " Fragen in zufälliger Reihenfolge, " : PRUEFUNG_FRAGEN + " zufällige Fragen, ") + PRUEFUNG_MINUTEN +
      " Minuten. Nur vollständig richtige Antworten zählen. Bestanden ab " + GRENZE_BESTANDEN + " %, mit Auszeichnung ab " + GRENZE_AUSZEICHNUNG + " %.</p>" +
      '<button class="btn primary" id="start-pruefung">' + (laufend ? "Neue Prüfung starten" : "Prüfung starten") + "</button></div></div>";

    if (letzte.length) {
      html += '<div class="card" style="margin-top:16px"><h2>Letzte Prüfungen</h2><table class="list"><tbody>' +
        letzte.map(function (p) {
          var v = p.prozent >= GRENZE_AUSZEICHNUNG ? '<span class="chip ok">Auszeichnung</span>' :
            p.prozent >= GRENZE_BESTANDEN ? '<span class="chip ok">bestanden</span>' : '<span class="chip bad">nicht bestanden</span>';
          return "<tr><td>" + datumFormat(p.datum) + '</td><td class="num">' + p.punkte + "/" + p.gesamt + " (" + p.prozent + " %)</td><td>" + v + "</td></tr>";
        }).join("") + "</tbody></table>" +
        (speicher.ergebnis ? '<p style="margin:12px 0 0"><a href="#/ergebnis">Letzte Auswertung ansehen</a></p>' : "") + "</div>";
    }

    html += '<div class="btn-row" style="margin-top:16px">' +
      '<a class="btn" href="#/fragen">Alle Fragen &amp; Fortschritt</a>' +
      '<a class="btn" href="#/erklaerungen">Erklärungen zu den Original-Fragen</a>' +
      '<button class="btn" id="teilen">Link teilen</button></div>' +
      '<label class="opt small muted" style="margin-top:12px"><input type="checkbox" id="opt-mischen"' + (speicher.einstellungen.mischen ? " checked" : "") + "> Antwortreihenfolge mischen</label>" +
      '<p class="small muted">Dein Fortschritt wird nur in diesem Browser auf diesem Gerät gespeichert.</p>';

    $app.innerHTML = html;

    $app.querySelector(".set-wahl .tabs").onclick = function (e) {
      var b = e.target.closest("[data-set]");
      if (!b || b.getAttribute("data-set") === SET_ID) return;
      $app.innerHTML = '<p class="muted">Lade Fragen …</p>';
      setAktivieren(b.getAttribute("data-set")).then(route, ladeFehler);
    };

    var sel = document.getElementById("filter");
    if (z.neu + z.lernend === 0) sel.value = "alle";
    document.getElementById("start-lernen").onclick = function () {
      lernSitzungStarten(sel.value);
      location.hash = "#/lernen";
    };
    document.getElementById("start-pruefung").onclick = function () {
      var p = laufend ? bestaetigen("Neue Prüfung starten?", "Die laufende Prüfung wird verworfen.", "Neu starten") : Promise.resolve(true);
      p.then(function (ok) { if (ok) { pruefungStarten(); location.hash = "#/pruefung"; } });
    };
    document.getElementById("opt-mischen").onchange = function (e) {
      speicher.einstellungen.mischen = e.target.checked; speichern();
    };
    document.getElementById("teilen").onclick = teilen;
  }

  function teilen() {
    var url = location.href.split("#")[0];
    if (navigator.share) {
      navigator.share({ title: "Karteikarten-Lerntool", url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(function () { toast("Link kopiert"); }, function () { toast(url); });
    } else {
      toast(url);
    }
  }

  // ---------- Karte rendern (Lernen, Prüfung, Auswertung) ----------
  function reihenfolge(q, gemischt) {
    var ids = q.antworten.map(function (a) { return a.id; });
    return gemischt ? mischen(ids) : ids;
  }
  function antwortVon(q, id) {
    for (var i = 0; i < q.antworten.length; i++) if (q.antworten[i].id === id) return q.antworten[i];
  }
  function hinweisChip(q) {
    return q.anzahlRichtig > 1 ? '<span class="chip hint">' + q.anzahlRichtig + " richtige Antworten</span>" : "";
  }
  // modus: "auswahl" (klickbar) oder "aufloesung" (farbig, nicht klickbar)
  function antwortenHtml(q, ordnung, gewaehlt, modus) {
    var radio = q.anzahlRichtig === 1;
    return '<ul class="answers">' + ordnung.map(function (id, i) {
      var a = antwortVon(q, id);
      var an = gewaehlt.indexOf(id) >= 0;
      var cls = "answer" + (radio ? " radio" : "");
      var tag = "";
      if (modus === "aufloesung") {
        if (a.richtig && an) { cls += " is-correct"; tag = "Richtig gewählt"; }
        else if (!a.richtig && an) { cls += " is-wrong"; tag = "Falsch gewählt"; }
        else if (a.richtig && !an) { cls += " is-missed"; tag = "Richtige Antwort – nicht gewählt"; }
      }
      return '<li><button type="button" class="' + cls + '" data-id="' + esc(id) + '" aria-pressed="' + an + '"' +
        (modus === "aufloesung" ? " disabled" : "") + '><span class="mark">' + buchstabe(i) + "</span><span>" + esc(a.text) +
        (tag ? '<span class="tag">' + tag + "</span>" : "") + "</span></button></li>";
    }).join("") + "</ul>";
  }
  function auswahlUmschalten(q, gewaehlt, id) {
    var idx = gewaehlt.indexOf(id);
    if (q.anzahlRichtig === 1) return idx >= 0 ? [] : [id];
    var neu = gewaehlt.slice();
    if (idx >= 0) neu.splice(idx, 1); else neu.push(id);
    return neu;
  }

  // ---------- Lernmodus ----------
  var lern = null;
  function lernSitzungStarten(filter) {
    var pool = FRAGEN.filter(function (q) {
      var s = status(q.key), f = speicher.fortschritt[q.key];
      if (filter === "offen") return s !== "gelernt";
      if (filter === "neu") return s === "neu";
      if (filter === "schwierig") return f && f.falsch > 0 && f.box < GELERNT_AB_BOX;
      if (Array.isArray(filter)) return filter.indexOf(q.key) >= 0;
      return true;
    });
    // Zuerst Karten mit niedriger Box (falsch/neu), innerhalb gleicher Box zufällig
    var queue = mischen(pool).sort(function (a, b) { return fp(a.key).box - fp(b.key).box; }).map(function (q) { return q.key; });
    lern = { queue: queue, gesamt: queue.length, beantwortet: 0, richtig: 0, falsch: 0, falschKeys: {}, aktuell: null };
  }

  function seiteLernen() {
    if (!lern) lernSitzungStarten("offen");
    if (!lern.queue.length && !lern.aktuell) return lernZusammenfassung();

    var karte = lern.aktuell;
    if (!karte) {
      var key = lern.queue.shift();
      var q0 = NACH_KEY[key];
      karte = lern.aktuell = { key: key, ordnung: reihenfolge(q0, speicher.einstellungen.mischen), gewaehlt: [], geprueft: false };
    }
    var q = NACH_KEY[karte.key];
    var f = fp(q.key), s = status(q.key);
    var stChip = s === "neu" ? '<span class="chip">neu</span>' : s === "gelernt" ? '<span class="chip ok">gelernt</span>' :
      '<span class="chip">' + f.box + "/" + GELERNT_AB_BOX + " richtig in Folge</span>";
    var offen = lern.queue.length + (karte.geprueft ? 0 : 1);

    $extra.innerHTML = '<span class="small muted">' + offen + " offen</span>";

    var html = '<div class="card">' +
      '<div class="q-meta"><span>Frage ' + q.nr + "</span>" + stChip + hinweisChip(q) +
      (q.quelle ? '<span class="small">' + esc(q.quelle) + "</span>" : "") + "</div>" +
      '<div class="q-text">' + esc(q.frage) + "</div>" +
      antwortenHtml(q, karte.ordnung, karte.gewaehlt, karte.geprueft ? "aufloesung" : "auswahl");
    if (karte.geprueft) {
      html += karte.korrekt ? '<div class="feedback ok">Richtig!</div>' :
        '<div class="feedback bad">Leider falsch. Die Karte kommt gleich noch einmal.</div>';
      var erkl = erklaerungZu(q);
      if (erkl) html += erklaerungHtml(q, erkl, karte.ordnung, { aufklappbar: true, offen: karte.erklOffen });
    }
    html += '</div><div class="actions-sticky btn-row">' +
      '<a class="btn" href="#/" id="beenden">Beenden</a>' +
      (karte.geprueft ? '<button class="btn primary grow" id="weiter">Weiter</button>' :
        '<button class="btn primary grow" id="pruefen"' + (karte.gewaehlt.length ? "" : " disabled") + ">Antwort prüfen</button>") +
      "</div>" +
      '<p class="small muted">Sitzung: ' + lern.richtig + " richtig, " + lern.falsch + " falsch · Tastatur: A–H wählen, Enter prüfen/weiter</p>";
    $app.innerHTML = html;

    $app.querySelector(".answers").onclick = function (e) {
      var b = e.target.closest(".answer");
      if (!b || karte.geprueft) return;
      karte.gewaehlt = auswahlUmschalten(q, karte.gewaehlt, b.getAttribute("data-id"));
      seiteLernen();
    };
    var det = $app.querySelector("details.erkl");
    if (det) det.ontoggle = function () { karte.erklOffen = det.open; };
    var pb = document.getElementById("pruefen");
    if (pb) pb.onclick = pruefen;
    var wb = document.getElementById("weiter");
    if (wb) { wb.onclick = weiter; wb.focus({ preventScroll: true }); }

    function pruefen() {
      if (!karte.gewaehlt.length || karte.geprueft) return;
      karte.geprueft = true;
      karte.korrekt = gleicheMenge(karte.gewaehlt, richtigeIds(q));
      fortschrittBuchen(q.key, karte.korrekt);
      lern.beantwortet++;
      if (karte.korrekt) lern.richtig++; else {
        lern.falsch++;
        lern.falschKeys[q.key] = true;
        lern.queue.splice(Math.min(WIEDERHOLEN_NACH, lern.queue.length), 0, q.key);
      }
      seiteLernen();
    }
    function weiter() { lern.aktuell = null; seiteLernen(); window.scrollTo(0, 0); }

    function taste(e) {
      if (e.ctrlKey || e.metaKey || e.altKey || !$dialog.hidden) return;
      var k = e.key.toUpperCase();
      if (k === "ENTER") { e.preventDefault(); karte.geprueft ? weiter() : pruefen(); return; }
      var i = k.charCodeAt(0) - 65;
      if (k.length === 1 && i >= 0 && i < karte.ordnung.length && !karte.geprueft) {
        karte.gewaehlt = auswahlUmschalten(q, karte.gewaehlt, karte.ordnung[i]);
        seiteLernen();
      }
    }
    document.addEventListener("keydown", taste);
    aufraeumen = function () { document.removeEventListener("keydown", taste); };
  }

  function lernZusammenfassung() {
    var falsch = Object.keys(lern.falschKeys);
    var html = '<div class="card result-head"><h1>Sitzung abgeschlossen</h1>';
    if (!lern.gesamt) {
      html += '<p class="muted">Für diese Auswahl gibt es keine Karten. Wähle auf der Startseite eine andere Auswahl.</p>';
    } else {
      html += '<p class="big">' + lern.gesamt + "</p><p class=\"muted\">Karten durchgearbeitet</p>" +
        "<p>" + lern.richtig + " Antworten richtig, " + lern.falsch + " falsch.</p>";
    }
    html += '<div class="btn-row" style="justify-content:center">' +
      (falsch.length ? '<button class="btn primary" id="nochmal">Die ' + falsch.length + " schwierigen Karten wiederholen</button>" : "") +
      '<a class="btn" href="#/">Zur Startseite</a></div></div>';
    $app.innerHTML = html;
    var nb = document.getElementById("nochmal");
    if (nb) nb.onclick = function () { lernSitzungStarten(falsch); seiteLernen(); };
  }

  // ---------- Prüfungssimulation ----------
  function pruefungStarten() {
    var auswahl = mischen(FRAGEN).slice(0, Math.min(PRUEFUNG_FRAGEN, FRAGEN.length));
    var ordnung = {}, antworten = {};
    auswahl.forEach(function (q) { ordnung[q.key] = reihenfolge(q, speicher.einstellungen.mischen); antworten[q.key] = []; });
    var jetzt = Date.now();
    speicher.laufend = {
      keys: auswahl.map(function (q) { return q.key; }),
      ordnung: ordnung, antworten: antworten, markiert: {},
      start: jetzt, ende: jetzt + PRUEFUNG_MINUTEN * 60 * 1000, index: 0
    };
    speichern();
  }

  function pruefungAblaufPruefen() {
    var l = speicher.laufend;
    if (l && Date.now() >= l.ende) { pruefungAbgeben(true); return true; }
    return false;
  }

  function pruefungAbgeben(zeitAbgelaufen) {
    var l = speicher.laufend;
    if (!l) return;
    var details = [], punkte = 0;
    l.keys.forEach(function (key) {
      var q = NACH_KEY[key];
      if (!q) return; // Frage wurde zwischenzeitlich aus den Daten entfernt
      var gew = l.antworten[key] || [];
      var korrekt = gleicheMenge(gew, richtigeIds(q));
      if (korrekt) punkte++;
      fortschrittBuchen(key, korrekt);
      details.push({ key: key, gewaehlt: gew, ordnung: l.ordnung[key], korrekt: korrekt });
    });
    var gesamt = details.length;
    var prozent = gesamt ? Math.round((punkte / gesamt) * 1000) / 10 : 0;
    var ende = Math.min(Date.now(), l.ende);
    speicher.ergebnis = {
      datum: Date.now(), punkte: punkte, gesamt: gesamt, prozent: prozent,
      dauer: ende - l.start, zeitAbgelaufen: !!zeitAbgelaufen, details: details
    };
    speicher.pruefungen.push({ datum: Date.now(), punkte: punkte, gesamt: gesamt, prozent: prozent });
    if (speicher.pruefungen.length > 50) speicher.pruefungen = speicher.pruefungen.slice(-50);
    speicher.laufend = null;
    speichern();
    if (location.hash !== "#/ergebnis") location.hash = "#/ergebnis";
  }

  function seitePruefung() {
    var l = speicher.laufend;
    if (!l) { location.hash = "#/"; return; }
    var idx = Math.max(0, Math.min(l.index || 0, l.keys.length - 1));
    var key = l.keys[idx], q = NACH_KEY[key];
    var gew = l.antworten[key] || [];
    var beantwortet = l.keys.filter(function (k) { return (l.antworten[k] || []).length; }).length;
    var zeigeUebersicht = seitePruefung.uebersicht;

    $extra.innerHTML = '<span class="timer" id="timer" role="timer" aria-label="Restzeit">' + zeitFormat(l.ende - Date.now()) + "</span>";

    var html = '<div class="card">' +
      '<div class="q-meta"><span><b>Frage ' + (idx + 1) + " von " + l.keys.length + "</b></span>" + hinweisChip(q) +
      (l.markiert[key] ? '<span class="chip hint">markiert</span>' : "") + "</div>" +
      '<div class="q-text">' + esc(q.frage) + "</div>" +
      antwortenHtml(q, l.ordnung[key], gew, "auswahl") + "</div>" +
      '<div class="btn-row">' +
      '<button class="btn" id="zurueck"' + (idx === 0 ? " disabled" : "") + ">‹ Zurück</button>" +
      '<button class="btn" id="markieren">' + (l.markiert[key] ? "Markierung entfernen" : "Markieren") + "</button>" +
      (idx < l.keys.length - 1 ? '<button class="btn primary grow" id="vor">Weiter ›</button>' :
        '<button class="btn primary grow" id="abgeben2">Prüfung abgeben</button>') +
      "</div>" +
      '<div class="card" style="margin-top:16px">' +
      '<div class="btn-row" style="justify-content:space-between;align-items:center">' +
      '<span class="muted small">' + beantwortet + " von " + l.keys.length + " beantwortet</span>" +
      '<button class="btn small" id="uebersicht">' + (zeigeUebersicht ? "Übersicht ausblenden" : "Übersicht zeigen") + "</button></div>" +
      (zeigeUebersicht ? '<div class="qgrid" style="margin-top:12px">' + l.keys.map(function (k, i) {
        var c = ((l.antworten[k] || []).length ? "answered " : "") + (l.markiert[k] ? "flagged " : "") + (i === idx ? "current" : "");
        return '<button class="' + c + '" data-i="' + i + '" aria-label="Frage ' + (i + 1) + '">' + (i + 1) + "</button>";
      }).join("") + '</div><p class="small muted" style="margin:8px 0 0">Blau = beantwortet, gelber Strich = markiert</p>' : "") +
      '<div class="btn-row" style="margin-top:12px"><button class="btn danger" id="abgeben">Prüfung abgeben</button>' +
      '<a class="btn" href="#/">Pausieren (Zeit läuft weiter)</a></div></div>';
    $app.innerHTML = html;

    function gehe(i) { l.index = i; speichern(); seitePruefung(); window.scrollTo(0, 0); }
    $app.querySelector(".answers").onclick = function (e) {
      var b = e.target.closest(".answer");
      if (!b) return;
      l.antworten[key] = auswahlUmschalten(q, gew, b.getAttribute("data-id"));
      speichern(); seitePruefung();
    };
    document.getElementById("zurueck").onclick = function () { gehe(idx - 1); };
    var vor = document.getElementById("vor");
    if (vor) vor.onclick = function () { gehe(idx + 1); };
    document.getElementById("markieren").onclick = function () {
      if (l.markiert[key]) delete l.markiert[key]; else l.markiert[key] = true;
      speichern(); seitePruefung();
    };
    document.getElementById("uebersicht").onclick = function () { seitePruefung.uebersicht = !zeigeUebersicht; seitePruefung(); };
    var grid = $app.querySelector(".qgrid");
    if (grid) grid.onclick = function (e) { var b = e.target.closest("[data-i]"); if (b) gehe(+b.getAttribute("data-i")); };
    function abgebenFragen() {
      var offen = l.keys.length - beantwortet;
      bestaetigen("Prüfung abgeben?",
        offen ? "Du hast <b>" + offen + "</b> Frage" + (offen === 1 ? "" : "n") + " noch nicht beantwortet. Unbeantwortete Fragen zählen als falsch." :
          "Alle Fragen sind beantwortet.", "Abgeben", "Weiter bearbeiten")
        .then(function (ok) { if (ok) pruefungAbgeben(false); });
    }
    document.getElementById("abgeben").onclick = abgebenFragen;
    var ab2 = document.getElementById("abgeben2");
    if (ab2) ab2.onclick = abgebenFragen;

    var timerEl = document.getElementById("timer");
    var iv = setInterval(function () {
      var rest = l.ende - Date.now();
      timerEl.textContent = zeitFormat(rest);
      timerEl.classList.toggle("low", rest < 5 * 60 * 1000);
      if (rest <= 0) { clearInterval(iv); $dialog.hidden = true; pruefungAbgeben(true); }
    }, 1000);
    timerEl.classList.toggle("low", l.ende - Date.now() < 5 * 60 * 1000);
    aufraeumen = function () { clearInterval(iv); };
  }

  function seiteErgebnis() {
    var e = speicher.ergebnis;
    if (!e) { location.hash = "#/"; return; }
    var verdict = e.prozent >= GRENZE_AUSZEICHNUNG ? '<span class="verdict distinction">Bestanden mit Auszeichnung</span>' :
      e.prozent >= GRENZE_BESTANDEN ? '<span class="verdict pass">Bestanden</span>' : '<span class="verdict fail">Nicht bestanden</span>';
    var falsch = e.details.filter(function (d) { return !d.korrekt; });
    var filter = seiteErgebnis.filter || "falsch";
    var liste = filter === "falsch" ? falsch : e.details;
    var benoetigt = Math.ceil(e.gesamt * GRENZE_BESTANDEN / 100);

    var html = '<div class="card result-head">' +
      (e.zeitAbgelaufen ? '<p class="chip hint">Die Zeit ist abgelaufen – die Prüfung wurde automatisch abgegeben.</p>' : "") +
      '<p class="big">' + String(e.prozent).replace(".", ",") + " %</p>" + verdict +
      "<p>" + e.punkte + " von " + e.gesamt + " Punkten · zum Bestehen nötig: " + benoetigt + "</p>" +
      '<p class="small muted">Bearbeitungszeit ' + zeitFormat(e.dauer) + " · " + datumFormat(e.datum) + "</p>" +
      '<div class="btn-row" style="justify-content:center">' +
      (falsch.length ? '<button class="btn primary" id="falsch-lernen">Falsche Fragen lernen (' + falsch.length + ")</button>" : "") +
      '<button class="btn" id="neu">Neue Prüfung</button><a class="btn" href="#/">Startseite</a></div></div>';

    html += '<div class="card"><h2>Auswertung</h2>' +
      '<div class="tabs"><button data-f="falsch" aria-pressed="' + (filter === "falsch") + '">Falsch (' + falsch.length + ")</button>" +
      '<button data-f="alle" aria-pressed="' + (filter === "alle") + '">Alle (' + e.details.length + ")</button></div>" +
      '<div class="qgrid" style="margin-bottom:16px">' + e.details.map(function (d, i) {
        return '<button class="' + (d.korrekt ? "r-ok" : "r-bad") + '" data-k="' + d.key + '" aria-label="Frage ' + (i + 1) + (d.korrekt ? " richtig" : " falsch") + '">' + (i + 1) + "</button>";
      }).join("") + "</div>";
    if (!liste.length) html += '<p class="muted">Keine falschen Antworten – stark!</p>';
    html += liste.map(function (d) {
      var q = NACH_KEY[d.key];
      if (!q) return "";
      var i = e.details.indexOf(d);
      return '<div class="review-item" id="r-' + d.key + '"><div class="q-meta"><b>Frage ' + (i + 1) + "</b>" +
        (d.korrekt ? '<span class="chip ok">richtig</span>' : '<span class="chip bad">' + (d.gewaehlt.length ? "falsch" : "nicht beantwortet") + "</span>") +
        hinweisChip(q) + '<span class="small">(Nr. ' + q.nr + ")</span></div>" +
        '<div class="q-text">' + esc(q.frage) + "</div>" + antwortenHtml(q, d.ordnung, d.gewaehlt, "aufloesung") +
        (erklaerungZu(q) ? erklaerungHtml(q, erklaerungZu(q), d.ordnung, { aufklappbar: true }) : "") + "</div>";
    }).join("") + "</div>";
    $app.innerHTML = html;

    $app.querySelector(".tabs").onclick = function (ev) {
      var b = ev.target.closest("[data-f]"); if (!b) return;
      seiteErgebnis.filter = b.getAttribute("data-f"); seiteErgebnis();
    };
    $app.querySelector(".qgrid").onclick = function (ev) {
      var b = ev.target.closest("[data-k]"); if (!b) return;
      var k = b.getAttribute("data-k");
      var ziel = document.getElementById("r-" + k);
      if (!ziel) { seiteErgebnis.filter = "alle"; seiteErgebnis(); ziel = document.getElementById("r-" + k); }
      if (ziel) ziel.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    var fl = document.getElementById("falsch-lernen");
    if (fl) fl.onclick = function () { lernSitzungStarten(falsch.map(function (d) { return d.key; })); location.hash = "#/lernen"; };
    document.getElementById("neu").onclick = function () { pruefungStarten(); location.hash = "#/pruefung"; };
  }

  // ---------- Erklärungen ----------
  // Zerlegt "Richtig (laut Lösung). Text" in Bewertung und Begründung
  function begruendung(text) {
    var m = /^(Richtig|Falsch)( \(laut Lösung\))?\.\s*/.exec(text);
    return m ? { richtig: m[1] === "Richtig", lautLoesung: !!m[2], text: text.slice(m[0].length) } : { richtig: null, text: text };
  }
  function fundstelleHtml(f) {
    var seiten = f.seiten.length > 1 ? "S. " + f.seiten.join(", ") : "S. " + f.seiten[0];
    return "<li><b>" + esc(f.buch) + "</b>, " + esc(f.kapitel || "") +
      (f.lektion ? " › Lektion „" + esc(f.lektion) + "“" : "") + ", <b>" + seiten + "</b></li>";
  }
  // ordnung: Reihenfolge der Antworten wie auf der Karte (Buchstaben passen dann zur Anzeige)
  function erklaerungHtml(q, e, ordnung, opt) {
    opt = opt || {};
    var inhalt =
      '<div class="erkl-block"><h3>Wo steht die Antwort?</h3><ul class="fund">' + e.fundstellen.map(fundstelleHtml).join("") + "</ul></div>" +
      '<div class="erkl-block"><h3>Warum richtig oder falsch?</h3><ul class="begr">' +
      ordnung.map(function (id, i) {
        var a = antwortVon(q, id), b = begruendung(e.antworten[id] || "");
        var ok = b.richtig === null ? a.richtig : b.richtig;
        return '<li class="' + (ok ? "r" : "f") + '"><span class="mark" aria-hidden="true">' + buchstabe(i) + "</span><div>" +
          '<span class="urteil">' + (ok ? "✓ Richtig" : "✗ Falsch") + (b.lautLoesung ? " (laut Lösung)" : "") + "</span> " +
          (opt.aufklappbar ? "" : '<span class="atext">' + esc(a.text) + "</span>") +
          "<p>" + esc(b.text) + "</p></div></li>";
      }).join("") + "</ul></div>" +
      (e.hinweis ? '<div class="erkl-hinweis"><b>Hinweis:</b> ' + esc(e.hinweis) + "</div>" : "") +
      '<div class="erkl-frage"><h3>Zum Nachdenken</h3><p>' + esc(e.offeneFrage) + "</p></div>";
    if (!opt.aufklappbar) return '<div class="erkl">' + inhalt + "</div>";
    return '<details class="erkl"' + (opt.offen ? " open" : "") + "><summary>Erklärung &amp; Fundstelle im Buch</summary>" + inhalt + "</details>";
  }

  function seiteErklaerungen(query) {
    var params = {};
    query.split("&").forEach(function (p) { var kv = p.split("="); if (kv[0]) params[kv[0]] = decodeURIComponent(kv[1] || ""); });
    $app.innerHTML = '<p class="muted">Lade Erklärungen …</p>';
    var meinAufruf = location.hash;
    Promise.all([datenLaden("original"), erklaerungenLaden()]).then(function (r) {
      if (location.hash !== meinAufruf) return;
      zeichnen(r[0].fragen, r[1]);
    }, function (err) {
      $app.innerHTML = '<div class="card"><h1>Erklärungen konnten nicht geladen werden</h1><p class="muted">' + esc(err.message || err) + "</p></div>";
    });

    function zeichnen(fragen, erkl) {
      var st = seiteErklaerungen.zustand || (seiteErklaerungen.zustand = { suche: "", filter: "alle" });
      var mitFortschritt = SET_ID === "original";
      var falschKeys = {};
      if (mitFortschritt) fragen.forEach(function (q) { var f = speicher.fortschritt[q.key]; if (f && f.falsch > 0) falschKeys[q.key] = true; });
      var nFalsch = Object.keys(falschKeys).length;
      if (!mitFortschritt || !nFalsch) st.filter = "alle";
      var ziel = params.nr ? +params.nr : null;
      if (ziel) st.suche = "";

      var bkeys = Object.keys(erkl.buecher);
      var html = '<div class="card"><h1>Erklärungen · Original-Fragen</h1>' +
        '<p class="muted">Zu jeder der ' + fragen.length + ' Original-Fragen: wo die Antwort im Buch steht, warum jede Antwort richtig oder falsch ist, und eine offene Frage zum Selbst-Beantworten.</p>' +
        '<ul class="small muted buecher">' + bkeys.map(function (b) { return "<li>" + esc(erkl.buecher[b]) + "</li>"; }).join("") + "</ul>" +
        '<p class="small muted">Seitenzahlen = gedruckte Seiten im Teilnehmerhandbuch. Die Begründungen sind eigene Kurzfassungen, keine Zitate.</p>' +
        '<input type="search" id="erkl-suche" class="suche" placeholder="Suchen, z. B. Orderbuch oder Frage 42" aria-label="Erklärungen durchsuchen" value="' + esc(st.suche) + '">' +
        (mitFortschritt && nFalsch ? '<div class="tabs" style="margin-top:10px"><button data-f="alle" aria-pressed="' + (st.filter === "alle") + '">Alle (' + fragen.length + ")</button>" +
          '<button data-f="falsch" aria-pressed="' + (st.filter === "falsch") + '">Schon mal falsch beantwortet (' + nFalsch + ")</button></div>" : "") +
        '<div class="btn-row" style="margin-top:10px"><button class="btn small" id="alle-auf">Alle aufklappen</button><button class="btn small" id="alle-zu">Alle zuklappen</button></div>' +
        "</div>" +
        '<div id="erkl-liste">' + fragen.map(function (q) {
          var e = erkl.nachKey[q.key];
          var ordnung = q.antworten.map(function (a) { return a.id; });
          var such = (q.nr + " " + q.frage + " " + q.antworten.map(function (a) { return a.text; }).join(" ") + " " +
            (e ? e.fundstellen.map(function (f) { return f.buch + " " + f.kapitel + " " + f.lektion; }).join(" ") : "")).toLowerCase();
          return '<details class="card erkl-eintrag" id="e-' + q.nr + '" data-key="' + q.key + '" data-such="' + esc(such) + '"' + (ziel === q.nr ? " open" : "") + ">" +
            '<summary><span class="nr">Frage ' + q.nr + "</span>" + (falschKeys[q.key] ? '<span class="chip bad">schon mal falsch</span>' : "") +
            '<span class="ftext">' + esc(q.frage) + "</span></summary>" +
            (e ? '<div class="erkl-quelle small muted">' + e.fundstellen.map(function (f) { return esc(f.buch) + " S. " + f.seiten.join(", "); }).join(" · ") + "</div>" +
              erklaerungHtml(q, e, ordnung, {}) : '<p class="muted">Zu dieser Frage gibt es noch keine Erklärung.</p>') +
            "</details>";
        }).join("") + '</div><p class="muted small" id="erkl-leer" hidden>Keine Frage gefunden.</p>';
      $app.innerHTML = html;

      var eintraege = $app.querySelectorAll(".erkl-eintrag");
      function filtern() {
        var w = st.suche.toLowerCase().trim(), n = 0;
        var nrSuche = /^(frage\s*)?(\d+)$/.exec(w);
        for (var i = 0; i < eintraege.length; i++) {
          var el = eintraege[i];
          var passt = nrSuche ? el.id === "e-" + nrSuche[2] : (!w || el.getAttribute("data-such").indexOf(w) >= 0);
          if (st.filter === "falsch" && !falschKeys[el.getAttribute("data-key")]) passt = false;
          el.hidden = !passt; if (passt) n++;
        }
        document.getElementById("erkl-leer").hidden = n > 0;
      }
      filtern();
      var suche = document.getElementById("erkl-suche");
      suche.oninput = function () { st.suche = suche.value; filtern(); };
      var tabs = $app.querySelector(".card .tabs");
      if (tabs) tabs.onclick = function (ev) {
        var b = ev.target.closest("[data-f]"); if (!b) return;
        st.filter = b.getAttribute("data-f");
        tabs.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
        filtern();
      };
      document.getElementById("alle-auf").onclick = function () { eintraege.forEach(function (d) { if (!d.hidden) d.open = true; }); };
      document.getElementById("alle-zu").onclick = function () { eintraege.forEach(function (d) { d.open = false; }); };
      if (ziel) {
        var z = document.getElementById("e-" + ziel);
        if (z) { z.hidden = false; z.scrollIntoView({ block: "start" }); }
      }
    }
  }

  // ---------- Fragenübersicht ----------
  function seiteFragen() {
    var filter = seiteFragen.filter || "alle";
    var liste = FRAGEN.filter(function (q) { return filter === "alle" || status(q.key) === filter; });
    var z = zaehlen(FRAGEN.map(function (q) { return q.key; }));
    var html = '<div class="card"><h1>Alle Fragen · ' + esc(SETS[SET_ID].kurz) + "</h1>" +
      '<div class="tabs">' + [["alle", "Alle", FRAGEN.length], ["neu", "Neu", z.neu], ["lernend", "In Arbeit", z.lernend], ["gelernt", "Gelernt", z.gelernt]].map(function (t) {
        return '<button data-f="' + t[0] + '" aria-pressed="' + (filter === t[0]) + '">' + t[1] + " (" + t[2] + ")</button>";
      }).join("") + "</div>" +
      '<table class="list"><thead><tr><th>Nr.</th><th>Frage</th><th>✓/✗</th></tr></thead><tbody>' +
      liste.map(function (q) {
        var f = fp(q.key), s = status(q.key);
        var chip = s === "gelernt" ? '<span class="chip ok">gelernt</span>' : s === "lernend" ? '<span class="chip hint">in Arbeit</span>' : '<span class="chip">neu</span>';
        return '<tr><td class="num">' + q.nr + "</td><td>" + esc(q.frage.length > 140 ? q.frage.slice(0, 140) + " …" : q.frage) + " " + chip +
          '</td><td class="num">' + f.richtig + " / " + f.falsch + "</td></tr>";
      }).join("") + "</tbody></table>" +
      '<div class="btn-row" style="margin-top:16px">' +
      (liste.length ? '<button class="btn primary" id="diese-lernen">Diese ' + liste.length + " lernen</button>" : "") +
      '<button class="btn danger" id="reset">Fortschritt zurücksetzen</button></div></div>';
    $app.innerHTML = html;

    $app.querySelector(".tabs").onclick = function (ev) {
      var b = ev.target.closest("[data-f]"); if (!b) return;
      seiteFragen.filter = b.getAttribute("data-f"); seiteFragen();
    };
    var dl = document.getElementById("diese-lernen");
    if (dl) dl.onclick = function () { lernSitzungStarten(liste.map(function (q) { return q.key; })); location.hash = "#/lernen"; };
    document.getElementById("reset").onclick = function () {
      bestaetigen("Fortschritt zurücksetzen?", "Alle Lernstände und Prüfungsergebnisse für „" + esc(SETS[SET_ID].name) + "“ auf diesem Gerät werden gelöscht. Das andere Fragenset bleibt unverändert.", "Zurücksetzen")
        .then(function (ok) {
          if (!ok) return;
          speicher.fortschritt = {}; speicher.pruefungen = []; speicher.ergebnis = null; speicher.laufend = null;
          speichern(); lern = null; toast("Fortschritt gelöscht"); seiteFragen();
        });
    };
  }

  // ---------- Start ----------
  window.addEventListener("hashchange", route);
  // Prüfung auch dann automatisch abgeben, wenn man gerade auf einer anderen Seite ist
  setInterval(function () {
    if (speicher && speicher.laufend && location.hash !== "#/pruefung" && Date.now() >= speicher.laufend.ende) pruefungAbgeben(true);
  }, 5000);
  window.addEventListener("storage", function (e) { if (e.key === SPEICHER_KEY) speicher = laden(); });

  function ladeFehler(err) {
    $app.innerHTML = '<div class="card"><h1>Fragen konnten nicht geladen werden</h1><p class="muted">' + esc(err.message || err) +
      '</p><p>Hinweis: Die App muss über einen Webserver (z. B. GitHub Pages) geöffnet werden, nicht als lokale Datei.</p>' +
      (SET_ID !== "original" || gespeichertesSet() !== "original" ? '<p><button class="btn" id="zum-original">Zu den Original-Fragen</button></p>' : "") + "</div>";
    var b = document.getElementById("zum-original");
    if (b) b.onclick = function () { setAktivieren("original").then(function () { location.hash = "#/"; route(); }, ladeFehler); };
  }
  setAktivieren(gespeichertesSet())
    .catch(function () { return setAktivieren("original"); })
    .then(route).catch(ladeFehler);

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    // Wenn ein neuer Service Worker eine ältere Version ablöst, Seite einmal neu laden,
    // damit sofort die neue App angezeigt wird (nicht beim allerersten Besuch).
    var hatteController = !!navigator.serviceWorker.controller, neuGeladen = false;
    navigator.serviceWorker.addEventListener("controllerchange", function () {
      if (!hatteController || neuGeladen) return;
      neuGeladen = true;
      location.reload();
    });
    navigator.serviceWorker.register("sw.js", { updateViaCache: "none" })
      .then(function (reg) { reg.update().catch(function () {}); })
      .catch(function () {});
  }
})();
