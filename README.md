# AP-Multitool

> **Local-first legal desktop workstation & command-line engine for discovery processing, court-compliant Bates stamping, document normalization, and pleading formatting.**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![Security](https://img.shields.io/badge/security-air--gapped%20%7C%20zero--telemetry-success)](#)
[![License](https://img.shields.io/badge/license-Proprietary-blue)](#license)
[![Release](https://img.shields.io/badge/version-v1.0.0-informational)](#)

---

## Executive Overview

**AP-Multitool** is an air-gapped litigation utility engineered for boutique law firms, solo trial attorneys, and litigation paralegals. It replaces brittle manual workflows and subscription-based cloud PDF portals with an offline, high-throughput desktop application and headless CLI engine.

* **100% Offline Processing:** Zero document bytes ever leave your workstation. No third-party API exposure, no cloud telemetry, and total preservation of attorney-client work product confidentiality.
* **Deterministic Bates Stamping:** High-precision vector stamping with automatic text repositioning and court-clearance margin preservation.
* **Format Normalization & Attachment Stripping:** Automated conversion of `.docx`, `.xlsx`, and MSG/EML containers into normalized litigation bundles.
* **Jurisdictional Geometry Presets:** Pre-configured margins and line allocations matching strict local and federal e-filing rules.

---

## Core Capabilities

### 1. Vector Bates Stamping (`bates`)
* **Court Clearance Presets:**
  * **Texas eFile:** Top/bottom clerk stamp isolation zones.
  * **California CRC Rule 2.111:** 28-line numbered pleading grid accommodation.
  * **Federal CM/ECF:** Bottom-right docket clearance.
* **Dynamic Geometry:** Optional affine scaling to shrink source content by 5-10%, guaranteeing stamps never obscure underlying evidentiary text or exhibit labels.
* **Audit Trail Export:** Generates deterministic CSV run logs detailing input MD5/SHA-256 hashes, assigned Bates ranges, and target output paths.

### 2. Pleading Geometry Engine (`doc-chameleon`)
* Enforces strict California CRC Rule 2.111 pleading standards (1.00" left margin, 24.0 pt line spacing, aligned 28-line numbering).
* Strips legacy printer formatting artifacts and unifies mismatched font metrics across collaborative drafts.

### 3. Headless Document Automation (`ap`)
* Single-binary execution suitable for automated batch pipelines and scheduled intake folders.
* Lossless container extraction from MSG and EML archives, isolating embedded attachments into ordered review sets.

---

## Architecture & Workspaces

The repository is structured as a dual-layer workspace:

```text
ap-multitool/
|-- apps/
|   |-- cli/                   # Headless Python/Rust CLI binaries (`ap`)
|   |-- desktop-slint/         # Native Slint/Rust high-performance desktop workstation
|   `-- desktop/               # Python/PySide6 core interfaces
|-- packages/
|   |-- ap-core/               # Stamping engine, hash verifiers, and court matrix math
|   `-- doc-chameleon/         # Pleading geometry and formatting rules
|-- assets/
|   `-- tokens/                # System Token standard branding SVGs
`-- docs/                      # Offline HTML documentation and operator manuals
