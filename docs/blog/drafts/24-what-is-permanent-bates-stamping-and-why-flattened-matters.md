# What Is Permanent Bates Stamping and Why "Flattened" Matters

*Pillar: Product Deep-Dive | Target keyword: permanent Bates stamping flattened PDF legal production*

---

Not all Bates stamping is the same. The difference between permanent, flattened Bates stamps and the alternative — layered or annotation-based stamping — is significant in legal production, and it's a distinction worth understanding before you choose a tool.

## How Bates Stamps Are Applied: The Two Methods

**Annotation-based stamping.** Some PDF tools apply Bates stamps as annotations — essentially labels that sit on top of the document but are separate from the underlying page content. Annotations can be edited, removed, or moved. They may not print correctly on all printers. In some PDF viewers, they can be toggled off. They are, in a sense, attached to the page rather than part of it.

**Flattened stamping.** Other tools burn the Bates stamp directly into the page content. The stamp is no longer a separate layer — it's part of the rendered page, like ink on paper. It cannot be edited, removed, or toggled without corrupting the document. When you open the PDF in any viewer, print it on any printer, or display it on any screen, the stamp is there exactly as applied.

For legal production, flattened stamping is the correct standard. Here's why.

## Why "Flattened" Is the Legal Standard

**Integrity.** An annotation-based stamp can, in theory, be modified or removed by anyone with the right PDF editor. A flattened stamp is as permanent as the document itself. When you're producing exhibits that will be cited in court filings, depositions, and briefs, the Bates stamp needs to be unambiguously part of the document — not a removable decoration on top of it.

**Printer and viewer consistency.** Annotations can render differently depending on the PDF viewer and print driver. Flattened stamps render identically on every device, because they're image data, not instructions for a rendering layer to interpret. If opposing counsel prints your production on a different printer than you used, the page looks identical.

**Court requirements.** Some jurisdictions have specific requirements about how exhibits must be stamped, and these typically contemplate permanent stamping. An annotation-based stamp may not satisfy a requirement that Bates numbers "appear on" the document.

**Long-term archiving.** Legal files are archived for years or decades. Annotation layers can degrade in compatibility as PDF format specifications evolve. Flattened content, being rendered image data, is stable across any PDF specification version.

## What "Permanently Flattened" Means in Practice

When APMultitool applies Bates stamps, the stamp is rendered directly into the page content at the time of processing. The resulting PDF page contains the stamp as visible, non-removable image data.

You can verify this by opening a stamped document and attempting to select the Bates stamp text. In a flattened PDF, the stamp is not selectable — it's part of the page image. In an annotation-based stamped PDF, you can often click and select the stamp as a separate object.

If you can click on the Bates stamp and it highlights or moves, it's not flattened. That's a problem.

## The Implications for Your QA Process

When you're verifying a produced exhibit packet before it goes out, add one quick check to your QA routine: try to click or select a Bates stamp in the merged PDF. If it's selectable or moveable, your tool is not applying flattened stamps and you need to investigate before sending.

If the stamp is part of the page — not clickable, not selectable, rendering identically to the surrounding text and graphics — your stamps are permanent.

## Why This Matters for the Paralegal

The paralegal who produces a packet with annotation-based Bates stamps may not know there's an issue until opposing counsel, a reviewing court, or a technical expert raises it. At that point, the question of whether the production was properly formatted becomes part of the record.

Understanding the distinction — and being able to articulate that your productions use permanent, flattened stamps — is a professional advantage. It demonstrates technical literacy about the production process and signals that your work meets the standard the legal record requires.

---

**APMultitool applies permanently flattened Bates stamps** — burned into page content at the time of processing, not applied as removable annotations. [Download the Windows beta](https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe) and see what a court-ready stamped packet looks like.

*More at the [FAQ](https://software.accessparalegalservices.com/faq.html) or email info@accessparalegalservices.com.*
