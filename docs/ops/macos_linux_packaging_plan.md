# macOS and Linux Packaging Plan

This document establishes the conceptual approach, architectural shapes, distribution formats, and command line exposure strategies for APMultitool on macOS and Linux platforms.

---

## 1. macOS Distribution & Packaging Strategy

APMultitool will be distributed as a dual-component macOS bundle containing:
1. A **macOS `.app` Bundle** for the desktop graphical user interface.
2. A **Standalone CLI Executable** optimized for terminal pipelines and automation.

### Package Formats:
- **DMG Installer Disk Image**: A standard `.dmg` container containing the `APMultitool.app` bundle and a symlink to `/Applications` for easy drag-and-drop installation.
- **Homebrew Cask / Formula (Enterprise/IT)**: A private or public Homebrew tap:
  - Cask to download and install the DMG bundle.
  - Formula to download and install the standalone CLI executable directly to `/usr/local/bin` or `/opt/homebrew/bin`.

### Code Signing & Notarization:
To avoid gatekeeper execution blocks, the packaging pipeline will include Apple developer signing:
1. **Developer ID Application Certificate**: Sign the compiled binary and the parent `.app` bundle using `codesign --sign "Developer ID Application: <TeamName> (<TeamID>)"`.
2. **Notarization Service (`xcrun altool` / `xcrun notarytool`)**: Submit the signed `.dmg` to Apple's notary server for automated security scanning.
3. **Stapling**: Staple the notarization ticket back to the DMG using `xcrun stapler staple APMultitool.dmg`.

---

## 2. Linux Distribution Strategy

For Linux systems, APMultitool will target two principal packaging systems:

### 1. AppImage (Standalone Executable Package)
- **Concept**: A single self-contained executable that packages all runtime dependencies, shared library bindings (e.g. libreoffice hooks, PDF libraries), and desktop icon resources.
- **Exposure**: Users can execute the AppImage directly. It does not require root permissions.
- **GUI & CLI Handling**: The AppImage can support a unified entry point. If arguments are passed, it runs the CLI subcommand. If launched without arguments, it spawns the GUI app.

### 2. Tarball Package (`.tar.gz`)
- **Concept**: A simple zipped directory containing the compiled binaries and a simple setup script (`install.sh`).
- **Setup script tasks**:
  1. Extract files to `/opt/ap_multitool/` or `~/.local/share/ap_multitool/`.
  2. Create a symlink in `/usr/local/bin/apmultitool` or `~/.local/bin/apmultitool` pointing to the main execution script.
  3. Copy desktop entry configuration file (`apmultitool.desktop`) to `/usr/share/applications/` or `~/.local/share/applications/`.

---

## 3. Platform Limitations & Core Dependencies

### LibreOffice and win32com Alternatives:
- On macOS and Linux, the Windows-exclusive `win32com` conversion adapters for Word and Excel are bypassed.
- The platform fallback will rely strictly on the **LibreOffice Headless Adapter** or python libraries like `docx2pdf` (utilizing native libreoffice under the hood) and custom parser conversion fallback layers.

### Packaging Tools Required:
- **macOS**: `pyinstaller`, `dmgbuild` (Python library to construct rich DMG installers with backgrounds and customized layouts).
- **Linux**: `pyinstaller`, `appimagetool` (to compile directories into single AppImage files).
