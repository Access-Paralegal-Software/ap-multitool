---
title: Email to PDF Operation Practical Usage Guide
date: 2026-05-19
status: active
project: Access Paralegal
tags: [ap_multitool, documentation, operations, email-ops]
---

# 📖 Email to PDF Operation: Practical Usage Guide

This guide describes how to construct, configure, and execute the `"email_to_pdf"` operation via the APMultitool core engine.

## 1. Importing Core Abstractions
To submit an email conversion job, import `Job`, `InputSpec`, `EmailToPdfParams`, `OutputSpec`, and `DocEngine` from the core modules:

```python
from pathlib import Path
from core.job import Job, InputSpec, EmailToPdfParams, OutputSpec
from core.engine import DocEngine
```

## 2. Instantiating Parameters
The `EmailToPdfParams` class holds the configuration options:

```python
params = EmailToPdfParams(
    grayscale=False,             # Set to True for PACER-compliant grayscale compression
    include_attachments=True,    # If True, appends and merges email attachments
    paper_size="letter",         # "letter" | "legal" | "a4"
    output_name="my_email.pdf"   # Optional filename override (auto-generated if None)
)
```

## 3. Creating and Submitting the Job
Define the input email file, output directory, and instantiate the `Job`:

```python
# 1. Define input (.eml or .msg)
job_input = InputSpec.from_path(Path("source_directory/case_email.eml"))

# 2. Define output destination directory
job_output = OutputSpec(directory=Path("output_directory"))

# 3. Create the Job
job = Job(
    operation="email_to_pdf",
    inputs=[job_input],
    params=params,
    output=job_output
)

# 4. Define progress callback (optional)
def on_progress(message: str, fraction: float):
    print(f"Progress [{int(fraction * 100)}%]: {message}")

# 5. Submit to the engine
engine = DocEngine(write_audit=True)
result_job = engine.submit(job, on_progress=on_progress)

# 6. Verify result
if result_job.status == JobStatus.COMPLETE:
    print(f"Success! Output PDF generated: {result_job.result.outputs[0]}")
    print(f"Generated Pages: {result_job.result.page_count_out}")
```

## 4. Cancellation Handling
To cancel a job mid-flight, set the status to `JobStatus.CANCELLED`. The operation handler checks this state at multiple checkpoints and raises an `OperationCancelled` exception, cleaning up any intermediate temporary files:

```python
from core.job import JobStatus, OperationCancelled

# Inside a callback or background thread:
job.status = JobStatus.CANCELLED
```
