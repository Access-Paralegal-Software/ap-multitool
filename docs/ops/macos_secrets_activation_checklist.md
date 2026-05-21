---
id: macos_secrets_activation_checklist
title: macOS Secrets Activation Checklist — Operator Guide
type: ops
status: draft
project: Access Paralegal / APMultitool
created: 2026-05-21
---

# macOS Secrets Activation Checklist — Operator Guide

This checklist is for the operator who will provision Apple Developer credentials and activate full macOS signing and notarization in CI. Complete every step in order. No private keys, certificates, or passwords are ever stored in the repository.

**Current state:** Probe mode (unsigned DMG). All signing/notarization CI steps are guarded and will activate automatically once the secrets in §3 are configured.

---

## 1. Prerequisites

Before starting, confirm the following are in place:

- [ ] **Apple Developer Program enrollment** — The Apple Developer account must be enrolled in the paid program (individual or organization). Free accounts cannot issue Developer ID certificates. Enroll at [developer.apple.com/programs/enroll](https://developer.apple.com/programs/enroll).
- [ ] **macOS workstation** — Certificate generation and export require Keychain Access, which is macOS-only.
- [ ] **Xcode Command Line Tools** — Required for `codesign`, `notarytool`, `stapler`. Install with `xcode-select --install`.
- [ ] **Access to GitHub repository settings** — You need "Admin" or "Owner" role to add Actions secrets.

---

## 2. Required Apple Assets

### 2A. Developer ID Application Certificate

This certificate is used to sign the app bundle and CLI binary with the Hardened Runtime flag. It identifies your organization to macOS Gatekeeper.

- **Type:** Developer ID Application (not "Mac App Distribution" or "Developer ID Installer")
- **Issuing authority:** Apple Developer Program — create via the portal
- **Validity:** 5 years from issuance

**Steps to create:**

1. Open Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority.
2. Enter your email and select "Saved to disk." Save the `.certSigningRequest` file.
3. Log in to [developer.apple.com](https://developer.apple.com) → Certificates, Identifiers & Profiles → Certificates → + (Create).
4. Select **Developer ID Application** and click Continue.
5. Upload the `.certSigningRequest` file.
6. Download the generated `.cer` file and double-click it to install into Keychain Access.

**Export the certificate as a `.p12` bundle for CI:**

```bash
# In Keychain Access → My Certificates:
# Right-click "Developer ID Application: <Your Org> (<Team ID>)" → Export...
# Choose .p12 format. Set a strong, unique password. Save to disk.

# Encode as a single-line base64 string for the GitHub secret:
base64 -i DeveloperID_Application.p12 | tr -d '\n' | pbcopy
# Clipboard now holds the value for APPLE_DEV_ID_CERT.
```

> **Security:** Delete the `.p12` file from your local machine once the secret is configured. The certificate remains in Keychain Access and can be re-exported if needed.

### 2B. Team ID

The 10-character alphanumeric identifier for your Apple Developer team. It appears in the certificate common name (e.g., `Developer ID Application: Access Paralegal Systems LLC (AB12CD34EF)`).

**Where to find it:**
- Apple Developer portal → Account → Membership Details → Team ID.
- Or: `security find-identity -v -p codesigning` — the Team ID is in parentheses at the end of the identity name.

### 2C. App-Specific Password

Apple requires an app-specific password (not your Apple ID password) for `notarytool` authentication from automated environments.

**Steps:**

1. Sign in to [appleid.apple.com](https://appleid.apple.com).
2. Navigate to **Security → App-Specific Passwords → Generate an app-specific password**.
3. Label it `APMultitool CI Notarization` (or similar — the label is for your reference only).
4. Copy the generated password immediately — Apple will not show it again.

---

## 3. GitHub Actions Secrets Configuration

Add these secrets to the repository at **Settings → Secrets and variables → Actions → New repository secret**.

| Secret Name | Value | Source |
|---|---|---|
| `APPLE_DEV_ID_CERT` | Base64-encoded `.p12` bundle (single line, no newlines) | §2A export |
| `APPLE_DEV_ID_CERT_PASSWORD` | Password set when exporting the `.p12` | §2A export |
| `APPLE_TEAM_ID` | 10-character Team ID (e.g., `AB12CD34EF`) | §2B |
| `APPLE_APPLE_ID` | Apple Developer account email address | Your account |
| `APPLE_APP_SPECIFIC_PASSWORD` | App-specific password | §2C |

Once all 5 secrets are present, the guarded steps in `.github/workflows/macos_packaging_probe.yml` activate automatically on the next workflow run. The secrets dry-run check step will log:

```
✅ All macOS signing secrets present — pipeline will run in ACTIVATED mode.
```

---

## 4. Validation After Configuration

Run the probe workflow manually (Actions → macOS Packaging Probe → Run workflow) and confirm:

- [ ] Dry-run secrets check step logs `ACTIVATED mode`.
- [ ] Certificate import step succeeds (no keychain errors).
- [ ] Codesign step completes for inner libraries, CLI, and outer bundle.
- [ ] `notarytool submit --wait` returns a successful notarization result.
- [ ] Stapler step completes without error.
- [ ] The `macos-dmg-signed-notarized` artifact is uploaded.

Verify the downloaded DMG on a real macOS machine:

```bash
spctl --assess --type open --context context:primary-signature -v APMultitool_Setup_v*.dmg
# Expected: "accepted  source=Notarized Developer ID"

xcrun stapler validate APMultitool_Setup_v*.dmg
# Expected: "The staple and validate action worked!"
```

---

## 5. Secret Rotation and Revocation

### Rotating the app-specific password

App-specific passwords do not expire automatically but should be rotated if a runner or system is compromised.

1. Sign in to appleid.apple.com → Security → App-Specific Passwords.
2. Revoke the existing `APMultitool CI Notarization` password.
3. Generate a new one and update the `APPLE_APP_SPECIFIC_PASSWORD` GitHub secret.

### Rotating the Developer ID certificate

Certificates expire after 5 years. When renewal is needed:

1. Create a new Developer ID Application certificate via the Apple Developer portal (same CSR process as §2A).
2. Export as `.p12` and encode as base64.
3. Update both `APPLE_DEV_ID_CERT` and `APPLE_DEV_ID_CERT_PASSWORD` GitHub secrets.
4. Artifacts signed with the old certificate remain valid (Apple's timestamp service locks in the validity at signing time).

### If a certificate is compromised

1. Log in to the Apple Developer portal → Certificates → revoke the certificate immediately.
2. Delete the corresponding `.p12` from all machines.
3. Remove and replace the `APPLE_DEV_ID_CERT` and `APPLE_DEV_ID_CERT_PASSWORD` GitHub secrets.
4. Generate a new certificate following §2A.

---

## 6. Security Reminders

- **Never commit** `.p12` files, raw passwords, or private keys to the repository.
- **Never paste** secret values into CI run logs, issue comments, or PR descriptions.
- **Never reuse** the app-specific password for any other service.
- The ephemeral keychain (`$RUNNER_TEMP/build.keychain`) created by the CI workflow is automatically destroyed at runner cleanup — no persistent credential storage occurs on GitHub-hosted runners.
- Restrict repository Actions secrets to the minimum required audience (consider using environment-scoped secrets for production notarization).
