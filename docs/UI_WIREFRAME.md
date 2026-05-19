---
title: APMultitool UI Wireframe — v2 Workbench Layout
type: reference
status: active
updated_at: "2026-05-18T00:00:00Z"
---

# APMultitool — UI Wireframe

## Design Philosophy

The tool should feel like a well-made knife: purposeful, balanced, satisfying to use. Not an enterprise nightmare with 40 buttons, not a web toy with rounded corners and animations everywhere. A serious local instrument that rewards the user for knowing their job.

---

## Main Window Layout (960 × 760 minimum)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  [LOGO]          ACCESS PARALEGAL MULTITOOL          [version] [license] │  ← Header bar (80px)
├──────────────────────────────────────────────────────────────────────────┤
│  📦 Document Merger  │  ✂️ Manipulate  │  ⚖️ Bates  │  📂 File Room     │  ← Tab bar
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────┐  ┌───────────────────────────────────────┐  │
│  │  SETTINGS PANEL (360px) │  │  DOCUMENT QUEUE (flex)                │  │
│  │                         │  │                                       │  │
│  │  ▸ Paper size           │  │  [📁 Open Folder]  [+ Add Files]      │  │
│  │  ▸ Bookmarks on/off     │  │  ┌────────────────────────────────┐   │  │
│  │  ▸ Grayscale toggle     │  │  │ #  Filename          Pages  St │   │  │
│  │  ▸ Compression          │  │  │ 1  Complaint.pdf       12   ✅ │   │  │
│  │  ▸ Email attachments    │  │  │ 2  Exhibit A.pdf        4   ✅ │   │  │
│  │                         │  │  │ 3  Depo_Jones.msg      --   ⏳ │   │  │
│  │  ─────────────────────  │  │  │ 4  Photo_scan.jpg       1   ✅ │   │  │
│  │                         │  │  └────────────────────────────────┘   │  │
│  │  QUEUE PREVIEW          │  │  [↑ Up] [↓ Down] [✕ Remove]          │  │
│  │  Documents:  4          │  │                                       │  │
│  │  Est. pages: 17+        │  │  [         MERGE DOCUMENTS          ] │  │
│  │                         │  │                                       │  │
│  │                         │  │  ░░░░░░░░░░░░░░░░░░░░ 0%            │  │
│  │                         │  │  Status: Ready                       │  │
│  │                         │  │                                       │  │
│  └─────────────────────────┘  └───────────────────────────────────────┘  │
│                                                                          │
│  [Output: C:\...\Merged_Output\]                              [Open ↗]  │  ← Footer bar
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Manipulate Tab Layout (New — MVP)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📦 Document Merger  │  ✂️ Manipulate  │  ⚖️ Bates  │  📂 File Room     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [📄 Load PDF...]   source_document.pdf (28 pages)          [✕ Clear]  │
│                                                                          │
│  ┌─── OPERATION ────────────────────────────────────────────────────┐   │
│  │  ○ Split    ● Extract    ○ Rotate    ○ Reorder                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─── EXTRACT OPTIONS ──────────────────────────────────────────────┐   │
│  │  Pages:  [1, 3-5, 9          ]   (e.g. "1-5", "3,7,12", "all")  │   │
│  │  Output: [source_extract_...  ]   [Browse...]                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌─── PAGE PREVIEW ─────────────────────────────────────────────────┐   │
│  │  [p.1 ▪] [p.2  ] [p.3 ▪] [p.4 ▪] [p.5 ▪] [p.6  ] [p.7  ] …   │   │
│  │   ▪ = selected for extraction                                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  [      EXTRACT PAGES      ]   ⚠ Non-destructive — source unchanged    │
│                                                                          │
│  ░░░░░░░░░░░░░░░░░░░░ 0%    Status: Ready                               │
└──────────────────────────────────────────────────────────────────────────┘
```

Operation switcher changes the options panel below it. Same tab, four modes.

---

## Bates Tab Layout (Existing — Enhanced Spec)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  📦 Document Merger  │  ✂️ Manipulate  │  ⚖️ Bates  │  📂 File Room     │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [📄 Select PDF to Stamp...]   exhibit_packet.pdf (47 pages)            │
│                                                                          │
│  ┌─── STAMP SETTINGS ───────────────────────────────────────────────┐   │
│  │  Prefix:   [SMITH        ]   Start #: [000001]   Padding: [6]    │   │
│  │  Position: [Bottom Right ▾]  Font size: [10]                     │   │
│  │  ☑ Shrink page if stamp conflicts with content                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Preview stamp:  SMITH000001 … SMITH000047                               │
│                                                                          │
│  [     APPLY BATES STAMPS     ]   ⚠ Permanent — vector-fused           │
│                                                                          │
│  ░░░░░░░░░░░░░░░░░░░░ 0%    Status: Ready                               │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Key UI Principles

- **Reversibility label always visible** before any destructive action. Green = non-destructive, amber = permanent.
- **Progress bar is honest** — shows real fraction, not a spinner that lies.
- **Status line** stays readable: "Merging page 12 of 47…" not "Working…"
- **Output path is always visible** in the footer. User should never wonder where the file went.
- **One primary action button per view.** No competing CTAs.
- **Queue supports drag-reorder.** Row click selects. Double-click opens source file.
