import requests

CF_TOKEN = "cfut_GI3A4iVoN10RAI67mStp7Wn8xyRnEs4eCzX1XWCVec7a7aab"
h = {"Authorization": f"Bearer {CF_TOKEN}"}
DOMAIN = "accessparalegalservices.com"

r = requests.get("https://api.cloudflare.com/client/v4/zones", headers=h, params={"name": DOMAIN})
zones = r.json().get("result", [])
if not zones:
    print("Zone not found")
else:
    zone_id = zones[0]["id"]
    print(f"Zone ID: {zone_id}\n")
    r2 = requests.get(f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records", headers=h, params={"per_page": 100})
    for rec in sorted(r2.json().get("result", []), key=lambda x: x["type"]):
        print(f"{rec['type']:<8} {rec['name']:<45} {str(rec.get('priority','')):<5} {rec['content'][:70]:<70} TTL:{rec['ttl']}")
