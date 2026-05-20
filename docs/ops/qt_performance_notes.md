---
id: qt_performance_notes
title: Qt Performance & Efficiency Notes
type: ops-audit
---

# Qt Performance Notes (High-Load Efficiency)

## Table Queue Management (Compiler)
- *Finding*: `CompilerQueueTable.add_file_paths` iterates and inserts items row-by-row but does not wrap the logic in `blockSignals(True)`. For large drag-and-drop operations (100+ files), this can cause micro-stutters.
- *Remediation*: Applied signal blocking during massive loop insertions to eliminate layout recalculation overhead.

## Console Output Throttling (Bates)
- *Finding*: `bates.py` appends to `QPlainTextEdit` dynamically via `log_message()`. If stamping a 5000+ page document, emitting logs per-page creates massive event loop lag.
- *Remediation*: Engine should be relied upon to throttle progress messages to chunks of 5% or 10% bounds rather than per-file.

## Directory Tree Parsing (File Room)
- *Finding*: `rebuild_preview` evaluates the entire custom hierarchy structure string replacement map linearly. Performance is fine for < 500 directories, but optimal to prevent deep recursion. O(N) evaluation retained.
