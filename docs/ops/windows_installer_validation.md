# APMultitool Windows Installer Smoke-Test & Verification Spec

This document details the manual validation and smoke checks to run after compiling a new version of the APMultitool installer.

---

## 🧪 Smoke Validation Checklist

After compiling the installer, perform the following validation steps on a target Windows machine:

### 1. Interactive GUI Installation
1. Double-click `dist\APMultitool_Setup_v0.5.0.exe`.
2. Verify the **Welcome Wizard Page** contains the correct branding title `APMultitool v0.5.0` and `Access Paralegal Systems` copyright information.
3. Review and accept the license page.
4. Verify the default target directory is set to:
   `%USERPROFILE%\AppData\Local\Programs\APMultitool` (no admin privileges requested).
5. On the additional options page, check:
   - [ ] *Create a desktop shortcut* (check and verify).
   - [ ] *Add APMultitool to local environment PATH* (check and verify).
6. Click Install and ensure the file extraction finishes without warning or blockages.
7. Confirm that the final wizard page gives the option to launch `APMultitool` immediately, and that doing so launches the correct GUI.

### 2. Standard Shortcuts & Files Verification
Navigate to `%LOCALAPPDATA%\Programs\APMultitool` and verify the existence of:
- [ ] `Access_Paralegal_Multitool.exe` (Launches Python GUI app)
- [ ] `apmultitool.exe` (CLI utility)
- [ ] `LICENSE`
- [ ] `logo_small.png`
- [ ] `water_texture.png`
- [ ] `README_BUNDLE.txt`
- [ ] `unins000.exe` (Uninstaller executable)

Verify Desktop and Start Menu:
- [ ] Verify that a desktop icon named `APMultitool` exists. Right-click -> Properties and ensure it points to `Access_Paralegal_Multitool.exe`.
- [ ] Verify the Start Menu group `Access Paralegal` contains:
  - `APMultitool` (App launcher)
  - `APMultitool CLI Help` (Command prompt shell launcher running `apmultitool.exe --help`)
  - `Uninstall APMultitool`

### 3. PATH Integration (CLI Verification)
1. Open a new Command Prompt or PowerShell window (do not use one that was open before installation).
2. Type:
   ```cmd
   apmultitool --version
   ```
3. Verify that the command executes and outputs:
   `APMultitool CLI v0.5.0`
4. Type:
   ```cmd
   apmultitool merge --help
   ```
5. Verify command usage and options print out correctly.

### 4. Silent Deployment Testing
Verify that silent/automated installations work for remote network provisioning:
1. Open terminal and run:
   ```cmd
   dist\APMultitool_Setup_v0.5.0.exe /SILENT /TASKS="desktopicon,addtopath"
   ```
2. Verify installation completes instantly in the background without prompting for inputs.
3. Uninstall the application.
4. Run:
   ```cmd
   dist\APMultitool_Setup_v0.5.0.exe /VERYSILENT /SUPPRESSMSGBOXES
   ```
5. Verify the app is installed completely silently.

### 5. Interactive Uninstallation & PATH Cleanup
1. Go to the Start Menu and click `Uninstall APMultitool` (or run `unins000.exe` in the application directory).
2. Complete the uninstallation wizard.
3. Verify that the folder `%LOCALAPPDATA%\Programs\APMultitool` is fully deleted.
4. Open a new Command Prompt, type `apmultitool`, and confirm it is no longer recognized as an internal or external command.
5. Inspect the User `PATH` environment variable in Registry Editor (`HKCU\Environment`) to verify that the entry has been cleanly removed without corrupting other paths.
