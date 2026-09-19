# Drag-and-Drop Exhibit Ordering: A Better Way to Manage Document Queues

*Pillar: Workflow & How-To | Target keyword: drag and drop PDF reorder exhibit queue paralegal*

---

Document ordering is one of those tasks that looks simple until you're doing it at scale. Reordering 10 PDFs is easy enough in a file system — rename them with numbered prefixes and sort. Reordering 40 PDFs, while verifying the correct sequence, while managing attorney feedback on exhibit priority, while working on a deadline — that's a different experience entirely.

Most file system approaches to ordering break down somewhere in that process. What makes them break is the gap between what you think the order is and what it actually is when you look at the merged output.

A visual document queue closes that gap.

## Why File System Ordering Fails at Scale

The default approach to PDF ordering in most small firm workflows looks something like this:

1. Name files with numeric prefixes: `01_medicalrecords.pdf`, `02_correspondence.pdf`, etc.
2. Process them in filename sort order
3. Hope that the sort order matches the intended exhibit order

The failure modes:
- A file gets renamed but the prefix doesn't change correctly, creating a gap or duplicate in the sequence
- The attorney asks you to move `07_contract.pdf` to the second position, so you rename it `02_contract.pdf` — which means `02_correspondence.pdf` is now in the wrong position
- You merge, the order is wrong, you start over

Every time you modify the order by renaming files, you create the possibility of an error. And in a large set of documents, renaming cascades — changing one position means changing every position above or below it.

## How a Visual Queue Changes the Workflow

A visual document queue shows you the exact order that will be used in the final merge, before the merge happens. Documents are displayed in a list. You change the order by interacting with the list — dragging items, typing position numbers — not by renaming files in a file system.

The advantages:
- **What you see is what you get.** The queue reflects the actual merge order. No translation between filename sequences and actual output order.
- **Reordering is non-destructive.** Moving a document in the queue doesn't modify the source file or its filename. You can change the order as many times as needed without creating any artifacts.
- **You can verify before committing.** Scroll through the queue top to bottom and check that every document is in the right position before clicking merge. This review step catches errors before they become problems.
- **Position changes are instant and accurate.** Move a document from position 35 to position 2 in seconds, with all other positions automatically adjusting.

## Two Ways to Order in APMultitool

APMultitool's queue supports two ordering methods depending on what you're doing:

**Drag-and-drop for general reordering.** Click and drag documents to rearrange their position in the queue. This is fast for coarse ordering — putting broad groups in the right sequence — and for making a handful of moves in a short list.

**Direct position entry for precision moves.** Double-click the `#` column on any document and type the exact position you want it in. Press Enter and the document jumps there, with all other documents shifting to accommodate. This is the right tool for:
- Moving a priority document to a specific position in a long list
- Making exact position adjustments without dragging through dozens of items
- Overriding an auto-loaded order when you know exactly where something needs to go

Most real-world ordering sessions use both: drag-and-drop to get the rough structure right, then direct position entry for specific adjustments.

## The Verification Step

After ordering, take 60 seconds to scroll the queue from top to bottom and verify it against your exhibit outline. This is the step that saves time — because catching a misplaced document in the queue takes a few seconds to fix, while catching it after the merge means starting over.

Check that:
- The sequence matches your exhibit list or the attorney's instructions
- Any priority documents (cover sheets, certification pages, key exhibits) are in the right positions
- No documents appear to be missing from the queue

Then merge.

## The Audit Log Confirms the Order

After merging, the automatically-generated audit log lists every document that was included, in the order it appeared in the final output. This serves as your permanent record of what was assembled and in what sequence — useful for your own records and available as documentation if the ordering is ever questioned.

---

**APMultitool's visual queue gives you full control over exhibit order, with both drag-and-drop and direct position entry.** [Download the Windows beta](https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe) and order your next packet without renaming a single file.

*More detail in the [FAQ](https://software.accessparalegalservices.com/faq.html) or email info@accessparalegalservices.com.*
