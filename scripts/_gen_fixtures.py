"""scripts/_gen_fixtures.py — generate minimal, repo-safe fixture documents.

Run once to populate tests/fixtures/conversion/.
Safe to re-run; files are overwritten each time.
"""
from pathlib import Path

import docx
import openpyxl
from openpyxl.styles import Font, PatternFill

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "conversion"
OUT.mkdir(parents=True, exist_ok=True)


# ── fixture 1: simple_text.docx ──────────────────────────────────────────────
d = docx.Document()
d.core_properties.title = "Simple Text Fixture"
d.core_properties.author = "APMultitool Test Suite"
d.add_heading("Simple Text Document", 0)
d.add_paragraph(
    "This is paragraph one. It contains plain prose with no special formatting."
)
d.add_paragraph("This is paragraph two. The document is intentionally minimal.")
d.add_paragraph(
    "This fixture exercises basic text flow through the conversion pipeline."
)
d.save(str(OUT / "simple_text.docx"))
print("wrote simple_text.docx")

# ── fixture 2: headings_and_lists.docx ───────────────────────────────────────
d = docx.Document()
d.core_properties.title = "Headings and Lists Fixture"
d.core_properties.author = "APMultitool Test Suite"
d.add_heading("Headings and Lists", 0)
d.add_heading("Section One", level=1)
d.add_paragraph("This section has a heading and body text.")
d.add_heading("Section Two", level=1)
d.add_heading("Subsection 2.1", level=2)
for label in ("Bullet item alpha", "Bullet item beta", "Bullet item gamma"):
    d.add_paragraph(label, style="List Bullet")
d.add_heading("Numbered List", level=2)
for i in range(1, 4):
    d.add_paragraph(f"Numbered item {i}", style="List Number")
d.save(str(OUT / "headings_and_lists.docx"))
print("wrote headings_and_lists.docx")

# ── fixture 3: basic_table.docx ──────────────────────────────────────────────
d = docx.Document()
d.core_properties.title = "Basic Table Fixture"
d.core_properties.author = "APMultitool Test Suite"
d.add_heading("Document with a Basic Table", 0)
d.add_paragraph("The table below contains four columns and four rows of data.")
table = d.add_table(rows=4, cols=4)
table.style = "Table Grid"
for i, h in enumerate(["Case ID", "Party", "Date Filed", "Status"]):
    cell = table.rows[0].cells[i]
    cell.text = h
    cell.paragraphs[0].runs[0].bold = True
for r_idx, row_data in enumerate(
    [
        ["AP-001", "Smith v Jones", "2025-01-15", "Active"],
        ["AP-002", "Doe v Roe",     "2025-03-22", "Closed"],
        ["AP-003", "State v Lee",   "2025-05-01", "Pending"],
    ],
    start=1,
):
    for c_idx, val in enumerate(row_data):
        table.rows[r_idx].cells[c_idx].text = val
d.add_paragraph("")
d.add_paragraph("End of document.")
d.save(str(OUT / "basic_table.docx"))
print("wrote basic_table.docx")

# ── fixture 4: simple_spreadsheet.xlsx ───────────────────────────────────────
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Data"
for col, h in enumerate(["Invoice #", "Client", "Amount", "Due Date", "Paid"], 1):
    cell = ws.cell(row=1, column=col, value=h)
    cell.font = Font(bold=True)
    cell.fill = PatternFill("solid", fgColor="D9E1F2")
for r, row in enumerate(
    [
        ["INV-001", "Acme Corp",  1250.00, "2025-02-01", "Yes"],
        ["INV-002", "Beta LLC",    875.50, "2025-02-15", "No"],
        ["INV-003", "Gamma Ltd", 2100.00,  "2025-03-01", "Yes"],
        ["INV-004", "Delta Inc",   430.00, "2025-03-15", "No"],
    ],
    start=2,
):
    for c, val in enumerate(row, 1):
        ws.cell(row=r, column=c, value=val)
for col in ws.columns:
    ws.column_dimensions[col[0].column_letter].width = 16
wb.save(str(OUT / "simple_spreadsheet.xlsx"))
print("wrote simple_spreadsheet.xlsx")

# ── fixture 5: multi_sheet.xlsx ──────────────────────────────────────────────
wb = openpyxl.Workbook()

ws1 = wb.active
ws1.title = "Summary"
for col, h in enumerate(["Quarter", "Revenue", "Expenses"], 1):
    ws1.cell(row=1, column=col, value=h).font = Font(bold=True)
for r, (q, rev, exp) in enumerate(
    [("Q1", 42000, 31000), ("Q2", 55000, 38000), ("Q3", 49000, 35000)], start=2
):
    ws1.cell(row=r, column=1, value=q)
    ws1.cell(row=r, column=2, value=rev)
    ws1.cell(row=r, column=3, value=exp)

ws2 = wb.create_sheet("Detail")
ws2.cell(row=1, column=1, value="Item").font = Font(bold=True)
ws2.cell(row=1, column=2, value="Amount").font = Font(bold=True)
for r, (item, amt) in enumerate(
    [("Office Supplies", 1200), ("Travel", 4800), ("Software", 8500)], start=2
):
    ws2.cell(row=r, column=1, value=item)
    ws2.cell(row=r, column=2, value=amt)

wb.save(str(OUT / "multi_sheet.xlsx"))
print("wrote multi_sheet.xlsx")

print(f"\nAll fixtures written to {OUT}")
