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

If a tester encounters a failure, the most efficient way to diagnose it is to ask them to export a **Support Bundle**:

1. **How to Export via the GUI:**
   * Open APMultitool.
   * Go to the **Help & About** tab.
   * Click **Export Support Bundle...** on the telemetry card.
   * Save the ZIP file (defaults to the Desktop) and click **Yes** to open the containing folder.
2. **How to Export via the CLI:**
   * If the GUI fails to open or is unresponsive, open a terminal (PowerShell or Command Prompt) and run:
     ```cmd
     apmultitool support-bundle
     ```
   * This generates the ZIP support bundle in the current folder or Desktop.
3. **What is Included & Privacy Safeguards:**
   * **Included:** Environment metadata (OS, scaling, Python version, MS Office/LibreOffice checks), application log files (`apmultitool.log*`), and local telemetry metrics.
   * **Excluded/Scrubbed:** Absolute user profile directories and system usernames are automatically replaced with `<USERPROFILE>` in all logs and metadata. Zero client data, case files, keys, or document contents are ever collected.

If the app cannot run at all, manually collect:
* **UAC/Installer Log:** For installer errors, look for logs inside: `%TEMP%\Setup Log *.txt`
* **UI Console Output:** Launch the app via Command Prompt to capture startup tracebacks:
  ```cmd
  %LocalAppData%\Programs\APMultitool\Access_Paralegal_Multitool.exe
  ```

---

## ❓ 3b. Troubleshooting FAQ

* **Q: The CLI returns `'apmultitool' is not recognized as an operable program` after installation.**
  * *A:* This is due to environment variable latency. The tester must close all active PowerShell/Command Prompt windows and open a new terminal session. If it still fails, have them verify that `%LocalAppData%\Programs\APMultitool` was added to their user PATH.
* **Q: Exporting the support bundle via CLI fails with `FileNotFoundError`.**
  * *A:* If specifying a custom path using `-o` or `--output-dir`, ensure the target directory exists. If it does not, run without `-o` to output to the current directory or create the target directory first.
* **Q: A job freezes or aborts silently (e.g., when merging encrypted PDFs or invalid directory characters).**
  * *A:* Look at the log output in the right panel or run the support bundle tool. Encrypted PDFs are currently not supported and should be decrypted before merging. Filesystem blueprints cannot contain illegal Windows characters like colons (`:`), slashes (`/`, `\`), or quotes.

---

## 🔁 4. Updated UI Labels (ho_0045 Patch)

Several button and panel labels were updated after the initial alpha1 build.
If you are sharing screenshots or written instructions with testers, use the
updated labels below:

| Tab | Old label | New label |
|---|---|---|
| Document Compiler | "Combine & Merge Files" button | **"Compile Documents"** |
| Bates Stamping | "⚡ FLATTEN & APPLY BATES STAMPS" button | **"Apply Bates Numbers"** |
| Bates Stamping | " ADVANCED STAMP OPTIONS" button | **"Stamp Options..."** |
| Bates Stamping | "BATES OUTPUT TERMINAL" panel | **"BATES STAMP LOG"** |
| File Room | "Spin Up Folder Tree" button | **"Create Folder Structure"** |
| File Room | "FOLDER TREE ARCHITECTURE PREVIEW" panel | **"FOLDER STRUCTURE PREVIEW"** |

**Workflow note (Compiler):** The "Confirm Merge Order" dialog that previously
appeared before every compile run has been removed. Users who want to check
their order should review the queue table before clicking the run button. The
overwrite protection dialog (shown only when a file already exists at the
target path) is still in place.

---

## 📂 5. Feedback Collection & Storage Conventions

To maintain a clean repository structure, completed feedback forms should be filed according to the following conventions:

1. **Filename Format:**
   * Save each file as `feedback_[tester_initials]_[yyyymmdd].md`
   * Example: `feedback_ae_20260521.md`
2. **Storage Directory:**
   * Save completed markdown intake forms in the repository under:
     * `docs/feedback/v1.0.0-alpha1/`
3. **Index Integration:**
   * When checking in feedback, register the file in the master documentation index (`docs/README.md`) under a new "Tester Feedback Archive" heading.
