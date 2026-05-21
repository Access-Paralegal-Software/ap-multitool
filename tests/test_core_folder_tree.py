# tests/test_core_folder_tree.py

"""Unit and integration tests for the core folder tree generation operation."""

import shutil
import tempfile
from pathlib import Path
import pytest

from core.job import Job, FolderTreeParams, OutputSpec, JobStatus, OperationCancelled
from core.engine import DocEngine

pytestmark = [pytest.mark.core, pytest.mark.integration]


@pytest.fixture
def temp_output_dir():
    """Fixture creating and cleaning up a temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_folder_tree_generation_standard(temp_output_dir):
    """Verify standard civil litigation archetype generates expected directories."""
    engine = DocEngine(write_audit=False)
    
    job_params = FolderTreeParams(
        archetype="Standard Civil Litigation",
        custom_subdirs=[],
        matter_id="AP-Matter-01"
    )
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="folder_tree",
        inputs=[],
        params=job_params,
        output=job_output
    )

    res_job = engine.submit(job)
    assert res_job.status == JobStatus.COMPLETE
    
    # Check that standard subfolders exist
    expected_folders = [
        "01_Pleadings", "02_Discovery", "03_Correspondence", "04_Court_Orders", "05_Research"
    ]
    for folder in expected_folders:
        assert (temp_output_dir / folder).exists()
        assert (temp_output_dir / folder).is_dir()


def test_folder_tree_generation_custom(temp_output_dir):
    """Verify custom archetype generates user-defined subdirs, replacing {Date}."""
    engine = DocEngine(write_audit=False)
    
    custom_dirs = [
        "Records",
        "Records/Medical",
        "Correspondence/{Date}"
    ]
    
    job_params = FolderTreeParams(
        archetype="⭐ Custom User Blueprint",
        custom_subdirs=custom_dirs,
        matter_id="Custom-Matter"
    )
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="folder_tree",
        inputs=[],
        params=job_params,
        output=job_output
    )

    res_job = engine.submit(job)
    assert res_job.status == JobStatus.COMPLETE
    
    # Check folder exists
    assert (temp_output_dir / "Records" / "Medical").exists()
    
    # Check date variable replacement
    from datetime import datetime
    curr_date = datetime.now().strftime("%Y-%m-%d")
    assert (temp_output_dir / "Correspondence" / curr_date).exists()


def test_folder_tree_generation_cancellation(temp_output_dir):
    """Verify folder tree builder handles cooperative cancellation mid-run."""
    engine = DocEngine(write_audit=False)
    
    custom_dirs = ["Folder1", "Folder2", "Folder3"]
    job_params = FolderTreeParams(
        archetype="⭐ Custom User Blueprint",
        custom_subdirs=custom_dirs
    )
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="folder_tree",
        inputs=[],
        params=job_params,
        output=job_output
    )

    def on_progress(msg, val):
        job.status = JobStatus.CANCELLED

    with pytest.raises(OperationCancelled):
        engine.submit(job, on_progress=on_progress)

    assert job.status == JobStatus.CANCELLED
