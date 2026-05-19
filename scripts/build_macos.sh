#!/bin/bash
# build_macos.sh — macOS build and packaging strategy script for APMultitool
# Run this from the repository root: bash scripts/build_macos.sh

echo "=========================================================="
echo "  APMultitool macOS Build Automation Strategy & Compiler"
echo "=========================================================="

# 1. Check dependencies
echo "[1/4] Checking Python environment & PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller was not found. Please install via 'pip install pyinstaller'."
    exit 1
fi

# 2. Clean previous build folders
echo "[2/4] Cleaning previous build outputs..."
rm -rf build/ dist/
echo "Cleaned build/ and dist/ folders."

# 3. Create macOS-specific spec file temporarily or run direct command
# Note: macOS does not support win32com/pythoncom. While PyInstaller ignores them,
# we create a macOS-tailored compilation script.
echo "[3/4] Running PyInstaller compilation..."

# We compile the CLI as a console app
pyinstaller --noconfirm --clean \
    --name="apmultitool" \
    --console \
    --hidden-import="pypdf" \
    --hidden-import="reportlab" \
    --hidden-import="pikepdf" \
    cli.py

# We compile the GUI as a windowed application (.app bundle)
pyinstaller --noconfirm --clean \
    --name="Access_Paralegal_Multitool" \
    --windowed \
    --add-data="logo_small.png:." \
    --add-data="water_texture.png:." \
    --hidden-import="pypdf" \
    --hidden-import="reportlab" \
    --hidden-import="pikepdf" \
    gui_apmultitool.py

# 4. Codesign / Notarization guidelines
echo "[4/4] Codesigning and Verification Guidelines..."
echo "To distribute this application to other macOS users without warnings, run:"
echo "  codesign --force --options runtime --sign \"Developer ID Application: <Your Name> (<TeamID>)\" dist/Access_Paralegal_Multitool.app"
echo "  codesign --force --options runtime --sign \"Developer ID Application: <Your Name> (<TeamID>)\" dist/apmultitool"
echo ""
echo "Verify build outputs:"
if [ -d "dist/Access_Paralegal_Multitool.app" ]; then
    echo "✅ Created GUI macOS Bundle: dist/Access_Paralegal_Multitool.app"
else
    echo "❌ GUI macOS Bundle missing."
fi

if [ -f "dist/apmultitool" ]; then
    echo "✅ Created CLI macOS Binary: dist/apmultitool"
else
    echo "❌ CLI macOS Binary missing."
fi
echo "=========================================================="
