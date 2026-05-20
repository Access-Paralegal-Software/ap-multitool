#!/bin/bash
# build_app.sh — macOS Build & Packaging Orchestrator for APMultitool
# Run from repository root: bash packaging/macos/build_app.sh [AppVersion] [ReleaseChannel] [SignIdentity] [TeamId]

set -euo pipefail

# Parameterized options
APP_VERSION="${1:-1.0.0}"
RELEASE_CHANNEL="${2:--alpha1}"
SIGN_IDENTITY="${3:-}"        # e.g., "Developer ID Application: Access Paralegal Systems LLC (12345ABCDE)"
TEAM_ID="${4:-}"              # e.g., "12345ABCDE"
APPLE_ID="${5:-}"              # Apple Developer account username
APPLE_PASSWORD_VAR="${6:-}"    # Name of environment variable containing app-specific password

FULL_VERSION="v${APP_VERSION}${RELEASE_CHANNEL}"

echo "=========================================================="
echo "  APMultitool macOS App Bundle & DMG Compiler Pipeline"
echo "  Target Version: ${FULL_VERSION}"
echo "=========================================================="

# 1. Dependency Checks
echo "[1/6] Checking requirements..."
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ Error: PyInstaller is not installed in the active environment."
    echo "Please run: pip install pyinstaller"
    exit 1
fi
echo "✅ PyInstaller verified."

# 2. Cleanup Old Outputs
echo "[2/6] Cleaning up old build/dist files..."
rm -rf build/ dist/
echo "✅ Workspace cleaned."

# 3. PyInstaller Compilation
echo "[3/6] Running PyInstaller compilation..."

# Compile CLI Binary
echo "  -> Compiling CLI..."
pyinstaller --noconfirm --clean \
    --name="apmultitool" \
    --console \
    --hidden-import="pypdf" \
    --hidden-import="reportlab" \
    --hidden-import="pikepdf" \
    cli.py

# Compile GUI App Bundle
echo "  -> Compiling GUI..."
# Note: macOS uses ':' as path separator for add-data, unlike Windows ';'
pyinstaller --noconfirm --clean \
    --name="Access_Paralegal_Multitool" \
    --windowed \
    --add-data="logo_small.png:." \
    --add-data="water_texture.png:." \
    --hidden-import="pypdf" \
    --hidden-import="reportlab" \
    --hidden-import="pikepdf" \
    gui_apmultitool.py

# Verify outputs exist
GUI_APP="dist/Access_Paralegal_Multitool.app"
CLI_EXE="dist/apmultitool"

if [ ! -d "$GUI_APP" ] || [ ! -f "$CLI_EXE" ]; then
    echo "❌ Error: PyInstaller failed to produce required macOS outputs."
    exit 1
fi
echo "✅ Compilation completed successfully."

# 4. Codesigning (Hardened Runtime required for Apple Notarization)
if [ -n "$SIGN_IDENTITY" ]; then
    echo "[4/6] Executing Apple codesigning..."
    
    # 4.1. Sign helper libraries/executables inside the .app bundle first
    echo "  -> Signing CLI and inner libraries..."
    find "$GUI_APP" -type f \( -name "*.so" -o -name "*.dylib" -o -name "Python" \) | while read -r lib; do
        codesign --force --options runtime --sign "$SIGN_IDENTITY" "$lib"
    done
    
    # 4.2. Sign CLI standalone binary
    codesign --force --options runtime --sign "$SIGN_IDENTITY" "$CLI_EXE"
    
    # 4.3. Sign GUI outer bundle
    echo "  -> Signing outer application bundle..."
    codesign --force --options runtime --deep --sign "$SIGN_IDENTITY" "$GUI_APP"
    
    echo "✅ Codesigning complete."
else
    echo "[4/6] Skipping Codesigning (No signing identity provided)"
fi

# 5. Native DMG Packaging
echo "[5/6] Creating DMG disk image installer..."
STAGE_DIR="dist/dmg_stage"
rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

# Copy GUI app to staging folder
cp -R "$GUI_APP" "$STAGE_DIR/"
# Include a shortcut link to /Applications for standard drag-and-drop installation
ln -s /Applications "$STAGE_DIR/Applications"

DMG_FILE="dist/APMultitool_Setup_${FULL_VERSION}.dmg"
rm -f "$DMG_FILE"

# Package using native macOS hdiutil tool
hdiutil create -volname "APMultitool Installer" -srcfolder "$STAGE_DIR" -ov -format UDZO "$DMG_FILE"
rm -rf "$STAGE_DIR"

echo "✅ DMG Disk Image generated: $DMG_FILE"

# 6. Apple Notarization Protocol
if [ -n "$SIGN_IDENTITY" ] && [ -n "$APPLE_ID" ] && [ -n "$TEAM_ID" ] && [ -n "$APPLE_PASSWORD_VAR" ]; then
    echo "[6/6] Submitting DMG to Apple Notarization service..."
    
    # Retrieve app-specific password from environment variable
    PASSWORD_VAL=$(eval echo "\$$APPLE_PASSWORD_VAR")
    
    # Submit using modern xcrun notarytool
    xcrun notarytool submit "$DMG_FILE" \
        --apple-id "$APPLE_ID" \
        --password "$PASSWORD_VAL" \
        --team-id "$TEAM_ID" \
        --wait
        
    echo "  -> Stapling notarization ticket back to DMG..."
    xcrun stapler staple "$DMG_FILE"
    
    echo "✅ Notarization and Stapling complete!"
else
    echo "[6/6] Skipping Notarization (Sign identity, Apple ID, Team ID, or app password missing)"
    echo "To notarize manually, execute:"
    echo "  xcrun notarytool submit $DMG_FILE --apple-id <AppleID> --password <AppPassword> --team-id <TeamID> --wait"
    echo "  xcrun stapler staple $DMG_FILE"
fi

echo "=========================================================="
echo "  Build finished. macOS DMG installer saved in ./dist"
echo "=========================================================="
