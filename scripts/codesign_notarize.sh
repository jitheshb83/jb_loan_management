#!/bin/bash
# Code-sign and notarize the .app with a real Apple Developer ID, so it runs
# on other Macs without a Gatekeeper "unidentified developer" warning.
#
# Requires:
#   - A "Developer ID Application" certificate installed in your login keychain
#     (from https://developer.apple.com/account/resources/certificates — needs
#     a paid Apple Developer Program membership).
#   - A notarytool keychain profile, created once via:
#       xcrun notarytool store-credentials "notarytool-profile" \
#           --apple-id "you@example.com" \
#           --team-id "TEAMID1234" \
#           --password "app-specific-password"
#
# Usage:
#   ./scripts/codesign_notarize.sh                          # sign only
#   ./scripts/codesign_notarize.sh --notarize                # sign + notarize + staple
#
# Env overrides:
#   APPLE_SIGNING_IDENTITY   Certificate common name (default: auto-detect "Developer ID Application")
#   APPLE_NOTARIZE_PROFILE   notarytool keychain profile name (default: notarytool-profile)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

APP_PATH="dist/Housing Loan Manager.app"
ENTITLEMENTS="assets/entitlements.plist"
NOTARIZE_PROFILE="${APPLE_NOTARIZE_PROFILE:-notarytool-profile}"
DO_NOTARIZE=false

for arg in "$@"; do
    if [ "$arg" == "--notarize" ]; then
        DO_NOTARIZE=true
    fi
done

if [ ! -d "$APP_PATH" ]; then
    echo "Error: '$APP_PATH' not found. Run ./scripts/build_app.sh first." >&2
    exit 1
fi

# Resolve signing identity
if [ -n "${APPLE_SIGNING_IDENTITY:-}" ]; then
    IDENTITY="$APPLE_SIGNING_IDENTITY"
else
    IDENTITY="$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1 | sed -E 's/.*"(.*)"/\1/' || true)"
fi

if [ -z "$IDENTITY" ]; then
    cat >&2 <<'EOF'
No "Developer ID Application" signing identity found in your keychain.

This app currently runs fine on this Mac (PyInstaller applies an ad-hoc
signature automatically), but distributing it to other Macs will trigger a
Gatekeeper "unidentified developer" warning unless it is signed with a real
Apple Developer ID.

To fix this:
  1. Enroll in the Apple Developer Program (developer.apple.com, paid).
  2. Create a "Developer ID Application" certificate and install it in your
     login keychain (Xcode > Settings > Accounts, or the developer portal).
  3. Re-run this script: ./scripts/codesign_notarize.sh

Skipping signing for now — dist/Housing Loan Manager.app is unchanged.
EOF
    exit 0
fi

echo "==> Signing with identity: $IDENTITY"
codesign --force --deep --options runtime \
    --entitlements "$ENTITLEMENTS" \
    --sign "$IDENTITY" \
    "$APP_PATH"

echo "==> Verifying signature..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"
spctl --assess --type execute --verbose "$APP_PATH" || true

if [ "$DO_NOTARIZE" = true ]; then
    ZIP_PATH="dist/HousingLoanManager-notarize.zip"
    echo "==> Zipping app for notarization submission..."
    ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"

    echo "==> Submitting to Apple notary service (profile: $NOTARIZE_PROFILE)..."
    xcrun notarytool submit "$ZIP_PATH" --keychain-profile "$NOTARIZE_PROFILE" --wait

    echo "==> Stapling notarization ticket..."
    xcrun stapler staple "$APP_PATH"

    rm -f "$ZIP_PATH"
    echo "==> Notarization complete."
fi

echo "==> Done."
