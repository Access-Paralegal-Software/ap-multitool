# Scenario 03 — Rotated Scan Correction

## Setup
- Input files: `scanned_pleading.pdf` (10pp) — pages 3, 7, 10 have `/Rotate: 90` (appear landscape in viewer)
- Operation: `rotate`
- Parameters: `angle=270`, `page_selection="3,7,10"` (270° CW == 90° CCW correction)
- Output dir: `tests/fixtures/output/`

## Expected Output
- One file: `scanned_pleading_rotated.pdf`
- Page count: 10 (unchanged)
- Pages 3, 7, 10: `/Rotate` value changed from 90 to 0 (net of 270 applied)
- Pages 1,2,4,5,6,8,9: `/Rotate` value unchanged

## Assertions
- [ ] Output file exists
- [ ] Output page count == 10
- [ ] Pages 3, 7, 10: effective rotation == 0 (upright)
- [ ] All other pages: rotation unchanged from source
- [ ] Source file unmodified
- [ ] No warnings

## Edge Cases Exercised
- Non-contiguous page selection
- Pages with existing rotation metadata that must be composed, not replaced

## Sample Data Notes
Generate a PDF with alternating rotations using pikepdf:
```python
import pikepdf
pdf = pikepdf.Pdf.new()
for i in range(10):
    page = pikepdf.Page(pikepdf.Dictionary(
        Type=pikepdf.Name("/Page"),
        MediaBox=[0, 0, 612, 792],
    ))
    if i in (2, 6, 9):  # 0-based: pages 3, 7, 10
        page.obj["/Rotate"] = 90
    pdf.pages.append(page)
pdf.save("scanned_pleading.pdf")
```
