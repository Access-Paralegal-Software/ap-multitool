#!/usr/bin/env python3
"""
Migrate accessparalegalservices.com mailboxes from Google Workspace to Mailcow
using OAuth2 service account impersonation + imapsync.
"""
import subprocess, os
from google.oauth2 import service_account
import google.auth.transport.requests

SERVICE_ACCOUNT_FILE = "/root/stax-mail-migration.json"
SCOPES = ["https://mail.google.com/"]

ACCOUNTS = [
    ("alan@accessparalegalservices.com",  "d0d3HbNsy3yaLl1!C2Sz"),
    ("renee@accessparalegalservices.com", "IA!T2h7UHPvBGFJhVm2M"),
]

MAILCOW_HOST = "mail.alanwoodyard.com"
MAILCOW_PORT = 993

def get_oauth_token(email):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    ).with_subject(email)
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    return creds.token

def migrate(gmail_user, mailcow_pass):
    print(f"\n{'='*60}")
    print(f"Migrating: {gmail_user}")
    print(f"{'='*60}")

    token = get_oauth_token(gmail_user)

    cmd = [
        "imapsync",
        "--host1", "imap.gmail.com",
        "--port1", "993",
        "--ssl1",
        "--user1", gmail_user,
        "--oauthaccesstoken1", token,
        "--host2", MAILCOW_HOST,
        "--port2", str(MAILCOW_PORT),
        "--ssl2",
        "--user2", gmail_user,
        "--password2", mailcow_pass,
        "--gmail1",
        "--skipcrossduplicates",
        "--synclabels",
        "--nofoldersizes",
        "--logfile", f"/var/log/imapsync_{gmail_user.split('@')[0]}.log",
    ]

    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    for email, pw in ACCOUNTS:
        ok = migrate(email, pw)
        print(f"\n{'OK' if ok else 'FAILED'}: {email}")
