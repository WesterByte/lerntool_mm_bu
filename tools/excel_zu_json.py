#!/usr/bin/env python3
"""Wandelt die Fragen-Excel in data/fragen.json für das Lerntool um.

Aufruf (im Repo-Ordner):
    pip install openpyxl
    python tools/excel_zu_json.py "Pfad/zur/Datei.xlsx"

Erwarteter Aufbau der Excel (erstes Tabellenblatt):
    Spalte D: Fragetext (beginnt meist mit "12. ...") bzw. Antwort ("A. ...")
    Spalte G: "X" bei jeder richtigen Antwort
Alle anderen Spalten werden ignoriert.

Die Anzahl richtiger Antworten wird aus den X-Markierungen berechnet.
Hinweise wie "Auf diese Frage gibt es 2 richtige Antworten" werden aus dem
Fragetext entfernt (die App zeigt den Hinweis selbst an). Weicht ein solcher
Hinweis von der Zahl der X-Markierungen ab, gibt das Skript eine Warnung aus.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("Bitte zuerst installieren:  pip install openpyxl")

SPALTE_TEXT = 4      # D
SPALTE_RICHTIG = 7   # G

RE_ANTWORT = re.compile(r"^([A-Z])\.\s*(.*)$", re.S)
RE_FRAGE_NR = re.compile(r"^(\d+)\.\s*(.*)$", re.S)
RE_HINWEIS = re.compile(
    r"\s*(Hinweis:\s*Auf diese Frage gibt es\s*(\d+)\s*richtige Antworten\.?"
    r"|(\d+)\s*richtige Antworten\.?)\s*$",
    re.I,
)


def bereinigen(text):
    text = str(text).replace("\r", "").strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    quelle = Path(sys.argv[1])
    ziel = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "data" / "fragen.json"

    ws = openpyxl.load_workbook(quelle, data_only=True).worksheets[0]
    fragen, aktuell, warnungen = [], None, []

    for zeile in range(2, ws.max_row + 1):
        roh = ws.cell(zeile, SPALTE_TEXT).value
        if roh is None or not str(roh).strip():
            continue
        text = bereinigen(roh)
        markierung = ws.cell(zeile, SPALTE_RICHTIG).value
        richtig = markierung is not None and str(markierung).strip().lower() == "x"

        m = RE_ANTWORT.match(text)
        if m and aktuell is not None:
            aktuell["antworten"].append({"id": m.group(1), "text": m.group(2).strip(), "richtig": richtig})
            continue

        # Neue Frage (mit oder ohne Nummer)
        nr = None
        m = RE_FRAGE_NR.match(text)
        if m:
            nr, text = int(m.group(1)), m.group(2)
        hinweis = None
        h = RE_HINWEIS.search(text)
        if h:
            hinweis = int(h.group(2) or h.group(3))
            text = text[: h.start()].strip()
        aktuell = {"nr": nr, "frage": text.strip(), "antworten": [], "_zeile": zeile, "_hinweis": hinweis}
        fragen.append(aktuell)

    ausgabe = []
    letzte_nr = 0
    for i, f in enumerate(fragen, start=1):
        anz = sum(a["richtig"] for a in f["antworten"])
        bez = f"Frage {f['nr'] or '(ohne Nr.)'} (Excel-Zeile {f['_zeile']})"
        if len(f["antworten"]) < 2:
            warnungen.append(f"{bez}: weniger als 2 Antworten – übersprungen")
            continue
        if anz == 0:
            warnungen.append(f"{bez}: keine richtige Antwort markiert – übersprungen")
            continue
        if f["_hinweis"] and f["_hinweis"] != anz:
            warnungen.append(f"{bez}: Text sagt {f['_hinweis']} richtige, markiert sind {anz} (es gilt die Markierung)")
        if f["nr"] is None:
            f["nr"] = letzte_nr + 1
            warnungen.append(f"{bez}: Frage hat keine Nummer – Nr. {f['nr']} angenommen")
        letzte_nr = f["nr"]
        ausgabe.append({
            "id": i,
            "nr": f["nr"],
            "frage": f["frage"],
            "antworten": f["antworten"],
            "anzahlRichtig": anz,
        })

    daten = {"quelle": quelle.name, "erstellt": date.today().isoformat(), "fragen": ausgabe}
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(ausgabe)} Fragen nach {ziel} geschrieben.")
    for w in warnungen:
        print("WARNUNG:", w)


if __name__ == "__main__":
    main()
