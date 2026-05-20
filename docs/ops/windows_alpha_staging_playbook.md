---
id: windows_alpha_staging_playbook
title: Windows Alpha Staging Playbook
type: ops-playbook
---

# Paralegal Alpha Staging Playbook

## Context
Before transitioning APMultitool to a fully public Stable release, it will undergo a "Paralegal Alpha" phase. This staging cohort acts as a proxy for real-world legal operations, verifying UX, engine stability, and security assertions.

## Target Cohort Profile
- **Demographic:** Independent or boutique firm Paralegals executing heavy document management workflows (discovery batching, bates stamping, exhibits).
- **Environment:** Windows 10/11 native workstations.
- **Technical Literacy:** Mid-level (comfortable navigating directories, unzipping files, but relying on GUI cues for advanced parameters).

## Deployment Protocol
1. **Artifact Delivery:** Distribute `APMultitool_Setup_v1.0.0-rc1.exe` via secure, tracked link.
2. **SmartScreen Warning:** Explicitly notify the cohort that they will encounter a Windows SmartScreen warning because this is a newly minted cryptographic certificate. Provide instructions to click "More Info" -> "Run anyway".

## Requested Testing Workflows
Testers should be instructed to execute the following distinct operations:
1. **The Overwrite Trap:** Attempt to compile a PDF into a folder where a file of the same name already exists. (Verify the new warning modal appears and functions).
2. **The Stress Test:** Drop 50+ PDFs into the Compiler queue, rearrange them dynamically, and trigger a merge.
3. **The Cancellation:** Trigger a massive Bates stamping job and immediately hit "Cancel" halfway through. (Verify the application gracefully stops without locking the UI).
4. **The File Room Setup:** Spin up a heavily nested Matter folder structure using the File Room tree builder.

## Feedback Matrix
STAX operators should collect feedback specifically addressing:
- Did the application boot cleanly (no ghost consoles)?
- Did the Vault local-encryption setup prompt behave intuitively?
- Did output files land exactly where expected?
- Was the UI scaling acceptable on their specific monitor resolution?
