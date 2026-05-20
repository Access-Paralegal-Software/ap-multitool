---
id: qt_async_worker_pattern
title: Qt Async Worker & Cancellation Robustness
type: ops-audit
---

# Async Worker Pattern & Robustness

## Thread Lifecycles
- `EngineJobWorker` inherits `QObject` and moves to a discrete `QThread`.
- **Cleanup**: `on_finished` correctly calls `self.thread.quit()`, `wait()`, and nullifies references. Memory leaks are structurally avoided.

## Cancellation Robustness
- **Compiler**: Uses `self.active_worker.request_cancel()`. Accurately cleans up UI state and disables active layout locks. Flags rows as `⚠️ Cancelled`.
- **Bates**: Properly intercepts mid-run, logs cancellation.
- **Edge Case**: If the main application window is closed while workers are active, the background thread could detach or segfault if `wait()` is not enforced. 
- *Remedy*: Ensure application teardown intercepts active threads.

## Temporary File Cleanup
- Engine operations (`core/operations/`) natively use PyPDF2 streams and do not generate arbitrary local `.tmp` files. Temporary I/O relies on Python `tempfile` scope handlers which self-clean.
