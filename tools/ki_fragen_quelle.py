"""Quelle der KI-generierten Übungsfragen (data/fragen_ki.json).

Die Fragen wurden auf Basis der Lernzusammenfassungen S4500 (Kapitel 1–8) und
S4520 (Kapitel 1–8) formuliert. Sie ergänzen die Originalfragen und sind keine
offiziellen Prüfungsfragen.

Aufruf:  python tools/ki_fragen_quelle.py
Schreibt data/fragen_ki.json neu. Richtige Antworten sind mit "X" markiert.
"""
import json
import os
import random
from datetime import date

# (Quelle, Frage, [(richtig, Antworttext), ...])
FRAGEN = [
    # ---------- S4500 Kapitel 1: Navigation ----------
    ("S4500 · Kapitel 1", "Welche der folgenden Prinzipien gehören zu den Designprinzipien von SAP Fiori?", [
        ("X", "Rollenbasiert"),
        ("X", "Einfach"),
        ("", "Transaktionsorientiert"),
        ("X", "Einheitlich"),
        ("", "Programmierbar"),
    ]),
    ("S4500 · Kapitel 1", "Sie möchten prüfen, welche Benutzer gerade mit aktiven Sitzungen im SAP-System angemeldet sind. Welche Transaktion verwenden Sie?", [
        ("X", "SM04"),
        ("", "SE16"),
        ("", "ME23N"),
        ("", "SU01"),
    ]),
    ("S4500 · Kapitel 1", "Welche Personalisierungsmöglichkeiten bietet Ihnen das SAP GUI?", [
        ("X", "Sie können Ihre Favoritenliste verwalten."),
        ("X", "Sie können sich im SAP Easy Access Menü die technischen Namen der Transaktionen anzeigen lassen."),
        ("", "Sie können Kachelgruppen anlegen und Themes für Ihre Kacheln auswählen."),
        ("", "Sie können die Transaktionscodes von Standardtransaktionen umbenennen."),
    ]),

    # ---------- S4500 Kapitel 2: Prozesse und Unternehmensstruktur ----------
    ("S4500 · Kapitel 2", "In welcher Reihenfolge laufen die Schritte des Beschaffungszyklus ab?", [
        ("X", "Bedarfsermittlung – Ermittlung der Bezugsquelle – Bestellungsbearbeitung – Bestellüberwachung – Wareneingang – Rechnungsprüfung – Zahlungsabwicklung"),
        ("", "Ermittlung der Bezugsquelle – Bedarfsermittlung – Bestellungsbearbeitung – Wareneingang – Bestellüberwachung – Rechnungsprüfung – Zahlungsabwicklung"),
        ("", "Bedarfsermittlung – Bestellungsbearbeitung – Ermittlung der Bezugsquelle – Bestellüberwachung – Rechnungsprüfung – Wareneingang – Zahlungsabwicklung"),
        ("", "Bedarfsermittlung – Ermittlung der Bezugsquelle – Bestellungsbearbeitung – Wareneingang – Zahlungsabwicklung – Rechnungsprüfung – Bestellüberwachung"),
    ]),
    ("S4500 · Kapitel 2", "Welche der folgenden Aussagen zur Einkäufergruppe sind richtig?", [
        ("X", "Eine Einkäufergruppe repräsentiert einzelne Einkäufer oder Teams, die für bestimmte Materialien oder Lieferanten zuständig sind."),
        ("X", "Die Einkäufergruppe ist nicht an andere Organisationseinheiten gebunden."),
        ("", "Jede Einkäufergruppe ist genau einem Werk fest zugeordnet."),
        ("", "Die Einkäufergruppe ist eine rechtlich eigenständige, bilanzierende Einheit."),
    ]),
    ("S4500 · Kapitel 2", "Bei welchem Sonderbeschaffungsprozess erhält ein externer Dienstleister beigestellte Komponenten, um damit ein Produkt zu fertigen oder zu veredeln?", [
        ("X", "Lohnbearbeitung"),
        ("", "Lieferantenkonsignation"),
        ("", "Umlagerung mit Umlagerungsbestellung"),
        ("", "Limitbestellung"),
    ]),

    # ---------- S4500 Kapitel 3: Einfacher Beschaffungsprozess ----------
    ("S4500 · Kapitel 3", "Welche Transaktionen verwenden Sie im einfachen Beschaffungsprozess für die drei Schritte Bestellung anlegen, Wareneingang buchen und Rechnung erfassen?", [
        ("X", "ME21N"),
        ("X", "MIGO"),
        ("X", "MIRO"),
        ("", "MM01"),
        ("", "ME11"),
    ]),
    ("S4500 · Kapitel 3", "Bei der Rechnungserfassung stellt das System Mengen- und Preisabweichungen fest, die die Toleranzgrenzen überschreiten. Wie reagiert das System?", [
        ("X", "Das System warnt den Benutzer und kann die Rechnung bei Bedarf automatisch zur Zahlung sperren."),
        ("", "Das System storniert die Rechnung automatisch."),
        ("", "Das System bucht den zugehörigen Wareneingang automatisch zurück."),
        ("", "Das System sendet die Bestellung automatisch erneut an den Lieferanten."),
    ]),
    ("S4500 · Kapitel 3", "Mit welchen Transaktionen können Sie eine bereits angelegte Bestellung ändern bzw. anzeigen?", [
        ("X", "ME22N"),
        ("X", "ME23N"),
        ("", "ME21N"),
        ("", "MIGO"),
    ]),

    # ---------- S4500 Kapitel 4: Stammdaten ----------
    ("S4500 · Kapitel 4", "Welche Aussagen zu den Methoden der Materialbewertung sind richtig?", [
        ("X", "Beim Standardpreis (S) bleibt der Preis konstant."),
        ("X", "Der gleitende Durchschnittspreis (V) passt sich mit jeder Wareneingangsbuchung an."),
        ("", "Der Standardpreis (S) wird mit jeder Wareneingangsbuchung neu berechnet."),
        ("", "Der gleitende Durchschnittspreis (V) bleibt konstant, bis er manuell geändert wird."),
    ]),
    ("S4500 · Kapitel 4", "Welche der folgenden Zuordnungen von Transaktion und Funktion sind richtig?", [
        ("X", "BP – Geschäftspartner pflegen"),
        ("X", "MM01 – Materialstammsatz anlegen"),
        ("X", "ME11 – Einkaufsinfosatz anlegen"),
        ("", "MIRO – Wareneingang buchen"),
        ("", "MIGO – Rechnung erfassen"),
    ]),
    ("S4500 · Kapitel 4", "Wodurch werden in SAP S/4HANA die bisher separaten Stammsätze für Lieferanten und Kunden ersetzt?", [
        ("X", "Durch den Geschäftspartner"),
        ("", "Durch den Einkaufsinfosatz"),
        ("", "Durch den Materialstammsatz"),
        ("", "Durch das Orderbuch"),
    ]),

    # ---------- S4500 Kapitel 5: Lager- und Verbrauchsmaterial ----------
    ("S4500 · Kapitel 5", "Welche Aussagen zur Beschaffung von Verbrauchsmaterial sind richtig?", [
        ("X", "Verbrauchsmaterial wird direkt auf ein Verbrauchskonto bzw. eine Kostenstelle oder ein anderes Kontierungsobjekt gebucht."),
        ("X", "Verbrauchsmaterial kann auch ohne Materialstammsatz beschafft werden."),
        ("", "Verbrauchsmaterial erhöht nach dem Wareneingang den Lagerbestand."),
        ("", "In der Bestellanforderung für Verbrauchsmaterial kann die Kontierung entfallen."),
    ]),
    ("S4500 · Kapitel 5", "Wann erfolgt bei einem unbewerteten Wareneingang die wertmäßige Buchung?", [
        ("X", "Erst mit der Rechnungserfassung"),
        ("", "Direkt mit dem Wareneingang auf ein Bestandskonto"),
        ("", "Bereits beim Anlegen der Bestellung"),
        ("", "Erst mit der Zahlung an den Lieferanten"),
    ]),
    ("S4500 · Kapitel 5", "Aus welchen Quellen kann die Preisfindung beim Anlegen einer Bestellung erfolgen?", [
        ("X", "Aus Einkaufsinfosätzen"),
        ("X", "Aus Rahmenverträgen"),
        ("", "Aus der Materialart"),
        ("", "Aus dem Lagerort"),
    ]),

    # ---------- S4500 Kapitel 6: Self-Service-Beschaffung ----------
    ("S4500 · Kapitel 6", "Welche Funktionen bietet die SAP-Fiori-App „Meine Bestellanforderungen – Neu“?", [
        ("X", "Neue Bestellanforderungen für Materialien oder Dienstleistungen anlegen"),
        ("X", "Bearbeitungsstatus und Folgebelege einer Anforderung anzeigen"),
        ("X", "Rücklieferungen bei fehlerhaften oder beschädigten Waren durchführen"),
        ("", "Freigabestrategien im Customizing konfigurieren"),
        ("", "Lieferantenrechnungen buchen"),
    ]),
    ("S4500 · Kapitel 6", "Auf welche Weise können Sie in der Self-Service-Beschaffung eine neue Bestellanforderungsposition erfassen?", [
        ("X", "Durch Auswahl eines Materials aus einem Katalog"),
        ("X", "Durch direkte Eingabe einer Materialnummer"),
        ("X", "Als Freitextposition für Materialien oder Dienstleistungen ohne Stammsatz"),
        ("", "Durch Hochladen einer Lieferantenrechnung"),
        ("", "Durch Übernahme aus der Lieferantenbewertung"),
    ]),
    ("S4500 · Kapitel 6", "Wer bestätigt im Self-Service-Beschaffungsprozess den Wareneingang, und mit welcher App?", [
        ("X", "Der anfordernde Mitarbeiter mit der App „Wareneingang bestätigen – Neu“"),
        ("", "Der Einkäufer mit der Transaktion ME21N"),
        ("", "Der Rechnungsprüfer mit der Transaktion MIRO"),
        ("", "Der Lieferant mit der App „Lieferantenrechnung anlegen“"),
    ]),
    ("S4500 · Kapitel 6", "Welche Möglichkeiten haben Sie in der App „Wareneingang bestätigen – Neu“?", [
        ("X", "Den Wareneingang für eine vollständige Lieferung bestätigen"),
        ("X", "Den Wareneingang für eine Teillieferung bestätigen"),
        ("X", "Das Endlieferungskennzeichen setzen"),
        ("", "Die Bestellung an einen anderen Lieferanten umleiten"),
        ("", "Der Bestellanforderung eine Bezugsquelle zuordnen"),
    ]),

    # ---------- S4500 Kapitel 7: Erweiterte Transaktionen ----------
    ("S4500 · Kapitel 7", "Für welche Werke ist ein Zentralkontrakt gültig?", [
        ("X", "Für alle Werke der Einkaufsorganisation"),
        ("", "Nur für genau ein Werk"),
        ("", "Nur für das Werk, in dem der Kontrakt angelegt wurde, und dessen Lagerorte"),
        ("", "Nur für Werke, die einem anderen Buchungskreis zugeordnet sind"),
    ]),
    ("S4500 · Kapitel 7", "In welche Bestandsarten können Sie einen Wareneingang mit der Transaktion MIGO buchen?", [
        ("X", "Frei verwendbarer Bestand"),
        ("X", "Qualitätsprüfbestand"),
        ("X", "Gesperrter Bestand"),
        ("", "Bestellbestand"),
        ("", "Kontraktbestand"),
    ]),
    ("S4500 · Kapitel 7", "Welche Belege können Sie mit der Transaktion MIRO erfassen?", [
        ("X", "Rechnungen"),
        ("X", "Gutschriften"),
        ("X", "Nachträgliche Belastungen"),
        ("", "Wareneingänge"),
        ("", "Bestellanforderungen"),
    ]),
    ("S4500 · Kapitel 7", "Mit welcher Transaktion legen Sie einen Einkaufskontrakt an?", [
        ("X", "ME31K"),
        ("", "ME59N"),
        ("", "ME51N"),
        ("", "ME31L"),
    ]),

    # ---------- S4500 Kapitel 8: Automatisierte Beschaffung ----------
    ("S4500 · Kapitel 8", "Welche Voraussetzungen müssen für die automatische Erzeugung von Bestellungen aus Bestellanforderungen erfüllt sein?", [
        ("X", "Im Materialstammsatz ist das Kennzeichen für automatische Bestellung gesetzt."),
        ("X", "Im Lieferantenstammsatz ist das Kennzeichen für automatische Bestellung gesetzt."),
        ("X", "Es gibt eine gültige Bezugsquelle, z. B. einen Einkaufsinfosatz, Kontrakt oder Lieferplan."),
        ("", "In der Bestellposition ist die Wareneingangsabrechnung aktiviert."),
        ("", "Das Material wird in den Qualitätsprüfbestand gebucht."),
    ]),
    ("S4500 · Kapitel 8", "Welche Voraussetzungen gelten für die automatische Wareneingangsabrechnung?", [
        ("X", "Im Lieferantenstammsatz ist das Kennzeichen für automatische Abrechnung gesetzt."),
        ("X", "In der Bestellposition ist die Wareneingangsabrechnung aktiviert."),
        ("", "Im Materialstammsatz ist das Kennzeichen für automatische Bestellung gesetzt."),
        ("", "Die Bestellung muss über ein Freigabeverfahren genehmigt worden sein."),
    ]),
    ("S4500 · Kapitel 8", "Welche Aussagen zur Materialbedarfsplanung (MRP) sind richtig?", [
        ("X", "MRP Live ist für SAP HANA optimiert und verarbeitet große Datenmengen effizient."),
        ("X", "Die klassische MRP ist flexibel, aber langsamer als MRP Live."),
        ("", "Bei fremdbeschafften Materialien muss die Bezugsquelle immer nach dem MRP-Lauf manuell zugeordnet werden."),
        ("", "MRP erzeugt ausschließlich Bestellungen, niemals Bestellanforderungen."),
    ]),

    # ---------- S4520 Kapitel 1: Stammdaten der Einkaufsabwicklung ----------
    ("S4520 · Kapitel 1", "Welche der folgenden Kürzel bezeichnen spezielle Materialarten?", [
        ("X", "NLAG"),
        ("X", "UNBW"),
        ("X", "SERV"),
        ("", "MEKE"),
        ("", "OMEB"),
    ]),
    ("S4520 · Kapitel 1", "Welche der folgenden Partnerrollen werden typischerweise im Lieferantenstammsatz gepflegt?", [
        ("X", "Bestelladresse"),
        ("X", "Warenlieferant"),
        ("X", "Rechnungssteller"),
        ("", "Einkäufergruppe"),
        ("", "Kostenstelle"),
    ]),
    ("S4520 · Kapitel 1", "Was bestimmt der Pflegestatus eines Materialstammsatzes?", [
        ("X", "Ob der Materialstammsatz für bestimmte Prozesse, z. B. das Anlegen von Bestellungen, genutzt werden kann"),
        ("", "Welcher Nummernkreis für das Material verwendet wird"),
        ("", "Ob das Material mit Standardpreis oder gleitendem Durchschnittspreis bewertet wird"),
        ("", "Welcher Einkaufsorganisation das Material zugeordnet ist"),
    ]),

    # ---------- S4520 Kapitel 2: Bezugsquellen und Konditionen ----------
    ("S4520 · Kapitel 2", "Was ist im Kalkulationsschema des Einkaufs hinterlegt?", [
        ("X", "Die Regeln für die Preisfindung, z. B. für Bruttopreis, Nettopreis und Effektivpreis"),
        ("", "Die Freigabestrategie für Bestellungen"),
        ("", "Die Nummernkreise für Einkaufsbelege"),
        ("", "Die Orderbuchsätze für ein Material"),
    ]),
    ("S4520 · Kapitel 2", "Welche Aussagen zu Lieferplänen mit und ohne Abrufdokumentation sind richtig?", [
        ("X", "Bei Lieferplänen ohne Abrufdokumentation werden die Lieferplaneinteilungen direkt an den Lieferanten übertragen."),
        ("X", "Bei Lieferplänen mit Abrufdokumentation dokumentiert das System jede übermittelte Einteilung und speichert die Abrufdetails."),
        ("", "Lieferpläne sind kurzfristige Einmalvereinbarungen ohne festgelegte Mengen und Termine."),
        ("", "Bei Lieferplänen mit Abrufdokumentation werden keine Einteilungen an den Lieferanten übermittelt."),
    ]),
    ("S4520 · Kapitel 2", "Welche Transaktionen verwenden Sie für die Arbeit mit Lieferplänen?", [
        ("X", "ME31L"),
        ("X", "ME32L"),
        ("X", "ME33L"),
        ("", "ME31K"),
        ("", "MEKP"),
    ]),

    # ---------- S4520 Kapitel 3: Bezugsquellenfindung ----------
    ("S4520 · Kapitel 3", "Wo können Bezugsquellen gesperrt werden?", [
        ("X", "Zentral im Lieferantenstammsatz"),
        ("X", "Im Orderbuch"),
        ("", "Im Kalkulationsschema"),
        ("", "In der Materialart"),
    ]),
    ("S4520 · Kapitel 3", "Welche der folgenden Zuordnungen von Transaktion und Funktion in der Bezugsquellenfindung sind richtig?", [
        ("X", "ME01 – Orderbuch pflegen"),
        ("X", "ME06 – Orderbuch analysieren"),
        ("X", "MEQ1 – Quotierung pflegen"),
        ("", "ME56 – Lieferanten sperren"),
        ("", "MK05 – Bestellanforderungen bearbeiten"),
    ]),
    ("S4520 · Kapitel 3", "Wofür werden Kataloge im Rahmen der Bezugsquellenfindung eingesetzt?", [
        ("X", "Sie ermöglichen Self-Service-Bestellungen direkt aus einer vordefinierten Auswahl."),
        ("", "Sie verteilen Bedarfe nach Quoten auf mehrere Bezugsquellen."),
        ("", "Sie sperren Lieferanten zentral für alle Werke."),
        ("", "Sie ersetzen Einkaufsinfosätze bei der Preisfindung."),
    ]),

    # ---------- S4520 Kapitel 4: Optimierte Einkaufsabwicklung ----------
    ("S4520 · Kapitel 4", "Welche der folgenden Zuordnungen von Transaktion und Funktion in der Einkaufsabwicklung sind richtig?", [
        ("X", "ME58 – Bestellung über Zuordnungsliste anlegen"),
        ("X", "ME2A – Bestellüberwachung"),
        ("X", "ME91F – Bestellungen mahnen"),
        ("", "ME59N – Bezugsquelle zuordnen"),
        ("", "ME56 – Automatische Bestellerzeugung"),
    ]),
    ("S4520 · Kapitel 4", "Welche Aufgabe hat die Situationsverarbeitung im Einkauf?", [
        ("X", "Sie erkennt kritische Geschäftsereignisse automatisch."),
        ("", "Sie gibt Bestellungen automatisch frei."),
        ("", "Sie berechnet die Gesamtbewertung von Lieferanten."),
        ("", "Sie ersetzt die Materialbedarfsplanung."),
    ]),
    ("S4520 · Kapitel 4", "Mit welchen SAP-Fiori-Apps unterstützen Sie die Überwachung von Bestellungen?", [
        ("X", "Lieferantenbestätigungen überwachen"),
        ("X", "Mahnerinnerung für Bestellung – Erweitert"),
        ("", "Lieferantenbewertung nach Fragebogen"),
        ("", "Material anlegen"),
    ]),

    # ---------- S4520 Kapitel 5: Belegfreigabeverfahren ----------
    ("S4520 · Kapitel 5", "Welche Freigabearten gibt es bei Bestellanforderungen?", [
        ("X", "Positionsfreigabe: Jede Position wird einzeln geprüft."),
        ("X", "Gesamtfreigabe: Die gesamte Bestellanforderung muss genehmigt werden."),
        ("", "Lieferantenfreigabe: Der Lieferant genehmigt die Bestellanforderung."),
        ("", "Werksfreigabe: Das anfordernde Werk genehmigt die Bestellanforderung selbst."),
    ]),
    ("S4520 · Kapitel 5", "Welche der folgenden Zuordnungen von Transaktion und Freigabefunktion sind richtig?", [
        ("X", "ME29N – Bestellung freigeben"),
        ("X", "ME28 – Bestellungen gesammelt freigeben"),
        ("X", "ME35K – Kontrakt freigeben"),
        ("", "ME54N – Lieferplan freigeben"),
        ("", "ME55 – Einzelfreigabe von Bestellanforderungen"),
    ]),
    ("S4520 · Kapitel 5", "Welche Aussagen zu flexiblen Workflows im Einkauf sind richtig?", [
        ("X", "Flexible Workflows können klassische Freigabeverfahren ersetzen."),
        ("X", "Die Genehmigung kann über die SAP Fiori Inbox erfolgen."),
        ("", "Flexible Workflows können nur in der Transaktion ME54N bearbeitet werden."),
        ("", "Flexible Workflows sind nur für Kontrakte verfügbar."),
    ]),

    # ---------- S4520 Kapitel 6: Besondere Beschaffungsprozesse ----------
    ("S4520 · Kapitel 6", "Ein IT-Projekt soll in mehreren Teilschritten abgerechnet werden, unabhängig vom Wareneingang. Was verwenden Sie?", [
        ("X", "Einen Teilrechnungsplan"),
        ("", "Einen periodischen Rechnungsplan"),
        ("", "Einen Lieferplan mit Abrufdokumentation"),
        ("", "Eine Lieferantenkonsignation"),
    ]),
    ("S4520 · Kapitel 6", "Mit welchen Transaktionen arbeiten Sie bei Rechnungsplänen?", [
        ("X", "MRIS – Rechnungspläne abrechnen"),
        ("X", "MLRP – Rechnungsplan-Termine aktualisieren"),
        ("", "ME2ON – Rechnungspläne anlegen"),
        ("", "ME2DP – Rechnungspläne sperren"),
    ]),
    ("S4520 · Kapitel 6", "Sie möchten den Lohnbearbeitungsbestand prüfen. Welche Transaktion bzw. SAP-Fiori-App verwenden Sie?", [
        ("X", "ME2ON bzw. die App „Lohnbearbeitungs-Cockpit“"),
        ("", "ME2DP bzw. die App „Bestellanzahlungen überwachen“"),
        ("", "MRIS bzw. die App „Rechnungsplanabrechnung anlegen“"),
        ("", "ME2A bzw. die App „Lieferantenbestätigungen überwachen“"),
    ]),

    # ---------- S4520 Kapitel 7: Customizing ----------
    ("S4520 · Kapitel 7", "Welche Einstellungen nehmen Sie bei Belegarten im Einkauf vor?", [
        ("X", "Das Positionsnummernintervall"),
        ("X", "Die Nummernkreisintervalle für interne und externe Nummernvergabe"),
        ("X", "Den Feldauswahlschlüssel"),
        ("", "Die Freigabestrategie"),
        ("", "Die Partnerrollen des Lieferanten"),
    ]),
    ("S4520 · Kapitel 7", "Welche Eigenschaften kann ein Feld in einem Einkaufsbeleg über die Feldauswahl erhalten?", [
        ("X", "Ausgeblendet"),
        ("X", "Nur Anzeige"),
        ("X", "Pflichtfeld"),
        ("", "Verschlüsselt"),
        ("", "Nur für den Lieferanten sichtbar"),
    ]),
    ("S4520 · Kapitel 7", "Mit welchem Benutzerparameter legen Sie Funktionsberechtigungen für Einkäufer fest, z. B. eine Einschränkung der Preisänderung?", [
        ("X", "EFB"),
        ("", "EVO"),
        ("", "OMT4"),
        ("", "OMSR"),
    ]),

    # ---------- S4520 Kapitel 8: Lieferantenbewertung ----------
    ("S4520 · Kapitel 8", "Welche Hard Facts fließen in die Gesamtbewertung eines Lieferanten ein?", [
        ("X", "Preis"),
        ("X", "Zeit"),
        ("X", "Menge"),
        ("", "Fragebogen"),
        ("", "Anzahl der Mitarbeiter des Lieferanten"),
    ]),
    ("S4520 · Kapitel 8", "Was misst die Lieferantenbewertung nach Zeit?", [
        ("X", "Zeitdifferenzen zwischen Bestell- und Lieferdatum"),
        ("", "Abweichungen zwischen bestellter und gelieferter Menge"),
        ("", "Abweichungen zwischen bestellten und abgerechneten Beträgen"),
        ("", "Die Dauer der Rechnungsprüfung"),
    ]),
    ("S4520 · Kapitel 8", "Worauf basiert die Lieferantenbewertung nach Qualität?", [
        ("X", "Auf den Prüfergebnissen von Wareneingängen (Prüflose)"),
        ("X", "Auf Qualitätsmeldungen, z. B. Beschwerden und Qualitätsabweichungen"),
        ("", "Auf den Preisabweichungen in der Rechnungsprüfung"),
        ("", "Auf der Anzahl der Bestellungen pro Jahr"),
    ]),
]


def main():
    fragen = []
    for nr, (quelle, frage, antworten) in enumerate(FRAGEN, start=1):
        assert 3 <= len(antworten) <= 6, (nr, frage)
        anz = sum(1 for r, _ in antworten if r == "X")
        # Richtige Antworten stehen im Quelltext oben; fest gemischt, damit die
        # Reihenfolge auch bei ausgeschaltetem Mischen nichts verrät.
        antworten = list(antworten)
        random.Random(nr).shuffle(antworten)
        assert 1 <= anz < len(antworten), (nr, frage)
        fragen.append({
            "id": nr,
            "nr": nr,
            "quelle": quelle,
            "frage": frage,
            "antworten": [{"id": chr(65 + i), "text": t, "richtig": r == "X"} for i, (r, t) in enumerate(antworten)],
            "anzahlRichtig": anz,
        })
    texte = [f["frage"] for f in fragen]
    assert len(texte) == len(set(texte)), "doppelte Frage"
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "fragen_ki.json")
    with open(ziel, "w", encoding="utf-8") as fh:
        json.dump({
            "quelle": "KI-generiert aus den Lernzusammenfassungen S4500 und S4520 (Kapitel 1–8)",
            "erstellt": date.today().isoformat(),
            "fragen": fragen,
        }, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    verteilung = {}
    for f in fragen:
        verteilung[f["anzahlRichtig"]] = verteilung.get(f["anzahlRichtig"], 0) + 1
    print(f"{len(fragen)} Fragen geschrieben nach {os.path.normpath(ziel)}; richtige Antworten pro Frage: {verteilung}")


if __name__ == "__main__":
    main()
