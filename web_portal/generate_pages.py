import os
import sys

# Define Matrix Dimensions
STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", 
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", 
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]

COURTS = [
    "Federal District Court", "Circuit Court", "Appellate Court", "Supreme Court", 
    "County Superior Court", "E-Filing ECF System", "PACER Upload Gateway", "Trial Joint Appendix"
]

PAIN_POINTS = {
    "bates-stamping": {
        "hook": "Flattened Bates Stamping",
        "sub": "Stop paying $300/mo for Adobe Acrobat just to Bates stamp local discovery.",
        "body": "Federal and State rules require un-editable, chronological Bates serialization. Access Paralegal Suite permanently fuses numbers into the vector layer locally on your PC.",
        "seo": "how to bates stamp pdf offline without acrobat"
    },
    "email-harvesting": {
        "hook": "Batch .MSG & .EML Attachment Ripping",
        "sub": "Tired of manually saving 500 Outlook email attachments for Joint Appendices?",
        "body": "Drag and drop your native emails. We automatically harvest all PDF attachments, generate expert cover sheets, and outline them natively.",
        "seo": "extract outlook msg attachments to pdf litigation"
    },
    "pacer-compress": {
        "hook": "High-Compression Court Size Optimizer",
        "sub": "ECF upload rejected because your color scan PDF was 40MB?",
        "body": "Toggle our High-Contrast Grayscale optimizer to compress color exhibits by up to 70% while preserving ultra-sharp text legibility.",
        "seo": "reduce pdf size for pacer e-filing federal court"
    },
    "redaction-flatten": {
        "hook": "Indelible Redaction Preservation",
        "sub": "Ensure opposing counsel cannot 'undo' your redaction blocks.",
        "body": "Privacy is paramount. Access Paralegal Suite fuses all layers, flattening the document to prevent metadata leakage and HIPAA/PII violations.",
        "seo": "how to flatten pdf redaction permanently"
    },
    "freelance-edge": {
        "hook": "The Solo & Freelancer Utility Pack",
        "sub": "Enterprise-grade legal tools priced for independent practitioners.",
        "body": "Don't let big firms with Relativity out-pace you. Bring massive litigation compiling power back to your local desktop with a lifetime software pass.",
        "seo": "software tools for freelance paralegals and legal assistants"
    }
}

def get_template(state, court, key, data):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Professional {data['hook']} built specifically for {state} {court} compliance. Download the 100% offline Access Paralegal Suite.">
    <title>{state} {court} {data['hook']} Utility | Access Paralegal Suite</title>
    <style>
        :root {{ --accent: #288F4F; --accent-hover: #1E6C3A; --silver: #F3F4F6; --dark: #1F2937; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: var(--dark); background: var(--silver); margin: 0; padding: 0; }}
        .container {{ max-width: 1000px; margin: 0 auto; padding: 2rem; }}
        .hero {{ text-align: center; padding: 4rem 1rem; background: white; border-bottom: 1px solid #E5E7EB; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
        h1 {{ font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; }}
        h1 span {{ color: var(--accent); }}
        .sub {{ font-size: 1.25rem; color: #4B5563; margin-bottom: 2rem; }}
        .desc-box {{ background: #F9FAFB; border: 1px solid #E5E7EB; padding: 2rem; border-radius: 8px; text-align: left; max-width: 600px; margin: 0 auto 3rem auto; }}
        .cta-form {{ background: white; padding: 2rem; border-radius: 12px; border: 2px solid var(--accent); text-align: center; margin: 2rem auto; max-width: 500px; }}
        .cta-form input {{ padding: 0.75rem; border: 1px solid #D1D5DB; border-radius: 6px; width: 70%; font-size: 1rem; margin-bottom: 1rem; }}
        .cta-form button {{ background: var(--accent); color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-size: 1rem; font-weight: bold; cursor: pointer; width: 75%; }}
        .cta-form button:hover {{ background: var(--accent-hover); }}
        .dls {{ display: flex; gap: 1.5rem; justify-content: center; margin-top: 4rem; flex-wrap: wrap; }}
        .dl-card {{ flex: 1; min-width: 250px; background: white; padding: 1.5rem; border-radius: 8px; text-align: center; text-decoration: none; color: inherit; border: 1px solid #E5E7EB; transition: all 0.2s; }}
        .dl-card:hover {{ border-color: var(--accent); box-shadow: 0 4px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }}
        .dl-card .ico {{ font-size: 2rem; margin-bottom: 0.5rem; display: block; }}
        .footer {{ text-align: center; margin-top: 4rem; padding: 2rem; font-size: 0.85rem; color: #6B7280; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <div>🛡️ Engineered for <strong>{state} {court}</strong></div>
            <h1>The Premier Offline <span>{data['hook']}</span></h1>
            <p class="sub">{data['sub']}</p>
            
            <div class="desc-box">
                <h3>🚀 Local & Legally Fused</h3>
                <p>{data['body']}</p>
                <p style="font-style:italic; color:#6B7280; font-size:0.9rem;">*100% local sandboxed software. Complies perfectly with state guidelines governing data ethics and PII management.</p>
            </div>

            <!-- EMAIL CAPTURE & TAGGING -->
            <div class="cta-form">
                <h3>📧 Get the {state} Compliance Setup</h3>
                <p style="font-size:0.9rem; color:#4B5563; margin-bottom:1.5rem;">Download the installer instantly and get free litigation tips.</p>
                <form action="#" method="POST" id="email-capture-form">
                    <input type="hidden" name="tags" value="SEO_{state}_{key}">
                    <input type="email" name="email" placeholder="Enter your work email" required><br>
                    <button type="submit">🔓 Unlock Free Installation</button>
                </form>
            </div>
        </div>

        <!-- DOWNLOAD BAR ACROSS BOTTOM -->
        <div class="dls">
            <a href="../Access_Paralegal_Setup_v1.3.0.exe" class="dl-card">
                <span class="ico">🪟</span>
                <h4>Windows Setup</h4>
                <span style="color:#6B7280; font-size:0.85rem;">v1.3.0 (.exe)</span>
            </a>
            <a href="../Access_Paralegal_Mac_Installer.dmg" class="dl-card">
                <span class="ico">🍏</span>
                <h4>macOS Disk Image</h4>
                <span style="color:#6B7280; font-size:0.85rem;">Apple Silicon & Intel</span>
            </a>
            <a href="../Access_Paralegal_Linux_Installer.deb" class="dl-card">
                <span class="ico">🐧</span>
                <h4>Linux Package</h4>
                <span style="color:#6B7280; font-size:0.85rem;">Ubuntu / Debian</span>
            </a>
        </div>

        <div class="footer">
            <p>Copyright &copy; 2026 Access Paralegal Services. All rights reserved.</p>
            <p>All document manipulation occurs 100% locally. Not affiliated with the {state} State Bar.</p>
        </div>
    </div>
</body>
</html>
"""

def main():
    output_dir = "web_portal/pages"
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    print(f"Executing mass matrix generation in {output_dir}...")
    
    for state in STATES:
        for court in COURTS:
            for key, data in PAIN_POINTS.items():
                # Generate URL slug
                slug_state = state.lower().replace(" ", "-")
                slug_court = court.lower().replace(" ", "-")
                filename = f"{slug_state}-{slug_court}-{key}.html"
                filepath = os.path.join(output_dir, filename)
                
                html = get_template(state, court, key, data)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html)
                
                count += 1
                
    print(f"SUCCESS! Programmatically synthesized {count} hyper-targeted SEO landing pages!")
    print(f"Accessible under 'web_portal/pages/'")

if __name__ == "__main__":
    main()
