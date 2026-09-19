# How the Bates Registry Ledger Prevents Duplicate Exhibit Numbers Across Sessions

*Pillar: Product Deep-Dive | Target keyword: Bates stamping duplicate numbers prevention paralegal software*

---

Duplicate Bates numbers are one of the most embarrassing — and consequential — errors a paralegal can introduce into a production. If your exhibits run `DEF-EX-00001` through `DEF-EX-00100` in one production and then your next production for the same case starts at `DEF-EX-00001` again, you've created a numbering conflict that opposing counsel will notice, the court will notice, and your attorney will definitely notice.

Fixing it means re-stamping, re-assembling, and potentially re-serving — with an explanation about how it happened.

APMultitool's Bates Registry Ledger is designed specifically to prevent this problem.

## How Duplicate Bates Numbers Happen

In a manual or single-session workflow, tracking the last-used Bates number seems simple. You wrote it down. You remember it. You have a spreadsheet.

The problem is sessions. Legal document production is rarely a single continuous session. You produce a set of documents today. You produce another set next week. Two weeks later, opposing counsel requests supplemental documents and you need to produce a third set in the same case.

Each time you return to Bates stamping for a case, you need to know where the last production left off. And each time you're relying on a handwritten note, a spreadsheet, a memory — all of which can be wrong.

The Bates Registry Ledger solves this by having the software track the last-used number for each prefix, so you don't have to.

## How the Registry Works

The Registry Ledger stores a record for each Bates prefix you've used. When you enter a prefix like `DEF-EX-` into the stamping configuration, APMultitool checks the registry:

- **If the prefix is new:** The start index defaults to 1, and you can confirm or change it
- **If the prefix has been used before:** The start index auto-populates with the next number in sequence — if the last production ended at `DEF-EX-00100`, the registry suggests `DEF-EX-00101`

This auto-suggestion happens automatically every time you return to a prefix, across sessions, across days, across weeks. You don't need to do anything to maintain it — just enter the prefix and review the suggested start number before you proceed.

## What to Do When You Need to Override It

The registry auto-suggestion is a safeguard, not a lock. There are legitimate reasons to start at a different number:

- You've agreed with opposing counsel on a specific numbering range for a category of documents
- You're correcting a stamping error from a previous session and need to re-issue a range
- The case has a pre-existing numbering convention from documents stamped before you started using APMultitool

To override, click into the Start Index field and type your intended number. The registry will update to reflect the new starting point and continue tracking from wherever you leave off.

This gives you the protection of automatic tracking while preserving the flexibility to intervene when the situation requires it.

## The Double-Check Before You Merge

Before you run any Bates stamping job, it's worth spending 10 seconds on a quick check:

1. Enter your prefix
2. Review the auto-suggested start index
3. Mentally verify: does this match where the last production ended?
4. If yes, proceed. If uncertain, check the previous production's audit log to confirm the last Bates number issued.

The audit log is your authoritative record of what was stamped in each session. The registry and the audit log work together — the registry tells you where to start, and the audit log provides the paper trail to verify.

## Why This Matters More Than It Sounds

Duplicate Bates numbers are not just an administrative error. In discovery, Bates numbers are used as citations — in deposition questions, in briefs, in court arguments. If two documents share a Bates number, every citation that uses that number is now ambiguous. Which document does `DEF-EX-00047` refer to?

Courts have sanctioned parties for discovery numbering errors. More commonly, the error creates confusion and work for everyone involved, and it damages the credibility of the production — and the paralegal responsible for it.

The Registry Ledger is a small feature with a disproportionately large impact on production quality.

---

**APMultitool's Bates Registry Ledger tracks your prefix history automatically, across sessions, entirely offline.** No spreadsheet to maintain, no handwritten notes to lose. [Download the Windows beta](https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe) and see it in action on your next production.

*Read more at the [FAQ](https://software.accessparalegalservices.com/faq.html) or reach out at info@accessparalegalservices.com.*
