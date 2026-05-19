# tests/test_docx_xlsx_bates.py — Unit and integration tests for converters and Bates stamping
import os
import shutil
import tempfile
from pathlib import Path
from unittest import mock
import pytest
import pikepdf

from core.job import Job, InputSpec, DocxToPdfParams, XlsxToPdfParams, BatesParams, OutputSpec, JobStatus, OperationCancelled
from core.engine import DocEngine
from core.operations.docx_to_pdf import handle as docx_handle
from core.operations.xlsx_to_pdf import handle as xlsx_handle
from core.operations.bates_stamp import handle as bates_handle


@pytest.fixture
def temp_output_dir():
    """Fixture creating and cleaning up a temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_pdf_path(temp_output_dir) -> Path:
    """Fixture returning a path to a simple mock PDF file for Bates Stamping tests."""
    pdf_path = temp_output_dir / "test_input.pdf"
    from reportlab.pdfgen import canvas
    can = canvas.Canvas(str(pdf_path))
    can.drawString(100, 100, "This is page 1 of the test document.")
    can.showPage()
    can.drawString(100, 100, "This is page 2 of the test document.")
    can.showPage()
    can.save()
    return pdf_path


# =============================================================================
# Docx Conversion Tests
# =============================================================================

def test_docx_conversion_fails_missing_input(temp_output_dir):
    """Verify that docx_to_pdf fails if the input file does not exist."""
    job_input = InputSpec.from_path(temp_output_dir / "missing.docx")
    job_params = DocxToPdfParams(output_name="out.pdf")
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="docx_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )
    with pytest.raises(FileNotFoundError):
        docx_handle(job, lambda m, v: None)


def test_docx_conversion_success(temp_output_dir):
    """Verify registration, job execution, and result metadata output for Word files."""
    dummy_docx = temp_output_dir / "test.docx"
    dummy_docx.write_bytes(b"Mock docx binary contents")

    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(dummy_docx)
    job_params = DocxToPdfParams(output_name="converted_word.pdf")
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="docx_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    # Setup mocks for win32com and pythoncom
    mock_word = mock.MagicMock()
    mock_doc = mock.MagicMock()
    mock_word.Documents.Open.return_value = mock_doc

    def mock_save_as(dest_path, FileFormat):
        from reportlab.pdfgen import canvas
        can = canvas.Canvas(dest_path)
        can.drawString(100, 100, "Mocked Word conversion output PDF")
        can.save()

    mock_doc.SaveAs.side_effect = mock_save_as

    import sys
    sys.modules['pythoncom'] = mock.MagicMock()
    
    with mock.patch('win32com.client.DispatchEx', return_value=mock_word, create=True):
        res_job = engine.submit(job)
        assert res_job.status == JobStatus.COMPLETE
        assert res_job.result is not None
        assert (temp_output_dir / "converted_word.pdf").exists()


# =============================================================================
# Xlsx Conversion Tests
# =============================================================================

def test_xlsx_conversion_fails_missing_input(temp_output_dir):
    """Verify that xlsx_to_pdf fails if the input file does not exist."""
    job_input = InputSpec.from_path(temp_output_dir / "missing.xlsx")
    job_params = XlsxToPdfParams(output_name="out.pdf")
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="xlsx_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )
    with pytest.raises(FileNotFoundError):
        xlsx_handle(job, lambda m, v: None)


def test_xlsx_conversion_success(temp_output_dir):
    """Verify registration, job execution, and result metadata output for Excel files."""
    dummy_xlsx = temp_output_dir / "test.xlsx"
    dummy_xlsx.write_bytes(b"Mock xlsx binary contents")

    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(dummy_xlsx)
    job_params = XlsxToPdfParams(output_name="converted_excel.pdf")
    job_output = OutputSpec(directory=temp_output_dir)
    job = Job(
        operation="xlsx_to_pdf",
        inputs=[job_input],
        params=job_params,
        output=job_output
    )

    # Setup mocks for win32com and pythoncom
    mock_excel = mock.MagicMock()
    mock_wb = mock.MagicMock()
    mock_excel.Workbooks.Open.return_value = mock_wb

    def mock_export(type_idx, dest_path):
        from reportlab.pdfgen import canvas
        can = canvas.Canvas(dest_path)
        can.drawString(100, 100, "Mocked Excel conversion output PDF")
        can.save()

    mock_wb.ExportAsFixedFormat.side_effect = mock_export

    import sys
    sys.modules['pythoncom'] = mock.MagicMock()

    with mock.patch('win32com.client.DispatchEx', return_value=mock_excel, create=True):
        res_job = engine.submit(job)
        assert res_job.status == JobStatus.COMPLETE
        assert res_job.result is not None
        assert (temp_output_dir / "converted_excel.pdf").exists()


# =============================================================================
# Bates Stamping Integration Tests
# =============================================================================

def test_bates_stamp_success(test_pdf_path, temp_output_dir):
    """Verify registration, job execution, and metadata output for Bates Stamping."""
    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(test_pdf_path)
    job_params = BatesParams(
        prefix="AP",
        start_number=100,
        padding=5,
        position="Bottom Right",
        font_size=10,
        shrink_conflict=True,
        sep="-"
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
    assert res_job.result is not None
    assert res_job.result.error is None
    
    # Check default name format Prefix-Start-End.pdf
    expected_path = temp_output_dir / "AP-00100-00101.pdf"
    assert expected_path.exists()
    assert len(res_job.result.outputs) == 1
    assert Path(res_job.result.outputs[0]) == expected_path
    
    # Verify the pages count is still 2
    with pikepdf.open(expected_path) as pdf:
        assert len(pdf.pages) == 2


def test_bates_stamp_custom_name(test_pdf_path, temp_output_dir):
    """Verify Bates stamping output name overrides work properly."""
    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(test_pdf_path)
    job_params = BatesParams(
        prefix="CONF",
        start_number=1,
        padding=4,
        position="Top Center",
        font_size=12,
        shrink_conflict=False,
        sep="_",
        output_name="confidential_stamped.pdf"
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
    
    expected_path = temp_output_dir / "confidential_stamped.pdf"
    assert expected_path.exists()


def test_bates_stamp_cancellation(test_pdf_path, temp_output_dir):
    """Verify cooperative cancellation of Bates jobs behaves cleanly."""
    engine = DocEngine(write_audit=False)
    job_input = InputSpec.from_path(test_pdf_path)
    job_params = BatesParams(
        prefix="CANCEL",
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

    def on_progress(msg, val):
        # Cancel job mid-flight
        job.status = JobStatus.CANCELLED

    with pytest.raises(OperationCancelled):
        engine.submit(job, on_progress=on_progress)

    assert job.status == JobStatus.CANCELLED
    # Verify temporary file cleanup
    # (Checking that no finalized PDF was moved to the destination)
    final_output = temp_output_dir / "CANCEL-0001-0002.pdf"
    assert not final_output.exists()
