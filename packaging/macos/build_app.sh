#!/bin/bash
# build_app.sh — macOS Build & Packaging Orchestrator for APMultitool
# Run from repository root:
#   bash packaging/macos/build_app.sh [AppVersion] [ReleaseChannel] [SignIdentity] [TeamId] [AppleID] [ApplePasswordVarName]
#
# PIPELINE MODES
#   Probe mode (default): omit signing credentials → unsigned DMG only.
#   Signing only: provide SIGN_IDENTITY → signed artifacts, no notarization.
#   Activated: provide all credentials → signed, notarized, stapled DMG.
#
# CREDENTIAL RULES
#   Partial notarization credentials (any but not all of APPLE_ID / TEAM_ID /
#   APPLE_PASSWORD_VAR) cause a loud, non-zero-exit failure rather than silent
#   degradation. Provide all three or omit all three.
#   No credential values are ever printed to stdout.
#
# HOOK MARKERS
#   SIGNING_HOOK_START / SIGNING_HOOK_END      — codesigning section (step 4)
#   NOTARIZATION_HOOK_START / NOTARIZATION_HOOK_END — notarization section (step 6)

set -euo pipefail

APP_VERSION="${1:-1.0.0}"
RELEASE_CHANNEL="${2:--alpha1}"
SIGN_IDENTITY="${3:-}"        # "Developer ID Application: <Org> (<TeamID>)"
TEAM_ID="${4:-}"              # 10-character Apple Team ID
APPLE_ID="${5:-}"             # Apple Developer account email
APPLE_PASSWORD_VAR="${6:-}"   # Name (not value) of env var holding app-specific password

FULL_VERSION="v${APP_VERSION}${RELEASE_CHANNEL}"

echo "=========================================================="
echo "  APMultitool macOS App Bundle & DMG Compiler Pipeline"
echo "  Target Version: ${FULL_VERSION}"
echo "=========================================================="

# ── Credential pre-flight ───────────────────────────────────────────────────
# Count notarization params and detect partial configurations early.

NOTARIZE_PARAM_COUNT=0
[ -n "$APPLE_ID" ]           && NOTARIZE_PARAM_COUNT=$((NOTARIZE_PARAM_COUNT + 1))
[ -n "$TEAM_ID" ]            && NOTARIZE_PARAM_COUNT=$((NOTARIZE_PARAM_COUNT + 1))
[ -n "$APPLE_PASSWORD_VAR" ] && NOTARIZE_PARAM_COUNT=$((NOTARIZE_PARAM_COUNT + 1))

if [ "$NOTARIZE_PARAM_COUNT" -gt 0 ] && [ "$NOTARIZE_PARAM_COUNT" -lt 3 ]; then
    echo "❌ Error: Partial notarization credentials detected ($NOTARIZE_PARAM_COUNT of 3 required)."
    echo "   Provide ALL THREE or NONE of: APPLE_ID (arg 5), TEAM_ID (arg 4), APPLE_PASSWORD_VAR (arg 6)."
    echo "   APPLE_ID set:           ${APPLE_ID:+yes}${APPLE_ID:-no}"
    echo "   TEAM_ID set:            ${TEAM_ID:+yes}${TEAM_ID:-no}"
    echo "   APPLE_PASSWORD_VAR set: ${APPLE_PASSWORD_VAR:+yes}${APPLE_PASSWORD_VAR:-no}"
    exit 1
fi

if [ -z "$SIGN_IDENTITY" ] && [ "$NOTARIZE_PARAM_COUNT" -eq 3 ]; then
    echo "❌ Error: Notarization credentials provided without a signing identity."
    echo "   Apple's notarization service requires signed artifacts."
    echo "   Provide SIGN_IDENTITY (arg 3) or omit all notarization credentials."
    exit 1
fi

# Report pipeline mode (no credential values printed)
if [ -n "$SIGN_IDENTITY" ] && [ "$NOTARIZE_PARAM_COUNT" -eq 3 ]; then
    echo "[mode] ACTIVATED — signing and notarization enabled."
elif [ -n "$SIGN_IDENTITY" ]; then
    echo "[mode] SIGNING ONLY — signing enabled; notarization credentials absent."
else
    echo "[mode] UNSIGNED PROBE — no credentials provided; producing unsigned DMG."
fi

# ── 1. Dependency checks ────────────────────────────────────────────────────

echo "[1/6] Checking requirements..."
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ Error: PyInstaller not found in the active environment."
    echo "   Run: pip install pyinstaller"
    exit 1
fi
echo "✅ PyInstaller verified."

# ── 2. Cleanup ──────────────────────────────────────────────────────────────

echo "[2/6] Cleaning up old build/dist files..."
rm -rf build/ dist/
echo "✅ Workspace cleaned."

# ── 3. PyInstaller compilation ──────────────────────────────────────────────

echo "[3/6] Running PyInstaller compilation..."

echo "  -> Compiling CLI binary..."
pyinstaller --noconfirm --clean \
    --name="apmultitool" \
    --console \
    --hidden-import="pypdf" \
    --hidden-import="reportlab" \
    --hidden-import="pikepdf" \
    cli.py

echo "  -> Compiling GUI app bundle..."
# macOS uses ':' as path separator for --add-data (unlike Windows ';')
pyinstaller --noconfirm --clean \
    --name="Access_Paralegal_Multitool" \
    --windowed \
    --add-data="logo_small.png:." \
    --add-data="water_texture.png:." \
    --hidden-import="pypdf" \
    --hidden-import="reportlab" \
    --hidden-import="pikepdf" \
    gui_apmultitool_qt.py

GUI_APP="dist/Access_Paralegal_Multitool.app"
CLI_EXE="dist/apmultitool"

if [ ! -d "$GUI_APP" ] || [ ! -f "$CLI_EXE" ]; then
    echo "❌ Error: PyInstaller failed to produce required macOS outputs."
    exit 1
fi
echo "✅ Compilation complete."

# ── SIGNING_HOOK_START ──────────────────────────────────────────────────────
# To activate: provide SIGN_IDENTITY (arg 3).
# When CI secrets are configured, the workflow imports the p12 into an ephemeral
# keychain and passes the identity string here.
#
# Requirements:
#   - All inner binaries (.so, .dylib, Python) must be signed before the outer
#     .app bundle — Apple enforces bottom-up signing order.
#   - --options runtime (Hardened Runtime) is mandatory for notarization.
#
# Verification command (run after this section):
#   codesign --verify --verbose=2 dist/Access_Paralegal_Multitool.app
#   codesign -dv --verbose=4 dist/Access_Paralegal_Multitool.app 2>&1 | grep TeamIdentifier

# ── 4. Codesigning ──────────────────────────────────────────────────────────

if [ -n "$SIGN_IDENTITY" ]; then
    echo "[4/6] Codesigning with Hardened Runtime..."

    echo "  -> Signing inner .so / .dylib / Python libraries..."
    find "$GUI_APP" -type f \( -name "*.so" -o -name "*.dylib" -o -name "Python" \) | \
        while read -r lib; do
            codesign --force --options runtime --sign "$SIGN_IDENTITY" "$lib"
        done

    echo "  -> Signing CLI binary..."
    codesign --force --options runtime --sign "$SIGN_IDENTITY" "$CLI_EXE"

    echo "  -> Signing outer app bundle..."
    codesign --force --options runtime --deep --sign "$SIGN_IDENTITY" "$GUI_APP"

    echo "  -> Verifying signature..."
    codesign --verify --verbose=2 "$GUI_APP"

    echo "✅ Codesigning complete."
else
    echo "[4/6] SIGNING_HOOK: Skipping — SIGN_IDENTITY not provided (unsigned probe mode)."
fi

# ── SIGNING_HOOK_END ────────────────────────────────────────────────────────

# ── 5. DMG packaging ────────────────────────────────────────────────────────

echo "[5/6] Creating DMG disk image installer..."
STAGE_DIR="dist/dmg_stage"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

cp -R "$GUI_APP" "$STAGE_DIR/"
ln -s /Applications "$STAGE_DIR/Applications"

DMG_FILE="dist/APMultitool_Setup_${FULL_VERSION}.dmg"
rm -f "$DMG_FILE"

hdiutil create -volname "APMultitool Installer" -srcfolder "$STAGE_DIR" -ov -format UDZO "$DMG_FILE"
rm -rf "$STAGE_DIR"

echo "✅ DMG generated: $DMG_FILE"

# ── NOTARIZATION_HOOK_START ─────────────────────────────────────────────────
# To activate: provide SIGN_IDENTITY (arg 3), TEAM_ID (arg 4), APPLE_ID (arg 5),
# and APPLE_PASSWORD_VAR (arg 6 — the NAME of the env var, not the raw value).
# When CI secrets are configured, the workflow passes all four.
#
# Requirements:
#   - The DMG must already be signed (see SIGNING_HOOK above).
#   - Uses xcrun notarytool (Xcode 13+). The legacy altool is deprecated.
#   - --wait blocks until Apple returns a result (typically 1–5 minutes).
#   - The app-specific password is read from the named env var, not arg 6 directly,
#     to avoid exposing the value in the process argument list.
#
# Verification command (run after this section):
#   spctl --assess --type open --context context:primary-signature -v "$DMG_FILE"
#   xcrun stapler validate "$DMG_FILE"

# ── 6. Notarization and stapling ────────────────────────────────────────────

if [ -n "$SIGN_IDENTITY" ] && [ "$NOTARIZE_PARAM_COUNT" -eq 3 ]; then
    echo "[6/6] Submitting to Apple Notarization service..."

    # Read the app-specific password from the named env var (not from arg 6 directly).
    PASSWORD_VAL=$(eval echo "\$$APPLE_PASSWORD_VAR")

    xcrun notarytool submit "$DMG_FILE" \
        --apple-id "$APPLE_ID" \
        --password "$PASSWORD_VAL" \
        --team-id "$TEAM_ID" \
        --wait

    echo "  -> Stapling notarization ticket..."
    xcrun stapler staple "$DMG_FILE"

    echo "✅ Notarization and stapling complete."
    echo "   Verify with:"
    echo "   spctl --assess --type open --context context:primary-signature -v $DMG_FILE"
else
    echo "[6/6] NOTARIZATION_HOOK: Skipping — credentials absent (unsigned probe mode)."
    echo "   To notarize manually once credentials are available:"
    echo "   xcrun notarytool submit $DMG_FILE --apple-id <ID> --password <PWD> --team-id <TEAM> --wait"
    echo "   xcrun stapler staple $DMG_FILE"
fi

# ── NOTARIZATION_HOOK_END ───────────────────────────────────────────────────

echo "=========================================================="
echo "  Build finished."
echo "  Output: $DMG_FILE"
echo "=========================================================="
