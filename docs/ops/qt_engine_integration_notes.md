# APMultitool Qt Engine Integration Specifications

This document outlines the architectural pattern for executing core python engine operations asynchronously within the PySide6 application.

---

## 🧵 1. Thread Separation Architecture

To prevent blocking the primary Qt event loop (which freezes the interface and triggers operating system "Not Responding" alerts), all document conversions, compilations, and Bates stamping runs must execute on isolated background threads.

We implement this using Qt's `QThread` and `QObject` worker pattern:

```
+------------------+                   +--------------------+
|   PySide6 UI     | --(1) Trigger---> |  QtWorkerObject    |
| (QMainWindow)    | <--(2) Signals--- |  (Runs on QThread) |
+------------------+                   +--------------------+
                                                |
                                           (3) Submits
                                                v
                                       +--------------------+
                                       |  core/engine.py    |
                                       |   (DocEngine)      |
                                       +--------------------+
```

### Protocol Sequence:
1. **Instantiation**: The UI view instantiates a subclassed `QObject` worker and a `QThread` controller.
2. **Move to Thread**: The worker is migrated to the thread using `worker.moveToThread(thread)`.
3. **Signal Connections**: The worker signals (started, progress, log, finished) are wired to the UI controller's slots (progress bar updates, text console appends, dialog popups).
4. **Execution**: The worker invokes the core `DocEngine.submit(job)` method.

---

## 📡 2. Signal Bridge Interface

The worker communicates with the UI strictly via Qt Signals:

```python
from PySide6 import QtCore

class EngineWorker(QtCore.QObject):
    # Emitted when execution starts
    started = QtCore.Signal()
    
    # Emitted to update progress bar (percentage value)
    progress = QtCore.Signal(int)
    
    # Emitted to print logs to the Bates console
    log_message = QtCore.Signal(str)
    
    # Emitted when execution concludes (success_bool, result_message)
    finished = QtCore.Signal(bool, str)
```

---

## 🛑 3. Cooperative Cancellation Loop

To support real-time cancellation of tasks, the worker thread polls for cancellation requests at each document page boundary.

- **Trigger**: Clicking the red **Cancel** button on the UI invokes `worker.request_cancel()`.
- **Worker Reaction**: The worker sets the local job state to `JobStatus.CANCELLED`.
- **Clean Cleanup**: The worker deletes any staging sub-folders, releases file descriptors, and emits the `finished(False, "Operation aborted by user")` signal.

---

## ⚡ 4. Proof of Concept (PoC) Diagnostic Wiring

In the foundation sprint, we implement a diagnostic check view to prove this communication architecture:
- **UI Trigger**: A "Run Diagnostic Engine Check" button in the placeholder view.
- **Worker Execution**: Spawns a background worker that fetches version details, checks SQLite database connectivity, counts current case directory matches, and logs results over a simulated 2-second sleep cycle.
- **UI Response**: Logs milestones on a diagnostic text box and pops up a confirmation alert once complete, verifying that signals cross the thread boundary safely.
