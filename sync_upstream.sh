#!/bin/bash
#
# sync_upstream.sh
#
# Automates the routine workflow for merging updates from the original
# GuruMaps/MapStyle repository into a custom Overlanding MapStyle fork.
#
# This script implements step 3 "Zukünftige Updates vom Original übernehmen
# (Routine-Workflow)" from WORKFLOW.md.
#
# Prerequisites:
#   - Repository cloned with both remotes configured:
#       origin  : user's fork (e.g., https://github.com/USER/Overlanding-MapStyle.git)
#       upstream: official repo (https://github.com/GuruMaps/MapStyle.git)
#   - Two branches exist locally: master (custom style) and upstream-sync (mirror)
#
# Usage:
#   ./sync_upstream.sh
#
# The script performs the following steps:
#   1. Detect and auto-commit uncommitted changes on master
#   2. Fetch latest from upstream
#   3. Update upstream-sync branch to match upstream/master
#   4. Merge upstream-sync into master
#   5. Push updated master to origin (user's fork)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "  Guru Maps MapStyle - Upstream Sync"
echo "========================================="
echo ""

# Step 1: Detect and auto-commit uncommitted changes on master
echo "=== Schritt 1: Lokalen Arbeitsstand sichern ==="
echo "Überprüfe aktuellen Status auf master..."

git checkout master > /dev/null 2>&1

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Es gibt uncommitsierte Änderungen im master-Branch."
    echo "   Werde Änderungen automatisch committen..."

    # Auto-detect changed files and create a commit
    # Get list of changed/modified files
    CHANGED_FILES=$(git diff --name-only HEAD)

    # Create a commit with all changes and a descriptive message
    if [ -n "$CHANGED_FILES" ]; then
        echo "   Gefundene geänderte Dateien:"
        echo "$CHANGED_FILES" | while read -r file; do
            echo "   - $file"
        done

        # Auto-commit with descriptive message
        git add -A
        git commit -m "Auto-commit: Vorbereitung upstream Sync $(date +%Y-%m-%d %H:%M:%S)"

        echo "✓ Änderungen automatisch commited."
    else
        echo "   Keine Änderungen zum Committen gefunden."
    fi
else
    echo "✓ Master-Branch ist sauber (keine uncommitsierten Änderungen)."
fi
echo ""

# Step 2: Fetch upstream data
echo "=== Schritt 2: Original-Daten abrufen ==="
echo "Hole Updates aus dem upstream-Repository..."
git fetch upstream
echo "✓ Updates erfolgreich abgerufen."
echo ""

# Step 3: Bring upstream-sync branch up to date
echo "=== Schritt 3: Spiegel-Branch auf den neuesten Stand bringen ==="
echo "Stelle upstream-sync auf upstream/master zurück..."

git checkout upstream-sync
git reset --hard upstream/master
echo "✓ upstream-sync ist jetzt identisch mit upstream/master."

echo "Pushe aktualisierten upstream-sync nach origin..."
git push origin upstream-sync --force
echo "✓ upstream-sync nach origin gepusht."
echo ""

# Step 4: Merge upstream-sync into master
echo "=== Schritt 4: Änderungen in den eigenen Stil mergen ==="
echo "Führe upstream-sync in master zusammen..."

git checkout master
git merge upstream-sync

# Check if merge had conflicts
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Merge wurde mit Konflikten durchgeführt."
    echo "   Es liegen Konflikte vor, die gelöst werden müssen."
    echo ""
    echo "   Bitte folgende Schritte in VS Code ausführen:"
    echo "   1. Source Control öffnen (Strg + Shift + G)"
    echo "   2. Dateien mit Konflikten auswählen"
    echo "   3. 'Open in Merge Editor' verwenden"
    echo "   4. Entscheide: 'Current' (eigene Anpassungen) oder 'Incoming' (Upstream)"
    echo "   5. 'Complete Merge' klicken und committen"
    echo ""
    exit 1
fi

echo "✓ Merge erfolgreich ohne Konflikte."
echo ""

# Step 5: Push updated master to origin
echo "=== Schritt 5: Aktualisierten Stand auf GitHub sichern ==="
echo "Pushere master nach origin..."

git push origin master
echo "✓ master erfolgreich nach origin (dein Fork) gepusht."
echo ""

echo "========================================="
echo "  Fertig! Upstream-Updates wurden integriert."
echo "========================================="