#!/bin/bash
# Build the Housing Loan Manager .app bundle from source.
#
# Usage: ./scripts/build_app.sh
#
# Regenerates the app icon (if missing) and rebuilds the PyInstaller bundle.
# Output: dist/Housing Loan Manager.app

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [ ! -f "assets/AppIcon.icns" ]; then
    echo "==> Generating app icon..."
    python scripts/generate_icon.py
fi

echo "==> Building .app bundle with PyInstaller..."
pyinstaller HousingLoanManager.spec --noconfirm --clean

APP_PATH="dist/Housing Loan Manager.app"
if [ -d "$APP_PATH" ]; then
    echo "==> Build complete: $APP_PATH"
    du -sh "$APP_PATH"
else
    echo "==> Build failed: $APP_PATH not found" >&2
    exit 1
fi
