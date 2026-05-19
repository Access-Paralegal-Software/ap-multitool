---
title: APMultitool Job Model
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Canonical Job Model

Every document manipulation task in APMultitool is represented as a **Job**. A Job captures everything needed to execute a task, reproduce it, and explain what happened afterward.

The job model is the connective tissue between the GUI, the engine, and the audit log. It lives in `core/job.py`.

---

## Job Structure

```python
@dataclass
class Job:
    job_id: str              # UUID, generated at job creation time
    created_at: datetime     # Wall-clock time when the job was queued
    operation: str           # Canonical operation name: "merge", "split", "rotate", etc.
    inputs: list[InputSpec]  # Ordered list of input files
    params: JobParams        # Operation-specific parameters
    output: OutputSpec       # Where the result goes, naming rules
    provenance: ProvenanceRecord  # Source traceability metadata
    status: JobStatus        # pending → running → complete | failed
    result: JobResult | None # Populated after execution
```

---

## InputSpec

Describes a single input document.

```python
@dataclass
class InputSpec:
    path: Path               # Absolute path to the source file
    kind: str                # "pdf", "docx", "eml", "msg", "image", "text"
    label: str | None        # User-assigned display name or exhibit label
    page_range: str | None   # "1-5", "3,7,12" — None means all pages
    order_index: int         # Position in the input sequence
    sha256: str              # Hash of source file at job creation time
```

---

## JobParams

Operation-specific parameters. Each operation defines its own params dataclass; `JobParams` is a union type or base class.

### MergeParams
```python
@dataclass
class MergeParams:
    bookmarks: bool = True         # Create a bookmark per input file
    enforce_page_size: bool = True # Normalize all pages to target size
    grayscale: bool = False        # Convert color content to grayscale
    paper_size: str = "letter"     # "letter", "legal", "a4"
    output_name: str | None = None # Override auto-generated output name
```

### SplitParams
```python
@dataclass
class SplitParams:
    mode: str                      # "ranges", "fixed", "blank_page"
    ranges: list[str] | None = None  # ["1-5", "6-12"] for "ranges" mode
    pages_per_chunk: int | None = None  # for "fixed" mode
    name_template: str = "{source}_{n:03d}"
```

### ExtractParams
```python
@dataclass
class ExtractParams:
    page_selection: str            # "1-5", "3,7,12", "1,3-5,9"
    output_name: str | None = None
```

### RotateParams
```python
@dataclass
class RotateParams:
    angle: int                     # 90, 180, 270
    page_selection: str = "all"    # "all", "1,3,5", "1-4"
```

### ReorderParams
```python
@dataclass
class ReorderParams:
    page_order: list[int]          # New 1-based page order: [3,1,2,4]
```

### BatesParams
```python
@dataclass
class BatesParams:
    prefix: str                    # e.g. "SMITH" → "SMITH000001"
    start_number: int = 1
    padding: int = 6               # Zero-pad width
    position: str = "bottom_right" # "bottom_right", "bottom_left", "bottom_center"
    font_size: int = 10
    shrink_conflict: bool = True   # Shrink page if stamp overlaps content
```

---

## OutputSpec

```python
@dataclass
class OutputSpec:
    directory: Path           # Target output directory
    name_template: str        # Filename pattern with substitution tokens
    overwrite: bool = False   # Whether to replace an existing file
    open_after: bool = False  # Whether to open output in system viewer
```

**Name template tokens:**
- `{source}` — stem of the first input file
- `{op}` — operation name
- `{date}` — YYYY-MM-DD
- `{time}` — HHMMSS
- `{n}` — sequence index (for split operations producing multiple outputs)

**Default templates by operation:**
- merge: `{source}_merged_{date}.pdf`
- split: `{source}_part{n:03d}.pdf`
- extract: `{source}_extract_{date}.pdf`
- rotate: `{source}_rotated.pdf`
- reorder: `{source}_reordered.pdf`
- bates: `{source}_BATES.pdf`

---

## ProvenanceRecord

Captures the traceability data so the user can always explain where an output came from.

```python
@dataclass
class ProvenanceRecord:
    source_hashes: dict[str, str]  # path → sha256 at job creation time
    tool_version: str              # config.__version__
    operator: str | None           # Machine username
    note: str | None               # Free-text note attached at job time
```

---

## JobStatus

```python
class JobStatus(Enum):
    PENDING  = "pending"
    RUNNING  = "running"
    COMPLETE = "complete"
    FAILED   = "failed"
    CANCELLED = "cancelled"
```

---

## JobResult

Populated by the engine after execution.

```python
@dataclass
class JobResult:
    outputs: list[Path]           # Paths of all files written
    duration_seconds: float       # Wall-clock execution time
    page_count_in: int            # Total input pages processed
    page_count_out: int           # Total output pages written
    warnings: list[str]           # Non-fatal issues encountered
    error: str | None             # Error message if status == FAILED
```

---

## Lifecycle

```
Job created (status=PENDING)
     │
     ▼
DocEngine.submit(job)
     │
     ▼
Engine validates inputs → status=RUNNING
     │
     ├── Success → result populated → status=COMPLETE
     │
     └── Error   → result.error set → status=FAILED
```

Jobs are serializable to JSON for audit log persistence. The engine writes a `.json` sidecar next to each output file by default.

---

## Reversibility Labels

The audit model uses three reversibility labels:

| Label | Meaning | Examples |
|---|---|---|
| `non-destructive` | Source files are never modified | merge, extract, split, rotate (new file output) |
| `in-place` | Source file is replaced | rotate with overwrite=True, bates stamp on original |
| `permanent` | Cannot be undone at the operation level | Bates stamp (vector-fused), flatten annotations |

The GUI should display the reversibility label when the user is about to execute an `in-place` or `permanent` operation.
