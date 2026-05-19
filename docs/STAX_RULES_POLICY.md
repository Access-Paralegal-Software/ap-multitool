---
category: software
plane_id: 
profit_likelihood: high
project: None
status: ready
tags: []
title: STAX_RULES_POLICY
type: "ops-guide"
updated_at: "2026-05-17T09:08:47Z"
---

# 📜 STAX (Stacks) Repository Rules & Governance Policy

This policy document governs all codebase modifications, workflow transitions, and developer hands-offs across the STAX (Stacks) portfolio of repositories. All agentic coding assistants and human developers must adhere to these policies.

---

## 🏁 1. SESSION HANDOFF & LOGGING POLICY

To ensure absolute workflow continuity when closing/opening chat sessions and switching between agentic assistants, every completed session must produce a formal **Handoff Document** and an **Audit Log**.

### 📁 Standardized Locations
*   **Handoffs Folder**: `/docs/handoffs/` (located within the master repository)
*   **Audit Reports Folder**: `/docs/chats/` (located within the master repository)

### 🏷️ Naming & Numbering Schema
All Handoff Documents must follow a strict, standardized filename syntax to guarantee clean chronological sorting, prevent name collisions, and avoid path-length failures:

$$\text{ho\_[seq]\_[chat\_id\_truncated]\_[slug\_truncated].md}$$

#### 📏 Specific Formatting Rules:
1.  **Sequence (`[seq]`)**: A zero-padded, 4-digit sequential integer (e.g., `0001`, `0002`). This enforces strict temporal order regardless of OS sorting parameters.
2.  **Conversation ID (`[chat_id_truncated]`)**: The first 8 characters of the conversation ID (e.g., `e6f0cb2c`). This creates an unambiguous, machine-readable link to systemic logs.
3.  **Title Slug (`[slug_truncated]`)**: A 2-3 word lowercased description using hyphens instead of spaces, representing the core focus of the turn.
4.  **Strict Truncation Ceiling**: The entire filename (including extension) **MUST NOT exceed 50 characters**. This explicitly protects the repository against Windows `MAX_PATH` (260 characters) checkout failures or systems that break on extremely deep directory nesting.

---

## 🛠️ 2. REPOSITORY & ENVIRONMENT ISOLATION POLICY

### 📦 Dependency Safekeeping (No-Collisions Rule)
To prevent cross-project package contamination or global python version breakages:
*   All project services MUST execute within isolated Python Virtual Environments (`venv`).
*   No project dependencies may be installed globally on host systems.
*   Systemd service files must reference absolute paths pointing to localized interpreters (e.g., `ExecStart=/home/.../venv/bin/python`).

### 🛡️ Air-Gapped Data Safety
*   All document processing (PDF parsing, Word rendering, Email conversions) must occur natively in isolated terminal RAM or safe staging environments.
*   Zero client documents or case metadata may ever be transmitted to external servers.

---

*Policy Author: Antigravity AI (Lead Architect)*  
*Owner: Alan Woodyard*  
*Last Updated: 2026-05-17*  
