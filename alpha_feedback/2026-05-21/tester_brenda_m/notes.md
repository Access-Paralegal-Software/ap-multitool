# Alpha Session Notes: Brenda M.
**Date:** 2026-05-21  
**Tester Identifier:** tester_brenda_m (Paralegal)  
**OS Environment:** Windows 11 Home, Display scaling 150%  

## Workflows Attempted
1. **Motion Packet Merging:** Adding 12 PDF files, 2 Word documents, and 1 Excel file. Merging them into a single unified motion packet.
2. **Bates Stamping:** Applying Bates numbers with prefix "BM" and start number 1 to the merged packet.

## Observations & Issues Encountered
1. **Drag-and-Drop Reordering Friction (Minor/Polish - Compiler):**
   * *Observation:* Brenda struggled to reorder rows in the merge queue using drag-and-drop. In Qt, the dropping zone was too narrow, causing accidental row drops or insertions at wrong places.
   * *User Quote:* *"It's hard to position the document exactly where I want it by dragging. I wish there were up and down arrow buttons."*
2. **Registry Lookup Empty Case ID Crash/Friction (Major - Bates):**
   * *Observation:* When Brenda tabbed out of the prefix field in the Bates view, she had not filled out the Case ID in the File Room view (leaving it empty). The autoincrement registry lookups triggered a KeyError internally when accessing `Matter-` registry keys for empty matter strings.
   * *Log Traceback (Scrubbed):*
     ```
     [ERROR] Exception in on_prefix_editing_finished: KeyError: ''
     ```
3. **Gear Icon Overlap (Polish - GUI Layout):**
   * *Observation:* At 150% display scaling, the Gear settings button slightly overlaps the neighboring text label in the Bates view parameters section.
