---
id: qt_browser_surface_alignment_audit
title: Browser Surface Alignment Audit
type: ops-audit
---

# Browser Surface Alignment Audit

## Purpose
APMultitool is on the Access Paralegal roadmap for a lightweight browser-based release. This audit assesses whether the recent Qt Desktop implementation inadvertently coupled core business logic into the view layer, which would complicate porting to a REST/GraphQL web API and frontend.

## Architecture State
### 1. The Core Job Data Models
The Qt view controllers (`compiler.py`, `bates.py`) utilize strict Pydantic-like dataclasses defined in `core/job.py` (e.g., `Job`, `MergeParams`, `InputSpec`).
- **Verdict**: Excellent. The UI constructs parameter dictionaries and passes them cleanly. A browser implementation can send JSON matching these exact same specs.

### 2. Output File System Mechanics
The Qt workers currently resolve output directory collisions and rely on native `os` commands.
- **Risk**: A web server generating outputs must return URLs or ZIP archives rather than writing to local paths arbitrarily.
- **Alignment Requirement**: The web API wrapper will need a unified storage adapter (as mandated by STAX rules) instead of accepting absolute paths directly from the UI payload. The core engine is already agnostic and just uses python `Path` objects.

### 3. Asynchronous Worker Abstraction
The `EngineJobWorker` inherits `QObject` and heavily relies on Qt Signal emitting (`self.progress.emit()`).
- **Risk**: This is heavily Desktop-bound.
- **Alignment Requirement**: The browser backend will need a Celery or Redis Queue worker equivalent that streams Server-Sent Events (SSE) or WebSockets instead of Qt Signals. However, the `operation_runner` logic within `core.operations` is completely uncoupled from Qt.

## Conclusion
The architectural boundary is pristine. The Qt UI is a dumb terminal assembling `Job` configurations. A web UI can replicate this exact logic by sending JSON payloads representing those `Job` definitions to a standard queue endpoint. No major refactoring is required.
