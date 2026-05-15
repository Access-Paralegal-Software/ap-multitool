# Version Upgrade Synchronization Checklist

To maintain marketing integrity and prevent users from hitting 404 errors, **always** update the version identifier and executable naming schemes across these specific files whenever you perform a new release.

### Current Active Version: `v1.8.1`

## 1. Artifact Naming
When running PyInstaller, the output executable must be explicitly renamed to follow the standardized scheme:
- **Windows Template:** `Access_Paralegal_Merge_Setup_v[MAJOR].[MINOR].[PATCH].exe`
- **Example Command:** 
  ```powershell
  Rename-Item "dist\AccessParalegal.exe" "Access_Paralegal_Merge_Setup_v1.8.1.exe"
  ```

## 2. Web Portal Updates
Ensure these files reflect the precise version string:
*   **`web_portal/index.html`**:
    *   Update `<span class="badge">💎 v[VERSION] Live</span>`
    *   Update `href="Access_Paralegal_Merge_Setup_v[VERSION].exe"` inside the download button.
    *   Update the SHA-256 checksum table to prevent safety warnings.

## 3. InnoSetup Script (Installer)
*   **`installer.iss`**:
    *   Update `AppVersion=[VERSION]`
    *   Update `AppVerName=... v[VERSION]`
    *   Update `OutputBaseFilename=Access_Paralegal_Merge_Setup_v[VERSION]`

## 4. QA Docs
*   **`docs/Bug_Hunter_Manual.md`**:
    *   Update Step 1's download text to reference the correct version executable string.

***
*This is a living document. Append any new release automation hooks to this file as they are added.*
