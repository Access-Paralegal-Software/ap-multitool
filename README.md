> **STAX Format** ? Lifecycle: `Active ? Building` ? Security: `Strong` ? [Governance](.orchestration/agent-instructions.md)

# âï¸ APMultitool


> [!IMPORTANT]
> **ð¤ FOR AI AGENTS, CODING COMPANIONS, AND AUTOMATED SYSTEMS:**
> This repository is governed by the **STAX Operating System**. Before taking *any* action, analyzing files, or proposing modifications, you **must** read and strictly adhere to:
> 1. [ops/soul.md](ops/soul.md) (Philosophical Compass)
> 2. [ops/agent-rules.md](ops/agent-rules.md) (Enforceable Rules & the 7-Step Sequence)
>
> You are required to run through the **Inventory â Summarize â Classify â Propose â Implement â Update Docs â Archive Leftovers** sequence for every run.



> **APMultitool** (Access Paralegal Multitool) is a professional, local-first legal document manipulation workbench engineered for paralegals and independent legal support specialists.

APMultitool acts as an offline, sovereign craftsman's utility suite. Unlike cloud tools that compromise attorney-client privilege, 100% of all operations occur locally, in-memory on the operator's machine.

---

## ðï¸ Repository Index & Navigation

This repository is organized in accordance with **STAX Fleet Rules**:

*   **`gui_apmultitool.py`**: Central CustomTkinter graphical workbench shell.
*   **[`core/`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/core/)**: Headless document manipulation engine and pure python operations.
*   **[`docs/`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/docs/)**: Detailed product, architectural, and operational manuals:
    *   **[`ARCHITECTURE.md`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/docs/ARCHITECTURE.md)**: Software layer stack, DocEngine abstractions, and technology rationale.
    *   **[`UI_SPEC.md`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/docs/UI_SPEC.md)**: Frosted glass themes, custom HSL styling palettes, and widget specifications.
    *   **[`BUG_HUNTER_MANUAL.md`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/docs/Bug_Hunter_Manual.md)**: Product manual, QA checklist, and lifetime license activation guide.
    *   **[`docs/handoffs/`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/docs/handoffs/)**: Rolling session history and project manager logs.
*   **[`tests/`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/tests/)**: Integration and regression scenario tests.
*   **[`scratch/`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/scratch/)**: Cleaned sandbox region for testing, licensing keygens, and experiment stubs.
*   **[`archive/`](file:///c:/Users/aewoo/Desktop/Repos/Access_Paralegal_PDF_Merger/archive/)**: Preserved legacy converters and out-of-scope utilities.

---

## 🔑 Licensing & Revenue Protection (Paywall v1)

APMultitool enforces a secure, startup-gated licensing framework (v1) to protect professional features:

### Licensing Verification Flow:
1. **Online Verification**: On license activation, the app securely posts the license key and machine-bound hardware fingerprint to the verify server endpoint.
2. **Offline Local Cache**: If activated, the app stores a signed local entitlement representation at `~/.access_paralegal_entitlement.json`. The cache:
   - Includes cryptographic integrity signatures (`last_verified_at` included in HMAC seed) to prevent manual tampering.
   - Restricts utility exclusively to the original hardware fingerprint (`wmic csproduct get uuid` or system platform combination).
   - Expires automatically per server-configured duration bounds.
3. **Startup Gating**: Invalid, expired, suspended, or tampered cached licenses block the application from loading, prompting an activation dialogue box.

### Webhook Flow (Purchase to Reuse):
```
[Purchase Checkout] ──(HTTP POST Event)──> [Webhook Handler (Port 8080)]
                                               │
                                       (Verify Signature)
                                               │
                                     [Keygen Provider API]
                                               │
                                        (Issue License)
                                               │
                                     [Customer Activation]
                                               │
                                      (Offline Local Reuse)
```
- **Webhook Events Supported**: `checkout.paid`, `payment.success`, `license.created`
- **Signature Security**: Request payloads verified via HMAC-SHA256 signature verification matching `APM_WEBHOOK_SHARED_SECRET`.

### Configuration Variables:
Set the following options in your local environment or system settings:
*   `APM_LICENSE_VERIFY_URL`: Endpoint to verify license keys online.
*   `APM_LICENSE_PUBLIC_KEY`: Public key used for verifying signed license tokens.
*   `APM_LICENSE_OFFLINE_GRACE_DAYS`: Number of days a verified license can run offline without re-validating online (default: `7`).
*   `APM_KEYGEN_ACCOUNT_ID`: Keygen.sh developer account identifier.
*   `APM_KEYGEN_PRODUCT_TOKEN`: Keygen.sh product token used to authorize webhook license issuance.
*   `APM_WEBHOOK_SHARED_SECRET`: SHA256 shared secret key used to verify inbound webhook signatures.

---

*System State: STAX ALIGNED | Security: 100% OFFLINE LOCAL FORENSIC INTEGRITY*

