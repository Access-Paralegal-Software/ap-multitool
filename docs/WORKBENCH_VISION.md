# Access Paralegal Multitool: Local-First Document Workbench Vision

## What is a Document Workbench?

The Access Paralegal Multitool (APMultitool) is **not** an accounts payable system, document repository, or cloud-synced collaboration tool. It is a **local-first document workbench** — a specialized place where legal professionals queue, execute, audit, and manage document operations for litigation support.

### Core Properties of the Workbench

**Local-First**: All processing occurs on the user's machine. Zero cloud uploads. Zero external APIs for document content. Data never leaves the physical PC.

**Job-Oriented**: Users don't "save" files or manage state manually. They initiate **jobs** — discrete operations like "merge these PDFs," "harvest these emails," "assemble this exhibit packet" — and the workbench tracks progress, captures audit logs, and stores outputs.

**Audit Trail**: Every operation is logged. What files went in, what came out, when, by whom (future), how long it took, and whether it succeeded. Legal work requires defensible records.

**Case Isolation**: Documents are organized by case. A case folder becomes a vault — encrypted, locked down, audited. Future features can isolate work by case and user role.

**Plug-In Architecture**: The workbench accepts future modules for specialized operations. Bates stamping, email-to-PDF, OCR, redaction — each plugs into the job model via a contract interface.

**Non-Scary UI**: Users see progress in real time. Jobs queue cleanly. Results are predictable. Errors are clear and actionable. No mysterious background processes.

---

## User Personas

### 1. **Solo Paralegal (Sarah)**
- Works for a 2-person law firm
- Handles document assembly for court filings
- Has 50-100 cases in active litigation
- Needs speed: can't afford to wait for uploads or subscriptions
- Loves the offline aspect — no internet worries during trial prep

### 2. **Document Specialist (Marcus)**
- Works at a mid-size firm (20 attorneys)
- Manages case vaults, coordinates with multiple paralegals
- Prepares exhibits, binders, ECF filing packets
- Needs auditability: partner demands proof of what was done, when, by whom
- Wants to lock down sensitive docs after work is done

### 3. **Trial Coordinator (Priya)**
- Coordinates trial logistics, including exhibit preparation
- Works with teams across multiple offices
- Needs batch operations — process 200 PDFs at once
- Wants the workbench to handle grunt work (merge, reorder, stamp) so humans focus on accuracy

---

## What APMultitool Does (and Doesn't Do)

### ✅ In Scope: Document Operations Workbench
- Queue and execute document transformation jobs (merge, split, extract, rotate, reorder)
- Harvest emails and attachments into structured outputs
- Apply permanent Bates numbering (future module)
- Assemble exhibit packets with indexes and cover pages
- Monitor job progress in real time
- Store immutable audit logs of all operations
- Organize case folders with encryption and access controls

### ❌ Out of Scope: Doesn't Compete With
- **Cloud collaboration** (Sharepoint, Google Drive) — APMultitool is local only
- **Case management systems** (Clio, Matters) — APMultitool doesn't track billing, contacts, deadlines
- **E-discovery platforms** (Relativity, Logikcull) — APMultitool doesn't search/index massive databases
- **Accounts payable** (QuickBooks, NetSuite) — APMultitool doesn't invoice, track expenses, or do accounting

---

## Design Principles

1. **Trust the User's Machine** — The workbench assumes the user's computer is secure. We don't use cloud for trust; we use encryption and local OS permissions.

2. **Audit Everything** — Every operation must be logged, timestamped, and stored. Future legal challenges will ask "prove you did this correctly."

3. **Fail Loudly** — When something goes wrong, stop and show the error clearly. Don't silently drop files or skip pages.

4. **Batch Before Complexity** — The workbench prioritizes batch operations over fancy UI. Processing 100 PDFs at once beats processing them one-by-one.

5. **Contracts Over Centralization** — New features plug in via defined interfaces, not by modifying the core. Bates stamping is a module, not built-in.

---

## Target Release Scope

**MVP**: Merge, extract, rotate, reorder PDFs. Harvest emails. Basic case folder init.

**Future Waves**:
- Bates stamping module
- Email-to-PDF module with advanced attachment parsing
- Obsidian/Notion integration (archive cases)
- Mobile companion (review, approve jobs on phone)
- Team features (assign jobs, share results, log user actions)

---

## Success Metrics

- **Speed**: Process a 500-page merged filing in <5 seconds
- **Reliability**: Zero silent failures; all operations logged
- **Ease**: A paralegal who has never used APMultitool can queue a job in <30 seconds
- **Trust**: All outputs are bit-identical reproducible (same input → same output hash)
