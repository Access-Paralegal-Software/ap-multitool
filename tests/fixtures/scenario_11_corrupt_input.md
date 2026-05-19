# Scenario 11 — Corrupt / Unreadable Input (Partial Failure)

## Setup
- Input files (ordered):
  1. `clean_01.pdf` (5pp) — valid
  2. `clean_02.pdf` (3pp) — valid
  3. `corrupt.pdf` — truncated binary, will raise pikepdf.PdfError on open
  4. `clean_04.pdf` (8pp) — valid
  5. `clean_05.pdf` (2pp) — valid
- Operation: `merge`
- Parameters: `bookmarks=True`, `grayscale=False`

## Expected Output
- One file: `clean_01_merged_YYYY-MM-DD.pdf`
- Page count: 18 (5 + 3 + 8 + 2 — corrupt file excluded)
- Bookmarks: 4 entries (clean files only)
- Warnings: 1 — "Skipped corrupt.pdf: [error message]"

## Assertions
- [ ] Output file exists
- [ ] Output page count == 18
- [ ] Bookmark count == 4
- [ ] `result.warnings` contains exactly 1 warning mentioning "corrupt.pdf"
- [ ] `result.status` == "complete" (not "failed")
- [ ] Source files unmodified
- [ ] Audit sidecar reflects warning in `result.warnings`

## Edge Cases Exercised
- Partial failure in a batch operation must not abort the job
- Corrupt file at position 3 (middle of queue) — files after it must still be processed
- Warning must name the specific file that failed

## Sample Data Notes
```python
# Create corrupt PDF
with open("corrupt.pdf", "wb") as f:
    f.write(b"%PDF-1.4\n%corrupt truncated content")
```
