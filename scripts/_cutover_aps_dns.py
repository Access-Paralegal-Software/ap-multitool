"""
DNS cutover for accessparalegalservices.com → Mailcow
Replaces Google MX records with Mailcow, updates SPF, pushes DKIM, updates DMARC.
"""
import requests

CF_TOKEN  = "cfut_GI3A4iVoN10RAI67mStp7Wn8xyRnEs4eCzX1XWCVec7a7aab"
MC_KEY    = "rb2hOz8Fpy5OOt0Ku6EpBOps8oWWDlp1"
ZONE_ID   = "15e699e73f5a3f3346e73a1200108a38"
DOMAIN    = "accessparalegalservices.com"
MAIL_HOST = "mail.alanwoodyard.com"
DMARC_RUA = "dmarc@alanwoodyard.com"

cf_h = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
mc_h = {"X-API-Key": MC_KEY, "Content-Type": "application/json"}

def cf_list(rtype=None, name=None):
    params = {"per_page": 100}
    if rtype: params["type"] = rtype
    if name:  params["name"] = name
    r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records", headers=cf_h, params=params)
    return r.json().get("result", [])

def cf_del(rid):
    requests.delete(f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{rid}", headers=cf_h)

def cf_add(rtype, name, content, priority=None, ttl=300):
    body = {"type": rtype, "name": name, "content": content, "ttl": ttl}
    if priority is not None: body["priority"] = priority
    r = requests.post(f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records", headers=cf_h, json=body)
    return r.json().get("success", False)

def cf_update(rid, rtype, name, content, priority=None, ttl=3600):
    body = {"type": rtype, "name": name, "content": content, "ttl": ttl}
    if priority is not None: body["priority"] = priority
    r = requests.put(f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{rid}", headers=cf_h, json=body)
    return r.json().get("success", False)

def mc_dkim(domain):
    r = requests.get(f"https://mail.alanwoodyard.com/api/v1/get/dkim/{domain}", headers=mc_h)
    return r.json().get("dkim_txt", "")

print(f"Cutting over DNS for {DOMAIN} to Mailcow...\n")

# 1. Remove all Google MX records, add Mailcow MX
print("MX records:")
for rec in cf_list("MX", DOMAIN):
    cf_del(rec["id"])
    print(f"  Removed: {rec['content']}")
ok = cf_add("MX", DOMAIN, MAIL_HOST, priority=10, ttl=300)
print(f"  Added: {MAIL_HOST} priority 10 — {'OK' if ok else 'ERR'}")

# 2. Update SPF
print("\nSPF:")
for rec in cf_list("TXT", DOMAIN):
    if "v=spf1" in rec.get("content", ""):
        ok = cf_update(rec["id"], "TXT", DOMAIN, "v=spf1 include:mailgun.org ~all", ttl=3600)
        print(f"  Updated SPF — {'OK' if ok else 'ERR'}")
        break

# 3. Push DKIM
print("\nDKIM:")
dkim_txt = mc_dkim(DOMAIN)
if dkim_txt:
    existing = cf_list("TXT", f"dkim._domainkey.{DOMAIN}")
    if existing:
        ok = cf_update(existing[0]["id"], "TXT", f"dkim._domainkey.{DOMAIN}", dkim_txt, ttl=3600)
        print(f"  Updated DKIM — {'OK' if ok else 'ERR'}")
    else:
        ok = cf_add("TXT", f"dkim._domainkey.{DOMAIN}", dkim_txt, ttl=3600)
        print(f"  Added DKIM — {'OK' if ok else 'ERR'}")
    # Remove old Google DKIM
    for rec in cf_list("TXT", f"google._domainkey.{DOMAIN}"):
        cf_del(rec["id"])
        print(f"  Removed Google DKIM")
else:
    print("  ERR: No DKIM key found in Mailcow")

# 4. Update DMARC
print("\nDMARC:")
dmarc_val = f"v=DMARC1; p=quarantine; rua=mailto:{DMARC_RUA}"
for rec in cf_list("TXT", f"_dmarc.{DOMAIN}"):
    ok = cf_update(rec["id"], "TXT", f"_dmarc.{DOMAIN}", dmarc_val, ttl=3600)
    print(f"  Updated DMARC — {'OK' if ok else 'ERR'}")
    break

# 5. Remove stale apple-domain TXT
print("\nCleaning stale records:")
for rec in cf_list("TXT", DOMAIN):
    if "apple-domain" in rec.get("content", ""):
        cf_del(rec["id"])
        print(f"  Removed apple-domain TXT")

print("\nDone. Cutover complete.")
print("Verify with: dig MX accessparalegalservices.com")
print("Send a test email to alan@accessparalegalservices.com to confirm delivery.")
