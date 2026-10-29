Hier ist eine vollständige, übersichtliche Dokumentation im Markdown-Format, zugeschnitten auf die Nutzung des **`master`**-Branches.

# Git-Workflow: Custom MapStyle & Upstream Sync

Diese Dokumentation beschreibt die Einrichtung und den Pflege-Workflow für diesen benutzerdefinierten Guru Maps Stil (`MapStyle`).
Ziel ist es, tiefgreifende eigene MapCSS-Anpassungen vorzunehmen und gleichzeitig zukünftige Updates des offiziellen Repositories ([GuruMaps/MapStyle](https://github.com/GuruMaps/MapStyle)) konfliktarm einzupflegen.

---

## 1. Branch-Architektur

Um den modifizierten Arbeitsstand sauber vom Original-Code zu trennen, werden zwei primäre Branches genutzt:

* **`master`** (Arbeits-Branch): Enthält den benutzerdefinierten Kartenstil mit allen eigenen Modifikationen (Farben, Symbole, Zoomstufen-Filter).
* **`upstream-sync`** (Spiegel-Branch): Ein unberührter 1:1-Spiegel des offiziellen `GuruMaps/MapStyle`-Repositories. Dient als Puffer für Merges.

---

## 2. Einmaliges Erst-Setup (Initialisierung)

Falls das Repository auf einem neuen Rechner frisch aufgesetzt wird:

### Schritt 1: Eigenen Fork klonen
```bash
git clone [https://github.com/DEIN-BENUTZERNAME/MapStyle.git](https://github.com/DEIN-BENUTZERNAME/MapStyle.git)
cd MapStyle


### Schritt 2: Upstream-Remote (Original) verknüpfen

Bash

```container
git remote add upstream [https://github.com/GuruMaps/MapStyle.git](https://github.com/GuruMaps/MapStyle.git)
git fetch upstream
```

### Schritt 3: Spiegel-Branch (`upstream-sync`) anlegen

Bash

```container
# Auf Basis des Upstream-Masters den Sync-Branch erstellen
git checkout -b upstream-sync upstream/master

# Den neuen Branch auf den eigenen Fork (origin) pushen
git push -u origin upstream-sync
```

### Schritt 4: Zurück auf den Haupt-Branch wechseln

Bash

```container
git checkout master
```

## 3\. Zukünftige Updates vom Original übernehmen (Routine-Workflow)

Führe folgende Schritte aus, sobald das Original-Repository aktualisiert wurde und du die Änderungen in deinen eigenen Stil integrieren möchtest:

### Schritt 1: Lokalen Arbeitsstand sichern

Stelle sicher, dass alle aktuellen eigenen Änderungen auf `master` committet sind:

Bash

```container
git status
```

### Schritt 2: Original-Daten abrufen

Bash

```container
git fetch upstream
```

### Schritt 3: Spiegel-Branch auf den neuesten Stand bringen

Bash

```container
git checkout upstream-sync
git reset --hard upstream/master
git push origin upstream-sync --force
```

### Schritt 4: Änderungen in den eigenen Stil mergen

Bash

```container
git checkout master
git merge upstream-sync
```

## 4\. Behandlung von Merge-Konflikten in VS Code

Da im `master`-Branch starke Modifikationen an `.mapcss`-Dateien vorliegen, kann es bei Schritt 4 zu Konflikten kommen.

1.  **Source Control öffnen:** Klicke in VS Code links auf das Git-Icon (`Strg + Shift + G` / `Cmd + Shift + G`).

2.  **Dateien mit Konflikten wählen:** Unter *Merge Changes* die betroffene `.mapcss`-Datei anklicken.

3.  **Merge Editor nutzen:** Klicke unten rechts auf **"Open in Merge Editor"**:

-   **Incoming (Links):** Neue Regeln/Features aus dem Upstream-Repository.

-   **Current (Rechts):** Deine eigenen Stilanpassungen (`master`).

-   **Result (Unten):** Das zusammengefügte Endergebnis.

4.  **Entscheidung treffen:**

-   **Farben / eigene Visuals:** Eigene Zeilen (`Current`) bevorzugen.

-   **Neue OSM-Tags / neue Symbole:** Upstream-Zeilen (`Incoming`) übernehmen.

5.  **Merge abschließen:** Klicke im Merge Editor auf **"Complete Merge"**, stage die Datei und committe das Ergebnis.

## 5\. Aktualisierten Stand auf GitHub sichern

Nach erfolgreichem Merge und Konfliktlösung den Stand auf deinen Fork pushen:

Bash

```container
git push origin master
```

## 6\. Best Practices zur Konfliktvermeidung

-   **Grafiken & Icons:** Eigene Symbole in einem Unterordner (z. B. `icons/custom/`) ablegen, anstatt vorhandene Standard-Icons von Upstream zu überschreiben.

-   **MapCSS-Struktur:** Eigene Farbschemata oder geänderte Zoom-Filter möglichst am Ende von Dateien bündeln oder in eigene Abschnitte strukturieren.

