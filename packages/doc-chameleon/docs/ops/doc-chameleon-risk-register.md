---
id: doc-chameleon-risk-register
title: Risk Register
type: risk-management
status: active
project: doc-chameleon
created: 2026-05-20
---

# Risk Register — doc-chameleon

> This register should be reviewed and updated at the start of each STAX batch. New risks should be added as discovered.

---

## Risk Matrix

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R01 | Word compatibility and editability drift | Medium | High | Use standard OpenXML specs only. Build regression test suite with canonical documents. |
| R02 | California line-number fragility | High | High | Lock line-heights in style definitions. Emit warnings on conflicting page setups. |
| R03 | Local-rule variation in Texas | High | Medium | Statewide baseline only at MVP. Clearly warn users output reflects statewide rules. Reserve overlay architecture. |
| R04 | State-rule update lag | Medium | High | Implement Rules Monitoring Plan. Display "Last Verified" dates prominently. Require manual approval before rule-pack release. |
| R05 | Over-automation risk | Medium | Medium | Default to human review. Warn on unhandled structures (complex tables, images, embedded objects). |
| R06 | User trust and review burden | Low | High | Emphasize in UI and exported report that tool assists formatting; final compliance review is user's responsibility. |
| R07 | Platform fragmentation | Low | Medium | Standardize on Python CLI core. Limit initial OS targets to primary audience (Windows). Add macOS and Linux after MVP validation. |
| R08 | Web-app scope creep | Low | High | Strict STAX guardrails. Do not architect for web app. Web is not planned. |

---

## Risk Detail Notes

### R01 — Word Compatibility and Editability Drift
Different versions of Microsoft Word, LibreOffice, and other word processors interpret OpenXML inconsistently. A document that looks correct in Word on Windows may reflow in LibreOffice on Linux. Regression testing with real document samples is critical before releasing any jurisdiction pack.

### R02 — California Line-Number Fragility
This is the highest-risk technical operation in the product. California Rule 2.108 requires numbered lines aligned with body text on every page. Achieving this in an editable Word document — rather than a printed layout — requires locking font size, line-height, and margin simultaneously. Any post-conversion edit by the user (e.g., changing font size) can visually break alignment even if the structural XML is technically correct.

**Mitigation note:** Consider adding an explicit disclaimer in the conversion report that line-number alignment should be verified after any font or margin changes.

### R03 — Local-Rule Variation in Texas
Texas practice varies meaningfully by county and court. If users assume the tool handles their specific local rules, they may file non-compliant documents. This is a trust and liability risk, not just a technical one.

**Mitigation note:** The TX statewide baseline module must prominently state its scope. Do not imply local coverage at MVP.

### R04 — State-Rule Update Lag
Court formatting rules change periodically. A jurisdiction pack that is months out of date poses a real compliance risk for users. The Rules Monitoring Plan addresses the workflow, but the risk must remain prominent.

### R05 — Over-Automation Risk
Complex input documents (heavily styled, table-heavy, image-rich) may not be safely transformable. Attempting to transform them silently and producing corrupt or mis-formatted output is worse than failing loudly.

**Mitigation note:** The validator step must produce a clear, readable warning report. The engine should refuse to silently destroy content it cannot handle.

### R06 — User Trust and Review Burden
If users over-trust the tool, they may skip final review before filing. This is both a product risk (reputational) and a real-world risk (client harm). Legal posture language must be prominent.

### R07 — Platform Fragmentation
The core user base is likely on Windows. macOS and Linux are in scope but lower priority. Tablet support is later still. Trying to build for all platforms simultaneously will fragment effort.

### R08 — Web-App Scope Creep
The offline-first mandate exists for client confidentiality reasons. Any drift toward a web-based SaaS model would undermine this core value proposition and create compliance risk for users handling privileged documents.
