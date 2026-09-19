# How to Merge and Bates Stamp a 200-Page Exhibit Packet in Under 5 Minutes

*Pillar: Workflow & How-To | Target keyword: how to merge and Bates stamp PDF exhibit packet quickly*

---

Assembling a large exhibit packet under deadline is one of those tasks that reveals exactly how good your document workflow is. When the attorney needs a 200-page merged and stamped packet in an hour, there's no room for a slow tool, a confusing interface, or a process that requires three separate applications.

This walkthrough shows how to do the whole job — load documents, set the order, apply Bates stamps, and produce an audit-logged output — in a single application, in under five minutes once you know the workflow.

## What You Need Before You Start

- All source PDFs in a single folder on your machine
- Your Bates prefix (e.g., `PL-EX-` for plaintiff exhibits, `DEF-EX-` for defense)
- The starting Bates number (APMultitool's registry will auto-suggest the correct next number if you've worked this case prefix before)
- Your case number, plaintiff, and defendant for the Case Vault

That's it. No account login, no internet connection required.

## Step 1: Set Up the Case Vault (30 Seconds)

When you open APMultitool, the first thing you'll see is the Case Vault at the top of the screen. Enter:
- Case Number
- Plaintiff name
- Defendant name

Click **Lock & Secure**. This associates your session with the case so the audit log captures the correct case context.

If you're coming back to a case you've worked before, the vault fields may auto-populate — verify them and lock.

## Step 2: Load Your Document Folder (30 Seconds)

Click the folder icon on the right side of the interface. Navigate to the folder containing your exhibit PDFs and select it. APMultitool will load all PDFs from that folder into the document queue.

For a 200-page packet spanning 20 or 30 individual documents, this takes seconds.

## Step 3: Set the Exhibit Order (1–2 Minutes)

This is where most of your time goes, and the tool is designed to make it fast.

**Drag-and-drop ordering:** Click and drag documents in the queue to set the correct exhibit sequence. The visual order in the list is the order they'll appear in the final merged PDF.

**Override ordering for priority documents:** If a document needs to be at the top of the queue regardless of where it loaded, double-click the `#` column on that document and type `1`. The document jumps to position one and everything else shifts down. No manual renumbering.

**Check your order** by scanning down the queue list. What you see is exactly what will be merged.

## Step 4: Configure Bates Stamping (1 Minute)

In the Bates stamping configuration:

1. Enter your prefix (e.g., `DEF-EX-`)
2. Check the auto-suggested start index — if you've worked this prefix before, APMultitool's offline registry will suggest the correct next number. If this is a new case or prefix, set the start number manually.
3. Select your stamp position (typically bottom center or bottom right for court filings)
4. Confirm your zero-padding (e.g., 5 digits: `DEF-EX-00001`)

## Step 5: Merge and Stamp (Under 1 Minute)

Click the **COMBINE & MERGE** button.

APMultitool uses background threading, so the application stays responsive while processing. For a 200-page packet, processing typically completes in 30–60 seconds depending on your machine.

When complete, two files automatically open:
- Your merged, Bates-stamped PDF
- `Merge_Audit_Log.txt` — a timestamped record of every document included, its page count, processing duration, and the final Bates sequence applied

## Total Time: Under 5 Minutes

For a paralegal who knows the workflow:
- Case Vault setup: 30 seconds
- Document load: 30 seconds
- Exhibit ordering: 1–2 minutes
- Bates configuration: 1 minute
- Processing: under 1 minute

The audit log is automatic — you don't need to do anything to produce it. And the output is ready to attach to an email or upload to the court's filing portal.

## Tips for High-Volume Cases

- **Pre-organize your folders.** If your source documents are already in a folder organized by exhibit order, the queue load step is close to zero additional work.
- **Let the registry do the math.** Once you've stamped anything with a given prefix, trust the registry's auto-suggestion for subsequent sessions. It's tracking the last-used number to prevent duplicates.
- **Run the audit log through your QA step.** Before you send the packet, open the audit log and verify the document count and Bates range match your expectations. It takes 30 seconds and has saved more than a few packets from going out wrong.

---

**APMultitool is available now in Windows beta.** [Download it here](https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe) and time yourself on your next exhibit packet.

*See the full [FAQ](https://software.accessparalegalservices.com/faq.html) or contact info@accessparalegalservices.com.*
