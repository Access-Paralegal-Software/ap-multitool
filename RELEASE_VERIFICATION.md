# AP-Multitool Release Integrity & Local Verification

This document provides checksum custody records, zero-network architectural boundaries, and a 3-minute local evaluation walkthrough for **AP-Multitool v1.0.0** on Windows x64 (`x86_64-pc-windows-msvc`).

**Scope Notice:** AP-Multitool is a local document compilation, PDF merge, and vector Bates numbering workbench. Access Paralegal Software makes no claim of e-discovery certification, third-party forensic certification, or court approval. Operators remain responsible for checking stamped page geometry, confidentiality prefixes, and loadfile delimiters against matter-specific production orders before service.

---

## 1. Binary Integrity & Custody Block

Release binaries are compiled locally into `dist\` and `apps\desktop-slint\target\release\`. Both directories are excluded from Git tracking in `.gitignore`. Verify any downloaded or locally built Windows x64 artifact against the byte sizes and SHA-256 digests below.

| Artifact | Role | Exact Size | Verified SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `ap-multitool-v1.0.0-windows-x64.exe` | Native Rust 2021 + Slint GUI workstation (`ap-desktop-slint.exe`, `lopdf`, `rayon`) | `16,217,600` bytes (`15.47 MiB`) | `7F308FAAC383D8331D58852B8A4F2D122C8DFBF4E7F510783AFFDF074694D4E4` |
| `ap.exe` | Standalone headless CLI bundle (Python 3.12 PyInstaller build) | `35,401,530` bytes (`33.76 MiB`) | `DD4CC558D8586ED3FD34FCDA308DBF044BD71CE3D3365337510FB89D6E3A12D2` |
| `AP-Multitool-v1.0-Win64.zip` | Combined Windows x64 workstation + CLI archive | `42,260,571` bytes (`40.30 MiB`) | `3C89025220E393A069310D8154AF57B79B2B9EF3B67CA2ADAA5FF85D59DB3AFC` |

### Checksum Verification Commands (PowerShell)

```powershell
# Verify staged Windows x64 workstation binary, headless CLI binary, and release archive
Get-FileHash -Algorithm SHA256 `
  .\dist\ap-multitool-v1.0.0-windows-x64.exe, `
  .\dist\ap.exe, `
  .\dist\AP-Multitool-v1.0-Win64.zip | Format-List Algorithm, Hash, Path

# Confirm exact byte lengths
Get-Item .\dist\ap-multitool-v1.0.0-windows-x64.exe, .\dist\ap.exe, .\dist\AP-Multitool-v1.0-Win64.zip |
  Select-Object Name, Length
```

If you compile the Rust workstation from source (`cd apps\desktop-slint && cargo build --release`), run `Get-FileHash -Algorithm SHA256 .\apps\desktop-slint\target\release\ap-desktop-slint.exe` to record the hash of your local build.

### Zero-Network-Calls Architectural Statement

All document intake, DOCX/XLSX/EML conversion (`python-docx`, `openpyxl`, `reportlab`), PDF merging (`pypdf`, `pikepdf`), vector Bates stamping (`lopdf` 95% affine page scale with `+36.0 pt` vertical shift in `ap-desktop-slint`), and CSV/loadfile export execute strictly against local filesystem paths. Neither `ap-desktop-slint` nor the `ap` CLI opens network sockets, transmits document metadata, or runs background telemetry during batch processing. Matter files never leave the host machine.

### Offline Activation & Licensing Notes

* **Zero-Network Headless & Evaluation Gate (`v1.0.0`):** On first run, `ap-multitool-v1.0.0-windows-x64.exe` starts in a local 14-day evaluation mode with no network call required. In the Python CLI (`apps/cli/src/ap_cli/main.py`), `enforce_offline_license_gate()` calls `evaluate_offline_access()` (`packages/ap-core/src/ap_core/licensing.py`), which evaluates only the local trial clock and the local SHA-256-signed entitlement cache (`~/.access_paralegal_entitlement.json` in `ap-desktop-slint`; Windows `MachineGuid`-bound cache in `ap-core`, 7-day offline cache freshness window). Alpha evaluation keys (`scripts/generate_eval_keys.py`) use offline HMAC-SHA256 Base32 tokens.
* **Optional Desktop Network Actions:** Network activity in `v1.0.0` occurs only if an operator explicitly triggers online raw-key verification (`verify_license_online`) or opens the external purchase page from the license badge while unactivated.
* **Ed25519 Offline Signature Roadmap:** Detached Ed25519 public-key signature verification for offline license files is planned for a future release so commercial seat activation can occur on permanently disconnected hosts without initial online key exchange. `v1.0.0` uses the local SHA-256 / HMAC-SHA256 cache verification described above.

---

## 2. 3-Minute Local Evaluation Walkthrough ($0 Synthetic Fixtures)

You can evaluate offline conversion, Bates stamping, and loadfile output in under three minutes at `$0` cost using synthetic matter fixtures included in this repository.

### Step 1: Verify Synthetic Matter Fixtures (`demo_production/` and `tests/fixtures/`)

On `master`, synthetic input documents live under `tests\fixtures\` (`raw_exhibit.pdf`, `conversion\simple_text.docx`, `conversion\simple_spreadsheet.xlsx`).

The pre-compiled synthetic `demo_production/` discovery volume and Concordance/Opticon loadfile generator (`scripts/demo_loadfile_production.py`, `doc_chameleon.bates.loadfile`) are isolated on local branch `feat/modular-legal-packages` (commit `68cc6def`). That volume contains five verified files:

* `demo_production/DATA/VOL0001.dat` (UTF-8 Concordance metadata loadfile using thorn `U+00FE` text qualifiers and `U+0014` field delimiters)
* `demo_production/DATA/VOL0001.opt` (Opticon 7-field page-to-image cross-reference for `VOL0001`)
* `demo_production/DATA/VOL0001.csv` (attorney-review summary CSV)
* `demo_production/IMAGES/ACME_001001 _CONF_Employment_Contract.pdf` (3 stamped pages, `2,965` bytes, `ACME_001001 _CONF` to `ACME_001003 _CONF`; note the space before `_CONF` in this branch fixture)
* `demo_production/IMAGES/ACME_001004 _CONF_Email_Chain_Breach.pdf` (2 stamped pages, `2,155` bytes, `ACME_001004 _CONF` to `ACME_001005 _CONF`)

Export `demo_production/` into gitignored `scratch\demo_production` without switching branches:

```powershell
New-Item -ItemType Directory -Force -Path .\scratch\eval_out | Out-Null
git archive --format=zip -o .\scratch\demo_production.zip 68cc6def demo_production
Expand-Archive -Force .\scratch\demo_production.zip -DestinationPath .\scratch
Get-ChildItem -Recurse -File .\scratch\demo_production | Select-Object FullName, Length
```

### Step 2: Run Offline Transformation & Bates Stamping (`master` CLI or Workstation)

Preview the Bates stamping plan (`--dry-run`), then stamp a synthetic PDF offline using the staged standalone CLI (`.\dist\ap.exe`):

```powershell
# 1. Dry-run Bates layout plan (writes zero files, zero network I/O)
.\dist\ap.exe --json bates `
  -i .\tests\fixtures\raw_exhibit.pdf `
  -o .\scratch\eval_out `
  --prefix ACME --sep _ --start-number 1001 --padding 6 --dry-run

# 2. Execute offline vector Bates stamping
.\dist\ap.exe --json --silent bates `
  -i .\tests\fixtures\raw_exhibit.pdf `
  -o .\scratch\eval_out `
  --output-name ACME_001001_CONF_Exhibit.pdf `
  --prefix ACME --sep _ --start-number 1001 --padding 6
```

Expected JSON output (`exit_code: 0`):

```json
{
  "status": "success",
  "job_id": "0a3db30f-d373-4f22-90ee-5ffd6d7c6c00",
  "operation": "bates_stamp",
  "outputs": [
    "scratch\\eval_out\\ACME_001001_CONF_Exhibit.pdf"
  ],
  "page_count": 1,
  "error": null
}
```

To test the native Slint GUI workstation instead, launch `.\dist\ap-multitool-v1.0.0-windows-x64.exe`, click **Add Files**, select PDFs from `.\scratch\demo_production\IMAGES` or `.\tests\fixtures\`, set your Bates prefix and starting serial, and run batch processing. Stamped PDFs and `production_index.csv` are written locally to `Stamped_Production\`.

### Step 3: Verify Bates Continuity and Loadfile Integrity

Inspect the exported `VOL0001.dat`, `VOL0001.opt`, and `VOL0001.csv` records in `.\scratch\demo_production\DATA` to confirm continuous 5-page serial numbering (`ACME_001001 _CONF` through `ACME_001005 _CONF`) and Concordance delimiters (`U+00FE` thorn, `U+0014` field separator):

```powershell
# Inspect CSV summary and Opticon 7-field page cross-reference
Get-Content .\scratch\demo_production\DATA\VOL0001.csv
Get-Content .\scratch\demo_production\DATA\VOL0001.opt

# Confirm 36 thorn qualifiers (U+00FE) and 15 field delimiters (U+0014) across 3 rows in VOL0001.dat
$dat = Get-Content -Raw -Encoding UTF8 .\scratch\demo_production\DATA\VOL0001.dat
"Thorn (U+00FE) count: $(($dat.ToCharArray() | Where-Object { [int]$_ -eq 0xFE }).Count); Delimiter (U+0014) count: $(($dat.ToCharArray() | Where-Object { [int]$_ -eq 0x14 }).Count)"
```

---

## 3. Automated Test Suite Verification

Run both repository test suites locally without modifying licensing state:

```powershell
# Python workspace unit and integration suite (ap-core, doc-chameleon, cli, desktop)
.\.venv\Scripts\python.exe -m pytest -q

# Native Rust Slint workstation crate build and test target
Push-Location .\apps\desktop-slint
cargo test
Pop-Location
```
