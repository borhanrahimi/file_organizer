#!/usr/bin/env bash
# Packages the Python backend as one executable that the release app ships
# with ("sidecar"), so users don't need Python installed.
#
# Output: src-tauri/binaries/organizer-server-<target triple>
# Run from frontend/: npm run build:sidecar
set -euo pipefail

FRONTEND="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(dirname "$FRONTEND")"
WORK="$FRONTEND/build/sidecar"
PYTHON="${PYTHON:-python3}"
TARGET="$(rustc -vV | sed -n 's/^host: //p')"

rm -rf "$WORK"
mkdir -p "$WORK" "$FRONTEND/src-tauri/binaries"

# A separate environment so the build never changes your own Python.
"$PYTHON" -m venv "$WORK/venv"
"$WORK/venv/bin/python" -m pip install --quiet --upgrade pip
"$WORK/venv/bin/python" -m pip install --quiet "$REPO/backend" pyinstaller

# uvicorn and watchdog choose some modules at run time, so include them all.
"$WORK/venv/bin/pyinstaller" \
  --onefile \
  --name organizer-server \
  --distpath "$WORK/dist" \
  --workpath "$WORK/pyinstaller" \
  --specpath "$WORK" \
  --collect-submodules uvicorn \
  --collect-submodules watchdog \
  --noconfirm \
  --log-level WARN \
  "$REPO/backend/packaging/organizer_server.py"

cp "$WORK/dist/organizer-server" "$FRONTEND/src-tauri/binaries/organizer-server-$TARGET"
echo "Built src-tauri/binaries/organizer-server-$TARGET"
