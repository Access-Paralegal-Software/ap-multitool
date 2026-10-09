# AP Multitool

[![Namespace](https://img.shields.io/badge/namespace-Access--Paralegal--Software-1B4F72)](https://alanwoodyard.com)
[![Stack](https://img.shields.io/badge/stack-Rust_Slint_%2B_Python_ap-1A5276)](https://alanwoodyard.com)
[![IP](https://img.shields.io/badge/IP-source__available_%7C_All_Rights_Reserved-6C3483)](https://alanwoodyard.com)

[Alan Woodyard](https://alanwoodyard.com)

## System Role

AP Multitool is the legal discovery and Bates numbering engine. It compiles emails, Word documents, and spreadsheets into production PDFs and stamps Bates serials on those pages. The work is air-gapped: the matter stays on the machine that runs the tool.

Registered tagline: air-gapped legal discovery compiler and Bates stamp workbench. Harvest maturity: working core (16,089 implementation LOC, 5,055 test LOC). The Loft's Bates ledger, audit logs, and queue ordering were absorbed into this repository.

## Audited Architecture & Runtime

uv workspace: `packages/ap-core`, `packages/doc-chameleon`, `apps/cli`, `apps/desktop`.

| Component | Stack |
| --- | --- |
| `apps/desktop-slint` | Rust 2021 binary `ap-desktop-slint`, Slint UI, `lopdf` |
| `apps/cli` | Python console script `ap` → `ap_cli.main:main` (`click`, `rich`, argparse in `main.py`) |
| `packages/ap-core` | `pypdf`, `pikepdf`, `reportlab`, `python-docx`, `openpyxl`, `cryptography`, `html2text` |
| `packages/doc-chameleon` | `doc-chameleon` CLI 0.8.0 for document conversion |
| `apps/desktop` | PySide6 desktop (`gui_apmultitool_qt.py`), beside the Slint binary |

`lopdf` is the Rust PDF path inside `ap-desktop-slint`. The Python CLI is the headless production path: merge, convert, stamp. `rayon` is named in the catalog stack for parallel page work on the native side. An offline license gate runs before dispatch (`enforce_offline_license_gate`).

## CLI / API Surface

Global flags on `ap`: `-v/--verbose`, `--silent` / `-q/--quiet`, `--json`, `--log-level {DEBUG,INFO,WARNING,ERROR}`, `--version`.

```text
ap email-to-pdf -i mail.eml -o out/ [--output-name NAME] [--no-attachments] [--grayscale]
ap merge -i <files-or-folders...> -o out/ [--output-name NAME] [--grayscale] [--dry-run]
ap docx-to-pdf -i document.docx -o out/ [--output-name NAME]
ap xlsx-to-pdf -i sheet.xlsx -o out/ [--output-name NAME]
ap bates -i document.pdf -o out/ [--prefix PROD] [--sep -] [--start-number 1] [--padding 7]
    [--position "Bottom Right"] [--font-name Helvetica] [--font-size 10] [--no-shrink] [--dry-run]
ap support-bundle [-o <dir>]
```

Bates placement choices: Bottom Right, Bottom Center, Top Center, Top Right, Top Left, Bottom Left. Default padding is 7. Default separator is `-`.

`doc-chameleon` is a second console script for format conversion samples. The only HTTP route harvested in this tree is `GET /Rotate` on a portal page, not a production API. The desktop binary is `ap-desktop-slint`.

## Operational Boundaries

Source-available. License posture: Proprietary / source-available (All Rights Reserved). Visibility in the fleet catalog is `source_available`.

Air gap: production PDFs, Bates plans, and support bundles are written to local directories. `--dry-run` prints the merge or Bates plan without writing. `--grayscale` exists for PACER-style email output. The offline license gate runs before an operation. Do not point this CLI at a remote matter store.

The Loft is archived and is not the live Bates engine. Queue ordering and audit-log behavior that used to live there now live in this repository's docs and core.
