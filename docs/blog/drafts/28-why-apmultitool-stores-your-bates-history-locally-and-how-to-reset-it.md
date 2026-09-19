# Why APMultitool Stores Your Bates History Locally (And How to Reset It)

*Pillar: Product Deep-Dive | Target keyword: Bates stamp history local storage reset paralegal software*

---

The Bates Registry Ledger — APMultitool's offline tracking system for Bates numbers — persists your stamping history across sessions. When you return to a prefix you've used before, the registry suggests the correct next number automatically.

This is a feature that solves a real problem: duplicate Bates numbers across productions. But how the registry works, where it stores data, and how to manage it when you need to — these are worth understanding for any paralegal who relies on it as part of their production workflow.

## Where the Registry Data Lives

The Bates Registry is stored as a local file on your machine — not in the cloud, not on a server, not in a shared location. It lives in the application's data directory on your Windows system.

This has several implications:

**It's private.** The registry contains information about the case prefixes you've worked with and the numbers you've issued. Storing this locally means it never leaves your machine — consistent with the application's offline-first design philosophy.

**It's machine-specific.** If you use APMultitool on two different computers, each machine has its own registry. The registries do not sync automatically. If you move a case to a different machine, you'll need to account for the registry state on the new machine (see the override section below).

**It persists between sessions.** The registry data survives closing and reopening the application, restarting the machine, and updating the software. It's not session data — it's a persistent record.

## How the Auto-Suggestion Works

When you type a Bates prefix into the stamping configuration:

1. APMultitool checks the registry for that exact prefix
2. If the prefix exists, the "Start Index" field auto-populates with the next number in sequence — one higher than the last number issued for that prefix
3. If the prefix doesn't exist, the Start Index defaults to 1

The auto-suggestion is exactly that — a suggestion. You review it before proceeding, and you can override it if needed.

## When to Trust It and When to Verify

For most same-machine, same-case productions, the auto-suggestion is correct and can be trusted as a starting point. For productions where any of the following are true, verify the suggestion against your independent records before proceeding:

- You've used APMultitool on a different machine for any prior production on this case
- A production was run and then cancelled (the registry may have updated even if a full output wasn't produced)
- There's been any disruption to the machine — a factory reset, a new operating system install, a migration to new hardware
- You're resuming work on a case that was inactive for several months

Your independent record is the audit log from the previous production session. Open it, find the last Bates number in the sequence, and confirm the registry suggestion matches.

## How to Reset or Override the Registry

**Single-prefix override:** For any individual stamping session, click into the Start Index field and type the number you want to start from. The registry will update based on the numbers you actually issue in that session — it tracks what's been stamped, not what was auto-suggested.

**Full registry reset:** If you need to clear the registry entirely — for example, when setting up the application fresh on a new machine, or after a significant workflow change — the registry file can be located in the application's local data directory and deleted or edited. The application will regenerate an empty registry on the next launch.

Note: resetting the registry does not affect your historical audit logs, which are stored as separate files in your chosen output locations. Your production history is preserved in the audit logs regardless of registry state.

## Best Practice: Registry + Audit Log Working Together

The most reliable Bates management workflow uses the registry and audit logs in tandem:

- **Registry:** Provides the auto-suggested next number for each prefix
- **Audit log:** Provides the authoritative record of what was actually stamped in each session

Before any new production: check the auto-suggestion, verify against the prior audit log, proceed if they agree.

If they ever disagree, investigate before proceeding. They should always agree.

---

**APMultitool's offline Bates Registry keeps your numbering accurate across sessions, entirely on your machine.** [Download the Windows beta](https://download.accessparalegalservices.com/ap-multitool/windows/APMultitool-windows-beta.exe) and see how automatic Bates tracking changes your production workflow.

*More details in the [FAQ](https://software.accessparalegalservices.com/faq.html) or email info@accessparalegalservices.com.*
