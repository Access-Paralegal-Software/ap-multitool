# Alpha Session Notes: Sarah T.
**Date:** 2026-05-21  
**Tester Identifier:** tester_sarah_t (Paralegal)  
**OS Environment:** Windows 11 Pro, Display scaling 125%  

## Workflows Attempted
1. **Document Merging with Protected Files:** Attempting to merge a mixed set of PDF files including a password-secured/encrypted PDF downloaded from a court portal.
2. **Bates Stamping with Monospaced Font:** Applying Bates numbers using the Courier font.

## Observations & Issues Encountered
1. **Encrypted PDF Crash in Compiler (Major - Document Compiler):**
   * *Observation:* When Sarah added an encrypted PDF and ran the compiler, the app crashed with a `PyPDF2.errors.FileNotDecryptedException` in the background worker thread. Instead of a helpful error, the UI showed a generic thread traceback.
   * *User Quote:* *"The program froze for a second, then gave me a huge wall of red text. I didn't know what it meant."*
2. **Courier Font Stamping Layout Metrics (Polish - Bates Stamping):**
   * *Observation:* Monospaced Courier stamps are slightly off-center or clipped when placed in margins compared to sans-serif fonts (Arial, Calibri), because of its wider letter boundaries.
3. **Telemetry Counter Increments (Polish - About Tab):**
   * *Observation:* Sarah noted that when she clicked "Cancel" halfway through a Bates stamping run, the telemetry counter on the "Help & About" page did not increase for "Pages Stamped". She expected it to show the count of pages processed before cancellation.
