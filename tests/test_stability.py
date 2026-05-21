# tests/test_stability.py — Stability and edge-case validation suite
import os
import shutil
import tempfile
from pathlib import Path
import pytest
import pikepdf
from reportlab.pdfgen import canvas

from core.job import Job, InputSpec, BatesParams, MergeParams, OutputSpec, JobStatus, OperationCancelled
from core.engine import DocEngine
from core.operations.bates_stamp import handle as bates_handle
from core.operations.merge import handle as merge_handle

pytestmark = [pytest.mark.core, pytest.mark.integration, pytest.mark.slow]


@pytest.fixture
def temp_output_dir():
    """Fixture creating and cleaning up a temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


def generate_mock_pdf(path: Path, pages: int, text_content: str = "Test Content") -> Path:
    """Generate a clean mock PDF with specific page count and text overlay."""
    can = canvas.Canvas(str(path))
    for i in range(pages):
        can.drawString(100, 500, f"{text_content} - Page {i + 1}")
        can.showPage()
    can.save()
    return path


# =============================================================================
# Task 9 — Stability Tests: Non-Standard Bates Placements
# =============================================================================

def test_bates_all_placements(temp_output_dir):
    """Verify that Bates overlay coordinates resolve correctly without exceptions for all positions."""
    src_pdf = temp_output_dir / "bates_source.pdf"
    generate_mock_pdf(src_pdf, pages=2, text_content="Placement Test")

    positions = ["Bottom Right", "Bottom Center", "Top Center", "Top Right", "Top Left", "Bottom Left"]

    engine = DocEngine(write_audit=False)

    for idx, pos in enumerate(positions):
        job_input = InputSpec.from_path(src_pdf)
        job_params = BatesParams(
            prefix=f"POS{idx}",
            start_number=1,
            padding=4,
            position=pos,
            font_size=9,
            shrink_conflict=True,
            output_name=f"output_{idx}.pdf"
        )
        job_output = OutputSpec(directory=temp_output_dir, overwrite=True)

        job = Job(
            operation="bates_stamp",
            inputs=[job_input],
            params=job_params,
            output=job_output
        )

        res_job = engine.submit(job)
        assert res_job.status == JobStatus.COMPLETE
        out_file = temp_output_dir / f"output_{idx}.pdf"
        assert out_file.exists()

        # Simple verification of PDF structure after stamping
        with pikepdf.open(out_file) as pdf:
            assert len(pdf.pages) == 2


# =============================================================================
# Task 10 — Stability Tests: Weird Encodings and Special Characters
# =============================================================================

def test_weird_encodings_and_unicode_paths(temp_output_dir):
    """Verify handling of special characters, emojis, and non-ASCII paths/metadata."""
    # Weird folder and file names containing spaces, accents, and emojis
    weird_dir = temp_output_dir / "⚖️ Scale & Accents éüö"
    weird_dir.mkdir(parents=True, exist_ok=True)
    
    src_pdf = weird_dir / "document_⚖️_input.pdf"
    generate_mock_pdf(src_pdf, pages=1, text_content="Unicode Metadata Test ⚖️")

    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(src_pdf)
    job_params = BatesParams(
        prefix="CONF-éü⚖️",
        start_number=77,
        padding=5,
        position="Bottom Center",
        sep="_",
        output_name="out_⚖️_é.pdf"
    )
    job_output = OutputSpec(directory=weird_dir, overwrite=True)

    job = Job(
        operation="bates_stamp",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    res_job = engine.submit(job)
    assert res_job.status == JobStatus.COMPLETE
    
    expected_output = weird_dir / "out_⚖️_é.pdf"
    assert expected_output.exists()
    
    # Read text back to verify it parses correctly without encoding exceptions
    with pikepdf.open(expected_output) as pdf:
        assert len(pdf.pages) == 1


# =============================================================================
# Task 11 — Stability Tests: Large PDF Document Processing
# =============================================================================

def test_large_pdf_processing(temp_output_dir):
    """Verify performance and stability of merging and stamping large PDF documents."""
    doc1 = temp_output_dir / "large_doc_1.pdf"
    doc2 = temp_output_dir / "large_doc_2.pdf"
    
    # Create 50 pages of mock PDFs
    generate_mock_pdf(doc1, pages=30, text_content="Big Pack Segment A")
    generate_mock_pdf(doc2, pages=20, text_content="Big Pack Segment B")

    engine = DocEngine(write_audit=False)

    # 1. Merge them
    merge_job = Job(
        operation="merge",
        inputs=[InputSpec.from_path(doc1), InputSpec.from_path(doc2)],
        params=MergeParams(output_name="merged_50_pages.pdf"),
        output=OutputSpec(directory=temp_output_dir, overwrite=True)
    )

    merge_res = engine.submit(merge_job)
    assert merge_res.status == JobStatus.COMPLETE
    merged_file = temp_output_dir / "merged_50_pages.pdf"
    assert merged_file.exists()

    with pikepdf.open(merged_file) as pdf:
        assert len(pdf.pages) == 50

    # 2. Bates stamp the 50-page document
    bates_job = Job(
        operation="bates_stamp",
        inputs=[InputSpec.from_path(merged_file)],
        params=BatesParams(
            prefix="LARGE",
            start_number=1,
            padding=6,
            position="Bottom Right",
            shrink_conflict=True,
            output_name="large_bates_output.pdf"
        ),
        output=OutputSpec(directory=temp_output_dir, overwrite=True)
    )

    bates_res = engine.submit(bates_job)
    assert bates_res.status == JobStatus.COMPLETE
    bates_file = temp_output_dir / "large_bates_output.pdf"
    assert bates_file.exists()

    with pikepdf.open(bates_file) as pdf:
        assert len(pdf.pages) == 50


# =============================================================================
# Task 12 — Resource Cleanup Verification
# =============================================================================

def test_resource_cleanup_after_completion(temp_output_dir):
    """Verify that execution leaves no hanging temp file allocations in the workspace."""
    src_pdf = temp_output_dir / "cleanup_src.pdf"
    generate_mock_pdf(src_pdf, pages=2, text_content="Cleanup Test")

    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(src_pdf)
    job_params = BatesParams(
        prefix="CLEAN",
        start_number=1,
        padding=4
    )
    job_output = OutputSpec(directory=temp_output_dir, overwrite=True)

    job = Job(
        operation="bates_stamp",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    # Record directory state before and after
    files_before = set(os.listdir(temp_output_dir))
    
    res_job = engine.submit(job)
    assert res_job.status == JobStatus.COMPLETE
    
    # Wait to ensure filesystem finishes updates
    files_after = set(os.listdir(temp_output_dir))
    
    # Filter out our explicitly expected files
    temp_garbage = [f for f in files_after - files_before if "CLEAN" not in f and f != "cleanup_src.pdf"]
    assert len(temp_garbage) == 0, f"Leaked temporary file assets: {temp_garbage}"


def test_resource_cleanup_on_failure(temp_output_dir):
    """Verify that failure paths cleanly collect and delete staged temp outputs."""
    bad_pdf = temp_output_dir / "corrupted.pdf"
    bad_pdf.write_text("Not a real PDF header or zip structure at all.")

    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(bad_pdf)
    job_params = BatesParams(
        prefix="FAIL",
        start_number=1,
        padding=4
    )
    job_output = OutputSpec(directory=temp_output_dir)

    job = Job(
        operation="bates_stamp",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    files_before = set(os.listdir(temp_output_dir))
    
    with pytest.raises(Exception):
        engine.submit(job)

    files_after = set(os.listdir(temp_output_dir))
    
    temp_garbage = [f for f in files_after - files_before if "FAIL" not in f and f != "corrupted.pdf"]
    assert len(temp_garbage) == 0, f"Leaked temporary file assets on exception failure: {temp_garbage}"
