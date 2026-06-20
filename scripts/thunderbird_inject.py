"""
Thunderbird/Betterbird prefs.js injector — Stax Mail primary accounts
Run with the client CLOSED. Makes a timestamped backup first.
Passwords are NOT injected — the client will prompt once per account on first connect.

Usage:
  python thunderbird_inject.py                  # Thunderbird (default)
  python thunderbird_inject.py --betterbird     # Betterbird
"""
import os, re, shutil, glob, sys
from datetime import datetime

ACCOUNTS = [
    ("Alan Woodyard", "alan@alanwoodyard.com"),
    ("Hello — AW.com", "hello@alanwoodyard.com"),
    ("Alan — Sail Southern", "alan@sailsouthern.com"),
    ("Info — Sail Southern", "info@sailsouthern.com"),
    ("Alan — Layline Digital", "alan@laylinedigital.com"),
    ("Info — Layline Digital", "info@laylinedigital.com"),
    ("Alan — AW.net", "alan@alanwoodyard.net"),
    ("Admin — AW.net", "admin@alanwoodyard.net"),
    ("Alan — AW.photo", "alan@alanwoodyard.photo"),
    ("Alan — Awoo Design", "alan@awoo.design"),
    ("Hello — Awoo Design", "hello@awoo.design"),
    ("Alan — Curb Appeal", "alan@curbappealdigital.com"),
    ("Info — Curb Appeal", "info@curbappealdigital.com"),
    ("Admin — Curb Appeal", "admin@curbappealdigital.com"),
    ("Post Modern Cereal", "postmoderncereal@postmoderncereal.com"),
    ("Info — Post Modern Cereal", "info@postmoderncereal.com"),
]

IMAP_HOST = "mail.alanwoodyard.com"
SMTP_HOST = "mail.alanwoodyard.com"

# ── Locate profile ───────────────────────────────────────────────────────────
client = "Betterbird" if "--betterbird" in sys.argv else "Thunderbird"
# Betterbird on Windows uses the Thunderbird profile directory
profile_base = os.path.expandvars(r"%APPDATA%\Thunderbird\Profiles")
if not os.path.exists(profile_base):
    raise SystemExit("Thunderbird/Betterbird profile directory not found.")
candidates = [p for p in glob.glob(os.path.join(profile_base, "*")) if os.path.isdir(p)]
if not candidates:
    raise SystemExit(f"No {client} profile found.")
# Betterbird uses the default-default profile; Thunderbird uses default-release
if "--betterbird" in sys.argv:
    preferred = [p for p in candidates if "default-default" in p]
else:
    preferred = [p for p in candidates if "default-release" in p]
profile_dir = preferred[0] if preferred else max(candidates, key=os.path.getmtime)
prefs_path  = os.path.join(profile_dir, "prefs.js")
print(f"Client:  {client}")
print(f"Profile: {profile_dir}")

# ── Backup ────────────────────────────────────────────────────────────────────
backup = prefs_path + f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(prefs_path, backup)
print(f"Backup:  {backup}")

with open(prefs_path, "r", encoding="utf-8") as f:
    content = f.read()

# ── Find highest existing indices ─────────────────────────────────────────────
def maxn(pat, s):
    m = re.findall(pat, s)
    return max([int(x) for x in m], default=0)

ms = maxn(r'mail\.server\.server(\d+)', content)
mi = maxn(r'mail\.identity\.id(\d+)', content)
ma = maxn(r'mail\.account\.account(\d+)', content)
mq = maxn(r'mail\.smtpserver\.smtp(\d+)', content)

ea = re.search(r'user_pref\("mail\.accountmanager\.accounts",\s*"([^"]+)"\)', content)
es = re.search(r'user_pref\("mail\.smtpservers",\s*"([^"]+)"\)', content)
existing_accounts = ea.group(1) if ea else ""
existing_smtp     = es.group(1) if es else ""

# ── Generate new entries ──────────────────────────────────────────────────────
new_lines    = ["\n// === Stax Mail accounts (auto-injected) ==="]
new_acct_ids = []
new_smtp_ids = []

for i, (display, email) in enumerate(ACCOUNTS):
    sn  = ms + i + 1
    idn = mi + i + 1
    an  = ma + i + 1
    smp = mq + i + 1
    new_acct_ids.append(f"account{an}")
    new_smtp_ids.append(f"smtp{smp}")
    local = email.split("@")[0]
    dir_suffix = f"{IMAP_HOST}-{i}" if i > 0 else IMAP_HOST
    new_lines += [
        f'user_pref("mail.server.server{sn}.type", "imap");',
        f'user_pref("mail.server.server{sn}.hostname", "{IMAP_HOST}");',
        f'user_pref("mail.server.server{sn}.port", 993);',
        f'user_pref("mail.server.server{sn}.socketType", 3);',
        f'user_pref("mail.server.server{sn}.authMethod", 3);',
        f'user_pref("mail.server.server{sn}.userName", "{email}");',
        f'user_pref("mail.server.server{sn}.name", "{display}");',
        f'user_pref("mail.server.server{sn}.login_at_startup", true);',
        f'user_pref("mail.server.server{sn}.check_new_mail", true);',
        f'user_pref("mail.server.server{sn}.directory-rel", "[ProfD]ImapMail/{dir_suffix}");',
        f'user_pref("mail.server.server{sn}.storeContractID", "@mozilla.org/msgstore/berkeleystore;1");',
        f'user_pref("mail.identity.id{idn}.fullName", "Alan Woodyard");',
        f'user_pref("mail.identity.id{idn}.useremail", "{email}");',
        f'user_pref("mail.identity.id{idn}.smtpServer", "smtp{smp}");',
        f'user_pref("mail.identity.id{idn}.valid", true);',
        f'user_pref("mail.smtpserver.smtp{smp}.hostname", "{SMTP_HOST}");',
        f'user_pref("mail.smtpserver.smtp{smp}.port", 587);',
        f'user_pref("mail.smtpserver.smtp{smp}.authMethod", 3);',
        f'user_pref("mail.smtpserver.smtp{smp}.try_ssl", 2);',
        f'user_pref("mail.smtpserver.smtp{smp}.username", "{email}");',
        f'user_pref("mail.account.account{an}.server", "server{sn}");',
        f'user_pref("mail.account.account{an}.identities", "id{idn}");',
        "",
    ]

all_accts = existing_accounts + ("," if existing_accounts else "") + ",".join(new_acct_ids)
all_smtp  = existing_smtp     + ("," if existing_smtp     else "") + ",".join(new_smtp_ids)

content = re.sub(r'user_pref\("mail\.accountmanager\.accounts",\s*"[^"]+"\);\n?', "", content)
content = re.sub(r'user_pref\("mail\.smtpservers",\s*"[^"]+"\);\n?', "", content)

with open(prefs_path, "w", encoding="utf-8") as f:
    f.write(content.rstrip() + "\n")
    f.write("\n".join(new_lines) + "\n")
    f.write(f'user_pref("mail.accountmanager.accounts", "{all_accts}");\n')
    f.write(f'user_pref("mail.smtpservers", "{all_smtp}");\n')

print(f"Done — {len(ACCOUNTS)} accounts injected.")
print(f"Open {client}. Each account will prompt for its password on first connect.")
