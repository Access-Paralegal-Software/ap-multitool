# How the Case Vault Keeps Client Information Organized Without a Database

*Pillar: Product Deep-Dive | Target keyword: case management legal document organization paralegal offline*

---

Legal document production tools face a specific organizational problem: every production is tied to a case, and every case has identifying information — a case number, parties, sometimes a court — that should be captured in the production record.

The obvious solution is a database: store case records, associate productions with cases, query by case number. Enterprise legal software does this. It also requires setup, maintenance, user accounts, and usually a server.

For a paralegal working in a small firm who needs document production capabilities without IT infrastructure, a full database is more complexity than the problem requires.

APMultitool's Case Vault solves the organizational problem without introducing database complexity.

## What the Case Vault Does

The Case Vault is the first thing you interact with when you open APMultitool. It has three fields:

- **Case Number**
- **Plaintiff**
- **Defendant**

You fill these in, click Lock & Secure, and the information is associated with your production session. Everything you do in that session — the documents you load, the Bates stamps you apply, the merge you execute — is tied to the case context you entered.

When the audit log is generated at the end of the merge, it includes the case context from the vault. The log doesn't just say "these 28 documents were merged." It says "these 28 documents were merged for Case No. [X], [Plaintiff] v. [Defendant], on [date] at [time]."

## What It Doesn't Do (By Design)

The Case Vault doesn't maintain a persistent case database. It doesn't create records you need to manage, users you need to administer, or a server you need to maintain. When you start a new session, you fill in the vault fields for that session.

This is a deliberate design choice. For the majority of small firm paralegal workflows, the overhead of managing a case database is unnecessary — you already know what case you're working on, you already have the case number in your head or your notes, and adding a database layer between you and the work creates friction without adding value.

What the vault does is capture the session context so the audit log is meaningful. That's the problem it's designed to solve, and it solves it with zero infrastructure overhead.

## How to Use It Effectively

**Be consistent with case number format.** Whatever format your firm uses for case numbers — alphanumeric, year-prefixed, court-docket-style — use it exactly the same way every time you work on a case. Case numbers in the audit log need to be consistent to be searchable and usable.

**Lock before you load documents.** Set the vault at the beginning of the session, before you load any documents into the queue. The vault context is applied to the entire session.

**Verify on case transitions.** If you're doing productions for multiple cases in the same day, verify that you've updated the vault before starting each new case. This is the one place where the lightweight design requires a moment of attention — the vault doesn't automatically detect which case you're working on.

## Using the Audit Log as Your Case Record

Because the Case Vault context appears in every audit log, your collection of audit logs is effectively a production record for each case. If you name your audit logs consistently (for example, `AuditLog_CaseNo123_2026-06-15_Production01.txt`) and keep them organized by case, you have a lightweight but complete record of every production session without managing a database.

For a small firm handling 10–20 active matters at any time, this approach works reliably. For a practice with hundreds of active matters with complex document relationships, a full case management system may be more appropriate. The Case Vault is designed for the former, not the latter.

## The Offline Advantage

Because the Case Vault is local — no database server, no network dependency — it works exactly the same whether you're at the office, at the courthouse, or working from a machine with no internet connection.

The case context is available immediately when you open the application. There's no login, no sync, no "waiting for the server to connect." You open the tool and you're working.

---

**APMultitool's Case Vault captures the case context you need for clean audit logs, without database overhead or IT requirements.** [Download the Windows beta](https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe) and see how light organizational infrastructure can be.

*More at the [FAQ](https://software.accessparalegalservices.com/faq.html) or email info@accessparalegalservices.com.*
