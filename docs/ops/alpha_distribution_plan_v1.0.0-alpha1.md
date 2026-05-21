---
id: alpha_distribution_plan_v1.0.0-alpha1
title: Alpha1 Distribution Plan
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Alpha1 Distribution Plan (v1.0.0-alpha1)

This document describes the deployment, cohort coordination, and feedback ingestion procedures for the **v1.0.0-alpha1** Windows Alpha release.

---

## 👥 Cohort Profile & Size

- **Target Size**: ~12 (one dozen) active legal operations specialists and paralegals.
- **Environment**: Native Windows 10 or 11 workstations.
- **Workflow Requirements**: Testers must regularly merge files (PDFs, DOCX, XLSX), apply Bates stamping, or structure Matter folder archives.

---

## 📦 Distribution Method

1.  **Hosting**: Secure internal shared link or file storage channel (e.g., SharePoint folder, OneDrive, or internal release bucket).
2.  **Required Assets**:
    - `APMultitool_Setup_v1.0.0-alpha1.exe` (Installer executable)
    - `APMultitool_Setup_v1.0.0-alpha1.exe.sha256` (Checksum verification file)
    - [windows_smartscreen_alpha_notes.md](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/docs/ops/windows_smartscreen_alpha_notes.md) (Bypass tutorial copy)
3.  **Tester Email Outline**:
    - Provide the secure download link.
    - Copy-paste the SHA256 checksum and explain how to verify it.
    - Detail the SmartScreen warning bypass flow.
    - Attach the [feedback_intake_v1.0.0.md](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/docs/ops/feedback_intake_v1.0.0.md) questionnaire.

---

## 📅 Timeline

- **Start of Testing**: Immediate upon receipt of build package link.
- **Testing Duration**: 14 calendar days (2-week window).
- **Target Feedback Date**: 14 days post-distribution.

---

## 📥 Feedback & Telemetry Collection Protocol

Operators are responsible for collecting two artifacts from each tester at the end of the test cycle:

### 1. The Completed Feedback Form (`.md`)
- Testers fill out [feedback_intake_v1.0.0.md](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/docs/ops/feedback_intake_v1.0.0.md).
- Filename convention for repository filing:
  ```text
  docs/feedback/v1.0.0-alpha1/feedback_tester_<last_name>_<first_initial>.md
  ```

### 2. Telemetry JSON File Snapshot
- The application automatically aggregates job counts and error messages to:
  ```text
  C:\Users\<Username>\.access_paralegal_telemetry.json
  ```
- Operators instruct testers to email or upload this file.
- Filename convention for repository filing:
  ```text
  docs/feedback/v1.0.0-alpha1/telemetry_tester_<last_name>_<first_initial>.json
  ```

### 3. Log File Export (Troubleshooting Only)
- In the event of a crash or unexpected engine failure, the operator will request the application logs from:
  ```text
  C:\Users\<Username>\AppData\Local\Access_Paralegal_Multitool\logs\
  ```
