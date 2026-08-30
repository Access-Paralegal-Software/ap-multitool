# core/operations/folder_tree.py — Folder tree generation operation
"""Handler for automating standardized firm directory structures."""

import os
from pathlib import Path
from typing import Callable
from datetime import datetime

from ap_core.job import Job, JobResult, JobStatus, OperationCancelled, FolderTreeParams


def handle(job: Job, progress: Callable[[str, float], None]) -> JobResult:
    """Core engine entry point for the *folder_tree* operation."""
    params: FolderTreeParams = job.params
    
    def check_cancelled():
        if job.status == JobStatus.CANCELLED:
            raise OperationCancelled("Folder tree generation was cancelled by user.")

    check_cancelled()
    progress("Initializing Folder Tree Builder...", 0.1)

    out_dir = Path(job.output.directory)
    # The output directory itself should contain the matter ID folder, or we can use it directly.
    # To keep perfect alignment with the spec, we will create the structure inside out_dir.
    out_dir.mkdir(parents=True, exist_ok=True)

    archetype = params.archetype
    subdirs = []
    
    if archetype == "⭐ Custom User Blueprint":
        subdirs = params.custom_subdirs
    elif archetype == "Standard Civil Litigation":
        subdirs = ["01_Pleadings", "02_Discovery", "03_Correspondence", "04_Court_Orders", "05_Research"]
    elif archetype == "Trial Notebook Model":
        subdirs = ["Exhibits_Plaintiff", "Exhibits_Defendant", "Witness_Outlines", "Jury_Instructions", "Opening_Closing_Statements"]
    else:  # Solo / Freelance Core
        subdirs = ["Admin_Billing", "Client_Intake", "Outbound_Production"]

    curr_date = datetime.now().strftime("%Y-%m-%d")
    created_paths = []
    warnings = []
    
    total = len(subdirs)
    if total == 0:
        progress("No directories to generate.", 1.0)
        return JobResult(outputs=[], warnings=["Blueprint was empty. No folders created."], error=None)

    for idx, sub in enumerate(subdirs):
        check_cancelled()
        percent = 0.1 + 0.8 * (idx / total)
        
        # Parse variables safely
        resolved_sub = sub.replace("{Date}", curr_date)
        resolved_sub = resolved_sub.replace("{Matter ID}", params.matter_id)
        
        # Clean illegal Windows folder characters
        for char in ['*', '?', '"', '<', '>', '|', ':']:
            resolved_sub = resolved_sub.replace(char, "")
            
        target_path = out_dir / resolved_sub
        progress(f"Creating directory: {resolved_sub}...", percent)
        
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            created_paths.append(target_path)
        except Exception as e:
            warnings.append(f"Could not create '{resolved_sub}': {str(e)}")

    progress("Saving configuration log...", 0.95)
    progress("Done.", 1.0)
    
    return JobResult(
        outputs=created_paths,
        warnings=warnings,
        error=None
    )
