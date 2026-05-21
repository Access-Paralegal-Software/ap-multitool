---
id: windows_uninstall_behavior_beta1
title: Windows Uninstall Behavior Beta1
type: ops-manual
status: active
project: APMultitool
created_at: 2026-05-21
---

# Windows Uninstall Behavior Beta1

This note documents the intended uninstall behavior for the `v1.0.0-beta1` Windows installer.

## What uninstall removes

The Inno Setup configuration is intended to remove:

- installed application files under `%LOCALAPPDATA%\Programs\APMultitool`
- desktop shortcut if created
- Start Menu shortcuts and uninstall shortcut
- the Apps & Features uninstall entry
- the optional `PATH` entry added under `HKCU\Environment`

The uninstaller also broadcasts `WM_SETTINGCHANGE` after PATH cleanup so new shells pick up the updated environment.

## What uninstall must not remove

Uninstall must not silently delete:

- user vault data
- user-created document outputs
- exported support bundles
- arbitrary files outside the install directory

Local logs and telemetry should be treated as retained user-side diagnostics unless a future lane explicitly adds an opt-in cleanup story.

## Current installer behavior source

`packaging/windows/apmultitool_installer.iss` currently:

- installs to `{localappdata}\Programs\APMultitool`
- adds shortcuts through `[Icons]`
- optionally writes `{app}` into `HKCU\Environment\Path`
- removes the PATH entry in `CurUninstallStepChanged`

## Validation sequence

Use `docs/ops/windows_installer_validation.md` for the full:

- install
- launch
- hero flow
- support bundle export
- uninstall
- reinstall

## Leftover review rubric

After uninstall, classify leftover items as:

- acceptable retained user data
- acceptable retained logs or diagnostics
- problematic leftover installer garbage

Problematic leftovers include:

- stale shortcuts
- stale Apps & Features entries
- orphaned install-directory binaries
- broken PATH fragments

Acceptable retained items include:

- user-side telemetry JSON under the profile
- user-side local logs
- support bundles the user exported manually
