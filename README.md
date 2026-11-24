# Karteikarten-Lerntool

Eine kleine Web-App zum Lernen der Multiple-Choice-Fragen aus der Excel-Datei.
Läuft im Browser auf PC, Android und iPhone, ohne Anmeldung. Der Lernfortschritt
wird nur lokal im Browser des jeweiligen Geräts gespeichert.

## Funktionen

- **Lernmodus:** Karten durchgehen, sofortiges Feedback. Falsch beantwortete Karten
  kommen nach drei weiteren Karten erneut und beim nächsten Lernen zuerst. Eine Karte
  gilt als „gelernt“, wenn sie 3× hintereinander richtig beantwortet wurde.
- **Prüfungssimulation:** 60 zufällige Fragen, 90-Minuten-Timer, automatische Abgabe
  bei Ablauf. Keine Teilpunkte: eine Frage zählt nur, wenn alle Antworten exakt stimmen.
  Bestanden ab 55 %, mit Auszeichnung ab 75 %. Auswertung mit Fehlern und richtigen Lösungen.
- **Zwei Fragensets**, auf der Startseite umschaltbar:
  - *Original-Fragen* (`data/fragen.json`, 89 Fragen aus der Excel): Prüfung mit 60 Fragen in 90 Minuten.
  - *Übungsfragen (KI-generiert)* (`data/fragen_ki.json`, 50 Fragen aus den Lernzusammenfassungen
    S4500/S4520, Kapitel 1–8): Prüfung mit allen 50 Fragen in 75 Minuten (gleiches Tempo, 1,5 Min./Frage).
  Lernstand und Prüfungen werden je Set getrennt gespeichert (`lerntool.v1` bzw. `lerntool.ki.v1`).
- Hinweis „X richtige Antworten“ bei Fragen mit mehreren richtigen Antworten.
- Als App installierbar („Zum Home-Bildschirm“) und offline nutzbar.

## Nutzen / Teilen

Nach dem Einschalten von GitHub Pages ist die App erreichbar unter:
`https://westerbyte.github.io/lerntool_mm_bu/`

**Auf dem Handy installieren:**
- iPhone (Safari): Teilen-Symbol → „Zum Home-Bildschirm“
- Android (Chrome): Menü ⋮ → „App installieren“ bzw. „Zum Startbildschirm hinzufügen“

## GitHub Pages einschalten (einmalig)

1. Im Repository oben auf **Settings** klicken.
2. Links im Menü **Pages** wählen.
3. Unter „Build and deployment“ → **Source**: „Deploy from a branch“.
4. **Branch**: `main`, Ordner `/ (root)` → **Save**.
5. Nach 1–2 Minuten erscheint oben der Link zur Seite.

## Fragen aktualisieren

Die Fragen liegen in `data/fragen.json` und werden aus der Excel erzeugt:

```bash
pip install openpyxl
python tools/excel_zu_json.py "Pfad/zur/KeyUser_Tool.xlsx"
```

Erwartet wird: Spalte D = Frage („12. …“) bzw. Antwort („A. …“), Spalte G = „X“ bei
richtigen Antworten. Die Zahl richtiger Antworten wird aus den X-Markierungen berechnet.
Das Skript meldet Auffälligkeiten (z. B. Fragen ohne Nummer oder ohne richtige Antwort).

Danach `data/fragen.json` committen. Der Lernfortschritt bleibt erhalten, solange der
Fragetext gleich bleibt. Wenn `app.js` oder `style.css` geändert werden, in `sw.js` die
Versionsnummer bei `CACHE` erhöhen, damit installierte Apps die neue Version laden.

## KI-Übungsfragen bearbeiten

Die Übungsfragen stehen lesbar in `tools/ki_fragen_quelle.py` (richtige Antworten mit „X“).
Nach einer Änderung `python tools/ki_fragen_quelle.py` ausführen und `data/fragen_ki.json` committen.

## Lokal ausprobieren

```bash
python -m http.server 8000
```
Dann http://localhost:8000 öffnen (direktes Öffnen der HTML-Datei funktioniert nicht,
weil die Fragen per `fetch` geladen werden).
