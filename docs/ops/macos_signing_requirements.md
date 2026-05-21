---
id: macos_signing_requirements
title: macOS Signing & Notarization — Secrets and Credentials Inventory
type: ops
status: draft
project: Access Paralegal / APMultitool
created: 2026-05-21
---

# macOS Signing & Notarization — Secrets Inventory

This document catalogs every credential required to enable Apple codesigning and notarization for APMultitool. None are currently configured. This document exists to guide the operator who provisions them.

For the notarization command sequence and pipeline overview, see `docs/ops/macos_packaging_overview.md`.

---

## 1. Required GitHub Actions Secrets

Add these to the repository via **Settings → Secrets and variables → Actions → New repository secret**. The guarded steps in `.github/workflows/macos_packaging_probe.yml` activate automatically once these secrets are present.

| Secret Name | Description | How to Obtain |
|---|---|---|
| `APPLE_DEV_ID_CERT` | Base64-encoded `.p12` Developer ID Application certificate bundle | Export from Keychain Access; encode with `base64 -i cert.p12 \| tr -d '\n'` |
| `APPLE_DEV_ID_CERT_PASSWORD` | Password set when exporting the `.p12` | Chosen during Keychain Access export |
| `APPLE_TEAM_ID` | 10-character Apple Developer Team ID (e.g., `AB12CD34EF`) | Apple Developer portal → Account → Membership |
| `APPLE_APPLE_ID` | Apple Developer account email address | The Apple ID associated with the Developer Program account |
| `APPLE_APP_SPECIFIC_PASSWORD` | App-specific password for use with `notarytool` | appleid.apple.com → Security → App-Specific Passwords → Generate |

---

## 2. Hardened Runtime & Codesigning

Apple requires applications to run with **Hardened Runtime** enabled to be notarized. This restricts certain operations (like dynamic memory loading or execution of unsigned code) unless explicit entitlements are defined.

### Signing Order (Bottom-Up)

Apple's verification enforces that all nested executables, shared libraries (`.dylib`), and Python extension modules (`.so`) are signed before the parent application bundle.

```bash
# 1. Nested binaries and libraries
find dist/Access_Paralegal_Multitool.app -type f \( -name "*.so" -o -name "*.dylib" -o -name "Python" \) | \
    while read -r lib; do
        codesign --force --options runtime --sign "$SIGN_IDENTITY" "$lib"
    done

# 2. CLI executable
codesign --force --options runtime --sign "$SIGN_IDENTITY" dist/apmultitool

# 3. App bundle wrapper
codesign --force --options runtime --deep --sign "$SIGN_IDENTITY" dist/Access_Paralegal_Multitool.app
```

---

## 3. Certificate Requirements

- **Certificate type:** Developer ID Application (not Mac App Store, not Developer ID Installer).
- **Issued by:** Apple Developer Program — requires a paid individual or organization membership.
- **Validity:** 5 years from issuance. Plan renewal before expiry to avoid breaking the release pipeline.
- **Hardened Runtime:** All binaries must be signed with `--options runtime`. This is non-negotiable for notarization.

### Exporting the .p12 for CI

On the Mac where the Developer ID certificate is installed:

```bash
# List available signing identities
security find-identity -v -p codesigning

# Export from Keychain Access:
# 1. Open Keychain Access → My Certificates
# 2. Right-click "Developer ID Application: <Org> (<Team ID>)" → Export
# 3. Choose .p12 format, set a strong password, save to disk

# Encode for use as a GitHub Actions secret:
base64 -i DeveloperID_Application.p12 | tr -d '\n' | pbcopy
# The clipboard now contains the value for APPLE_DEV_ID_CERT
```

---

## 4. Apple Notarization Protocol

### Submission

```bash
xcrun notarytool submit dist/APMultitool_Setup_v<version>.dmg \
    --apple-id "$APPLE_ID" \
    --password "$APP_SPECIFIC_PASSWORD" \
    --team-id "$TEAM_ID" \
    --wait
```

The `--wait` flag blocks until the scan finishes (usually 1–5 minutes) and displays a success log or diagnostic link for failures.

### Stapling the Ticket

When notarization succeeds, staple the ticket directly to the installer so offline Gatekeeper checks work without a network round-trip:

```bash
xcrun stapler staple dist/APMultitool_Setup_v<version>.dmg
```

---

## 5. Post-Signing Verification

```bash
# Verify code signature on the app bundle
codesign --verify --verbose=2 dist/Access_Paralegal_Multitool.app

# Confirm Hardened Runtime and Team ID are embedded
codesign -dv --verbose=4 dist/Access_Paralegal_Multitool.app 2>&1 | grep -E "TeamIdentifier|flags"

# Verify Gatekeeper acceptance of the final DMG
spctl --assess --type open --context context:primary-signature -v dist/APMultitool_Setup_v*.dmg
# Expected output: "accepted  source=Notarized Developer ID"
```

---

## 6. Security Posture

- **Never commit** the `.p12` file or its password to the repository.
- **Never log** secrets in CI output — GitHub Actions redacts known secret values, but avoid explicit `echo $SECRET` patterns.
- Use an ephemeral keychain (`$RUNNER_TEMP/build.keychain`) that is automatically discarded when the GitHub-hosted runner is cleaned up.
- The app-specific password should be rotated if a runner is compromised or if the Apple ID credentials are exposed.
- Restrict repository secret access to the minimum required branches/environments.

---

## 7. Provisioning Status

| Credential | Provisioned |
|---|---|
| `APPLE_DEV_ID_CERT` | ❌ Not configured |
| `APPLE_DEV_ID_CERT_PASSWORD` | ❌ Not configured |
| `APPLE_TEAM_ID` | ❌ Not configured |
| `APPLE_APPLE_ID` | ❌ Not configured |
| `APPLE_APP_SPECIFIC_PASSWORD` | ❌ Not configured |
