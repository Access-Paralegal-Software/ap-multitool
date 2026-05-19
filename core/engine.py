"""
core/engine.py — APMultitool document operation engine.

DocEngine accepts Jobs, dispatches them to the correct operation handler,
tracks status, and writes audit records. It has no GUI imports.
"""

from __future__ import annotations

import getpass
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import config
from core.job import Job, JobResult, JobStatus, ProvenanceRecord, OperationCancelled
from core.operations import OPERATION_REGISTRY


class DocEngine:
    """
    Central engine for all document manipulation jobs.

    Usage:
        engine = DocEngine(output_root=Path("Merged_Output"))
        engine.submit(job)               # synchronous
        engine.submit(job, on_progress=cb)  # with progress callback
    """

    def __init__(
        self,
        output_root: Path | None = None,
        write_audit: bool = True,
    ):
        self.output_root = Path(output_root) if output_root else Path.cwd()
        self.write_audit = write_audit
        self._history: list[Job] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(
        self,
        job: Job,
        on_progress: Callable[[str, float], None] | None = None,
    ) -> Job:
        """
        Execute a job synchronously.

        Args:
            job: A fully-constructed Job object.
            on_progress: Optional callback(message, fraction_0_to_1).

        Returns:
            The same job object with status and result populated.
        """
        self._prepare(job)
        job.status = JobStatus.RUNNING
        started = time.monotonic()

        try:
            handler = OPERATION_REGISTRY.get(job.operation)
            if handler is None:
                raise ValueError(f"Unknown operation: '{job.operation}'. "
                                 f"Registered: {list(OPERATION_REGISTRY)}")

            result = handler(job, on_progress or _noop_progress)
            result.duration_seconds = time.monotonic() - started
            job.result = result
            job.status = JobStatus.COMPLETE

        except OperationCancelled as exc:
            job.result = JobResult(
                error="Operation cancelled by user",
                duration_seconds=time.monotonic() - started,
            )
            job.status = JobStatus.CANCELLED
            raise

        except Exception as exc:
            job.result = JobResult(
                error=str(exc),
                duration_seconds=time.monotonic() - started,
            )
            job.status = JobStatus.FAILED
            raise

        finally:
            self._history.append(job)
            if self.write_audit and job.result:
                self._write_audit_sidecar(job)

        return job

    @property
    def history(self) -> list[Job]:
        return list(self._history)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _prepare(self, job: Job) -> None:
        """Validate inputs and fill provenance fields."""
        for spec in job.inputs:
            if not spec.path.exists():
                raise FileNotFoundError(f"Input not found: {spec.path}")

        job.provenance = ProvenanceRecord(
            source_hashes={str(s.path): s.sha256 for s in job.inputs},
            tool_version=config.__version__,
            operator=_get_operator(),
            note=job.provenance.note if job.provenance else None,
        )
        job.output.directory.mkdir(parents=True, exist_ok=True)

    def _write_audit_sidecar(self, job: Job) -> None:
        """Write a JSON sidecar record next to the first output file."""
        try:
            if job.result and job.result.outputs:
                sidecar = job.result.outputs[0].with_suffix(".apm_audit.json")
            else:
                sidecar = job.output.directory / f"{job.job_id}.apm_audit.json"

            with open(sidecar, "w", encoding="utf-8") as f:
                json.dump(job.to_dict(), f, indent=2, default=str)
        except Exception:
            pass  # Audit write failure must never block the operation result


def _noop_progress(message: str, fraction: float) -> None:
    pass


def _get_operator() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"
