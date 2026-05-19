---
title: APMultitool Output & Audit Model
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Output & Audit Model

## Principles

Legal document work requires confidence about what happened. The output model answers: what was produced, from what, in what order, by whom, and when. Users should be able to hand an output file to a supervising attorney and explain its provenance without consulting their memory.

---

## Output Naming Rules

Every output file name is generated from a template. Defaults are chosen to be unambiguous and sort chronologically.

### Default templates by operation

| Operation | Default template | Example |
|---|---|---|
| merge | `{source}_merged_{date}.pdf` | `Complaint_merged_2026-05-18.pdf` |
| split (range/fixed) | `{source}_part{n:03d}.pdf` | `Deposition_part001.pdf` |
| extract | `{source}_extract_{date}.pdf` | `Deposition_extract_2026-05-18.pdf` |
| rotate | `{source}_rotated.pdf` | `Scan_rotated.pdf` |
| reorder | `{source}_reordered.pdf` | `Scan_reordered.pdf` |
| bates | `{source}_BATES.pdf` | `ExhibitPacket_BATES.pdf` |

### Collision handling
If the output file already exists and `overwrite=False` (the default), append `_01`, `_02`, etc. to the stem before the extension:
`Complaint_merged_2026-05-18_01.pdf`

The user is never silently overwritten.

### User overrides
The user may supply a custom output name in any operation. Custom names still receive the collision-prevention suffix if needed. The `.pdf` extension is always enforced.

---

## Source / Input Traceability

Every output file gets a **JSON sidecar** written alongside it:

`Complaint_merged_2026-05-18.pdf`  
`Complaint_merged_2026-05-18.apm_audit.json`

The sidecar contains the full serialized `Job` object (see `core/job.py:Job.to_dict()`), including:

- `job_id` — unique UUID for this run
- `created_at` — ISO 8601 timestamp
- `operation` — operation name
- `inputs` — ordered list of source files with their SHA-256 hashes at time of job creation
- `params` — full parameter set used
- `provenance.tool_version` — APMultitool version that produced the output
- `provenance.operator` — machine username

The SHA-256 hash of each input allows later verification that the source file has not changed since the output was produced.

**The sidecar is not required for the output to be valid.** It is metadata. If the user deletes it, the output PDF is unaffected. If the sidecar write fails (permissions, disk space), the operation is not aborted.

---

## Operation History

The engine maintains an in-session `history` list of all completed jobs. Future enhancement: persist history to a local SQLite or JSON log file in the output directory, so the user can review past runs across sessions.

For now, the sidecar files serve as the durable record. A user can reconstruct the full history of a working directory by reading all `.apm_audit.json` files in it.

---

## Error Reporting

### Operation-level errors
If a job fails entirely, the sidecar is still written with `status: "failed"` and `result.error` populated with the exception message. The output PDF is not written (or is deleted if partially written).

### File-level warnings (partial failures)
For batch operations (merge with 10 inputs, email harvest), individual file failures are non-fatal. The engine:
1. Logs the failure as a warning in `result.warnings`
2. Continues processing remaining files
3. Includes the warning list in the sidecar

The user sees all warnings in the status area after completion.

### User-visible error messages
Error messages shown in the UI must be plain English, not stack traces. Examples:
- "Could not read Deposition.pdf — the file may be password-protected."
- "Jones_email.msg was skipped — attachment type .xlsb is not supported."
- "Output folder is not writable. Check permissions on C:\Users\...\Merged_Output."

Stack traces go to a log file, not the UI.

---

## Reversibility Labels

Every operation has a declared reversibility level. The GUI displays this label before the user runs an operation.

| Label | Meaning | Operations |
|---|---|---|
| `non-destructive` | Source files are never modified. Output is a new file. | merge, split, extract, rotate, reorder |
| `in-place` | Source file is replaced. Original is gone unless the user made a backup. | rotate with overwrite=True (future) |
| `permanent` | The change is baked into the output and cannot be reversed at the application level. | Bates stamping (vector-fused), flatten annotations (future) |

**The `permanent` label requires explicit user acknowledgment** before the operation runs — a confirmation line ("I understand this cannot be undone") rather than a blocking modal.

For `non-destructive` operations, no confirmation is needed — just the green label below the button.
