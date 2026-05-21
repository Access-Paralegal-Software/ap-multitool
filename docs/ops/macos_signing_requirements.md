---
id: macos_signing_requirements
title: macOS Signing & Notarization Requirements
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# macOS Signing & Notarization Requirements

To distribute the Access Paralegal Multitool (APMultitool) to macOS users without triggering severe security blocks by Apple's Gatekeeper system, the software must be cryptographically signed with an Apple Developer ID Application certificate and notarized by Apple's automated malware scanning service.

---

## 🔒 Hardened Runtime & Codesigning

Apple requires applications to run with **Hardened Runtime** enabled to be notarized. This restricts certain operations (like dynamic memory loading or execution of unsigned code) unless explicit entitlements are defined.

### 1. Signing Order (Bottom-Up)
Apple's verification checks enforce that all nested executables, shared libraries (`.dylib`), and Python extension modules (`.so`) are signed before the parent application bundle. 

The [build_app.sh](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/packaging/macos/build_app.sh) script automates this sequence:
1. **Nested Binaries & Libraries**:
   ```bash
   find "dist/Access_Paralegal_Multitool.app" -type f \( -name "*.so" -o -name "*.dylib" -o -name "Python" \) | while read -r lib; do
       codesign --force --options runtime --sign "Developer ID Application: <Company> (<TeamID>)" "$lib"
   done
   ```
2. **CLI Executable**:
   ```bash
   codesign --force --options runtime --sign "Developer ID Application: <Company> (<TeamID>)" dist/apmultitool
   ```
3. **App Bundle Wrapper**:
   ```bash
   codesign --force --options runtime --deep --sign "Developer ID Application: <Company> (<TeamID>)" dist/Access_Paralegal_Multitool.app
   ```

---

## ☁️ Apple Notarization Protocol

Once signed and packed into a DMG disk image, the installer must be uploaded to Apple's Cloud Notary Service.

### 1. Submission
Submissions are handled via Apple's `notarytool` utility:
```bash
xcrun notarytool submit dist/APMultitool_Setup_v1.0.0-alpha1.dmg \
    --apple-id "<developer_email>" \
    --password "<app_specific_password>" \
    --team-id "<10_character_team_id>" \
    --wait
```
The `--wait` flag blocks the terminal until the scan finishes (usually 1–5 minutes) and displays a success log or diagnostic link for failures.

### 2. Stapling the Ticket
When notarization succeeds, Apple records a ticket online. However, offline installations or Gatekeeper runs are faster and more reliable if the ticket is directly attached ("stapled") to the installer:
```bash
xcrun stapler staple dist/APMultitool_Setup_v1.0.0-alpha1.dmg
```

---

## 🚨 Gatekeeper Behavior & Manual Tester Bypass

If a macOS tester runs a DMG build that is **unsigned** or **unnotarized**, Gatekeeper will show a warning dialog block:
> **"Access_Paralegal_Multitool" cannot be opened because it is from an unidentified developer.**

### Manual Bypass Flow for Alpha Testers (macOS)
If testers are given a local developer test build before notarization:
1. Double-click the DMG to mount it, and drag `Access_Paralegal_Multitool` to `/Applications`.
2. Open `/Applications` in **Finder** (do not use Launchpad or terminal).
3. Right-click (or Control-click) `Access_Paralegal_Multitool` and select **Open**.
4. A dialog will appear with an **Open** button option (which is absent during a standard double-click attempt). Click **Open**.
5. Once opened this way, macOS remembers the exception, and the application will boot normally on subsequent runs.
