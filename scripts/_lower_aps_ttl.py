import requests

CF_TOKEN = "cfut_GI3A4iVoN10RAI67mStp7Wn8xyRnEs4eCzX1XWCVec7a7aab"
h = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
ZONE_ID = "15e699e73f5a3f3346e73a1200108a38"

r = requests.get(f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records", headers=h, params={"per_page": 100})
records = r.json().get("result", [])

mx_records = [rec for rec in records if rec["type"] == "MX"]
print(f"Lowering TTL on {len(mx_records)} MX records to 300...")

for rec in mx_records:
    res = requests.put(
        f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{rec['id']}",
        headers=h,
        json={"type": rec["type"], "name": rec["name"], "content": rec["content"],
              "priority": rec["priority"], "ttl": 300}
    )
    ok = res.json().get("success", False)
    print(f"  {'OK' if ok else 'ERR'} MX {rec['priority']:>3}  {rec['content']}")

print("\nDone. MX TTL is now 300 seconds (5 min). Wait ~1 hour before cutting over.")
