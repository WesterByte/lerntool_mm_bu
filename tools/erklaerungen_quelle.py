# -*- coding: utf-8 -*-
"""Erklärungen zu den 89 Original-Fragen (Quelle für data/erklaerungen.json).

Pro Frage (Schlüssel = Nummer in data/fragen.json):
  ref    = Fundstellen als (Buch, Seite); Kapitel und Lektion werden aus dem
           Inhaltsverzeichnis unten ergänzt. Seiten = gedruckte Seitenzahlen.
  A, B … = kurze Begründung je Antwort, beginnt mit „Richtig“ oder „Falsch“.
  frage  = offene Frage zum Selbst-Beantworten.
  hinweis (optional) = Abweichung zwischen Buch und Lösungsschlüssel o. Ä.

Bewusst keine wörtlichen Auszüge aus den Schulungsunterlagen, nur Fundstellen
und eigene Kurzbegründungen. Die PDFs selbst gehören nicht ins Repository.

Aufruf:  python tools/erklaerungen_quelle.py
Prüft, dass jede Antwort eine Begründung hat und „Richtig/Falsch“ zum
Lösungsschlüssel in data/fragen.json passt, und schreibt data/erklaerungen.json.
"""
import json
import os
import sys

BUECHER = {
    "S4500": "S4500 – Geschäftsprozesse in SAP S/4HANA Sourcing and Procurement (Teilnehmerhandbuch, Version 26)",
    "S4520": "S4520 – Einkauf in SAP S/4HANA (Teilnehmerhandbuch, Version 26)",
}

TOC = {
  "S4500": [
    ("K", 1, "Kapitel 1: Navigation in SAP S/4HANA"),
    ("L", 2, "Identifizieren der SAP-Fiori-Benutzererfahrung"),
    ("L", 13, "Arbeiten mit dem SAP GUI"),
    ("K", 25, "Kapitel 2: Prozesse und Unternehmensstruktur in der Beschaffung"),
    ("L", 27, "Beschaffungsprozesse beschreiben"),
    ("L", 32, "Identifizierung der Organisationseinheiten in der Beschaffung"),
    ("K", 45, "Kapitel 3: Einfacher Beschaffungsprozess"),
    ("L", 46, "Eine Bestellung anlegen"),
    ("L", 57, "Einen Wareneingang buchen"),
    ("L", 67, "Eine Rechnung erfassen"),
    ("K", 83, "Kapitel 4: Stammdaten der Beschaffung"),
    ("L", 85, "Geschäftspartner-Stammdaten pflegen"),
    ("L", 103, "Materialstammdaten pflegen"),
    ("L", 127, "Einkaufsinfosatz pflegen"),
    ("L", 142, "Materialbewertung analysieren"),
    ("K", 177, "Kapitel 5: Lagermaterial im Vergleich zu Verbrauchsmaterial"),
    ("L", 179, "Vergleich der Beschaffungsprozesse für Lager- und Verbrauchsmaterial"),
    ("L", 183, "Bestellanforderung anlegen"),
    ("L", 199, "Bestellungen mit Bezug zu Bestellanforderungen anlegen"),
    ("L", 212, "Bewertete und unbewertete Wareneingänge erfassen"),
    ("K", 241, "Kapitel 6: Anforderung per Self-Service"),
    ("L", 242, "Einen Self-Service-Prozess ausführen"),
    ("L", 254, "Wareneingang bestätigen"),
    ("K", 267, "Kapitel 7: Erweiterte Transaktionen in der Beschaffung"),
    ("L", 269, "Einen Einkaufskontrakt pflegen"),
    ("L", 277, "Eine Bestellanforderung mit Bezugsquellenfindung anlegen"),
    ("L", 294, "Die erweiterte Transaktion zum Anlegen von Bestellungen verwenden"),
    ("L", 311, "Die erweiterte Transaktion für den Wareneingang verwenden"),
    ("L", 324, "Die erweiterte Transaktion zur Rechnungsprüfung verwenden"),
    ("K", 341, "Kapitel 8: Automatisierter Beschaffungsprozess"),
    ("L", 342, "Materialbedarfsplanung durchführen"),
    ("L", 367, "Bestellungen automatisch erzeugen"),
    ("L", 375, "Rechnungen automatisch mithilfe der automatischen Wareneingangsabrechnung anlegen"),
    ("K", 389, "Kapitel 9: Auswertungen und Analysen"),
    ("L", 390, "Analytische Apps verwenden"),
    ("L", 409, "Die App „Beschaffungsübersicht“ verwenden"),
  ],
  "S4520": [
    ("K", 1, "Kapitel 1: Stammdaten der Einkaufsabwicklung"),
    ("L", 2, "Materialstammsätze für den Einkauf anlegen"),
    ("L", 19, "Geschäftspartner anlegen"),
    ("L", 40, "Partnerfunktionen im Einkauf verwenden"),
    ("K", 65, "Kapitel 2: Bezugsquellen und Konditionen"),
    ("L", 67, "Grundlagen der Preisfindung analysieren"),
    ("L", 77, "Arbeiten mit Einkaufsinfosätzen"),
    ("L", 95, "Besondere Infosätze anlegen"),
    ("L", 104, "Preise in Infosätzen gesammelt anpassen"),
    ("L", 110, "Arbeiten mit Kontrakten"),
    ("L", 130, "Kontrakte zu Warengruppen anlegen"),
    ("L", 141, "Arbeiten mit Lieferplänen"),
    ("L", 145, "Lieferpläne ohne Abrufdokumentation anlegen"),
    ("L", 153, "Lieferpläne mit Abrufdokumentation anlegen"),
    ("K", 181, "Kapitel 3: Bezugsquellenfindung"),
    ("L", 183, "Bezugsquellenfindung mit Orderbüchern steuern"),
    ("L", 201, "Orderbücher pflegen"),
    ("L", 211, "Bezugsquellenfindung mit Quotierungen steuern"),
    ("L", 223, "Planungslauf mit Quotierungen ausführen"),
    ("L", 237, "Weitere Aspekte der Bezugsquellenfindung identifizieren"),
    ("L", 250, "Bezugsquellen sperren"),
    ("L", 259, "Verwenden von Katalogen für die Bezugsquellenfindung"),
    ("K", 279, "Kapitel 4: Optimierte Einkaufsabwicklung"),
    ("L", 280, "Nicht zugeordnete Bestellanforderungen bearbeiten"),
    ("L", 288, "Bearbeitung zugeordneter Bestellanforderungen"),
    ("L", 307, "Bestellüberwachung"),
    ("L", 323, "Situationsverarbeitung einsetzen"),
    ("K", 349, "Kapitel 5: Belegfreigabeverfahren"),
    ("L", 350, "Bestellanforderungen freigeben"),
    ("L", 361, "Einkaufsbelege freigeben"),
    ("L", 370, "Freigabeverfahren im Customizing konfigurieren"),
    ("L", 388, "Flexible Workflows im Einkauf einrichten"),
    ("K", 403, "Kapitel 6: Besondere Beschaffungsprozesse"),
    ("L", 404, "Rechnungspläne verwenden"),
    ("L", 418, "Limitbestellungen anlegen"),
    ("L", 429, "Mit der Lohnbearbeitung arbeiten"),
    ("L", 445, "Zusätzliche Sonderfunktionen einsetzen"),
    ("K", 469, "Kapitel 7: Ausgewählte zusätzliche Customizing-Themen"),
    ("L", 470, "Belegarten im Einkauf einstellen"),
    ("L", 480, "Feldauswahl in Einkaufsbelegen einrichten"),
    ("L", 492, "Spezielle Aspekte im Customizing analysieren"),
    ("L", 506, "Funktionsberechtigungen für Einkäufer festlegen"),
    ("K", 523, "Kapitel 8: Lieferantenbewertung"),
    ("L", 524, "KPIs für die Lieferantenbeurteilung erläutern"),
    ("K", 537, "Kapitel 9: Zusatzinformationen - kein Trainingsinhalt"),
    ("L", 538, "Lieferanten mit dem Logistikinfosystem bewerten"),
    ("L", 556, "Lieferantenbeurteilung mit dem Logistikinfosystem einrichten"),
    ("L", 573, "Einkauf mit Herstellerteilenummern (HTN)"),
  ],
}

E = {}

E[1] = dict(ref=[("S4520",361),("S4520",350)],
 A="Falsch. Bestellungen und andere Einkaufsbelege werden nur auf Kopfebene freigegeben oder abgelehnt; eine Freigabe pro Position gibt es nur bei Bestellanforderungen.",
 B="Richtig. Genau das ist der Zweck der Bestellfreigabe: Solange die Bestellung gesperrt ist, kann die Nachricht (Druck, E-Mail, EDI) nicht an den Lieferanten ausgegeben werden.",
 C="Falsch. Wie viele Stufen es gibt und in welcher Reihenfolge freigegeben wird, legt die jeweilige Freigabestrategie fest. Das können auch eine oder mehr als zwei Stufen sein.",
 D="Falsch. Eine gesperrte Bestellung ist für die Weiterverarbeitung blockiert; Wareneingang und Rechnung sind erst nach der Freigabe möglich.",
 frage="Warum setzt die Sperre bei Bestellungen gerade an der Nachrichtenausgabe an und nicht schon beim Sichern? Welches Risiko wird damit vermieden?")
E[8] = dict(ref=[("S4520",353)],
 A="Falsch. Für die Sammelfreigabe brauchen Sie keinen speziellen Code; Sie geben Ihren normalen Freigabecode ein und erhalten alle Belege, die Sie damit freigeben dürfen.",
 B="Richtig. Die Sammelfreigabe listet alle Positionen und Bestellanforderungen zu Ihrem Freigabecode auf, sodass Sie viele auf einmal freigeben können.",
 C="Richtig. Mit der Einzelfreigabe können Sie bei Positionsfreigabe jede Position für sich freigeben oder ablehnen.",
 D="Falsch. Die Einzelfreigabe bearbeitet immer eine Bestellanforderung. Mehrere Belege gleichzeitig gehen nur mit der Sammelfreigabe.",
 frage="In welcher Situation würden Sie bewusst die Einzelfreigabe statt der Sammelfreigabe wählen, obwohl Sie viele Belege freizugeben haben? (Tipp: Was kann die Sammelfreigabe nicht?)")
E[18] = dict(ref=[("S4520",354)],
 A="Richtig. Die Registerkarte zeigt die ermittelte Freigabestrategie.",
 B="Falsch. Angezeigt werden die Freigabecodes, also Freigabestellen. Welche Person dahintersteht, ergibt sich erst aus den Berechtigungen.",
 C="Richtig. Die Freigabegruppe wird angezeigt; sie bestimmt zusammen mit der Belegart, ob Positions- oder Gesamtfreigabe gilt.",
 D="Falsch. Ein Freigabedatum ist kein Bestandteil dieser Registerkarte.",
 E="Richtig. Das Freigabekennzeichen zeigt den aktuellen Freigabezustand, zu Beginn meist „gesperrt“.",
 frage="Die Kriterien, die zur Sperre geführt haben, werden auf der Registerkarte nicht angezeigt. Wo würden Sie nachsehen, warum genau diese Strategie gezogen wurde?")
E[22] = dict(ref=[("S4520",354)],
 A="Falsch. Das Freigabekennzeichen beschreibt nur den Zustand des Belegs (z. B. gesperrt oder freigegeben). Es ist kein Berechtigungsobjekt.",
 B="Falsch. Wertgrenzen stecken in der Klassifizierung der Freigabestrategie, nicht in einer Berechtigung für „Freigabegrenzen“.",
 C="Richtig. Freigegeben wird immer mit einem Freigabecode, und wer welchen Code benutzen darf, wird über Berechtigungen gesteuert.",
 D="Falsch. Die Freigabeklasse sammelt im Customizing die Merkmale für die Strategiefindung. Sie hat mit der Berechtigung des Freigebenden nichts zu tun.",
 frage="Ein Kollege ist drei Wochen im Urlaub und hat einen Freigabecode, der in vielen Strategien vorkommt. Wie würden Sie die Vertretung organisieren, ohne die Strategien zu ändern?")
E[44] = dict(ref=[("S4520",374),("S4520",373),("S4520",351)],
 A="Richtig. Die Freigabestrategie legt fest, welche Freigabecodes beteiligt sind und in welcher Reihenfolge sie freigeben dürfen (Freigabevoraussetzungen).",
 B="Falsch. Bestellanforderungen können je nach Freigabegruppe und Belegart positionsweise oder insgesamt freigegeben werden; nur Bestellungen sind auf die Kopfebene beschränkt.",
 C="Falsch. Die Strategie ermittelt das System selbst anhand der Merkmalswerte in der Klassifizierung (z. B. Wert, Kontierung, Werk). Der Ersteller wählt sie nicht aus.",
 D="Richtig. Im Freigabekennzeichen ist hinterlegt, ob die Bestellanforderung schon in eine Anfrage und/oder in eine Bestellung umgesetzt werden darf.",
 frage="Wie könnte eine Strategie aussehen, bei der eine Bestellanforderung nach der ersten Freigabe bereits angefragt, aber erst nach der zweiten Freigabe bestellt werden darf?")
E[2] = dict(ref=[("S4500",33)],
 A="Falsch. Der Buchungskreis ist eine Einheit des Rechnungswesens; mengenmäßig werden dort keine Bestände geführt.",
 B="Falsch. Die Lagernummer gehört zur Lagerverwaltung (EWM/WM) und ist nicht die Ebene der mengenmäßigen Bestandsführung in MM.",
 C="Richtig. Die mengenmäßige Bestandsführung im Werk erfolgt auf Lagerortebene; dort wird auch die Inventur durchgeführt.",
 D="Falsch. Lagerplätze sind eine Ebene der Lagerverwaltung unterhalb des Lagerorts, nicht die Ebene der Bestandsführung in MM.",
 frage="Warum wird der Bestand mengenmäßig auf Lagerortebene, wertmäßig aber auf Werks- oder Buchungskreisebene geführt? Was wäre der Nachteil, wenn auch der Wert pro Lagerort geführt würde?")
E[6] = dict(ref=[("S4500",33)],
 A="Falsch. „Verschiedene Daten“ ist keine Organisationsebene.",
 B="Falsch. Der Buchungskreis wird erst in den Belegen (z. B. über das Werk) bestimmt, nicht bei der Anmeldung.",
 C="Richtig. Benutzerstammsätze und Berechtigungen gibt es pro Mandant; bei der Anmeldung geben Sie den Mandanten an.",
 D="Falsch. Die Einkaufsorganisation geben Sie in Einkaufsbelegen an, nicht beim Anmelden.",
 frage="Was bedeutet es für Ihre Arbeit, dass alle Eingaben mandantenspezifisch gespeichert werden? Denken Sie an Test- und Produktivmandanten.")
E[13] = dict(ref=[("S4520",6),("S4520",7)],
 A="Falsch. Der Lagerort ist eine Organisationsebene, die Sie beim Pflegen der Lagerdaten angeben. Die Materialart legt ihn nicht fest.",
 B="Richtig. Die Materialart steuert Nummernkreis und Art der Nummernvergabe (intern oder extern).",
 C="Falsch. Ob auf Werks- oder Buchungskreisebene bewertet wird, ist eine Customizing-Einstellung (Bewertungskreis) und hängt nicht von der Materialart ab.",
 D="Richtig. Die Materialart bestimmt, welche Datenbilder und Fachbereiche (Sichten) gepflegt werden können und in welcher Reihenfolge.",
 E="Richtig. Die Materialart legt fest, ob ein Material fremdbeschafft, eigengefertigt oder beides werden darf (z. B. ROH nur fremd).",
 frage="Sie möchten ein Material von NLAG auf ROH umstellen. Welche Voraussetzungen müssen erfüllt sein, und warum verlangt das System das?")
E[15] = dict(ref=[("S4500",105),("S4500",33)],
 A="Falsch. Werksbezogen sind z. B. Einkäufergruppe oder Dispositionsdaten, nicht die Grunddaten.",
 B="Falsch. Kombinationen aus Buchungskreis und Werk sind keine eigene Ebene im Materialstamm.",
 C="Richtig. Grunddaten wie Kurztext, Basismengeneinheit oder Warengruppe gelten mandantenweit und werden genau einmal gepflegt.",
 D="Falsch. Der Buchungskreis spielt für die Grunddaten keine Rolle; er kann allenfalls Bewertungsebene sein.",
 frage="Welche Daten desselben Materials müssen Sie in diesem Beispiel trotzdem fünfmal pflegen, und warum?")
E[21] = dict(ref=[("S4520",5),("S4520",6)],
 A="Falsch. Nur einige Einkaufsdaten (z. B. Einkaufswerteschlüssel, Bestelltext) gelten auf Mandantenebene.",
 B="Richtig. Die meisten Einkaufsdaten wie Einkäufergruppe oder die Kennzeichen „Automatische Bestellung“ und „Orderbuchpflicht“ werden pro Werk gepflegt.",
 C="Falsch. „Alle“ stimmt nicht, denn ein Teil der Einkaufsdaten liegt auf Mandantenebene.",
 frage="Warum ist es sinnvoll, dass die Orderbuchpflicht pro Werk und nicht mandantenweit gesetzt wird?")
E[45] = dict(ref=[("S4500",34),("S4500",35),("S4520",80)],
 A="Richtig. Eine buchungskreisübergreifende Einkaufsorganisation ist keinem Buchungskreis zugeordnet und kann Werke aus mehreren Buchungskreisen betreuen.",
 B="Falsch. Zwischen Einkaufsorganisation und Werk besteht eine n:m-Beziehung; ein Werk kann mehreren Einkaufsorganisationen zugeordnet sein.",
 C="Falsch. Die Einkaufsdaten im Materialstamm liegen auf Mandanten- und Werksebene, nicht pro Einkaufsorganisation.",
 D="Richtig. Die Einkaufsorganisation handelt die Konditionen aus; Einkaufskonditionen (z. B. im Infosatz) hängen deshalb immer an einer Einkaufsorganisation.",
 frage="Ihr Konzern will Rahmenverträge zentral verhandeln, die Werke sollen aber selbst bestellen. Wie würden Sie Einkaufsorganisationen und Werke zuordnen?")
E[52] = dict(ref=[("S4500",35),("S4500",36)],
 A="Falsch. Einkäufergruppen werden keiner Organisationseinheit zugeordnet.",
 B="Falsch. Auch eine Zuordnung von Einkäufergruppe zu Werk gibt es nicht.",
 C="Richtig. Die Zuordnung Einkaufsorganisation zu Werk ist immer notwendig, bei der werksbezogenen genau ein Werk.",
 D="Richtig. Bei der werksbezogenen Einkaufsorganisation ordnen Sie die Einkaufsorganisation zusätzlich einem Buchungskreis zu.",
 frage="Was unterscheidet in den Zuordnungen eine werksbezogene von einer werksübergreifenden Einkaufsorganisation?")
E[54] = dict(ref=[("S4500",33),("S4500",34)],
 A="Falsch. Lagerorte gehören zu einem Werk und stehen deshalb darunter.",
 B="Richtig. Mandant (Konzern) → Buchungskreis (bilanzierende Firma) → Werk → Lagerort.",
 C="Falsch. Der Buchungskreis liegt über dem Werk, denn jedes Werk gehört genau einem Buchungskreis.",
 D="Falsch. Der Mandant ist die höchste Ebene im SAP-System.",
 frage="Warum reicht in Belegen die Angabe des Werks, um auch den Buchungskreis zu kennen?")
E[59] = dict(ref=[("S4500",35),("S4500",36)],
 A="Falsch. Lagerorte spielen für die Kategorie einer Einkaufsorganisation keine Rolle.",
 B="Richtig. Eine werksbezogene Einkaufsorganisation ist für genau ein Werk zuständig.",
 C="Falsch. Eine lagerortspezifische Einkaufsorganisation gibt es nicht.",
 D="Richtig. Sie ist keinem Buchungskreis zugeordnet und kann Werke mehrerer Buchungskreise betreuen.",
 E="Richtig (laut Lösung). Im Buch heißt diese Variante „werksübergreifende Einkaufsorganisation“: Sie ist einem Buchungskreis zugeordnet und für mehrere Werke dieses Buchungskreises zuständig.",
 hinweis="Das Buch nennt die drei Kategorien werksbezogen, werksübergreifend und buchungskreisübergreifend. „Buchungskreisspezifisch“ entspricht der werksübergreifenden Variante innerhalb eines Buchungskreises.",
 frage="Ordnen Sie Ihrem eigenen Unternehmen eine der drei Kategorien zu. Welche Zuordnungen müssten dafür im Customizing bestehen?")
E[62] = dict(ref=[("S4500",118)],
 A="Richtig. Der Bewertungskreis kann im Customizing auf Werksebene festgelegt werden.",
 B="Falsch. Der Geschäftsbereich ist keine mögliche Bewertungsebene.",
 C="Richtig. Alternativ kann der Bewertungskreis auf Buchungskreisebene liegen.",
 D="Falsch. Lagerorte führen nur Mengen, keinen eigenen Wert.",
 frage="Welche Folgen hätte es, die Bewertungsebene nachträglich von Buchungskreis auf Werk umzustellen, und warum rät das Buch davon ab?")
E[69] = dict(ref=[("S4500",33),("S4500",34)],
 A="Richtig. Der Mandant ist eine rechtlich und organisatorisch abgeschlossene Einheit mit eigenen Stammsätzen und Tabellen.",
 B="Falsch. In einem Mandanten können mehrere Buchungskreise angelegt werden.",
 C="Richtig. Der Buchungskreis ist die kleinste Einheit des externen Rechnungswesens mit einer vollständigen, in sich abgeschlossenen Buchhaltung.",
 D="Falsch. Benutzer werden pro Mandant angelegt, nicht einem Buchungskreis zugeordnet.",
 frage="Ein Konzern hat drei rechtlich selbstständige Firmen. Wie viele Mandanten und wie viele Buchungskreise würden Sie einrichten, und warum?")
E[80] = dict(ref=[("S4500",34)],
 A="Richtig. Einem Buchungskreis können mehrere Werke zugeordnet werden.",
 B="Falsch. Lagerorte werden immer innerhalb eines Werks angelegt; ohne Werk gibt es keinen Lagerort.",
 C="Richtig. Der Lagerortschlüssel muss nur innerhalb eines Werks eindeutig sein, weil zum Lagerort immer das Werk angegeben wird.",
 D="Falsch. Ein Werk gehört genau einem Buchungskreis.",
 E="Richtig. Einem Werk können mehrere Lagerorte zugeordnet werden.",
 frage="Warum darf derselbe Lagerortschlüssel (z. B. 0001) in verschiedenen Werken vorkommen, ein Werksschlüssel aber nur einmal im Mandanten?")
E[88] = dict(ref=[("S4520",2),("S4520",4),("S4520",6)],
 A="Richtig. Die Daten sind in Sichten nach Fachbereichen gegliedert; jeder Fachbereich sieht nur die für ihn relevanten Daten.",
 B="Falsch. Sichten können später ergänzt werden (Material erweitern, z. B. über „Erweiterbare Materialien“).",
 C="Richtig. Über den Pflegestatus (z. B. E für Einkauf, B für Buchhaltung) erkennt das System, welche Fachbereiche gepflegt sind.",
 D="Falsch. Die Materialart steuert, welche Fachbereiche und Datenbilder gepflegt werden können.",
 frage="Ein Material soll bestellt werden, die Bestellung wird aber abgelehnt. Welche Pflegestatus würden Sie prüfen, und wann reicht „E“ allein nicht aus?")
E[4] = dict(ref=[("S4520",239),("S4520",240)],
 A="Falsch. Rahmenverträge und Infosätze werden erst geprüft, wenn es weder Quotierung noch Orderbuch gibt.",
 B="Richtig. Außerhalb des Planungslaufs gilt: zuerst Quotierung, dann Orderbuch, dann Rahmenvertragspositionen und zuletzt Infosätze.",
 C="Falsch. Eine gültige Quotierung hat immer die höchste Priorität und wird vor dem Orderbuch geprüft.",
 D="Falsch. Die Reihenfolge ist umgekehrt: Quotierung und Orderbuch stehen vor Rahmenverträgen und Infosätzen.",
 frage="Im Planungslauf (MRP) weicht die Reihenfolge ab, etwa bei Lieferplänen und Kontrakten. Was ist dort anders, und warum braucht die Disposition für Rahmenverträge ein disporelevantes Orderbuch?")
E[10] = dict(ref=[("S4520",185),("S4520",186),("S4520",188),("S4520",204)],
 A="Falsch. Eine Obergrenze von 20 Orderbuchsätzen pro Material gibt es nicht.",
 B="Falsch. Ein Orderbuchsatz kann direkt mit Lieferant und Einkaufsorganisation angelegt werden; ein Infosatz ist dafür nicht nötig. Nötig ist nur ein Materialstammsatz, denn Materialien ohne Stammsatz lassen sich nicht über das Orderbuch sperren.",
 C="Richtig. Jeder Orderbuchsatz hat einen Gültigkeitszeitraum, in dem seine Einstellungen (fix, gesperrt, Disposition) gelten.",
 D="Richtig. Im Customizing lässt sich die Orderbuchpflicht für ein ganzes Werk festlegen. Dann braucht jedes Material dieses Werks einen gültigen Orderbuchsatz, bevor es bestellt werden kann.",
 frage="Gegen welches Datum prüft das System den Gültigkeitszeitraum bei einer manuellen Bestellanforderung, und gegen welches im Planungslauf?")
E[28] = dict(ref=[("S4520",187),("S4520",6)],
 A="Falsch. „Automatische Bestellung“ erlaubt die automatische Umsetzung von Bestellanforderungen, schränkt aber die Bezugsquellen nicht ein.",
 B="Falsch. Die Orderbuchpflicht ist eine Eigenschaft des Materials pro Werk, nicht des Lieferanten.",
 C="Richtig. Die Orderbuchpflicht wird in den Einkaufsdaten des Materialstammsatzes auf Werksebene gesetzt.",
 D="Falsch. Im Infosatz gibt es kein Kennzeichen „Orderbuchpflicht“.",
 frage="Wofür ist die Orderbuchpflicht laut Buch besonders nützlich? Fällt Ihnen ein Fall aus Ihrem Alltag ein, z. B. Lieferantenfreigabe durch die Qualitätssicherung?")
E[35] = dict(ref=[("S4520",201),("S4520",202)],
 A="Richtig. Orderbuchsätze können manuell gepflegt werden (ME01 bzw. App „Orderbücher verwalten“).",
 B="Richtig. Aus einem Rahmenvertrag (Position → Orderbuch pflegen) oder aus einem Infosatz (Zusätze → Orderbuch) lassen sich Orderbuchsätze direkt anlegen.",
 C="Falsch. Quotierung und Orderbuch sind getrennte Objekte; eine Quotierung erzeugt keine Orderbuchsätze.",
 D="Falsch. Die automatische Erzeugung (ME05) ist nicht auf ein Werk beschränkt; Sie wählen Materialien und Werke selbst aus.",
 frage="Sie erzeugen Orderbuchsätze automatisch für eine ganze Warengruppe. Welche Fragen müssen Sie vorher klären, damit bestehende Einträge nicht ungewollt überschrieben werden?")
E[47] = dict(ref=[("S4520",214)],
 A="Richtig. Ohne Quotenbasismenge bekäme eine neu aufgenommene Bezugsquelle (quotierte Menge 0) so lange alle Bedarfe, bis sie die anderen eingeholt hat.",
 B="Falsch. Die Quotenbasismenge ist optional und dient nur der manuellen Steuerung.",
 C="Richtig. In MEQ1 gibt es die Einzelrechnung (markierte Positionen) und die Sammelrechnung (alle Positionen).",
 D="Falsch. Sie kann manuell erfasst oder vom System berechnet werden.",
 frage="Rechnen Sie nach: Lieferant A hat Quote 1 und quotierte Menge 600, der neue Lieferant B Quote 1 und quotierte Menge 0. Welche Quotenbasismenge braucht B, damit beide ab sofort gleich behandelt werden?")
E[56] = dict(ref=[("S4520",239)],
 A="Richtig. Das Orderbuch ist eine der Stufen der automatischen Bezugsquellenfindung.",
 B="Falsch. Das Kennzeichen InfoUpdate steuert nur, ob eine Bestellung den Infosatz fortschreibt. Für die Bezugsquellenfindung spielt es keine Rolle.",
 C="Richtig. Eine gültige Quotierung wird zuerst geprüft; zugeordnet wird die Bezugsquelle mit der niedrigsten Quotenzahl.",
 D="Falsch. Partnerrollen legen z. B. abweichende Rechnungssteller fest. Eine Bezugsquelle ermitteln sie nicht.",
 frage="Eine Bestellanforderung über 1.000 Stück wird manuell angelegt, und es gibt eine Quotierung 50:50. Wird die Menge aufgeteilt? Begründen Sie mit dem Buch.")
E[61] = dict(ref=[("S4520",213),("S4520",214)],
 A="Falsch (laut Lösung). Die Basismenge fließt zwar in die Quotenzahl ein, die Quote selbst (der Anteil) bleibt aber unverändert.",
 B="Falsch. Die Aufteilung richtet sich weiterhin nach der Quote; die Basismenge gleicht nur einen Vorsprung bei der quotierten Menge aus.",
 C="Falsch. Gesperrt wird über das Orderbuch oder den Lieferanten, nicht über die Quotenbasismenge.",
 D="Richtig. Mit der Quotenbasismenge verhindern Sie, dass eine neue Bezugsquelle zunächst sämtliche Bedarfe erhält.",
 hinweis="Formel: Quotenzahl = (quotierte Menge + Quotenbasismenge) / Quote. Zugeordnet wird die niedrigste Quotenzahl.",
 frage="Warum würde ohne Basismenge eine neue Bezugsquelle alle Bedarfe bekommen? Erklären Sie es mit der Formel.")
E[66] = dict(ref=[("S4520",225),("S4520",226),("S4520",227)],
 A="Falsch. Die minimale Losgröße ist eine Untergrenze pro Beschaffungsvorschlag, keine Monatsgrenze.",
 B="Richtig. Eine Obergrenze pro Zeitraum wird über die maximale Abrufmenge pro Periode (z. B. pro Monat) festgelegt.",
 C="Falsch. Eine „Mindestmenge für die Splittung“ begrenzt keine Liefermenge pro Monat.",
 D="Falsch. Die maximale Losgröße begrenzt nur die Menge pro einzelnem Beschaffungsvorschlag im Planungslauf, nicht die Gesamtmenge pro Monat.",
 frage="Worin unterscheiden sich maximale Losgröße, maximale Menge und maximale Abrufmenge? Ordnen Sie jedem ein eigenes Beispiel zu.")
E[89] = dict(ref=[("S4520",185),("S4520",186),("S4520",250)],
 A="Richtig. Mit dem Kennzeichen „Fix“ wird ein Orderbuchsatz als feste Bezugsquelle markiert.",
 B="Falsch. Das Orderbuch wird pro Material und Werk gepflegt, nicht pro Lieferant und Einkaufsorganisation.",
 C="Richtig. Über das Sperrkennzeichen oder die Orderbuchpflicht schränken Sie die zulässigen Bezugsquellen ein.",
 D="Richtig. Das Orderbuch ist eine Liste der Bezugsquellen für ein Material in einem Werk.",
 E="Falsch. Das Orderbuch sperrt nur die Kombination Material/Lieferant. Für alle Materialien gesperrt wird ein Lieferant über die Einkaufssperre im Geschäftspartner.",
 frage="Sie haben im Orderbuch sowohl einen Infosatz als auch eine Kontraktposition als fix markiert. Welche Bezugsquelle schlägt das System vor, und warum?")
E[3] = dict(ref=[("S4520",446),("S4520",447)],
 A="Richtig. Bestellungen können vorerfasst und gemerkt werden (z. B. in ME21N).",
 B="Falsch. Kontrakte werden im Buch nicht genannt; die Funktionen gelten für Bestellanforderungen und Bestellungen.",
 C="Falsch. Auch Anfragen gehören nicht dazu.",
 D="Richtig. Bestellanforderungen können ebenfalls vorerfasst und gemerkt werden (z. B. in ME51N).",
 frage="Die Fiori-App „Bestellungen verwalten“ kennt kein Merken und Vorerfassen. Wie löst sie das Problem halbfertiger Belege, und was ist bei Entwürfen für die Disposition zu beachten?")
E[17] = dict(ref=[("S4520",447)],
 A="Falsch. Für Rahmenbestellungen wird „Merken“ ausdrücklich nicht unterstützt.",
 B="Richtig. Ein gemerkter Beleg ist für Folgeaktivitäten gesperrt, z. B. Umsetzung in eine Bestellung oder Wareneingang.",
 C="Richtig. Beim Merken sind sämtliche Fehlerarten zulässig; der Beleg darf noch unvollständig sein.",
 D="Falsch. Eine spezielle Belegart ist nicht nötig. Die Funktion wird einmal mandantenweit im Customizing aktiviert.",
 frage="Worin unterscheidet sich „Vorerfassen“ von „Merken“? Welche Fehler lässt Vorerfassen zu und welche nicht?")
E[5] = dict(ref=[("S4500",143),("S4500",68)],
 A="Falsch. Ein Obligo entsteht schon mit der kontierten Bestellung im Controlling. Die Rechnung legt keinen eigenen Obligobeleg an.",
 B="Falsch. Ein Wareneingangsbeleg (Materialbeleg) entsteht beim Wareneingang, nicht bei der Rechnung.",
 C="Richtig. Die Logistik-Rechnungsprüfung legt einen Rechnungsbeleg in MM an.",
 D="Richtig. Zusätzlich wird ein separater Buchhaltungsbeleg in FI erzeugt, z. B. Kreditor an WE/RE-Konto.",
 frage="Welche Konten werden beim Buchen einer Rechnung zu einer Lagerbestellung typischerweise angesprochen, und was passiert mit dem WE/RE-Verrechnungskonto?")
E[16] = dict(ref=[("S4500",58),("S4500",142)],
 A="Richtig. Weil der Wareneingang bewertet ist, entsteht zusätzlich ein Buchhaltungsbeleg.",
 B="Falsch. Ein Obligobeleg wird beim Wareneingang nicht erzeugt; bei Kontierung wird das Obligo höchstens abgebaut.",
 C="Falsch. Ein Rechnungsbeleg entsteht erst in der Rechnungsprüfung.",
 D="Richtig. Jede Warenbewegung erzeugt einen Materialbeleg.",
 frage="Nennen Sie eine Warenbewegung, die nur einen Materialbeleg und keinen Buchhaltungsbeleg erzeugt. Warum ist das so?")
E[11] = dict(ref=[("S4500",213),("S4500",223)],
 A="Falsch. Ein Wareneingang ist weiterhin möglich, er wird nur ohne Wert gebucht.",
 B="Richtig. Beim unbewerteten Wareneingang gibt es keine Buchung auf Verbrauchs- oder WE/RE-Konto. Bewertet wird erst beim Rechnungseingang.",
 C="Falsch. Die Menge wird beim Wareneingang fortgeschrieben, nur ein Wert wird nicht gebucht.",
 D="Falsch. Die Position wird bewertet, nur später, nämlich mit der Rechnung.",
 frage="Warum kann es sinnvoll sein, bei kontierten Bestellungen den Wareneingang unbewertet zu buchen? Denken Sie an den Zeitpunkt, zu dem Kosten auf der Kostenstelle erscheinen.")
E[63] = dict(ref=[("S4500",213),("S4500",223)],
 A="Falsch. Die Position wird bewertet, nur erst bei der Rechnung.",
 B="Falsch. Ein Wareneingang ist weiterhin möglich, er wird nur ohne Wert gebucht.",
 C="Falsch. Die Menge wird beim Wareneingang fortgeschrieben, nur ein Wert wird nicht gebucht.",
 D="Richtig. Beim unbewerteten Wareneingang erfolgt keine Buchung auf Verbrauchs- oder WE/RE-Konto. Das Verbrauchskonto wird erst mit dem Rechnungsbetrag belastet.",
 frage="Welche Buchungen sehen Sie beim Wareneingang und bei der Rechnung, wenn das Kennzeichen „WE unbewertet“ gesetzt ist, und welche, wenn es nicht gesetzt ist?")
E[58] = dict(ref=[("S4500",213),("S4520",449)],
 A="Richtig. Ist das Kennzeichen „Wareneingang“ gesetzt (und „WE unbewertet“ nicht), wird der Wareneingang zur kontierten Position bewertet gebucht.",
 B="Falsch. Das Rechnungseingangskennzeichen steuert, ob eine Rechnung erwartet wird, nicht die Bewertung des Wareneingangs.",
 C="Falsch. Ein Kennzeichen „Wareneingang bewertet“ gibt es nicht; es gibt nur das Gegenstück „WE unbewertet“.",
 D="Falsch. Der Kontierungstyp bestimmt das Kontierungsobjekt. Ob der Wareneingang bewertet wird, hängt an den WE-Kennzeichen.",
 frage="Was passiert mit dem Obligo, wenn ein bewerteter Wareneingang zu einer kontierten Bestellposition gebucht wird?")
E[30] = dict(ref=[("S4500",212),("S4500",180)],
 A="Richtig. Für Lagermaterial darf kein Kontierungstyp eingegeben werden, sonst wird für den Verbrauch beschafft.",
 B="Falsch. Lagermaterial wird beim Wareneingang mengen- und wertmäßig fortgeschrieben; eine Wahlmöglichkeit gibt es nicht.",
 C="Falsch. Der Lagerort ist in der Bestellung optional und kann spätestens beim Wareneingang angegeben werden.",
 D="Richtig. Für Lagermaterial braucht es eine Materialnummer, also einen Materialstammsatz.",
 frage="Wann würden Sie ein Lagermaterial bewusst mit Kontierung bestellen? Nennen Sie ein Beispiel aus dem Buch.")
E[20] = dict(ref=[("S4500",184)],
 A="Falsch. Die Rechnungsprüfung bezieht sich auf Bestellungen, nicht auf Bestellanforderungen.",
 B="Falsch. Einen Lieferschein erstellt der Lieferant bzw. der Versand, nicht der Einkauf aus einer Bestellanforderung.",
 C="Richtig. Bestellanforderungen können in Anfragen, Bestellungen oder Rahmenverträge umgesetzt werden.",
 D="Falsch. Ein Wareneingang braucht eine Bestellung (oder einen Lieferplan) als Bezug, keine Bestellanforderung.",
 frage="In welche drei Folgebelege kann eine Bestellanforderung laut Buch umgesetzt werden, und wann wählen Sie welchen?")
E[24] = dict(ref=[("S4500",184),("S4500",185)],
 A="Falsch (laut Buch). Der Bewertungspreis wird aus dem Materialstamm gezogen; der Infosatzpreis spielt erst bei der Umsetzung in die Bestellung eine Rolle.",
 B="Falsch. Genau umgekehrt: Bei unbewertetem Material oder Material ohne Stammsatz muss der Ersteller den Bewertungspreis selbst eingeben.",
 C="Falsch. Das „nie“ stimmt nicht; in den oben genannten Fällen ist die Eingabe nötig.",
 D="Richtig. Bei bewertetem Material schlägt das System den Bewertungspreis aus dem Materialstammsatz vor.",
 frage="Wofür wird der Bewertungspreis der Bestellanforderung verwendet, und wird er in die Bestellung übernommen?")
E[36] = dict(ref=[("S4500",181)],
 A="Falsch. Ein Kennzeichen „Keine Bestandsführung“ gibt es in der Bestellanforderung nicht. Ob Verbrauch vorliegt, ergibt sich aus dem Kontierungstyp.",
 B="Falsch. „Aktivitätstyp“ ist hier kein Begriff aus dem Einkauf.",
 C="Richtig. Erst der Kontierungstyp K (Kostenstelle) legt fest, welche Kontierungsdaten (Sachkonto, Kostenstelle) einzugeben sind.",
 D="Falsch. Einen Positionstyp „Verbrauchsmaterial“ gibt es nicht. Verbrauch wird über die Kontierung gesteuert.",
 frage="Welche Daten müssen Sie bei Kontierungstyp K eingeben, und was ist bei Kontierungstyp A (Anlage) anders?")
E[38] = dict(ref=[("S4500",184),("S4500",185),("S4520",419)],
 A="Richtig. In Bestellanforderungen ist der Kontierungstyp U erlaubt.",
 B="Richtig. In Bestellungen ist U ausnahmsweise bei Dienstleistungspositionen zulässig.",
 C="Falsch. In normalen Bestellungen ist U nicht zulässig; dort braucht es ein echtes Kontierungsobjekt.",
 D="Falsch. Konsignationsbestellungen erlauben U nicht.",
 E="Richtig. Auch bei Limitpositionen ist U zulässig; die Kontierung wird dann erst bei der Rechnung angegeben.",
 frage="Welche Folge hat Kontierungstyp U für das Obligo im Controlling, und warum könnte das für das Budget problematisch sein?")
E[71] = dict(ref=[("S4500",181),("S4500",184)],
 A="Falsch. Für Lagermaterial darf gerade kein Kontierungstyp eingegeben werden.",
 B="Richtig. In Bestellanforderungen mit Positionstyp Standard ist U (Unbekannt) zulässig.",
 C="Richtig. Der Kontierungstyp legt fest, welches Kontierungsobjekt (z. B. Kostenstelle, Anlage) und welche Daten erforderlich sind.",
 D="Falsch. Kontierungstypen sind Customizing-Einstellungen und können angepasst oder ergänzt werden.",
 frage="Warum ist U in der Bestellanforderung erlaubt, in der normalen Bestellung aber nicht?")
E[74] = dict(ref=[("S4500",182),("S4520",448),("S4520",449)],
 A="Falsch. Beim Wareneingang lässt sich die Verteilung per BAdI anpassen, und auch in der Rechnungsprüfung gibt es Verteilungslogiken. Ein generelles Änderungsverbot nennt das Buch nicht.",
 B="Richtig. Sie legen fest, ob Teilrechnungsbeträge proportional oder auffüllend auf die Kontierungen verteilt werden.",
 C="Falsch. Auch bewertete Wareneingänge sind möglich; bei Lohnbearbeitung mit Mehrfachkontierung ist ein bewerteter Wareneingang sogar Pflicht.",
 D="Richtig. Die Verteilung kann mengenmäßig, prozentual oder wertmäßig erfolgen.",
 frage="Eine Bestellung über 1.000 EUR ist 60:40 auf zwei Kostenstellen verteilt, die erste Teilrechnung lautet über 300 EUR. Wie wird sie proportional und wie auffüllend verteilt?")
E[86] = dict(ref=[("S4500",182),("S4520",448)],
 A="Richtig. Prozentuale Verteilung ist möglich.",
 B="Falsch. „Nach Basismengeneinheit“ ist keine Verteilungsmethode. Es gibt eine mengenmäßige Verteilung nach Bestellmenge.",
 C="Falsch. „In der definierten Reihenfolge“ (auffüllend) betrifft die Verteilung von Teilrechnungen, nicht die Aufteilung der Beträge.",
 D="Richtig. Wertmäßige Verteilung ist möglich und hilft gegen Rundungsprobleme bei kleinen Beträgen.",
 frage="Wann ist die wertmäßige Verteilung der prozentualen vorzuziehen? Nennen Sie ein konkretes Beispiel mit Rundung.")
E[70] = dict(ref=[("S4500",69),("S4500",70)],
 A="Falsch. Die Buchhaltungsbelegnummer des Wareneingangs ist kein Zuordnungskriterium.",
 B="Richtig. Die Bestellnummer ist der Standardbezug.",
 C="Falsch. Die Materialbelegnummer wird nicht als Zuordnungskriterium angeboten.",
 D="Richtig. Die Lieferscheinnummer geht, sofern sie beim Wareneingang erfasst wurde.",
 E="Richtig. Auch die Frachtbriefnummer geht, sofern sie beim Wareneingang erfasst wurde.",
 frage="Warum lohnt es sich, schon beim Wareneingang die Lieferscheinnummer sauber zu erfassen? Wer profitiert davon später im Prozess?")
E[12] = dict(ref=[("S4520",407),("S4520",408)],
 A="Richtig. Wareneingang gesetzt und „WE unbewertet“ gesetzt ist erlaubt, denn es darf nur ein unbewerteter Wareneingang erfolgen.",
 B="Richtig. Ohne Wareneingangskennzeichen, nur mit Rechnungseingang, ist ebenfalls erlaubt.",
 C="Falsch. Damit würde ein bewerteter Wareneingang erwartet, und das ist bei Rechnungsplänen nicht zulässig.",
 D="Falsch. Ohne Rechnungseingangskennzeichen gäbe es nichts abzurechnen, der Rechnungsplan liefe ins Leere.",
 frage="Warum verträgt sich ein Rechnungsplan nicht mit einem bewerteten Wareneingang? Denken Sie an das WE/RE-Verrechnungskonto.")
E[31] = dict(ref=[("S4520",404),("S4520",405),("S4520",406)],
 A="Falsch. „Finanzrechnungspläne“ gibt es nicht.",
 B="Richtig. Teilrechnungspläne teilen den Gesamtwert auf Termine auf, z. B. bei Projekten.",
 C="Falsch. „Vollständige Rechnungspläne“ gibt es nicht.",
 D="Richtig. Periodische Rechnungspläne rechnen den vollen Wert regelmäßig ab, z. B. Miete oder Leasing.",
 frage="Ordnen Sie zu: Wartungsvertrag mit Monatspauschale, Softwareprojekt mit drei Meilensteinen. Welche Rechnungsplanart passt jeweils?")
E[78] = dict(ref=[("S4520",404),("S4520",405),("S4520",406)],
 A="Richtig. Teilrechnungspläne teilen den Gesamtwert auf Termine auf (prozentual oder wertmäßig).",
 B="Richtig. Periodische Rechnungspläne gibt es für wiederkehrende Zahlungen wie Mieten.",
 C="Falsch. „Vollständige Rechnungspläne“ gibt es nicht.",
 D="Falsch. „Finanzrechnungspläne“ gibt es nicht.",
 frage="Wie markieren Sie im Teilrechnungsplan einen Termin als Anzahlung, und was bedeutet das für die automatische Abrechnung?")
E[55] = dict(ref=[("S4520",404),("S4520",405)],
 A="Falsch. Ein Rechnungsplan ist kein eigenständiger Belegtyp, sondern eine besondere Form der Bestellung.",
 B="Falsch. Mit der App „Bestellungen verwalten“ können Rechnungspläne weder angelegt noch bearbeitet werden.",
 C="Richtig. Rechnungspläne können nicht über eine Bestellanforderung angefordert werden.",
 D="Richtig. Rechnungen können anhand der Termine in der Bestellposition automatisch erzeugt werden (z. B. MRIS).",
 frage="Welche Voraussetzungen braucht die automatische Rechnungsplanabrechnung (Kennzeichen, Steuerkennzeichen, Zahlungsbedingungen)?")
E[19] = dict(ref=[("S4520",419),("S4520",420)],
 A="Richtig. Der erwartete Wert ist Pflicht; er dient als Bestellwert, für die Freigabe und für das Obligo.",
 B="Richtig. Das Gesamtlimit ist die Obergrenze, bis zu der Rechnungen gebucht werden können.",
 C="Falsch. In einer Limitposition können Sie keine Bestellmenge eingeben.",
 D="Falsch. Einen Nettopreis geben Sie nicht ein; der erwartete Wert wird automatisch als Nettopreis übernommen.",
 frage="Was passiert, wenn eine Rechnung den erwarteten Wert überschreitet, aber unter dem Gesamtlimit bleibt? Und was, wenn das Gesamtlimit überschritten wird?")
E[41] = dict(ref=[("S4520",418),("S4520",419),("S4520",420)],
 A="Richtig. Eine Limitbestellung ist über einen längeren Zeitraum gültig; der Gültigkeitszeitraum wird im Kopf (FO) bzw. in der Position (E) gepflegt.",
 B="Richtig. Zu Limitpositionen erfolgt kein Wareneingang und keine Leistungserfassung; abgerechnet wird direkt per Rechnung.",
 C="Richtig (laut Lösung). In der klassischen Transaktion mit Belegart FO wird Positionstyp B verwendet. Das Buch nennt zusätzlich den Positionstyp E (Erweitertes Limit), der z. B. in der App „Bestellungen verwalten“ automatisch gezogen wird.",
 D="Falsch. Das Gesamtlimit wird pro Position gepflegt, nicht als Maximalwert im Kopf.",
 hinweis="Prüfungsfragen beziehen sich hier auf den klassischen Positionstyp B. Merken Sie sich trotzdem, dass das Buch auch E (Erweitertes Limit) nennt.",
 frage="Warum senkt eine Limitbestellung die Prozesskosten? Nennen Sie die vier Gründe aus dem Buch.")
E[7] = dict(ref=[("S4500",87),("S4520",23)],
 A="Falsch. Ein Rückmeldebeleg kommt aus der Fertigung und ist keine Datenkategorie des Geschäftspartners.",
 B="Falsch. „Geschäftsbereichsdaten“ ist keine Kategorie der Lieferantendaten.",
 C="Richtig. Einkaufsdaten werden je Einkaufsorganisation gepflegt, z. B. Bestellwährung, Incoterms, Partnerrollen und Steuerungskennzeichen.",
 D="Richtig. Allgemeine Daten wie Anschrift und Bankverbindung gelten mandantenweit.",
 E="Richtig. Buchhaltungsdaten (Buchungskreisdaten) werden pro Buchungskreis gepflegt, z. B. Abstimmkonto und Zahlwege.",
 frage="Ordnen Sie jede Kategorie ihrer Organisationsebene zu. Warum liegt die Bankverbindung auf Mandantenebene, das Abstimmkonto aber auf Buchungskreisebene?")
E[14] = dict(ref=[("S4500",15)],
 A="Richtig. Über die Favoriten im SAP-Easy-Access-Menü können Sie navigieren.",
 B="Falsch. Transaktionen aus Excel heraus aufzurufen ist keine Navigationsart im SAP GUI.",
 C="Richtig. Transaktionscodes können direkt im Befehlsfeld eingegeben werden.",
 D="Falsch. Die Statusleiste zeigt Meldungen und Systeminformationen an; navigieren lässt sich darüber nicht.",
 frage="Welche drei Navigationswege nennt das Buch für das SAP GUI, und welchen nutzen Sie im Alltag am häufigsten?")
E[81] = dict(ref=[("S4500",6),("S4500",7)],
 A="Falsch. Sprache und Region sind einstellbar, Adresse und Telefonnummer aber nicht; sie gehören zum Benutzerstamm.",
 B="Falsch (laut Lösung). Favoriten gehören zur Personalisierung im SAP GUI (Easy Access) und stehen nicht in der Liste der Launchpad-Einstellungen.",
 C="Richtig. Benutzer können im Launchpad Standardwerte pflegen, z. B. für Werk oder Einkaufsorganisation.",
 D="Richtig. Das Design-Theme ist frei wählbar.",
 frage="Welche Standardwerte würden Sie sich in Ihrem Launchpad hinterlegen, damit Sie in den Einkaufs-Apps weniger tippen müssen?")
E[27] = dict(ref=[("S4500",85),("S4500",87)],
 A="Falsch. Gerade weil Geschäftspartner zentral gepflegt werden, sollten Sie vor dem Anlegen prüfen, ob der Lieferant schon existiert; sonst entstehen Dubletten.",
 B="Falsch. Ein Geschäftspartner wird von Buchhaltung und Einkauf gemeinsam genutzt; jede Abteilung ergänzt nur ihre Rollen und Daten.",
 C="Richtig. Durch die Integration gehen Rechnungen und Gutschriften automatisch mit den nötigen Daten in die Kreditorenbuchhaltung.",
 D="Richtig. Der Geschäftspartner enthält allgemeine Daten, Buchungskreisdaten und Einkaufsdaten, also alles, was beide Bereiche brauchen.",
 frage="Was passiert im Hintergrund, wenn Sie einem Geschäftspartner die Rolle Kreditor (FLVN00) hinzufügen? Was bedeutet das für die Abstimmung zwischen Einkauf und Buchhaltung?")
E[39] = dict(ref=[("S4520",24),("S4520",308)],
 A="Falsch. Der Infosatz übernimmt die Bestätigungspflicht als Vorschlag aus dem Lieferanten. Für alle Bestellungen eines Lieferanten ist er nicht die richtige Stelle.",
 B="Richtig. „Auftragsbestätigungspflicht“ ist ein Steuerungskennzeichen in den Einkaufsdaten des Geschäftspartners und wird in Belege dieses Lieferanten vorgeschlagen.",
 C="Falsch. Der Materialstamm ist lieferantenunabhängig; eine lieferantenbezogene Vorgabe gehört nicht dorthin.",
 D="Falsch. Grunddaten sind allgemeine, lieferantenunabhängige Materialdaten.",
 frage="Welche weiteren Steuerungskennzeichen nennt das Buch in den Einkaufsdaten des Geschäftspartners, und welche Wirkung haben sie auf Infosätze und Bestellungen?")
E[77] = dict(ref=[("S4520",24),("S4520",308)],
 A="Falsch. Der Materialstamm ist lieferantenunabhängig; eine lieferantenbezogene Vorgabe gehört nicht dorthin.",
 B="Richtig. „Auftragsbestätigungspflicht“ ist ein Steuerungskennzeichen in den Einkaufsdaten des Geschäftspartners und wird in Belege dieses Lieferanten vorgeschlagen.",
 C="Falsch. Grunddaten sind allgemeine, lieferantenunabhängige Materialdaten.",
 D="Falsch. Der Infosatz bekommt das Kennzeichen als Vorschlag aus dem Lieferanten; für alle Bestellungen eines Lieferanten ist der Geschäftspartner die richtige Stelle.",
 frage="Sie wollen die Bestätigungspflicht nur für ein bestimmtes Material dieses Lieferanten. Wo würden Sie sie dann pflegen?")
E[67] = dict(ref=[("S4520",24),("S4520",41),("S4520",42)],
 A="Falsch. Partnerrollen werden direkt im Geschäftspartner (Transaktion BP) bei den Einkaufsdaten gepflegt; eine Spezialtransaktion braucht es nicht.",
 B="Falsch. Sie können mehrere Partnerrollen pflegen (Bestelladresse, Warenlieferant, Rechnungssteller, Zahlungsempfänger), und je nach Customizing sogar mehrere Partner pro Rolle.",
 C="Richtig. Ist ein abweichender Rechnungssteller hinterlegt, wird er beim Buchen der Rechnung automatisch ermittelt.",
 D="Richtig. Jeder Partner, der eine Rolle übernimmt, braucht einen eigenen Geschäftspartnerstammsatz, so auch der Warenlieferant.",
 frage="Spielen Sie das ABC-Beispiel aus dem Buch durch: Welche drei Stammsätze brauchen Sie, und in welchem davon pflegen Sie die Partnerrollen?")
E[87] = dict(ref=[("S4520",41)],
 A="Falsch. Der Stammsatz ist nicht von der Belegart abhängig. Er ist immer nötig.",
 B="Richtig. Jeder abweichende Partner muss selbst als Geschäftspartner angelegt sein.",
 C="Falsch. Auch der Positionstyp ändert nichts an dieser Voraussetzung.",
 frage="Welche Customizing-Einstellungen (Partnerschema, Kontengruppe) müssen außerdem stimmen, damit eine abweichende Bestelladresse in der Bestellung erscheint?")
E[85] = dict(ref=[("S4520",26),("S4520",27)],
 A="Richtig. Ein CpD- bzw. Einmallieferant ist ein Sammelstammsatz, den Sie für viele verschiedene Lieferanten verwenden.",
 B="Falsch. Die Anzahl der Lieferungen ist egal. Ein CpD-Lieferant lohnt sich, wenn Sie nur selten oder einmalig bei einem Lieferanten kaufen.",
 C="Falsch. Der CpD-Stammsatz trägt den ganzen Prozess bis zur Rechnung; die individuellen Adressdaten werden im Beleg erfasst.",
 D="Richtig. Weil er für viele Lieferanten gilt, enthält er keine lieferantenspezifische Adresse; diese wird im Einkaufsbeleg manuell eingegeben.",
 frage="Ab wann würden Sie aus einem CpD-Lieferanten einen „richtigen“ Geschäftspartner machen? Nennen Sie zwei Kriterien.")
E[9] = dict(ref=[("S4520",153),("S4520",154),("S4520",155),("S4520",156)],
 A="Richtig. Feinabrufe informieren über den kurzfristigen Bedarf, tages- oder sogar stundengenau.",
 B="Falsch. Es gibt nur das Feinabrufkennzeichen. Bleibt es leer, sind nur Lieferabrufe möglich; mit Wert 1 sind auch Feinabrufe möglich.",
 C="Falsch. Abrufe können auch direkt in der Einteilungspflege (ME38: LAB bzw. FAB erzeugen) oder automatisch per Bericht angelegt werden.",
 D="Richtig. Lieferabrufe geben dem Lieferanten einen mittel- bis langfristigen Überblick.",
 E="Richtig. Liefer- und Feinabrufe gibt es nur bei Lieferplänen mit Abrufdokumentation (z. B. Belegart LPA).",
 frage="Warum muss das Feinabrufkennzeichen schon im Materialstamm gesetzt sein, bevor der Lieferplan angelegt wird? Was würden Sie tun, wenn Sie es vergessen haben?")
E[26] = dict(ref=[("S4520",141),("S4520",142)],
 A="Falsch. Ein Zielwert ist typisch für Wertkontrakte; der Lieferplan arbeitet mit einer Gesamtabnahmemenge.",
 B="Richtig. Ein Lieferplan gilt für einen vorgegebenen Zeitraum, deshalb braucht er ein Beginndatum (Laufzeit).",
 C="Richtig. Lieferpläne sind immer werksbezogen; einen Zentral-Lieferplan ohne Werk gibt es nicht.",
 D="Falsch. Das Abruferstellungsprofil ist nur bei Lieferplänen mit Abrufdokumentation relevant und auch dort optional.",
 E="Richtig. Der Lieferplan gilt für eine vereinbarte Gesamtabnahmemenge, die Zielmenge der Position.",
 frage="Ein Kontrakt kann ein Zentralkontrakt ohne Werk sein, ein Lieferplan nicht. Warum ergibt das bei Lieferplänen Sinn? Denken Sie an die Einteilungen aus der Disposition.")
E[64] = dict(ref=[("S4520",153),("S4520",156),("S4520",145)],
 A="Falsch. Das Kennzeichen wird nicht im einzelnen Lieferplan gesetzt, sondern ist im Customizing an der Belegart hinterlegt.",
 B="Richtig. Bei der Belegart LPA ist die Abrufdokumentation im Customizing voreingestellt.",
 C="Falsch. LP ist die Belegart ohne Abrufdokumentation.",
 D="Falsch. Weder im Lieferplan noch im Materialstamm gibt es ein solches Kennzeichen. Im Materialstamm gibt es nur das Feinabrufkennzeichen.",
 frage="Wann würden Sie bewusst LP statt LPA nehmen? Denken Sie an die Zahl der Einteilungen und die Nachvollziehbarkeit.")
E[65] = dict(ref=[("S4520",159),("S4520",160)],
 A="Richtig. Beide Fixierungszeiträume werden in den Einteilungen gedruckt und mit übermittelt.",
 B="Falsch. Umgekehrt: Einteilungen im ersten Fixierungszeitraum (Produktionsfreigabe) gelten als fixiert und damit als verbindliche Bestellung.",
 C="Falsch. Der erste Fixierungszeitraum hat den höheren Verbindlichkeitsgrad.",
 D="Richtig. Der zweite Fixierungszeitraum (Materialfreigabe) kann einen geringeren Verbindlichkeitsgrad haben als der erste.",
 frage="Welche Zeitspanne bildet der Produktionsfreigabezeitraum beim Lieferanten typischerweise ab, und welche der Materialfreigabezeitraum?")
E[23] = dict(ref=[("S4520",111),("S4520",113),("S4500",271)],
 A="Falsch. Beim Kontrakt ist jeder Abruf eine eigene Bestellung. Weniger Belege hat man beim Lieferplan.",
 B="Richtig. Über die Abrufdokumentation sehen Sie jederzeit, wie viel Zielmenge oder Zielwert schon abgerufen ist. Sie ist die Grundlage der Kontraktüberwachung.",
 C="Falsch. Liefertermine vorab planen und als Vorschau senden ist eine Stärke des Lieferplans (Einteilungen, Lieferabrufe).",
 D="Falsch. Die Disposition kann den Kontrakt nur als Bezugsquelle zuordnen; die Bestellanforderung muss trotzdem noch in einen Kontraktabruf umgesetzt werden. Direkte Einteilungen gibt es nur beim Lieferplan.",
 frage="Sie beziehen ein Material täglich in Serie. Würden Sie Kontrakt oder Lieferplan wählen? Begründen Sie mit Belegvolumen und Disposition.")
E[37] = dict(ref=[("S4520",113),("S4500",271)],
 A="Richtig. Die bereits abgerufene Menge (bzw. der abgerufene Wert) wird angezeigt.",
 B="Falsch. Der Ersteller eines Abrufs ist nicht Teil der Abrufdokumentation.",
 C="Richtig. Pro Abruf wird der Bestellwert angezeigt.",
 D="Richtig. Pro Abruf werden Bestellnummer und Position angezeigt.",
 E="Falsch. Angezeigt wird das Bestelldatum, nicht das Lieferdatum.",
 frage="Wo wird bei einem Wertkontrakt fortgeschrieben, und wo bei einem Mengenkontrakt (Kopf oder Position)?")
E[75] = dict(ref=[("S4520",113),("S4500",271)],
 A="Falsch. Der Ersteller eines Abrufs ist nicht Teil der Abrufdokumentation.",
 B="Richtig. Pro Abruf werden Bestellnummer und Position angezeigt.",
 C="Richtig. Pro Abruf wird der Bestellwert angezeigt.",
 D="Falsch. Angezeigt wird das Bestelldatum, nicht das Lieferdatum.",
 E="Richtig. Die bereits abgerufene Menge (bzw. der abgerufene Wert) wird angezeigt.",
 frage="Ein Lieferant liefert bei einem Kontraktabruf 10 % mehr als bestellt. Taucht das in der Abrufdokumentation auf? (Tipp: Customizing OMXX)")
E[53] = dict(ref=[("S4500",270),("S4500",367),("S4500",368)],
 A="Richtig. Ein Kontraktabruf ist eine normale Bestellung mit Bezug zum Kontrakt, z. B. in „Bestellung anlegen“ (ME21N).",
 B="Falsch. Eine eigene Transaktion „Kontraktabruf anlegen“ gibt es nicht; Abrufe sind Bestellungen.",
 C="Richtig. Hat die Bestellanforderung die Kontraktposition als Bezugsquelle, erzeugt die automatische Bestellerzeugung daraus einen Kontraktabruf.",
 D="Falsch. In „Kontrakt ändern“ gibt es keine Folgefunktion, die einen Abruf erzeugt.",
 frage="Welche Voraussetzungen müssen im Material- und im Lieferantenstamm erfüllt sein, damit die automatische Bestellerzeugung funktioniert?")
E[84] = dict(ref=[("S4520",114),("S4500",270)],
 A="Richtig. Der Mengenkontrakt (MK) ist erfüllt, wenn die Zielmenge pro Position erreicht ist.",
 B="Richtig. Der Wertkontrakt (WK) ist erfüllt, wenn der Zielwert im Kopf erreicht ist.",
 C="Falsch. Einen „Lieferkontrakt“ gibt es nicht. Gemeint ist wohl der Lieferplan, und der ist eine eigene Art Rahmenvertrag.",
 D="Falsch. „Werkskontrakt“ ist keine Kontraktart. Werks- und Zentralkontrakt unterscheiden sich nur darin, ob in der Position ein Werk steht.",
 frage="Sie kennen nur das Jahresbudget für Büromaterial, aber nicht die einzelnen Mengen. Welche Kontraktart wählen Sie, und was müssen Sie im Kopf eingeben?")
E[29] = dict(ref=[("S4500",295),("S4500",296)],
 A="Richtig. Ein Doppelklick auf eine Bestellanforderung zeigt diese an.",
 B="Falsch. Lieferpläne lassen sich aus der Belegübersicht nicht per Doppelklick anzeigen.",
 C="Falsch. Auch Anfragen und Angebote nicht; das geht nur bei Bestellungen und Bestellanforderungen.",
 D="Richtig. Ein Doppelklick auf eine Bestellung zeigt diese an.",
 frage="Ein Doppelklick zeigt einen Beleg nur an. Wie übernehmen Sie dagegen eine Bestellanforderung als Vorlage in Ihre neue Bestellung?")
E[42] = dict(ref=[("S4500",295)],
 A="Richtig. Beleg markieren und „Übernehmen“ wählen kopiert ihn in die Bestellung.",
 B="Falsch. Ein einfacher Klick markiert den Beleg nur.",
 C="Richtig. Sie können den Beleg per Drag-and-Drop in den Einkaufswagen ziehen.",
 D="Falsch. Ein Doppelklick zeigt den Beleg nur an, er wird nicht kopiert.",
 frage="Wie fassen Sie zwei Bestellanforderungen für dasselbe Material, die sich nur im Lieferdatum unterscheiden, in einer Bestellposition mit zwei Einteilungen zusammen?")
E[73] = dict(ref=[("S4500",295)],
 A="Falsch. Ein Doppelklick zeigt den Beleg nur an, er wird nicht kopiert.",
 B="Richtig. Sie können den Beleg per Drag-and-Drop in den Einkaufswagen ziehen.",
 C="Richtig. Beleg markieren und „Übernehmen“ wählen kopiert ihn in die Bestellung.",
 D="Falsch. Ein einfacher Klick markiert den Beleg nur.",
 frage="Welche Daten werden beim Anlegen mit Bezug aus dem Vorlagebeleg übernommen, und wo sehen Sie später, aus welchem Beleg eine Position stammt?")
E[33] = dict(ref=[("S4500",295)],
 A="Falsch. In der Belegübersicht wählen Sie Vorlagebelege aus, Vorschlagswerte pflegen Sie dort nicht.",
 B="Richtig. Über die persönlichen Einstellungen (Pers. Einstellungen) hinterlegt jeder Benutzer eigene Vorschlagswerte in ME21N.",
 C="Falsch. „Standardeinstellungen“ heißt die Funktion nicht.",
 D="Falsch. „Individuelle Einstellungen“ heißt die Funktion ebenfalls nicht.",
 frage="Welche Vorschlagswerte würden Sie in ME21N hinterlegen, und welcher Wert lässt sich zusätzlich über den Benutzerparameter EVO vorbelegen?")
E[83] = dict(ref=[("S4500",49)],
 A="Falsch. Der Positionstyp Warengruppe (W) ist nur in Kontrakten zulässig.",
 B="Falsch. „Material unbekannt“ (M) ist ebenfalls nur in Kontrakten zulässig.",
 C="Richtig. Normal bzw. Standard ist möglich.",
 D="Richtig. Strecke (S) ist möglich, ebenso Konsignation (K), Lohnbearbeitung (L) und Erweitertes Limit (E).",
 frage="Welche Positionstypen bietet „Bestellungen verwalten“ an, die Sie in ME21N auch haben, und welcher klassische Typ fehlt? (Tipp: Limit B gegen E)")
E[43] = dict(ref=[("S4500",48),("S4500",49),("S4520",429)],
 A="Richtig. Standard ist in Bestellanforderung und Bestellung möglich.",
 B="Richtig. Konsignation ist in beiden Belegen möglich.",
 C="Richtig. Lohnbearbeitung ist in beiden möglich; das Material kann über eine Bestellanforderung angefordert und mit Positionstyp L bestellt werden.",
 D="Falsch. Warengruppe (W) ist nur in Kontrakten zulässig.",
 E="Falsch. Material unbekannt (M) ist nur in Kontrakten zulässig.",
 frage="Warum ergeben die Positionstypen M und W nur im Kontrakt Sinn und nicht in einer Bestellung?")
E[25] = dict(ref=[("S4500",48),("S4500",49),("S4520",429)],
 A="Falsch. Bei der Lohnbearbeitung wird Positionstyp L verwendet; B steht für Limit.",
 B="Richtig (laut Lösung). Der Lieferant fertigt ein Endprodukt und braucht dafür Komponenten, die ihm beigestellt werden. Das Buch ergänzt, dass Komponenten auch von einem Drittlieferanten direkt an den Lohnbearbeiter geliefert werden können.",
 C="Richtig. Mit der Umlagerungsbestellung wird Material zwischen Werken eines Unternehmens beschafft und geliefert.",
 D="Falsch. Bei Konsignation wird Positionstyp K verwendet; L steht für Lohnbearbeitung.",
 frage="Welche Positionstypen gehören zu welchem Buchstaben: K, L, S, B, U? Und was passiert bei Lohnbearbeitung automatisch beim Wareneingang des Endprodukts?")
E[46] = dict(ref=[("S4500",48),("S4520",96)],
 A="Falsch. Konsignationsbestand wird pro Lieferant getrennt geführt, denn jeder Lieferant ist Eigentümer seiner Ware.",
 B="Falsch. Bis zur Entnahme wird der Bestand nicht bewertet. Erst die Entnahme löst eine Verbindlichkeit mit dem Preis aus dem Konsignationsinfosatz aus.",
 C="Richtig. Konsignationsbestand liegt bei Ihnen im Lager und wird mengenmäßig auf Lagerortebene geführt.",
 D="Richtig. Bis zur Entnahme gehört das Material dem Lieferanten.",
 frage="Warum enthält eine Konsignationsbestellung keinen Preis, und woher kommt der Preis bei der Entnahme?")
E[51] = dict(ref=[("S4500",48),("S4520",96)],
 A="Falsch. Der Wareneingang in den Konsignationsbestand führt noch zu keiner Bewertung und keiner Verbindlichkeit.",
 B="Falsch. Die Einplanung beim Lieferanten hat keine buchhalterische Wirkung.",
 C="Falsch. Die Übermittlung der Bestellung erzeugt keine Verbindlichkeit.",
 D="Richtig. Die Verbindlichkeit entsteht erst bei der Entnahme aus dem Konsignationsbestand.",
 frage="Welchen Vorteil hat Konsignation für Ihre Liquidität, und welchen Nachteil könnte sie für den Lieferanten haben?")
E[82] = dict(ref=[("S4500",128),("S4520",95),("S4520",96)],
 A="Richtig. Lohnbearbeitung ist ein Infotyp.",
 B="Richtig. Konsignation ist ein Infotyp; der Preis daraus wird bei Entnahme verwendet.",
 C="Falsch. Limit ist ein Positionstyp in Bestellungen, kein Infotyp.",
 D="Falsch. Strecke ist ein Positionstyp, kein Infotyp.",
 frage="Welcher vierte Infotyp neben Normal, Lohnbearbeitung und Konsignation steht im Buch, und warum gibt es ihn nur mit Material?")
E[32] = dict(ref=[("S4520",95),("S4520",96),("S4500",127)],
 A="Falsch (laut Lösung). Gemeint sind Infosätze ohne Materialstammsatz. Diese beziehen sich zwar auf eine Warengruppe, in der Lösung zählt aber die Formulierung „unabhängig vom Materialstamm“.",
 B="Falsch. Ein Infosatz gilt nie für einen Lieferanten allein, sondern immer für eine Kombination aus Lieferant und Material oder Warengruppe.",
 C="Richtig. Infosätze ohne Materialstammsatz, z. B. für Verbrauchsmaterial, gibt es.",
 D="Richtig. Infosätze mit Materialstammsatz, z. B. für Lagermaterial, gibt es ebenfalls.",
 hinweis="Im Buch heißen die beiden Arten „Infosätze mit Materialstammsatz“ und „Infosätze ohne Materialstammsatz (Warengruppe/Lieferant)“.",
 frage="Wird ein Warengruppen-Infosatz in der Bestellung automatisch als Bezugsquelle vorgeschlagen? Und in der Bestellanforderung?")
E[57] = dict(ref=[("S4500",127),("S4520",78),("S4520",79)],
 A="Richtig. Derzeitige und künftige Preise und Konditionen sind im Infosatz enthalten.",
 B="Falsch. Infosätze werden auf Mandanten-, Einkaufsorganisations- und ggf. Werksebene gepflegt, nicht pro Buchungskreis.",
 C="Richtig. Die Planlieferzeit des Lieferanten für das Material steht im Infosatz.",
 D="Falsch. Lagerorte spielen im Infosatz keine Rolle.",
 E="Richtig. Einkaufsdaten wie Unter- und Überlieferungstoleranzen sind enthalten.",
 frage="Welche Infosatzdaten liegen auf Mandantenebene und welche pro Einkaufsorganisation bzw. Werk?")
E[40] = dict(ref=[("S4500",129),("S4500",130),("S4520",81),("S4520",82)],
 A="Richtig. Aus Bestellungen werden Beleg- und Positionsnummer als letzter Beleg in den Infosatz geschrieben.",
 B="Richtig. Gibt es noch keinen Infosatz, wird er über das Kennzeichen automatisch angelegt.",
 C="Falsch. Konditionen werden über InfoUpdate in einer Bestellung nie angelegt oder fortgeschrieben.",
 D="Falsch. Vorgeschlagen werden die Konditionen des Infosatzes. Nur wenn dort keine gepflegt sind, kommt der Preis der letzten Bestellung, und das steuert der Benutzerparameter EVO, nicht das Kennzeichen.",
 frage="Was bewirkt InfoUpdate bei einem Angebot und bei einem Kontrakt im Unterschied zur Bestellung?")
E[49] = dict(ref=[("S4520",81),("S4520",80)],
 A="Richtig. Zuerst werden werksbezogene Konditionen gesucht, dann die der Einkaufsorganisation; erst ohne Konditionen kommt der Preis aus dem letzten Beleg.",
 B="Falsch. Der letzte Beleg ist nur die Rückfallebene, wenn im Infosatz keine Konditionen gepflegt sind.",
 C="Falsch. Die spezifischere Ebene (mit Werk) geht vor der allgemeinen.",
 D="Falsch. Auch hier steht die allgemeine Ebene vor der spezifischeren; es ist genau umgekehrt.",
 frage="Was müssen Sie im Customizing einstellen, damit Konditionen überhaupt auf Werksebene im Infosatz gesichert werden können?")
E[50] = dict(ref=[("S4520",68),("S4500",131)],
 A="Falsch. Bei Lieferplänen bestimmt die Belegart, ob Konditionen zeitabhängig oder zeitunabhängig sind.",
 B="Richtig. Konditionen in Infosätzen sind immer zeitabhängig.",
 C="Falsch. Konditionen in Bestellungen sind immer zeitunabhängig.",
 D="Richtig. Konditionen in Kontrakten sind immer zeitabhängig.",
 frage="Was können Sie mit zeitabhängigen Konditionen machen, was mit zeitunabhängigen nicht geht? (Gültigkeit, Staffeln, Preisspannen)")
E[34] = dict(ref=[("S4520",67),("S4520",70),("S4500",130),("S4500",131)],
 A="Falsch. In Bestellanforderungen pflegen Sie keine Konditionen, sondern nur einen Bewertungspreis.",
 B="Falsch. Kopfkonditionen gelten für alle Positionen eines Belegs.",
 C="Richtig. Konditionen können in Angeboten, Infosätzen, Rahmenverträgen und Bestellungen gespeichert werden.",
 D="Richtig. Die Kontraktkonditionen kommen nur dann in die Bestellposition, wenn sie mit Bezug zum Kontrakt (als Kontraktabruf) angelegt wird.",
 frage="Sie legen eine Bestellung für ein Material an, für das es einen Infosatz und einen Kontrakt gibt, aber ohne Kontraktbezug. Welche Konditionen werden vorgeschlagen?")
E[60] = dict(ref=[("S4520",70),("S4500",131)],
 A="Richtig. Kopfkonditionen gelten für sämtliche Positionen des Belegs.",
 B="Falsch. Zahlungsbedingungen regeln Zahlungsziele und Skonto, keinen einmaligen Rabatt.",
 C="Falsch. Allgemeine Lieferantenkonditionen (z. B. MEKE) würden für alle künftigen Bestellungen gelten, nicht nur für diese eine.",
 D="Falsch. Positionskonditionen gelten nur für die jeweilige Position; Sie müssten den Rabatt bei jeder Position einzeln erfassen.",
 frage="Wie wird ein absoluter Kopfrabatt (z. B. 100 EUR) auf mehrere Positionen verteilt, und welche Rolle spielt dabei die Gruppenkondition?")
E[76] = dict(ref=[("S4520",70),("S4500",131)],
 A="Falsch. Zahlungsbedingungen regeln Zahlungsziele und Skonto, keinen einmaligen Rabatt.",
 B="Falsch. Allgemeine Lieferantenkonditionen würden für alle künftigen Bestellungen gelten, nicht nur für diese eine.",
 C="Falsch. Positionskonditionen gelten nur für die jeweilige Position.",
 D="Richtig. Kopfkonditionen gelten für sämtliche Positionen des Belegs.",
 frage="Wann würden Sie statt einer Kopfkondition doch allgemeine Lieferantenkonditionen pflegen?")
E[68] = dict(ref=[("S4520",69),("S4500",130)],
 A="Falsch. Bezugsnebenkosten und Skonto gehören zum Effektivpreis, nicht zum Nettopreis.",
 B="Falsch. Skonto wird beim Effektivpreis abgezogen, nicht beim Nettopreis addiert.",
 C="Richtig. Nettopreis = Bruttopreis plus/minus Zu- und Abschläge, ohne Bezugsnebenkosten und ohne Skonto.",
 D="Falsch. Bezugsnebenkosten sind nicht Teil des Nettopreises.",
 frage="Rechnen Sie: Bruttopreis 100 EUR, 5 % Rabatt, 2 EUR Mindermengenzuschlag, 3 EUR Fracht, 2 % Skonto. Wie hoch sind Netto- und Effektivpreis?")
E[48] = dict(ref=[("S4520",308),("S4520",309)],
 A="Falsch. Im Materialstamm gibt es keine Option „Mahnungen senden“. Er kann höchstens über den Einkaufswerteschlüssel die Bestätigungspflicht vorschlagen.",
 B="Falsch. Auch im Lieferantenstamm wird nur die Bestätigungspflicht vorbelegt; einen Schalter für Mahnungen gibt es dort nicht.",
 C="Richtig. In der Bestellung muss „Bestätigungspflicht“ markiert sein.",
 D="Richtig. Der Beleg muss bereits ausgegeben worden sein, denn wer nichts bekommen hat, kann nicht gemahnt werden.",
 frage="Welche weiteren Voraussetzungen nennt das Buch, z. B. für Nachrichtenfindung und Nachrichtensätze? Und wie überwachen Sie Bestätigungen ohne Mahnungen (ME2A)?")
E[72] = dict(ref=[("S4520",281),("S4520",282),("S4500",270)],
 A="Richtig. Ist eine Kontraktposition die Bezugsquelle, entsteht bei der Umsetzung eine Bestellung mit Kontraktbezug, also ein Kontraktabruf.",
 B="Richtig. Die zugeordneten Positionen können direkt in Bestellungen umgesetzt werden.",
 C="Falsch. Umgesetzt wird in Anfragen. Angebote erfasst man erst, wenn der Lieferant auf die Anfrage antwortet.",
 D="Falsch. Quotierungen sind Stammdaten der Bezugsquellenfindung und keine Folgebelege.",
 E="Richtig. Ist ein Lieferplan zugeordnet, werden Lieferplaneinteilungen erzeugt.",
 frage="Was passiert mit einer Vormerkung für die Anfrage, wenn Sie die Transaktion verlassen, ohne die Anfrage anzulegen?")
E[79] = dict(ref=[("S4500",51),("S4500",52),("S4520",56),("S4520",319)],
 A="Richtig. Druck ist ein Ausgabekanal.",
 B="Richtig. EDI ist ein gängiger elektronischer Ausgabekanal.",
 C="Falsch. Nachrichten werden über die Nachrichtenwarteschlange ausgegeben, sofort beim Sichern oder später per Job bzw. App. Das ist nicht an ME21N gebunden.",
 D="Richtig. E-Mail ist ein Ausgabekanal (im Buch über die Ausgabeparameterfindung mit Kanal EMAIL eingerichtet).",
 E="Falsch. Das SAP Business Workplace ist kein alleiniger Ausgabeweg.",
 hinweis="Das Buch zeigt Druck und E-Mail in Übungen. EDI ist allgemeines SAP-Wissen und wird im Buch nicht ausführlich behandelt.",
 frage="Wann würden Sie eine Nachricht sofort ausgeben und wann über einen Hintergrundjob?")


def fnv1a(text):
    """Gleicher Hash wie hash() in app.js (FNV-1a über UTF-16-Codeeinheiten)."""
    h = 0x811C9DC5
    daten = text.encode("utf-16-le")
    for i in range(0, len(daten), 2):
        h ^= daten[i] | (daten[i + 1] << 8)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return "%08x" % h


def fundort(buch, seite):
    kapitel = lektion = None
    for art, ab, titel in TOC[buch]:
        if ab <= seite:
            if art == "K":
                kapitel, lektion = titel, None
            else:
                lektion = titel
    return kapitel, lektion


def fundstellen(refs):
    gruppen = []
    for buch, seite in sorted(set(refs), key=lambda r: (r[0], r[1])):
        kapitel, lektion = fundort(buch, seite)
        if gruppen and gruppen[-1]["buch"] == buch and gruppen[-1]["lektion"] == lektion:
            gruppen[-1]["seiten"].append(seite)
        else:
            gruppen.append({"buch": buch, "kapitel": kapitel, "lektion": lektion, "seiten": [seite]})
    return gruppen


def main():
    basis = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    fragen = json.load(open(os.path.join(basis, "data", "fragen.json"), encoding="utf-8"))["fragen"]
    fehler = []
    aus = []
    for q in fragen:
        e = E.get(q["nr"])
        if not e:
            fehler.append("Frage %s: keine Erklärung" % q["nr"])
            continue
        antworten = {}
        for a in q["antworten"]:
            text = e.get(a["id"])
            if not text:
                fehler.append("Frage %s: Antwort %s ohne Begründung" % (q["nr"], a["id"]))
                continue
            if text.startswith("Richtig") != a["richtig"]:
                fehler.append("Frage %s: Antwort %s passt nicht zum Lösungsschlüssel" % (q["nr"], a["id"]))
            antworten[a["id"]] = text
        key = fnv1a(q["frage"] + "|" + "|".join(a["text"] for a in q["antworten"]))
        eintrag = {"nr": q["nr"], "key": key, "fundstellen": fundstellen(e["ref"]),
                   "antworten": antworten, "offeneFrage": e["frage"]}
        if e.get("hinweis"):
            eintrag["hinweis"] = e["hinweis"]
        aus.append(eintrag)
    if fehler:
        print("\n".join(fehler))
        sys.exit(1)
    ziel = os.path.join(basis, "data", "erklaerungen.json")
    with open(ziel, "w", encoding="utf-8") as f:
        json.dump({"buecher": BUECHER, "erklaerungen": aus}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("%d Erklärungen geschrieben: %s" % (len(aus), ziel))


if __name__ == "__main__":
    main()
