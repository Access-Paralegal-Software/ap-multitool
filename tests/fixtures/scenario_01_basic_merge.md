# Scenario 01 — Basic Merge (Golden Path)

## Setup
- Input files: `complaint.pdf` (12pp), `exhibit_a.pdf` (4pp), `deposition_jones.pdf` (22pp) — all clean, letter-size, portrait
- Operation: `merge`
- Parameters: `bookmarks=True`, `grayscale=False`, `paper_size="letter"`
- Output dir: `tests/fixtures/output/`

## Expected Output
- One file: `complaint_merged_YYYY-MM-DD.pdf`
- Page count: 38
- Bookmarks: 3 entries — "complaint", "exhibit_a", "deposition_jones"
- No warnings

## Assertions
- [ ] Output file exists
- [ ] Output page count == 38
- [ ] PDF outline (bookmarks) contains exactly 3 items
- [ ] Bookmark 1 → page 1, Bookmark 2 → page 13, Bookmark 3 → page 17
- [ ] Source files unmodified (SHA-256 unchanged)
- [ ] Audit sidecar `.apm_audit.json` exists alongside output
- [ ] Sidecar `status` == "complete"

## Edge Cases Exercised
- None (this is the pure golden path)

## Sample Data Notes
Generate with:
```python
make_test_pdf("complaint.pdf", pages=12, label="Complaint")
make_test_pdf("exhibit_a.pdf", pages=4, label="Exhibit A")
make_test_pdf("deposition_jones.pdf", pages=22, label="Deposition of Jones")
```
