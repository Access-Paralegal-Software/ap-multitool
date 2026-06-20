import requests, secrets, string

MAILCOW_BASE = "https://mail.alanwoodyard.com/api/v1"
MAILCOW_KEY  = "rb2hOz8Fpy5OOt0Ku6EpBOps8oWWDlp1"
mc_h = {"X-API-Key": MAILCOW_KEY, "Content-Type": "application/json"}
DOMAIN = "accessparalegalservices.com"

def gen_pw(length=20):
    alpha = string.ascii_letters + string.digits
    while True:
        core = "".join(secrets.choice(alpha) for _ in range(length - 1))
        pos  = secrets.randbelow(length - 1)
        pw   = core[:pos] + "!" + core[pos:]
        if (any(c.isupper() for c in pw) and
                any(c.islower() for c in pw) and
                any(c.isdigit() for c in pw)):
            return pw

MAILBOXES = [
    ("renee",  "Renee Perez"),
    ("alan",   "Alan Woodyard"),
    ("admin",  "Admin"),
]

ALIASES = [
    ("info",       f"alan@{DOMAIN}"),
    ("postmaster", f"alan@{DOMAIN}"),
    ("abuse",      f"alan@{DOMAIN}"),
    ("security",   f"alan@{DOMAIN}"),
    ("noreply",    "dmarc@alanwoodyard.com"),
    (f"@{DOMAIN}", f"alan@{DOMAIN}"),  # catch-all
]

print("Creating mailboxes...\n")
credentials = []
for local, name in MAILBOXES:
    pw = gen_pw()
    r = requests.post(f"{MAILCOW_BASE}/add/mailbox", headers=mc_h, json={
        "local_part": local, "domain": DOMAIN, "name": name,
        "password": pw, "password2": pw, "quota": "10240",
        "active": "1", "force_pw_update": "0",
        "tls_enforce_in": "0", "tls_enforce_out": "0",
    })
    res = r.json()
    ok = isinstance(res, list) and res and res[0].get("type") == "success"
    print(f"  {local}@{DOMAIN:<35} {'OK' if ok else 'ERR: ' + str(res)}")
    credentials.append((f"{local}@{DOMAIN}", pw, ok))

print("\nCreating aliases...\n")
for local, goto in ALIASES:
    addr = local if local.startswith("@") else f"{local}@{DOMAIN}"
    r = requests.post(f"{MAILCOW_BASE}/add/alias", headers=mc_h, json={
        "address": addr, "goto": goto, "active": "1"
    })
    res = r.json()
    ok = isinstance(res, list) and res and res[0].get("type") == "success"
    print(f"  {addr:<45} -> {goto:<40} {'OK' if ok else 'ERR: ' + str(res)}")

print("\n" + "=" * 65)
print("CREDENTIALS")
print("=" * 65)
for addr, pw, ok in credentials:
    if ok:
        print(f"  {addr:<45} {pw}")
