"""
APS delta sync — run before and after DNS cutover.
Skips already-copied messages via --useuid, only grabs new arrivals.
Excludes [Gmail]/All Mail (virtual, massive, all duplicates).
Safe to run multiple times.
"""
import subprocess, sys
from datetime import datetime, timezone
from google.oauth2 import service_account
import google.auth.transport.requests

SERVICE_ACCOUNT_FILE = "/root/stax-mail-migration.json"
SCOPES = ["https://mail.google.com/"]

ACCOUNTS = [
    ("alan@accessparalegalservices.com",  "d0d3HbNsy3yaLl1!C2Sz"),
    ("renee@accessparalegalservices.com", "IA!T2h7UHPvBGFJhVm2M"),
]

MAILCOW_HOST = "mail.alanwoodyard.com"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def get_token(email):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    ).with_subject(email)
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token

def delta_sync(email, password):
    user = email.split("@")[0]
    logfile = f"/var/log/imapsync_{user}_delta_{STAMP}.log"
    print(f"\n{'='*60}")
    print(f"Delta sync: {email}")
    print(f"Log: {logfile}")
    print(f"{'='*60}")

    token = get_token(email)

    cmd = [
        "imapsync",
        "--host1", "imap.gmail.com", "--port1", "993", "--ssl1",
        "--user1", email, "--oauthaccesstoken1", token,
        "--host2", MAILCOW_HOST, "--port2", "993", "--ssl2",
        "--user2", email, "--password2", password,
        "--gmail1",
        "--useuid",
        "--skipcrossduplicates",
        "--synclabels",
        "--nofoldersizes",
        "--errorsmax", "50",
        # Skip virtual Gmail folders that contain only duplicates
        "--exclude", "\\[Gmail\\]/All Mail",
        "--exclude", "\\[Gmail\\]/Spam",
        "--exclude", "\\[Gmail\\]/Trash",
        "--logfile", logfile,
    ]

    result = subprocess.run(cmd)
    ok = result.returncode == 0
    status = "OK" if ok else f"FAILED (exit {result.returncode})"
    print(f"\n{email}: {status}")
    print(f"Verify: grep 'EX_OK\\|nb_errors' {logfile}")
    return ok

if __name__ == "__main__":
    print(f"APS delta sync — {STAMP} UTC")
    print("Skips already-copied messages. Excludes Gmail virtual folders.\n")

    results = {}
    for email, pw in ACCOUNTS:
        results[email] = delta_sync(email, pw)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for email, ok in results.items():
        print(f"  {'OK' if ok else 'FAIL'}  {email}")

    if all(results.values()):
        print("\nAll accounts clean. Safe to cut DNS.")
    else:
        print("\nOne or more accounts had errors. Check logs before cutting DNS.")
        sys.exit(1)
