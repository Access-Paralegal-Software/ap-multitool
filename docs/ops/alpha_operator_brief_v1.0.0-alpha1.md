---
id: alpha-operator-brief-v1.0.0-alpha1
title: Alpha Operator Brief (v1.0.0-alpha1)
type: operations
status: active
project: APMultitool
created_at: 2026-05-21T03:30:00Z
tags:
  - testing
  - instructions
  - alpha-release
---

# 📖 APMultitool Alpha Operator Brief (v1.0.0-alpha1)

This brief outlines instructions for STAX Operators distributing the **v1.0.0-alpha1 Windows Alpha Build** to the tester cohort.

---

## 🚚 1. Installer Distribution Protocol

1. **Host Securely:** Upload `APMultitool_Setup_v1.0.0-alpha1.exe` and its accompanying `.sha256` checksum file to the secure internal shared drive or release channel.
2. **Verify Checksum:** Before sending download links to testers, confirm the hash matches:
   * **Expected SHA256:** `F0706FC434E4753219008EC13096A21DD34EA36B92470A3E3F178CA7DA97344C`
3. **Tester Communications:** Send the download link along with a link to the **SmartScreen Bypass Notes** (`docs/ops/windows_smartscreen_alpha_notes.md`).

---

## 📣 2. Key Instructions to Share with Testers

* **Windows SmartScreen is Expected:** Inform testers they *will* see a blue warning screen because this is an unsigned developer alpha build. Instruct them to click **"More info"** and then **"Run anyway"**.
* **Clean User-space Install:** The installer defaults to a local user-space path (`%LocalAppData%\Programs\APMultitool`) to avoid requiring administrator privileges.
* **Known Limitations to Highlight:**
  * **Document Converter (Word/Excel):** Requires Microsoft Word or Excel to be installed locally on the machine. (No headless LibreOffice wrapper is enabled in this build).
  * **PATH Environment Refresh:** If they select "Add to PATH", they must open a *new* terminal window for the `apmultitool` CLI command to be recognized.

---

## 🛠️ 3. Troubleshooting & Diagnostics Intake

If a tester encounters an installer or runtime failure, instruct them to retrieve the following:

1. **Local Telemetry File:**
   * **Path:** `%USERPROFILE%\.access_paralegal_telemetry.json` (e.g. `C:\Users\tester\.access_paralegal_telemetry.json`)
   * **Purpose:** Contains run histories, operation success rates, and the exact text/timestamp of the last encountered error.
2. **UI Console Output:**
   * If the app won't boot, request they run it via the command prompt:
     ```cmd
     %LocalAppData%\Programs\APMultitool\Access_Paralegal_Multitool.exe
     ```
   * Ask them to copy any traceback errors printed to the console window.
3. **UAC/Installer Log:**
   * For installer errors, look for logs inside the temporary folder:
     * `%TEMP%\Setup Log *.txt`

---

## 📂 4. Feedback Collection & Storage Conventions

To maintain a clean repository structure, completed feedback forms should be filed according to the following conventions:

1. **Filename Format:**
   * Save each file as `feedback_[tester_initials]_[yyyymmdd].md`
   * Example: `feedback_ae_20260521.md`
2. **Storage Directory:**
   * Save completed markdown intake forms in the repository under:
     * `docs/feedback/v1.0.0-alpha1/`
3. **Index Integration:**
   * When checking in feedback, register the file in the master documentation index (`docs/README.md`) under a new "Tester Feedback Archive" heading.
