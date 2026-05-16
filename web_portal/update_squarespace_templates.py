import os

# Base CSS and Header for all Squarespace Injections
V3_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@700;800&display=swap');
    
    .sqs-access-block {
        font-family: 'Inter', -apple-system, sans-serif;
        color: #111827;
        background: #F9FAFB;
        border-radius: 32px;
        padding: 4rem 2rem;
        max-width: 900px;
        margin: 2rem auto;
        position: relative;
        overflow: hidden;
        border: 1px solid #E5E7EB;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
    }
    
    .sqs-access-glass {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        padding: 2.5rem;
        border-radius: 24px;
        margin: 2rem 0;
    }
    
    .sqs-access-badge {
        display: inline-block;
        padding: 0.5rem 1.25rem;
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #288F4F;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .sqs-access-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 1.5rem;
        letter-spacing: -0.02em;
    }
    
    .sqs-access-title span {
        background: linear-gradient(135deg, #288F4F, #1E6C3A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sqs-access-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .sqs-access-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid #E5E7EB;
    }
    
    .sqs-access-card span { font-size: 2rem; display: block; margin-bottom: 0.5rem; }
    
    .sqs-access-btn {
        background: #111827;
        color: white;
        text-decoration: none;
        padding: 1.25rem 2.5rem;
        border-radius: 14px;
        font-weight: 800;
        display: inline-block;
        transition: all 0.3s;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    
    .sqs-access-btn:hover { transform: translateY(-2px); box-shadow: 0 15px 40px rgba(0,0,0,0.15); }
</style>
"""

TEMPLATES = {
    "Squarespace_A1_Value_Local.html": {
        "badge": "💼 STOP RENTING ADOBE DC PRO",
        "title": "The Elite Local Alternative to <span>Enterprise Monthly Fees</span>",
        "sub": "Why pay $300 a year forever? Own your legal toolbox. One price. Infinite merges. 100% local.",
        "points": ["<strong>Indelible Bates Stamping:</strong> Vector-fused directly into your PDF streams.", "<strong>Email Ripping:</strong> Drag-and-drop harvesting of .MSG & .EML attachments.", "<strong>Court Size Optimizer:</strong> Compress exhibits up to 70% for E-Filing."],
        "cta": "Get Your Lifetime Founder Pass"
    },
    "Squarespace_B1_Fear_Privacy.html": {
        "badge": "⚠️ AVOID CLOUD SECURITY MALPRACTICE",
        "title": "Stop Uploading <span>Confidential Client Data</span> to the Web",
        "sub": "Online converters sell your data and leak PII metadata. Safeguard your firm with a 100% air-gapped, local PC compiler.",
        "points": ["<strong>Air-Gapped Sandbox:</strong> 0% internet requirement to merge or Bates stamp.", "<strong>Indelible Redaction:</strong> Fuses and flattens layers so opposing counsel can't peek.", "<strong>No Subscriptions:</strong> 100% independent code operating solely on your hardware."],
        "cta": "Download Secure Offline Installer"
    },
    "Squarespace_B2_Product_Speed.html": {
        "badge": "⚡ ZERO LATENCY. ZERO FRICTION.",
        "title": "Legal Document Compiling at the <span>Speed of Thought</span>",
        "sub": "Stop waiting for cloud uploads. Process 5,000 pages of discovery in seconds, not hours.",
        "points": ["<strong>Instant Local Rendering:</strong> No lag, no buffering, just raw performance.", "<strong>Multi-Threaded Merging:</strong> Harness your workstation's power to audit PDFs.", "<strong>Verified E-Filing:</strong> Automated compliance checks for Federal & State ECF."],
        "cta": "Unlock Pro Speed Access"
    }
}

def generate():
    output_dir = "web_portal/squarespace_ab_tests"
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, data in TEMPLATES.items():
        points_html = "".join([f"<li>{p}</li>" for p in data['points']])
        html = f"""{V3_STYLE}
<div class="sqs-access-block">
    <div style="text-align: center;">
        <div class="sqs-access-badge">{data['badge']}</div>
        <h2 class="sqs-access-title">{data['title']}</h2>
        <p style="font-size: 1.15rem; color: #4B5563; max-width: 700px; margin: 0 auto;">{data['sub']}</p>
    </div>
    
    <div class="sqs-access-glass">
        <ul style="margin: 0; padding-left: 1.25rem; line-height: 1.8; font-size: 1.05rem;">
            {points_html}
        </ul>
    </div>
    
    <div style="text-align: center;">
        <div class="sqs-access-grid">
            <div class="sqs-access-card"><span>🪟</span><div style="font-weight:700;font-size:0.85rem;">Windows</div></div>
            <div class="sqs-access-card"><span>🍏</span><div style="font-weight:700;font-size:0.85rem;">macOS</div></div>
            <div class="sqs-access-card"><span>🐧</span><div style="font-weight:700;font-size:0.85rem;">Linux</div></div>
        </div>
        <br>
        <a href="https://software.accessparalegalservices.com" class="sqs-access-btn">{data['cta']}</a>
        <p style="font-size: 0.75rem; color: #9CA3AF; margin-top: 1.5rem;">Access Paralegal Multitool v1.0.0 • Verified Zero-Cloud Standard</p>
    </div>
</div>
"""
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            f.write(html)
    print("SUCCESS: Updated Squarespace Core Templates with V3 Premium Design.")

if __name__ == "__main__":
    generate()
