# How to Export a Support Bundle When Something Goes Wrong

*Pillar: Workflow & How-To | Target keyword: APMultitool support bundle export troubleshoot*

---

Software doesn't always behave the way you expect. When something goes wrong — an unexpected error, behavior that doesn't match the documentation, a result that looks off — the difference between getting the problem resolved quickly and spending a week in back-and-forth emails is usually the quality of the information you can provide.

APMultitool includes an Offline Support Bundle export feature specifically for this situation. This post explains what it contains, when to use it, and how to export it.

## What the Support Bundle Contains

The Offline Support Bundle is a compressed package of diagnostic information that helps the support team reproduce and diagnose issues without requiring access to your client files. It includes:

- Application logs from the current session and recent sessions
- Configuration state (which settings are active, version information)
- Error records and stack traces from any crashes or failures
- System information (OS version, available memory, processor type) that affects how the application performs

What it does **not** include:
- Any of your source PDF documents
- Any client information, case data, or document content
- Your Bates registry data or case vault contents

The bundle is designed to contain everything a developer needs to reproduce a bug and nothing that a paralegal isn't comfortable sharing with a third party.

## When to Export a Support Bundle

Export a bundle whenever you're contacting support about a technical issue. Situations that warrant a bundle:

- The application closed unexpectedly during a merge operation
- A merge completed but the output looks wrong (wrong order, missing pages, incorrect Bates numbering)
- The application launched but certain features aren't responding correctly
- Processing is significantly slower than you'd expect for your document set
- You received an error message, especially one with a code or technical description

Even if you're not sure whether the issue is worth reporting, the bundle is the right thing to send — it gives support the context to tell you whether what you experienced is a known issue, a configuration problem, or something that needs investigation.

## How to Export the Bundle

The export is accessible through the Help & About section of the application:

1. Open APMultitool
2. Navigate to **Help & About** in the application menu
3. Click **Export Support Bundle**
4. Choose a save location on your machine
5. The bundle will be saved as a compressed file in your chosen location

The export takes only a few seconds. The resulting file is small — typically a few hundred kilobytes — and safe to send by email.

## What to Include in Your Support Report

When you send the bundle to support, include:

1. **What you were trying to do:** "I was merging 28 documents with Bates stamping enabled"
2. **What happened:** "The application closed unexpectedly during the merge" or "The output PDF is missing the last 6 documents"
3. **What you expected to happen:** "I expected a merged 200-page PDF with Bates stamps starting at PL-EX-00001"
4. **Your OS version:** Windows 10 or Windows 11, and whether it's fully updated
5. **The support bundle file** as an attachment

The more specific the description, the faster the turnaround. "It didn't work" requires follow-up questions. "The merge completed but the output has 80 pages instead of the 200 I expected, and the audit log shows all 28 documents were processed" is something the team can investigate immediately.

## After You Send the Bundle

Send everything to **info@accessparalegalservices.com** with a subject line that includes "Support Bundle" and a brief description of the issue.

If your work is time-sensitive — if you're working toward a filing deadline — say so in the subject line. Support prioritizes accordingly.

While you wait for a response, try the most common workarounds for merge issues:
- Close and reopen the application, then retry the merge
- Try with a smaller subset of documents to see if the issue is document-specific
- Check available disk space — if the output drive is nearly full, the merge may fail or produce incomplete output

---

**APMultitool's support bundle export keeps your client files private while giving the support team everything they need.** If something's not working, [export a bundle and send it](mailto:info@accessparalegalservices.com) — that's the fastest path to a fix.

*More troubleshooting info in the [FAQ](https://software.accessparalegalservices.com/faq.html).*
