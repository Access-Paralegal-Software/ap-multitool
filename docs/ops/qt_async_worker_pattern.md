# APMultitool Qt Async Worker Pattern

This document establishes the architecture for invoking long-running document operations in the PySide6 application without locking the user interface.

---

## 🧵 1. Threading Strategy

All `DocEngine` executions are synchronous and CPU-bound. To maintain interface responsiveness (and avoid operating system "Not Responding" warnings):
1. **Thread Separation**: All job submits must run inside a background `QThread`.
2. **Signal Communication**: The worker communicates with the UI thread strictly using `QtCore.Signal`. It must never directly write to GUI widgets.
3. **Cooperative Cancellation**: Standard engine operations accept a progress callback. When the user requests a cancel, the callback raises `OperationCancelled`, aborting execution thread-safely.

---

## 🏛 2. EngineJobWorker Blueprint

```python
from PySide6 import QtCore
from apmultitool_qt.core_bridge import EngineJobWorker
from core.job import Job, MergeParams, OutputSpec

def run_merge_job(self):
    # 1. Setup Job parameters
    job = Job(
        operation="merge",
        inputs=[...],
        params=MergeParams(...),
        output=OutputSpec(...)
    )

    # 2. Instantiate thread and worker
    self.thread = QtCore.QThread()
    self.worker = EngineJobWorker(job)
    self.worker.moveToThread(self.thread)

    # 3. Wire Slots / Signals
    self.thread.started.connect(self.worker.run_job)
    self.worker.progress.connect(self.on_progress)
    self.worker.log_message.connect(self.on_log)
    self.worker.finished.connect(self.on_finished)

    # 4. Start background processing
    self.thread.start()
```

---

## 🧼 3. Teardown and Resource Cleanup

When `finished` is emitted, the thread must be stopped and dereferenced cleanly to prevent memory leaks:

```python
def on_finished(self, success, error_message, result):
    # Quit thread event loop
    self.thread.quit()
    self.thread.wait()

    # Clear references
    self.worker = None
    self.thread = None

    if success:
        # handle completed result payload
        pass
```
