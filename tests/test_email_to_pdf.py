import os
import shutil
import tempfile
from pathlib import Path
import pytest
import pikepdf

from core.job import Job, InputSpec, EmailToPdfParams, OutputSpec, JobStatus, OperationCancelled
from core.engine import DocEngine
from core.operations.email_to_pdf import handle as email_handle
import email_processing

pytestmark = [pytest.mark.core, pytest.mark.integration]


@pytest.fixture
def test_email_path() -> Path:
    """Fixture returning the path to the test EML file.
    Creates one dynamically if not present in scratch/test_temp/test_email.eml.
    """
    repo_root = Path(__file__).parent.parent
    eml_path = repo_root / "scratch" / "test_temp" / "test_email.eml"
    
    if eml_path.exists():
        return eml_path
        
    # Dynamically scaffold a mock EML if missing
    eml_dir = repo_root / "scratch" / "test_temp"
    eml_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple EML format with headers, body and a basic image attachment
    content = (
        "From: sender@accessparalegalservices.com\n"
        "To: recipient@accessparalegalservices.com\n"
        "Subject: Access Paralegal Test Subject ⚖️\n"
        "Date: Mon, 18 May 2026 12:00:00 -0500\n"
        "Content-Type: multipart/mixed; boundary=\"boundary-cell\"\n\n"
        "--boundary-cell\n"
        "Content-Type: text/plain; charset=utf-8\n\n"
        "This is a test email body for APMultitool validation.\n\n"
        "--boundary-cell\n"
        "Content-Type: text/plain; name=\"test_att.txt\"\n"
        "Content-Disposition: attachment; filename=\"test_att.txt\"\n\n"
        "Attachment content goes here.\n"
        "--boundary-cell--"
    )
    eml_path.write_text(content, encoding="utf-8")
    return eml_path


@pytest.fixture
def temp_output_dir():
    """Fixture creating and cleaning up a temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


# =============================================================================
# Task 4 – Unit Tests for Core Email Behavior
# =============================================================================

def test_unified_email_parsing(test_email_path):
    """Verify that UnifiedEmail correctly parses headers, subject, and attachments."""
    email_obj = email_processing.UnifiedEmail(test_email_path)
    
    assert "Access Paralegal" in email_obj.subject
    assert "sender@accessparalegalservices.com" in email_obj.sender
    assert len(email_obj.attachments) >= 1


def test_email_body_to_pdf_conversion(test_email_path, temp_output_dir):
    """Verify that email body cover page can be generated as a PDF file."""
    email_obj = email_processing.UnifiedEmail(test_email_path)
    out_pdf = temp_output_dir / "cover.pdf"
    
    email_processing.email_to_pdf(email_obj, out_pdf, grayscale=False)
    
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
    with pikepdf.open(out_pdf) as pdf:
        assert len(pdf.pages) >= 1


def test_attachment_conversion(temp_output_dir):
    """Verify attachment_to_pdf conversions for text and image formats."""
    text_data = b"This is attachment content"
    out_pdf = temp_output_dir / "att_text.pdf"
    
    success = email_processing.attachment_to_pdf(
        text_data, "test.txt", out_pdf, "text/plain", grayscale=False
    )
    assert success
    assert out_pdf.exists()
    
    # Try an invalid type to verify placeholder conversion fallback
    bad_data = b"unknown data"
    bad_pdf = temp_output_dir / "att_bad.pdf"
    success_bad = email_processing.attachment_to_pdf(
        bad_data, "test.unknown", bad_pdf, "application/octet-stream", grayscale=False
    )
    assert success_bad
    assert bad_pdf.exists()
    with pikepdf.open(bad_pdf) as pdf:
        # Should have created a placeholder page
        assert len(pdf.pages) == 1


# =============================================================================
# Task 5 – Engine-level Integration Tests for Email Jobs
# =============================================================================

def test_engine_integration_success(test_email_path, temp_output_dir):
    """Verify registration, job execution, and result metadata output in DocEngine."""
    engine = DocEngine(write_audit=False)
    
    job_input = InputSpec.from_path(test_email_path)
    job_params = EmailToPdfParams(
        grayscale=True,
        include_attachments=True,
        output_name="integration_output.pdf"
    )
    job_output = OutputSpec(directory=temp_output_dir)
    
    job = Job(
        operation="email_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )
    
    progress_calls = []
    def progress_cb(msg, progress_val):
        progress_calls.append((msg, progress_val))
        
    res_job = engine.submit(job, on_progress=progress_cb)
    
    assert res_job.status == JobStatus.COMPLETE
    assert res_job.result is not None
    assert res_job.result.error is None
    
    final_path = temp_output_dir / "integration_output.pdf"
    assert final_path.exists()
    assert len(res_job.result.outputs) == 1
    assert Path(res_job.result.outputs[0]) == final_path
    
    # Verify page count is positive and accurate
    assert res_job.result.page_count_out > 0
    with pikepdf.open(final_path) as pdf:
        assert len(pdf.pages) == res_job.result.page_count_out
        
    # Check that progress updates occurred
    assert len(progress_calls) > 0
    assert progress_calls[-1][1] == 1.0


# =============================================================================
# Task 6 – Cancellation and Failure Tests
# =============================================================================

def test_engine_cancellation(test_email_path, temp_output_dir):
    """Verify that setting cancel status raises OperationCancelled and cleans up temp files."""
    engine = DocEngine(write_audit=False)
    
    job_input = InputSpec.from_path(test_email_path)
    job_params = EmailToPdfParams(
        grayscale=False,
        include_attachments=True,
        output_name="cancelled_output.pdf"
    )
    job_output = OutputSpec(directory=temp_output_dir)
    
    job = Job(
        operation="email_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )
    
    # Progress callback that cancels the job mid-flight
    def progress_cb(msg, progress_val):
        job.status = JobStatus.CANCELLED
    
    with pytest.raises(OperationCancelled):
        engine.submit(job, on_progress=progress_cb)
        
    # Verify no file was created
    final_path = temp_output_dir / "cancelled_output.pdf"
    assert not final_path.exists()
    assert job.status == JobStatus.CANCELLED


def test_engine_failure_invalid_format(temp_output_dir, monkeypatch):
    """Verify that an invalid/empty email file sets the job to FAILED and reports error."""
    engine = DocEngine(write_audit=False)
    
    # Mock UnifiedEmail to raise a parsing failure
    def mock_parse_fail(*args, **kwargs):
        raise ValueError("Simulated parsing error")
    monkeypatch.setattr(email_processing, "UnifiedEmail", mock_parse_fail)
    
    # Create an empty file (which exists, so _prepare succeeds, but parsing fails)
    invalid_file = temp_output_dir / "invalid_email.eml"
    invalid_file.write_text("Not an email content", encoding="utf-8")
    
    job_input = InputSpec.from_path(invalid_file)
    job_params = EmailToPdfParams(
        grayscale=False,
        include_attachments=True,
        output_name="failed_output.pdf"
    )
    job_output = OutputSpec(directory=temp_output_dir)
    
    job = Job(
        operation="email_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )
    
    # Execution should raise Exception due to parsing/conversion failure
    with pytest.raises(Exception):
        engine.submit(job)
        
    assert job.status == JobStatus.FAILED
    assert job.result is not None
    assert job.result.error is not None
    assert "Simulated parsing error" in job.result.error
    
    final_path = temp_output_dir / "failed_output.pdf"
    assert not final_path.exists()


