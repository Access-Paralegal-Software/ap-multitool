---
title: APMultitool User Journeys
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — Core User Journeys

## User Persona

**Primary:** Paralegal at a small-to-mid law firm or solo practice. Windows machine, moderate tech comfort. Works with PDFs, emails, and document sets daily. Currently uses Adobe Acrobat, drag-and-drop into email, or clunky web converters. Frustrated by cost, slowness, and lack of legal-workflow awareness in general tools.

**Secondary:** Litigation support specialist. More technical. Handles high-volume Bates production runs and exhibit packet assembly. Cares about correctness and audit trail above all.

---

## Journey Map

### J1 — Merge Documents into a Single PDF

**Who:** Any paralegal assembling a filing packet or delivery set.  
**Trigger:** "I have 8 files — 3 PDFs, 2 Word docs, 4 emails — and I need one merged PDF for the court."  
**Release:** MVP

**Steps:**
1. Open APMultitool → Document Merger tab
2. Point to source folder or drag files into queue
3. Reorder queue to match desired output order
4. Set options: bookmarks per file, paper size, grayscale toggle
5. Click Merge → progress fills → output PDF lands in Merged_Output/
6. Open output to verify

**Success state:** Single clean PDF, correct order, bookmarks for each source file, ready to attach or file.

**Edge cases:** Mixed portrait/landscape pages, password-protected source PDFs, corrupt source files, very large sets (100+ pages).

---

### J2 — Split a PDF into Separate Files

**Who:** Paralegal receiving a bulk scan or production set that needs to be broken into individual documents.  
**Trigger:** "Opposing counsel sent a 200-page PDF dump. I need to split it into the individual letters and exhibits."  
**Release:** MVP

**Steps:**
1. Open APMultitool → (future: Split tab or Manipulate tab)
2. Load source PDF
3. Choose split mode: by page range, by fixed page count, or by blank-page divider
4. Preview split points
5. Execute → one output file per segment, named sequentially or with custom prefixes
6. Review output list

**Success state:** N output PDFs, each a clean slice of the original, names reflect content or sequence.

**Edge cases:** No clean split points in a scanned doc, single-page source, odd page counts with fixed split.

---

### J3 — Reorder Pages Within a PDF

**Who:** Paralegal who received a scan in the wrong order, or needs to move an exhibit to a different position in the packet.  
**Trigger:** "The exhibit was scanned backwards. I need to flip the page order before I Bates it."  
**Release:** MVP

**Steps:**
1. Load PDF into page view
2. See thumbnails or page list
3. Drag pages into correct order, or use move-up/down controls
4. Apply → output is new reordered PDF

**Success state:** PDF with pages in the user-specified order, original preserved unless user chooses overwrite.

**Edge cases:** Very large PDFs (slow thumbnail generation), mixed-orientation pages.

---

### J4 — Rotate Pages

**Who:** Paralegal dealing with a scanned document where some pages are sideways.  
**Trigger:** "Pages 3, 7, and 12 are landscape. I need to rotate them 90° so they read correctly."  
**Release:** MVP

**Steps:**
1. Load PDF into page view
2. Select pages (individual or all)
3. Choose rotation: 90° CW, 90° CCW, 180°
4. Preview → Apply

**Success state:** PDF with specified pages rotated, all other pages unchanged.

**Edge cases:** Already-rotated pages (double rotation), rotate-all-pages for a fully sideways scan.

---

### J5 — Extract Pages into a New PDF

**Who:** Paralegal who needs to pull specific pages or a range out of a larger document for a separate exhibit.  
**Trigger:** "I need pages 14–22 of this deposition as a standalone exhibit."  
**Release:** MVP

**Steps:**
1. Load source PDF
2. Select page range or click individual pages
3. Extract → new PDF created from selection
4. Original is untouched

**Success state:** Clean output PDF containing only the selected pages, original file unchanged.

**Edge cases:** Non-contiguous page selections, extracting a single page, extracting the entire file (no-op detection).

---

### J6 — Assemble a Document Packet

**Who:** Paralegal preparing a formal exhibit set for filing or service.  
**Trigger:** "I need to build Exhibit A through G, each with a cover page, in one PDF, numbered continuously."  
**Release:** MVP (basic); Next-wave (cover pages, dividers, TOC)

**Steps (MVP):**
1. Merge tab: build ordered queue of source files
2. Set bookmarks = on (each file becomes a named bookmark)
3. Merge → single PDF
4. Run Bates stamping on the output (sequential numbering across the full packet)

**Steps (Next-wave):**
1. Packet assembly tab: add files and label each as a named exhibit
2. Auto-generate cover page per exhibit (label, date, description)
3. Insert separator page between exhibits
4. Choose continuous numbering scheme
5. Output: polished packet with TOC, covers, and Bates numbers

**Success state (MVP):** One bookmarked PDF with continuous Bates numbering.  
**Success state (Next-wave):** Full exhibit packet with covers, separators, and TOC, print-ready.

---

## Release Classification

| Journey | MVP | Next-Wave | Research Required |
|---|---|---|---|
| J1 Merge | ✅ | — | — |
| J2 Split | ✅ | — | Split-by-blank-page detection |
| J3 Reorder | ✅ | — | — |
| J4 Rotate | ✅ | — | — |
| J5 Extract | ✅ | — | — |
| J6 Packet (basic) | ✅ | — | — |
| J6 Packet (covers, dividers, TOC) | — | ✅ | Cover page template system |
| Bates numbering | ✅ | — | — |
| Email-to-PDF batch | ✅ | — | — |
| Watermarking | — | ✅ | — |
| Page numbering | — | ✅ | — |
| OCR integration | — | — | ✅ |
| Form field flatten | — | — | ✅ |

---

## Open Questions

- Should Split be a tab of its own, or a mode inside a unified "Manipulate" tab alongside Reorder/Rotate/Extract?
- Page thumbnail generation for Reorder/Rotate/Extract — acceptable performance threshold for large PDFs?
- Should the output always be a new file, or should in-place overwrite be an option (with confirmation)?
