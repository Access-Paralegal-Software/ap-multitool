import os
import sys

# Matrix Dimensions: 50 States x 4 Court Levels x 5 Case Specs = 1000 base locations.
# Campaign 1 (Original) has 5 keys per location = 5000.
# Campaign 2 (Psychology) has 5 keys per location = 5000.
# Total = 10,000 unique pages.

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
COURTS = ["Federal District Court", "County Circuit Court", "State Supreme Court", "Appellate Division"]
SPECIALTIES = ["Personal Injury", "Family & Divorce Law", "Corporate & Commercial", "Trusts & Estates", "Criminal Defense"]

ORIGINAL_POINTS = {
    "bates": {"hook": "Flattened Bates Stamping", "sub": "Stop paying for Adobe just to Bates stamp.", "body": "Permanently fuse numbers into the vector layer locally."},
    "email": {"hook": "Batch Attachment Ripping", "sub": "Stop manually saving attachments.", "body": "Automatically harvest all PDF attachments from .MSG & .EML."},
    "pacer": {"hook": "Court Size Optimizer", "sub": "ECF upload rejected?", "body": "Compress exhibits by up to 70% while preserving text."},
    "flatten": {"hook": "Redaction Preservation", "sub": "Stop Opposing Counsel from undoing your work.", "body": "Fuses all layers to prevent metadata leakage."},
    "solo": {"hook": "The Freelancer Utility Pack", "sub": "Enterprise tools for independent practitioners.", "body": "Bring massive litigation power to your local desktop."}
}

NEW_CAMPAIGN_POINTS = {
    "grind": {"mode": "icons", "hook": "Daily Grind Fix", "sub": "Does it slow down your day when discovery piles up?", "body": "Stop wasting hours on manual document prep. Access Paralegal Multitool automates the legal friction away."},
    "power": {"mode": "icons", "hook": "Legal Powerhouse", "sub": "The elite legal automation suite for modern paralegals.", "body": "Touting high-performance local AI engines to audit, merge, and serialize your cases in seconds."},
    "fix": {"mode": "text", "hook": "The Solution", "sub": "Tired of software that makes your life harder?", "body": "Fix your discovery workflow complaints instantly with the Multitool. It does what it says, offline, forever."},
    "life": {"mode": "text", "hook": "Freedom Pack", "sub": "Get your weekends back.", "body": "How much free time would you have if document production took 5 minutes instead of 5 hours? reclaim your life."},
    "legal": {"mode": "text", "hook": "The Paralegal Standard", "sub": "Handcrafted for top-tier legal departments.", "body": "100% Offline Forensic Integrity. The Multitool is the zero-cloud alternative to enterprise monthly fees."}
}

BASE_URL = "https://software.accessparalegalservices.com/pages/"

def get_template(state, court, spec, key, data, show_icons=True):
    header_html = f"""
    <nav style="display: flex; justify-content: space-between; align-items: center; padding: 2rem 0;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <img src="../assets/silver_seal_premium.png" style="height: 80px; width: auto;">
            <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.02em; display: none;">
                ACCESS PARALEGAL <span style="color: #288F4F;">MULTITOOL</span>
            </div>
        </div>
        <div style="background: white; padding: 6px 16px; border-radius: 99px; border: 1px solid #E5E7EB; font-weight: 700; font-size: 0.85rem; color: #288F4F;">💎 v1.0.0 Stable</div>
    </nav>
    """
    
    if show_icons:
        dl_section = """<div class="grid">
            <a href="../Access_Paralegal_Multitool_Setup_v1.0.0.exe" class="dl-card"><span class="ico">🪟</span><h4 style="font-family:'Outfit';margin:0;font-size:1.25rem;">Windows</h4><p style="color:#6B7280;font-size:0.85rem;margin:0.5rem 0;">Enterprise Setup (.exe)</p><div style="margin-top:1rem;font-size:0.75rem;font-weight:600;color:var(--accent);background:var(--accent-glow);display:inline-block;padding:2px 8px;border-radius:4px;">v1.0.0 Stable</div></a>
            <a href="../Access_Paralegal_Mac_Installer.dmg" class="dl-card"><span class="ico">🍏</span><h4 style="font-family:'Outfit';margin:0;font-size:1.25rem;">macOS</h4><p style="color:#6B7280;font-size:0.85rem;margin:0.5rem 0;">Universal DMG</p><div style="margin-top:1rem;font-size:0.75rem;font-weight:600;color:#4B5563;background:#F3F4F6;display:inline-block;padding:2px 8px;border-radius:4px;">Universal</div></a>
            <a href="../Access_Paralegal_Linux_Installer.deb" class="dl-card"><span class="ico">🐧</span><h4 style="font-family:'Outfit';margin:0;font-size:1.25rem;">Linux</h4><p style="color:#6B7280;font-size:0.85rem;margin:0.5rem 0;">.DEB Package</p><div style="margin-top:1rem;font-size:0.75rem;font-weight:600;color:#4B5563;background:#F3F4F6;display:inline-block;padding:2px 8px;border-radius:4px;">Debian/Ubuntu</div></a>
        </div>"""
    else:
        dl_section = """<div style="margin-top:3rem;">
            <a href="../Access_Paralegal_Multitool_Setup_v1.0.0.exe" style="display:block;max-width:400px;margin:0 auto;text-decoration:none;text-align:center;background:#111827;color:white;padding:1.5rem;border-radius:16px;font-weight:800;font-size:1.25rem;box-shadow:0 10px 30px rgba(0,0,0,0.15);">🛡️ SECURE DOWNLOAD LINK (v1.0.0 Stable)</a>
            <p style="text-align:center;color:#6B7280;font-size:0.85rem;margin-top:1rem;">Verified Malware-Free • No Cloud Account Required</p>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Professional {data['hook']} optimized for {state} {court} {spec} litigation requirements. 100% offline.">
    <title>{state} {court} {spec} {data['hook']} | Access Paralegal Multitool</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@700;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --accent: #288F4F; --accent-glow: rgba(40, 143, 79, 0.2); --dark: #111827; --glass: rgba(255, 255, 255, 0.85); --silver: #F9FAFB; }}
        body {{ font-family: 'Inter', sans-serif; color: var(--dark); background: var(--silver); margin: 0; line-height: 1.6; }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 2rem; }}
        .hero {{ padding: 4rem 1rem; text-align: center; background: radial-gradient(circle at top right, #EBF8F1, white); }}
        h1 {{ font-family: 'Outfit', sans-serif; font-size: 3rem; font-weight: 800; margin: 1rem 0; }}
        h1 span {{ background: linear-gradient(135deg, #288F4F, #1E6C3A); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .badge {{ display: inline-block; padding: 0.5rem 1.25rem; background: white; border: 1px solid #E5E7EB; border-radius: 9999px; font-weight: 600; font-size: 0.875rem; margin-bottom: 1rem; }}
        .glass-card {{ background: var(--glass); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.4); padding: 2.5rem; border-radius: 24px; text-align: left; max-width: 700px; margin: 0 auto 4rem auto; box-shadow: 0 20px 40px rgba(0,0,0,0.05); }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 3rem; }}
        .dl-card {{ background: white; padding: 2rem; border-radius: 20px; text-align: center; text-decoration: none; color: inherit; border: 1px solid #E5E7EB; transition: all 0.3s; }}
        .dl-card:hover {{ border-color: var(--accent); transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.05); }}
        .dl-card .ico {{ font-size: 2.5rem; margin-bottom: 1rem; display: block; }}
        .footer {{ text-align: center; padding: 4rem 2rem; font-size: 0.875rem; color: #9CA3AF; }}
    </style>
</head>
<body>
    <div class="container">
        {header_html}
        <div class="hero">
            <div class="badge">🛡️ {state} {court} COMPLIANT</div>
            <h1>Offline <span>{data['hook']}</span></h1>
            <p style="font-size:1.35rem;color:#4B5563;margin-bottom:3rem;">{data['sub']}</p>
            <div class="glass-card">
                <h3 style="font-family:'Outfit';margin-top:0;">🚀 Handcrafted for {spec}</h3>
                <p>{data['body']}</p>
            </div>
            {dl_section}
        </div>
        <div class="footer"><p>&copy; 2026 Access Paralegal Services. 100% Offline Forensic Integrity.</p></div>
    </div>
</body></html>"""

def generate_sitemap_xml(filenames):
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for fn in filenames: xml_lines.append(f'  <url><loc>{BASE_URL}{fn}</loc><changefreq>monthly</changefreq></url>')
    xml_lines.append('</urlset>')
    return "\n".join(xml_lines)

def main():
    output_dir = "web_portal/pages"
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    all_filenames = []
    
    # Original Loop (5000)
    for state in STATES:
        for court in COURTS:
            for spec in SPECIALTIES:
                for key, data in ORIGINAL_POINTS.items():
                    fn = f"{state.lower().replace(' ','-')}-{court.lower().replace(' ','-')}-{spec.lower().replace(' ','-').replace('&','and')}-{key}.html"
                    with open(os.path.join(output_dir, fn), "w", encoding="utf-8") as f: f.write(get_template(state, court, spec, key, data, True))
                    all_filenames.append(fn); count += 1

    # Psychology Loop (5000)
    for state in STATES:
        for court in COURTS:
            for spec in SPECIALTIES:
                for key, data in NEW_CAMPAIGN_POINTS.items():
                    fn = f"{state.lower().replace(' ','-')}-{court.lower().replace(' ','-')}-{spec.lower().replace(' ','-').replace('&','and')}-v4-{key}.html"
                    with open(os.path.join(output_dir, fn), "w", encoding="utf-8") as f: f.write(get_template(state, court, spec, key, data, data['mode']=='icons'))
                    all_filenames.append(fn); count += 1

    with open("web_portal/sitemap.xml", "w", encoding="utf-8") as sf: sf.write(generate_sitemap_xml(all_filenames))
    print(f"SUCCESS! Synthesized {count} SEO landing pages!")

if __name__ == "__main__": main()
