# Anleitung zur Wetteranalyse Kassel

Diese Anwendung ermöglicht eine umfassende Analyse historischer Wetterdaten für den Raum Kassel und den Landkreis Kassel mit interaktiven Visualisierungen und Diagrammen.

## Installationsanleitung

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python-Paketmanager)

### Installation

1. Klonen Sie das Repository oder entpacken Sie die Dateien in einen Ordner Ihrer Wahl.

2. Öffnen Sie eine Kommandozeile (cmd/PowerShell unter Windows, Terminal unter macOS/Linux) und navigieren Sie zum Projektordner:
   ```
   cd pfad/zum/wetteranalyse-ordner
   ```

3. Installieren Sie die benötigten Abhängigkeiten mit:
   ```
   pip install -r requirements.txt
   ```
   
   Dies installiert alle erforderlichen Python-Bibliotheken wie pandas, matplotlib, plotly, dash und meteostat.

## Verwendung der Anwendung

1. Starten Sie die Anwendung mit:
   ```
   python app.py
   ```

2. Öffnen Sie einen Webbrowser und navigieren Sie zu:
   ```
   http://127.0.0.1:8050
   ```

3. Die Benutzeroberfläche ist in mehrere Bereiche unterteilt:

   Linke Seitenleiste:
   - Datenauswahl: Hier können Sie den Zeitraum (von Jahr bis Jahr) für die Analyse auswählen.
   - Wetterstationen: Nach dem Klicken auf "Daten laden" werden verfügbare Wetterstationen in der Nähe von Kassel angezeigt. Sie können eine spezifische Station auswählen oder die automatische Auswahl verwenden.
   - Statistiken: Zeigt statistische Zusammenfassungen der ausgewählten Daten an.
   - Datenexport: Ermöglicht den Export der erzeugten Diagramme als Bilddateien.

   Hauptbereich (Registerkarten):
   - Dashboard: Zeigt eine Übersicht mit mehreren Diagrammen (Temperatur, Niederschlag, Jahreszeiten, Trends).
   - Temperatur: Detaillierte Ansicht des Temperaturverlaufs mit Minimum, Maximum und Durchschnitt.
   - Niederschlag: Analyse der Niederschlagsmengen über den gewählten Zeitraum.
   - Jahreszeiten: Vergleich der Wetterdaten nach Jahreszeiten.
   - Trends: Langzeittrends und Entwicklungen der Wetterdaten.

## Datenanalyse

Die Anwendung ermöglicht folgende Analysen:

1. Temperaturanalyse:
   - Langzeittrends der Durchschnittstemperaturen
   - Saisonale Schwankungen und Extreme
   - Identifikation von Hitzewellen und Kälteperioden

2. Niederschlagsanalyse:
   - Jahres- und Monatsniederschläge
   - Trends in der Niederschlagsmenge
   - Verteilung über Jahreszeiten

3. Klimawandelanalyse:
   - Temperaturtrends über längere Zeiträume
   - Veränderungen in Niederschlagsmustern
   - Saisonale Verschiebungen

## Exportieren der Ergebnisse

Sie können die erstellten Diagramme als Bilddateien exportieren, indem Sie auf die Schaltfläche "Grafiken exportieren" klicken. Die Dateien werden im Ordner "exports" gespeichert und können für Präsentationen, Berichte oder weitere Analysen verwendet werden.

Die exportierten Dateien umfassen:
- Wetterdashboard
- Temperaturverlauf
- Niederschlagsanalyse
- Saisonale Vergleiche
- Langzeittrends

## Tipps zur Dateninterpretation

- Langzeittrends: Achten Sie auf die roten Trendlinien in den Diagrammen, die langfristige Entwicklungen anzeigen.
- Saisonalität: Die Boxplots der Jahreszeiten zeigen die typische Verteilung sowie Ausreißer.
- Extremwerte: In den Statistiken werden die extremsten Ereignisse mit Datum angezeigt.
- Datenlücken: Bei manchen Zeiträumen oder Wetterstationen können Datenlücken auftreten. Diese werden in den Diagrammen entsprechend visualisiert.

## Fehlerbehebung

Problem: Die Anwendung startet nicht.
Lösung: Überprüfen Sie, ob alle Abhängigkeiten korrekt installiert sind. Installieren Sie die Pakete erneut mit `pip install -r requirements.txt`.

Problem: Es werden keine Daten angezeigt.
Lösung: Stellen Sie sicher, dass der ausgewählte Zeitraum gültige Daten enthält und eine Wetterstation verfügbar ist. Möglicherweise sind für sehr weit zurückliegende Zeiträume keine Daten verfügbar.

Problem: Die Grafiken werden nicht exportiert.
Lösung: Überprüfen Sie, ob der Ordner "exports" existiert und ob die Anwendung Schreibrechte für diesen Ordner hat.

## Datenquellen

Die Anwendung nutzt die Meteostat-API, die Daten von offiziellen Wetterstationen des Deutschen Wetterdienstes (DWD) und anderen Quellen bezieht. Die Daten werden über die meteostat-Bibliothek abgerufen, die eine einfache Schnittstelle zu historischen Wetterdaten bietet. 