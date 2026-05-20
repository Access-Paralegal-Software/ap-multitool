---
id: qt_security_and_safety_audit
title: Qt Security & Safety Audit
type: ops-audit
---

# Qt Security and Safety Audit

## File Path Validation & Outputs
- **Compiler View**: Allows arbitrary OS target directory selection. Hardcodes `overwrite=True` in output spec.
  - *Risk*: A user picking an existing compiled PDF name will overwrite it silently.
  - *Fix Needed*: Add file collision check before execution.
- **Bates View**: Defaults to nested directory creation based on timestamp (`Prefix-Bates-YYYY-MM-DD`). 
  - *Safety*: Excellent, effectively prevents overwriting original documents by generating copies in isolated scope.
- **File Room View**: Checks if target root contains files before generation.
  - *Safety*: Prompts user with "Folder Contains Files" collision warning. Perfect behavior.

## Application Security (Phase 6 additions)
- **Fernet Vault**: `CASE_VAULT_FILE` successfully binds UI data to the physical device.
- **Motherboard UUID**: Local `get_machine_uuid()` implemented via WMI/subprocess safely without exposing keys to external networks.
- **Key Validation**: License validation loop successfully locks access. 

## Destructive Operations
- Queue removal in Compiler is local and non-destructive.
- No source files are modified during generation; only copies are pushed to the output engine.

## Task 9: Post-Hardening Validation Addendum
- **Overwrite Safety**: The Compiler view now explicitly intercepts output paths that collide with existing compiled PDFs, rendering a prompt: *"The file already exists... Do you want to overwrite it?"* This resolves the critical safety gap identified in Task 2.
- **Output Clarity**: All output destinations are explicitly declared in the UI path fields before execution begins.
- **License Messaging**: Trust boundaries are clean. The Vault intercept dialog prevents bypass gracefully without leaking cryptographic signatures to standard out.
