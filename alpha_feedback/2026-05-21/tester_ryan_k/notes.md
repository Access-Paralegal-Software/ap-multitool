# Alpha Session Notes: Ryan K.
**Date:** 2026-05-21  
**Tester Identifier:** tester_ryan_k (IT / Operator)  
**OS Environment:** Windows 10 Pro, Display scaling 100%  

## Workflows Attempted
1. **Command-Line Setup:** Verifying installer CLI registration and path environment variables.
2. **Support Bundle (CLI):** Exporting support diagnostic ZIP archives via the terminal.
3. **File Room Generation:** Building folder structure templates for legal cases.

## Observations & Issues Encountered
1. **PATH Environment Refresh Latency (Minor - CLI UX):**
   * *Observation:* After the installer completed with "Add to PATH" selected, Ryan opened a PowerShell session to test `apmultitool`. The command was not found because the active PowerShell environment did not reload the environment variables automatically.
   * *Mitigation:* User had to log out/log in or open a fresh command prompt. The operator brief should highlight this clearly.
2. **CLI Output Path Directories Creation (Minor - CLI UX):**
   * *Observation:* Running `apmultitool support-bundle -o C:\temp\new_bundle` throws a `FileNotFoundError` if the folder `C:\temp\new_bundle` does not exist. The CLI should automatically make parent directories before writing.
   * *User Quote:* *"I expected the CLI to create the destination folder if it wasn't already there."*
3. **File Room Special Characters Crash (Minor - File Room):**
   * *Observation:* Ryan added a custom folder named `Subpoena: Records` (containing a colon `:`). This is an illegal character on Windows filesystems. The app attempted to create the folder and threw a generic `OSError: [WinError 123]` which was logged, but the UI just stopped without updating the console to say *why* it failed.
