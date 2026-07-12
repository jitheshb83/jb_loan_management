#!/bin/bash
# Package the built .app into a distributable .dmg installer.
#
# Usage: ./scripts/build_dmg.sh
#
# Requires dist/Housing Loan Manager.app to already exist (run build_app.sh first).
# Output: dist/HousingLoanManager-<version>.dmg with a drag-to-Applications layout.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

APP_NAME="Housing Loan Manager"
APP_PATH="dist/${APP_NAME}.app"
VERSION="0.1.0"
DMG_NAME="HousingLoanManager-${VERSION}.dmg"
DMG_PATH="dist/${DMG_NAME}"
STAGING_DIR="$(mktemp -d)"

if [ ! -d "$APP_PATH" ]; then
    echo "Error: '$APP_PATH' not found. Run ./scripts/build_app.sh first." >&2
    exit 1
fi

cleanup() {
    rm -rf "$STAGING_DIR"
}
trap cleanup EXIT

echo "==> Staging DMG contents..."
cp -R "$APP_PATH" "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"

rm -f "$DMG_PATH"

echo "==> Creating $DMG_PATH..."
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    "$DMG_PATH"

echo "==> Done: $DMG_PATH"
du -sh "$DMG_PATH"
