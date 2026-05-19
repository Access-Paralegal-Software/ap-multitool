---
category: software
plane_id: 
profit_likelihood: high
project: None
status: archived
tags: []
title: README
type: reference
updated_at: "2026-05-17T09:08:47Z"
---

# 🏛️ Archivist Core
> *The Universal Translation Layer and Multi-Provider Inbox for Structured Personal Knowledge Graphs.*

Archivist Core is an elite, enterprise-grade engine engineered to ingest, parse, and normalize complex, messy data from disparate digital brain ecosystems (Evernote, RemNote, Notion, Inbox) and pipeline them into resilient, high-property Markdown notes optimized for Obsidian and Logseq.

---

## 🏛️ Project Architecture

```mermaid
flowchart TD
    subgraph Providers [Ingestion Adapters]
        EV[.ENEX Adapter]
        NO[Notion JSON Adapter]
        EM[.MBOX Email Adapter]
    end

    subgraph Database [Universal Intermediate DB]
        UID[(PostgreSQL / SQLite)]
        S1[Notes Ledger]
        S2[Asset Mapping]
    end

    subgraph Triage [AI-Assisted Triage API]
        AI[Pre-Filter Classifiers]
        FE[[Triage PWA Frontend]]
    end

    subgraph Target [Obsidian Target Pipeline]
        OB[[Portable Note Bundles]]
        LDG[Single-File Ledger]
    end

    Providers -->|Standardize| UID
    UID <--> Triage
    Triage -->|Approve / Distill| Target
```

---

## 🏗️ Directory Structure

- `database/`: SQL schema DDL and universal index migrations.
- `core/`: Strict Type Hinted entity models (Notes, Attachments, Collections).
- `adapters/`: Extensible provider implementations utilizing the Abstract Base Adapter.
- `classifiers/`: Intelligent heuristic engines for flagging junk images/content.

---

## 🧬 Elite Standards

1. **Zero Plagiarism**: Clean-room engineered.
2. **Strict Type Safety**: Fully typed Python 3 and TypeScript models.
3. **Documentation First**: Docstring architectures on every component.
