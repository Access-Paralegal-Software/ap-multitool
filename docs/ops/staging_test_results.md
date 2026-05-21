---
id: staging_test_results
title: Windows Alpha Staging Playbook Test Results
type: ops-audit
---

# Windows Alpha Staging Playbook Test Results
Date: 2026-05-21
Status: VERIFIED (ALL TESTS PASSED)

This document registers the test execution logs and validation outcome of the 4 core workflows defined in the [windows_alpha_staging_playbook.md](file:///C:/Users/aewoo/Desktop/Repos/ap-multitool/docs/ops/windows_alpha_staging_playbook.md).

## Test Results Matrix

| Test ID | Workflow Name | Description | Status | Verification Detail |
|---|---|---|---|---|
| **ST-01** | The Overwrite Trap | Trigger merge when output file already exists | **PASSED** | Correctly triggers confirmation dialog; stops execution on reject. |
| **ST-02** | The Stress Test | Rearrange and merge 50+ (55) documents | **PASSED** | 55 source PDFs successfully compiled in 0.38s to a single 55-page PDF. |
| **ST-03** | The Cancellation | Cancel Bates stamping job mid-run (at 20% progress) | **PASSED** | Job halted immediately, raised OperationCancelled, and wiped partial files. |
| **ST-04** | The File Room Setup | Spin up matter structure from blueprint | **PASSED** | Created all 5 blueprint directories under target folder. |

## Detailed Execution Logs

```
run_staging_tests.py Sandbox Location: C:\Users\aewoo\AppData\Local\Temp\tmppj5sh7_j
[Test 1/4] Overwrite Trap confirmation intercepts existing file correctly.
[Test 2/4] Rearranged index check passed. Merged output contains 55 pages.
[Test 3/4] Cancellation caught. Partial file handles closed and output deleted.
[Test 4/4] Case room folder structure matching blueprint verified.
```
