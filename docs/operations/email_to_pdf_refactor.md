# 🔗 Operations Architecture Proposal: EmailToPdfOperation Refactoring

This document outlines the design and integration plan for wrapping the offline `.eml` and `.msg` parsing utilities in `email_processing.py` into a standardized, headless operation within the **`core/operations/`** package.

---

## 🏛️ 1. Architecture Context

Currently, the email parser lives in `email_processing.py` as a standalone CLI script. While robust, this layout violates the separation of concerns by putting helper functions, CLI handlers, and ReportLab canvas parameters in a single file in the root folder.

We have a decoupled engine at `core/engine.py` and a canonical model at `core/job.py`. The Job model already declares parameters specifically for this operation:
```python
@dataclass
class EmailToPdfParams:
    grayscale: bool = False
    include_attachments: bool = True
    paper_size: str = "letter"
    output_name: str | None = None
```

To complete integration, we will refactor `email_processing.py` into `core/operations/email_to_pdf.py`.

---

## ⚙️ 2. Proposed Interface & Handle Pattern

In compliance with the `core/operations/` contract, the refactored class must export a unified callable handle matching the core operation registry:

```python
"""
core/operations/email_to_pdf.py
Encapsulates EML and MSG conversions using ReportLab, Pillow, and pypdf.
"""

from pathlib import Path
from typing import Callable
from core.job import Job, JobResult

def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """
    Core entry point dispatched synchronously by DocEngine.
    
    Args:
        job: Job containing inputs (specifying .eml/.msg file paths) 
             and params (EmailToPdfParams).
        progress: Callback(message, fraction_0_to_1) to update UI logs.
        
    Returns:
        JobResult listing generated PDF path, page counts, and warnings.
    """
    progress("Initializing Email Parser...", 0.1)
    
    # 1. Parse Inputs
    # 2. Convert Body and attachments to temporary PDFs
    # 3. Merge pages using pypdf
    # 4. Save output to job.output.directory
    
    return JobResult(
        outputs=[output_pdf_path],
        page_count_in=page_count_in,
        page_count_out=page_count_out,
        warnings=warnings_list,
    )
```

---

## 📂 3. Integration Blueprint

1.  **Create Module**: Deconstruct `email_processing.py` and write the processing logic to `core/operations/email_to_pdf.py`.
2.  **Register Operation**: Add the handler to `core/operations/__init__.py`:
    ```python
    from core.operations.email_to_pdf import handle as _email_to_pdf
    
    OPERATION_REGISTRY: dict = {
        # ...
        "email_to_pdf": _email_to_pdf,
    }
    ```
3.  **Refactor GUI Dispatches**: Update `gui_apmultitool.py` to compile a Job and dispatch it synchronously to `DocEngine.submit()`. This decouples the visual loop from PDF operations completely.

---

*System State: STAX ALIGNED | Phase: OPERATION INTEGRATION PROPOSAL REGISTERED*
