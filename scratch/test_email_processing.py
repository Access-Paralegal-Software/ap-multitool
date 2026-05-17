# test_email_processing.py
"""Automated verification test for email_processing.py."""

import os
import sys
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from PIL import Image, ImageDraw

# Add current workspace to path
sys.path.append(str(Path(__file__).parent.parent))
import email_processing

def create_mock_assets(tmp_dir: Path):
    # 1. Create a dummy image
    img = Image.new("RGB", (200, 100), color=(255, 0, 0)) # Red block
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 190, 90], outline=(0, 255, 0), width=3) # Green border
    img_path = tmp_dir / "test_inline.png"
    img.save(img_path)
    
    # 2. Create another dummy image for attachment
    img_att_path = tmp_dir / "test_att.png"
    img.save(img_att_path)
    
    # 3. Create dummy text file
    txt_path = tmp_dir / "test_att.txt"
    txt_path.write_text("Hello from the text attachment!\nLine 2 of attachment.", encoding="utf-8")
    
    return img_path, img_att_path, txt_path

def create_mock_eml(eml_path: Path, inline_img_path: Path, att_img_path: Path, att_txt_path: Path):
    msg = MIMEMultipart("mixed")
    msg["Subject"] = "Access Paralegal Test Subject ⚖️"
    msg["From"] = "sender@accessparalegalservices.com"
    msg["To"] = "client@domain.com"
    msg["CC"] = "paralegal@accessparalegalservices.com"
    msg["Date"] = "Sun, 17 May 2026 02:15:00 -0500"
    
    # Create related container for body + inline images
    msg_related = MIMEMultipart("related")
    msg.attach(msg_related)
    
    # HTML body referencing the inline image
    html = """
    <html>
      <body>
        <h1 style="color: #67BE5E;">Access Email Harvester Test</h1>
        <p>This is a test of the premium ReportLab email to PDF rendering system.</p>
        <p>Here is an inline image:</p>
        <img src="cid:inline_image_cid">
        <p>And here is some footer text.</p>
      </body>
    </html>
    """
    msg_related.attach(MIMEText(html, "html"))
    
    # Attach inline image
    with open(inline_img_path, "rb") as f:
        mime_img = MIMEImage(f.read(), name="test_inline.png")
        mime_img.add_header("Content-ID", "<inline_image_cid>")
        mime_img.add_header("Content-Disposition", "inline", filename="test_inline.png")
        msg_related.attach(mime_img)
        
    # Attach files
    with open(att_img_path, "rb") as f:
        img_part = MIMEImage(f.read(), name="test_att.png")
        img_part.add_header("Content-Disposition", "attachment", filename="test_att.png")
        msg.attach(img_part)
        
    with open(att_txt_path, "rb") as f:
        txt_part = MIMEText(f.read().decode(), "plain")
        txt_part.add_header("Content-Disposition", "attachment", filename="test_att.txt")
        msg.attach(txt_part)
        
    with open(eml_path, "wb") as f:
        f.write(msg.as_bytes())

def main():
    print("=== Access Email Attachment Harvester Test ===")
    tmp_dir = Path(__file__).parent / "test_temp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    eml_path = tmp_dir / "test_email.eml"
    out_dir = tmp_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("1. Creating mock assets and attachments...")
    inline_img, att_img, att_txt = create_mock_assets(tmp_dir)
    
    print("2. Generating test EML file...")
    create_mock_eml(eml_path, inline_img, att_img, att_txt)
    print(f" -> EML file generated: {eml_path}")
    
    # Test A: Color Mode
    print("\n3. Processing EML (Color Mode)...")
    out_color = email_processing.process_email(eml_path, out_dir, grayscale=False)
    print(f" -> Created color PDF: {out_color}")
    assert out_color.exists(), "Color PDF was not generated!"
    print(f" -> Size: {out_color.stat().st_size} bytes")
    
    # Test B: Grayscale Mode
    print("\n4. Processing EML (PACER Grayscale Mode)...")
    out_gray = email_processing.process_email(eml_path, out_dir, grayscale=True)
    print(f" -> Created grayscale PDF: {out_gray}")
    assert out_gray.exists(), "Grayscale PDF was not generated!"
    print(f" -> Size: {out_gray.stat().st_size} bytes")
    
    print("\n=== SUCCESS: All automated email processor tests passed! ===")
    
if __name__ == "__main__":
    main()
