# APMultitool Desktop GUI Smoke Test Checklist

This checklist guides manual and automated testing of the **APMultitool** graphical user interface. Perform these verification steps prior to releasing any software updates to ensure zero regression across features.

---

## 🏗️ 1. Environment & Initialization

- [ ] **Launch GUI**: Run the application:
  ```powershell
  python gui_apmultitool.py
  ```
  Verify that the application launches within 3 seconds and there are no syntax or encoding errors on stderr/stdout.
- [ ] **Visual Slashes & Watermark**: Confirm the premium matte light silver background (light mode) and glowing velvet charcoal background (dark mode) scale dynamically when resizing the window.
- [ ] **Window Dimensions**: Verify the starting geometry is `960x760` pixels and cannot be resized below `920x600`.
- [ ] **Interface Modes (Theme Hot-Swapping)**:
  - Select **View > Ultra Low-Glare (Dark Mode)** from the menu bar. Verify UI updates to dark theme.
  - Select **View > Standard Bright (Light Mode)**. Verify UI updates to light theme.

---

## 📐 2. Tab 1: Document Compiler (Merger)

- [ ] **Local Landing Scan**: Drop some sample PDFs, DOCX, and EML files into the configured `Input_Staging` folder. Verify that the files appear correctly in the Queue table.
- [ ] **Interactive Reordering**:
  - Click a file in the queue, click **Move Up ⬆️** and **Move Down ⬇️**. Verify files swap places.
  - Use the Right-Click context menu to move to top, move to bottom, or delete.
- [ ] **Compile Execution (Successful Run)**:
  - Keep bookmarks, standardize viewer fit, and stream compression checked.
  - Click **🚀 COMBINE & MERGE FILES**.
  - Check that all input widgets on the left panel (checkboxes, dropdowns) are disabled.
  - Wait for compilation. Verify popup asking to open output directory. Check that a valid compiled PDF is saved under `Merged_Output`.
- [ ] **Compile Cancellation**:
  - Click **🚀 COMBINE & MERGE FILES**.
  - While processing is in progress, click the red **🛑 CANCEL MERGE** button.
  - Verify that compilation aborts, temporary directories are purged, and all input controls are re-enabled.

---

## 🔢 3. Tab 2: Bates Stamping & Locking System

- [ ] **Target Selection**: Click **📂 Browse for PDF** to select a target PDF. Confirm the absolute path is populated in the entry.
- [ ] **Bates Persistence**:
  - Type a unique prefix (e.g. `QA-TEST`).
  - Move focus away (click outside). Verify that the start number retrieves correctly from local registry for the active case.
- [ ] **Advanced Settings Modal**:
  - Click **⚙️ ADVANCED STAMP OPTIONS**.
  - Verify that the modal centers over the parent window and locks input focus (`grab_set`).
  - Press the **Escape** key. Confirm the modal dismisses immediately.
  - Re-open, check options (e.g. Font Calibri, Size 11, Placement Bottom Center), click **Save Protocol**.
- [ ] **Production Run (Successful)**:
  - Click **⚡ FLATTEN & APPLY BATES STAMPS**.
  - Confirm all configuration options are disabled during execution.
  - Check the output console logs each page stamped in real-time.
  - Verify that the file opens in a viewer showing stamps in the correct location.
- [ ] **Production Cancellation**:
  - Click **⚡ FLATTEN & APPLY BATES STAMPS** on a large file (e.g. >10 pages).
  - Click **🛑 CANCEL PRODUCTION**.
  - Verify the console logs cancellation, the dialog pops up showing it was cancelled, and inputs are restored.

---

## 🏛️ 4. Tab 3: File Room & Case Trees

- [ ] **Dynamic Structure Load**:
  - Input a test case number in the entry.
  - Click **Load Case Structure**. Verify the case folder tree on the right updates to reflect standard directories.
- [ ] **Tree Generation**:
  - Click **⚡ SPIN UP FOLDER TREE**.
  - Verify that folders corresponding to the blueprint are successfully created under the active workspace root directory.

---

## ⚙️ 5. Global Modals & System Options

- [ ] **Help > About Software**:
  - Open the About window. Confirm it displays the application version, lifetime license registration, and a Support Security Token.
  - Verify the presence of the **CLI Companion** instruction box (`apmultitool --help`).
  - Press **Escape** and confirm the dialog closes.
- [ ] **Help > View License Terms (EULA)**:
  - Open the EULA modal. Verify the text scrollbar functions.
  - Press **Escape** or click **Close Terms** to exit.
- [ ] **File > Settings & Preferences**:
  - Open System Preferences. Change default workspace root or toggle shadow safeguarding switch.
  - Confirm the settings save and behave correctly.
