import os

TEMPLATES = {
    "Squarespace_A1_Value_Local.html": """<!-- HOOK: Own Your Software / Cost Savings -->
<div class="access-landing-block" style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1F2937; padding: 3rem 1.5rem; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); max-width: 800px; margin: auto;">
    <div style="text-align: center;">
        <span style="color: #288F4F; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem;">💼 Stop Renting Adobe DC Pro</span>
        <h2 style="font-size: 2.25rem; font-weight: 800; margin: 0.5rem 0 1rem 0; line-height: 1.2;">The Elite Local Alternative to Enterprise Monthly Fees</h2>
        <p style="font-size: 1.1rem; color: #4B5563; max-width: 600px; margin: 0 auto 2rem auto;">Why pay $300 a year forever? Own your legal toolbox. One price. Infinite merges. 100% local.</p>
    </div>
    <div style="background: #F3F4F6; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
        <ul style="margin: 0; padding-left: 1.25rem; line-height: 1.7;">
            <li><strong>Indelible Bates Stamping:</strong> Vector-fused directly into your PDF streams.</li>
            <li><strong>Email Ripping:</strong> Drag-and-drop harvesting of .MSG & .EML attachments.</li>
            <li><strong>Court Size Optimizer:</strong> Compress exhibits up to 70% for E-Filing.</li>
        </ul>
    </div>
    <!-- EMAIL CAPTURE -->
    <form action="#" style="text-align: center; background: #EBF8F1; padding: 1.5rem; border-radius: 8px; border: 1px solid #A7F3D0;">
        <h4 style="margin: 0 0 0.5rem 0; color: #065F46;">Get the Access Paralegal Suite Demo</h4>
        <p style="font-size: 0.85rem; margin: 0 0 1rem 0;">Includes our "E-Filing Optimization Guide"</p>
        <input type="email" placeholder="Work Email" required style="padding: 0.75rem; border: 1px solid #C4B5FD; border-radius: 4px; width: 60%; margin-bottom: 1rem;"><br>
        <button style="background: #288F4F; color: white; border: none; padding: 0.75rem 2rem; font-weight: bold; border-radius: 4px; cursor: pointer; width: 60%;">🔓 Get Free Download</button>
    </form>
</div>""",

    "Squarespace_B1_Fear_Privacy.html": """<!-- HOOK: Avoid Cloud Security Malpractice -->
<div class="access-landing-block" style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1F2937; padding: 3rem 1.5rem; background: #FFFFFF; border: 2px solid #EF4444; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); max-width: 800px; margin: auto;">
    <div style="text-align: center;">
        <span style="color: #DC2626; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem;">⚠️ Zero Cloud. Zero Malpractice Risk.</span>
        <h2 style="font-size: 2.25rem; font-weight: 800; margin: 0.5rem 0 1rem 0; line-height: 1.2;">Stop Uploading Confidential Client Data to the Web</h2>
        <p style="font-size: 1.1rem; color: #4B5563; max-width: 600px; margin: 0 auto 2rem auto;">Online converters sell your data and leak PII metadata. Safeguard your firm with a 100% air-gapped, local PC compiler.</p>
    </div>
    <div style="background: #FEF2F2; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; border: 1px solid #FEE2E2;">
        <p style="margin: 0; font-weight: bold; color: #991B1B; font-size: 0.95rem;">🔒 The HIPAA & NALA Local Promise:</p>
        <ul style="margin: 0.5rem 0 0 0; padding-left: 1.25rem; line-height: 1.7;">
            <li><strong>Air-Gapped Sandbox:</strong> 0% internet requirement to merge or Bates stamp.</li>
            <li><strong>Indelible Redaction:</strong> Fuses and flattens layers so opposing counsel can't peek.</li>
            <li><strong>No Subscriptions:</strong> 100% independent code operating solely on your hardware.</li>
        </ul>
    </div>
    <!-- EMAIL CAPTURE -->
    <form action="#" style="text-align: center; background: #F3F4F6; padding: 1.5rem; border-radius: 8px;">
        <h4 style="margin: 0 0 0.5rem 0;">Request Encrypted Download Token</h4>
        <input type="email" placeholder="Your Secure Email" required style="padding: 0.75rem; border: 1px solid #D1D5DB; border-radius: 4px; width: 60%; margin-bottom: 1rem;"><br>
        <button style="background: #1F2937; color: white; border: none; padding: 0.75rem 2rem; font-weight: bold; border-radius: 4px; cursor: pointer; width: 60%;">🛡️ Download Secure Installer</button>
    </form>
</div>""",

    "Squarespace_A2_Social_Review.html": """<!-- HOOK: Built by Paralegals -->
<div class="access-landing-block" style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1F2937; padding: 3rem 1.5rem; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; max-width: 800px; margin: auto;">
    <div style="text-align: center;">
        <span style="color: #2563EB; font-weight: bold; text-transform: uppercase; font-size: 0.85rem;">⭐ Recommending by Top Freelance Specialists</span>
        <h2 style="font-size: 2.25rem; font-weight: 800; margin: 0.5rem 0 1rem 0; line-height: 1.2;">Built by Real Paralegals Who Know the Grind</h2>
        <p style="font-size: 1.1rem; color: #4B5563; max-width: 600px; margin: 0 auto 2.5rem auto;">"I saved 14 hours of EML conversion in my first trial prep week." — Modernized litigation automation at your fingertips.</p>
    </div>
    <!-- Quote Card -->
    <div style="border-left: 4px solid #288F4F; padding: 1rem 1.5rem; background: #F9FAFB; border-radius: 0 8px 8px 0; margin-bottom: 2rem; font-style: italic;">
        "The big firms use Relativity. Independent contractors couldn't compete until Access Paralegal Suite. Now I harvest 500 email attachments in 1 minute."
    </div>
    <!-- EMAIL CAPTURE -->
    <form action="#" style="text-align: center; background: #EBF8F1; padding: 1.5rem; border-radius: 8px; border: 1px solid #A7F3D0;">
        <h4 style="margin: 0 0 1rem 0;">Join 500+ High-Productivity Virtual Assistants</h4>
        <input type="email" placeholder="Paralegal Email" required style="padding: 0.75rem; border: 1px solid #C4B5FD; border-radius: 4px; width: 60%; margin-bottom: 1rem;"><br>
        <button style="background: #288F4F; color: white; border: none; padding: 0.75rem 2rem; font-weight: bold; border-radius: 4px; cursor: pointer; width: 60%;">Get Started Free</button>
    </form>
</div>""",

    "Squarespace_B2_Product_Speed.html": """<!-- HOOK: Tech Specs & Raw Speed -->
<div class="access-landing-block" style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1F2937; padding: 3rem 1.5rem; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; max-width: 800px; margin: auto;">
    <div style="text-align: center;">
        <span style="color: #288F4F; font-weight: bold; text-transform: uppercase; font-size: 0.85rem;">⚡ High-Speed Reconstructive Engine</span>
        <h2 style="font-size: 2.25rem; font-weight: 800; margin: 0.5rem 0 1rem 0; line-height: 1.2;">Compile 1,000 Court Pages In Less Than 3 Seconds</h2>
        <p style="font-size: 1.1rem; color: #4B5563; max-width: 600px; margin: 0 auto 2rem auto;">No loading spinners. No browser timeouts. True multi-threaded desktop acceleration built for massive trial datasets.</p>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
        <div style="border: 1px solid #E5E7EB; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #288F4F;">0ms</div>
            <div style="font-size: 0.8rem; color: #6B7280;">Upload Waiting Time</div>
        </div>
        <div style="border: 1px solid #E5E7EB; padding: 1rem; border-radius: 8px; text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #288F4F;">100%</div>
            <div style="font-size: 0.8rem; color: #6B7280;">Local Device Utilization</div>
        </div>
    </div>
    <!-- EMAIL CAPTURE -->
    <form action="#" style="text-align: center; background: #F3F4F6; padding: 1.5rem; border-radius: 8px;">
        <h4 style="margin: 0 0 1rem 0;">Unlock Hyper-Speed Compiling</h4>
        <input type="email" placeholder="Email Address" required style="padding: 0.75rem; border: 1px solid #D1D5DB; border-radius: 4px; width: 60%; margin-bottom: 1rem;"><br>
        <button style="background: #288F4F; color: white; border: none; padding: 0.75rem 2rem; font-weight: bold; border-radius: 4px; cursor: pointer; width: 60%;">Download Access Paralegal Suite (Beta)</button>
    </form>
</div>""",

    "Squarespace_A3_Bates_Flatten.html": """<!-- FEATURE HOOK: Bates Stamping Focus -->
<div class="access-landing-block" style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1F2937; padding: 3rem 1.5rem; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; max-width: 800px; margin: auto;">
    <div style="text-align: center;">
        <span style="color: #D97706; font-weight: bold; text-transform: uppercase; font-size: 0.85rem;">🔢 Permanent Bates Fusing</span>
        <h2 style="font-size: 2.25rem; font-weight: 800; margin: 0.5rem 0 1rem 0; line-height: 1.2;">Vector-Fused Bates Stamping That Cannot Be Undone</h2>
        <p style="font-size: 1.1rem; color: #4B5563; max-width: 600px; margin: 0 auto 2rem auto;">Standard PDF editors add "annotations" which are easily deleted by opposing counsel. Our engine fuses text directly to the content layer.</p>
    </div>
    <ul style="line-height: 2; margin-bottom: 2rem;">
        <li>✅ Auto-generated <strong>eDiscovery CSV Load Files</strong></li>
        <li>✅ Dynamic Alphanumeric Padding (000001)</li>
        <li>✅ Deep-vector metadata flattening & security</li>
    </ul>
    <!-- EMAIL CAPTURE -->
    <form action="#" style="text-align: center; background: #FFFBEB; padding: 1.5rem; border-radius: 8px; border: 1px solid #FDE68A;">
        <h4 style="margin: 0 0 1rem 0; color: #92400E;">Start Free Bates Serializing</h4>
        <input type="email" placeholder="Enter Work Email" required style="padding: 0.75rem; border: 1px solid #D1D5DB; border-radius: 4px; width: 60%; margin-bottom: 1rem;"><br>
        <button style="background: #D97706; color: white; border: none; padding: 0.75rem 2rem; font-weight: bold; border-radius: 4px; cursor: pointer; width: 60%;">🔓 Download Bates Utility</button>
    </form>
</div>""",

    "Squarespace_B3_Email_Harvester.html": """<!-- FEATURE HOOK: Email attachment Harvesting -->
<div class="access-landing-block" style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; color: #1F2937; padding: 3rem 1.5rem; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; max-width: 800px; margin: auto;">
    <div style="text-align: center;">
        <span style="color: #059669; font-weight: bold; text-transform: uppercase; font-size: 0.85rem;">📧 The Attachment Harvesting Core</span>
        <h2 style="font-size: 2.25rem; font-weight: 800; margin: 0.5rem 0 1rem 0; line-height: 1.2;">Stop "Right-Clicking" Outlook Attachments Manually</h2>
        <p style="font-size: 1.1rem; color: #4B5563; max-width: 600px; margin: 0 auto 2rem auto;">Feed us .MSG or .EML files. We rip the PDF attachments, auto-format professional correspondence cover sheets, and nest them into a table of contents instantly.</p>
    </div>
    <div style="background: #F0FDF4; border: 1px solid #DCFCE7; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
        <strong>🕒 Time-Tracking Stats:</strong> Batch extracting 200 Outlook emails manually takes 2.5 hours. Access Paralegal Suite does it in <strong>12 seconds.</strong>
    </div>
    <!-- EMAIL CAPTURE -->
    <form action="#" style="text-align: center; background: #F3F4F6; padding: 1.5rem; border-radius: 8px;">
        <h4 style="margin: 0 0 1rem 0;">Download the Attachment Harvester</h4>
        <input type="email" placeholder="Email Address" required style="padding: 0.75rem; border: 1px solid #D1D5DB; border-radius: 4px; width: 60%; margin-bottom: 1rem;"><br>
        <button style="background: #059669; color: white; border: none; padding: 0.75rem 2rem; font-weight: bold; border-radius: 4px; cursor: pointer; width: 60%;">Download Now</button>
    </form>
</div>"""
}

def main():
    out_dir = "web_portal/squarespace_ab_tests"
    os.makedirs(out_dir, exist_ok=True)
    for name, html in TEMPLATES.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(html)
    print(f"SUCCESS: Created 6 A/B Code Injection landing pages in '{out_dir}'!")

if __name__ == "__main__":
    main()
