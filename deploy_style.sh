#!/bin/bash
# Deploy the "Default.style" map style into the Guru Maps (Galileo) app Documents folder.
# Overwrites an existing installation.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/Default.style"
DEST_DIR="${HOME}/Library/Containers/com.bodunov.galileo/Data/Documents"

if [ ! -d "$SRC_DIR" ]; then
  echo "ERROR: source folder not found: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

# Remove previous installation so that renamed/removed files don't linger.
rm -rf "$DEST_DIR/Default.style"
cp -R "$SRC_DIR" "$DEST_DIR/Default.style"

echo "Installed style to: $DEST_DIR/Default.style"
