import os
import sys
import tempfile
import extract_msg
from bs4 import BeautifulSoup, Comment
from xhtml2pdf import pisa
import tkinter as tk
from tkinter import filedialog, messagebox
from email import policy
from email.parser import BytesParser

def clean_microsoft_html(soup):
    """
    Deep-sanitizes Microsoft HTML bloat to eliminate strict CSS parser failures.
    Strips malformed internal <style> blocks, Office XML tags, and conditional comments.
    """
    print("[Sanitizer]: Pruning Microsoft syntax artifacts...")
    
    # 1. Strip internal <style> blocks containing non-standard Microsoft Word CSS
    # (Email layouts are robustly preserved via industry-standard inline styles)
    for s in soup.find_all("style"):
        s.decompose()
        
    # 2. Strip non-standard XML namespaces and MS Office tags (e.g., <o:OfficeDocumentSettings>)
    # Standard HTML engines cannot interpret these and they disrupt document flow.
    all_tags = soup.find_all(True)
    for tag in all_tags:
        if ":" in tag.name or tag.name.startswith(('o', 'w', 'v', 'x', 'm')):
            # Instead of deleting the whole tag and losing text content,
            # we unwrap it so the raw content/subtags remain visible!
            tag.unwrap()
            
    # 3. Eliminate all HTML Comments which house dangerous conditional Office/IE blocks
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()
        
    return soup

def convert_email_to_pdf():
    """
    Dual-Engine Super-Utility to parse Outlook MSG AND standard RFC 822 EML files,
    dynamically resolve all inline images to disk, and convert perfectly to PDF.
    """
    root = tk.Tk()
    root.withdraw()
    
    email_path = filedialog.askopenfilename(
        title="Select Email File (EML or MSG)",
        filetypes=[
            ("All Email Formats", "*.eml;*.msg"),
            ("Standard Email (.eml)", "*.eml"),
            ("Outlook Message (.msg)", "*.msg")
        ]
    )
    if not email_path:
        print("[Status]: Operations aborted by user.")
        return
        
    temp_files = []
    msg_obj = None
    ext_low = os.path.splitext(email_path)[1].lower()
    
    try:
        print(f"[Initiating]: Loading {os.path.basename(email_path)}...")
        
        subj = "No Subject"
        sender = "Unknown Sender"
        to = "Unknown Recipient"
        date = "Unknown Date"
        html_body = ""
        cid_map = {}

        # ==========================================================
        # ENGINE A: DYNAMIC EML INTERPRETER (Standard / Gmail / Mac)
        # ==========================================================
        if ext_low == '.eml':
            print("[Branch]: EML RFC-822 Engine routing...")
            with open(email_path, 'rb') as f:
                msg_obj = BytesParser(policy=policy.default).parse(f)
                
            subj = str(msg_obj.get('Subject', 'No Subject'))
            sender = str(msg_obj.get('From', 'Unknown Sender'))
            to = str(msg_obj.get('To', 'Unknown Recipient'))
            date = str(msg_obj.get('Date', 'Unknown Date'))
            
            # Smart Payload Extraction
            body_part = msg_obj.get_body(preferencelist=('html', 'plain'))
            if body_part:
                html_body = body_part.get_content()
                if body_part.get_content_type() == 'text/plain':
                    # Graceful indentation wrapper
                    html_body = f"<html><body><pre style='white-space: pre-wrap; font-family: Arial, Helvetica; font-size: 12px;'>{html_body}</pre></body></html>"
            
            # Map EML Content-IDs to physical cache
            for part in msg_obj.walk():
                content_id = part.get('Content-ID')
                if content_id:
                    cid = str(content_id).strip('<>').strip()
                    payload = part.get_payload(decode=True)
                    if payload:
                        ext = ".png"
                        fn = part.get_filename() or ""
                        low_fn = fn.lower()
                        if low_fn.endswith(('.jpg', '.jpeg')): ext = ".jpg"
                        elif low_fn.endswith('.gif'): ext = ".gif"
                        elif low_fn.endswith('.bmp'): ext = ".bmp"
                        
                        tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                        tf.write(payload)
                        tf.close()
                        temp_files.append(tf.name)
                        cid_map[cid] = tf.name
                        
        # ==========================================================
        # ENGINE B: OUTLOOK MSG INTERPRETER (Microsoft Corporate OLE)
        # ==========================================================
        elif ext_low == '.msg':
            print("[Branch]: MSG Corporate OLE Engine routing...")
            msg_obj = extract_msg.Message(email_path)
            subj = msg_obj.subject or "No Subject"
            sender = msg_obj.sender or "Unknown Sender"
            to = msg_obj.to or "Unknown Recipient"
            date = msg_obj.date or "Unknown Date"
            
            if msg_obj.htmlBody:
                html_body = msg_obj.htmlBody.decode('utf-8', errors='ignore')
            elif msg_obj.body:
                html_body = f"<html><body><pre style='white-space: pre-wrap; font-family: Arial, Helvetica; font-size: 12px;'>{msg_obj.body}</pre></body></html>"
                
            if msg_obj.attachments:
                for att in msg_obj.attachments:
                    cid = att.cid
                    if not cid and hasattr(att, 'contentId'):
                        cid = att.contentId
                    if cid:
                        ext = ".png"
                        orig_name = att.longFilename or att.shortFilename or ""
                        low_name = orig_name.lower()
                        if low_name.endswith(('.jpg', '.jpeg')): ext = ".jpg"
                        elif low_name.endswith('.gif'): ext = ".gif"
                        elif low_name.endswith('.bmp'): ext = ".bmp"
                        
                        tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                        tf.write(att.data)
                        tf.close()
                        temp_files.append(tf.name)
                        cid_map[str(cid).strip('<>').strip()] = tf.name
        else:
            raise ValueError("File selection was not a recognized .eml or .msg structure.")

        # ==========================================================
        # DOM SANITIZATION & IMAGE RESOLUTION
        # ==========================================================
        print(f"[Payload]: Extracted {len(cid_map)} inline assets. Initiating DOM traversal...")
        soup = BeautifulSoup(html_body, 'html.parser')
        
        # Run enterprise-grade Microsoft Syntax Purge
        soup = clean_microsoft_html(soup)
        
        image_elements = soup.find_all('img')
        for img in image_elements:
            src = img.get('src', '')
            if src.startswith('cid:'):
                target_cid = src[4:].strip('<>').strip()
                local_path = None
                
                # Exact or fuzzy mapping to ensure maximum resilience
                for k, v in cid_map.items():
                    if target_cid in k or k in target_cid:
                        local_path = v
                        break
                
                if local_path:
                    img['src'] = local_path
                    print(f" -> Spliced resolution path for CID [{target_cid}]")
                    
        # Elegant Metadata Header Plate
        header_html = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; border-bottom: 2px solid #107C41; padding-bottom: 15px; margin-bottom: 25px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="width: 75px; font-weight: bold; font-size: 12px; color: #555; padding: 4px 0;">From:</td>
                    <td style="font-size: 12px; padding: 4px 0; color: #000;">{sender}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; font-size: 12px; color: #555; padding: 4px 0;">Sent:</td>
                    <td style="font-size: 12px; padding: 4px 0; color: #000;">{date}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; font-size: 12px; color: #555; padding: 4px 0;">To:</td>
                    <td style="font-size: 12px; padding: 4px 0; color: #000;">{to}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; font-size: 12px; color: #555; padding: 4px 0;">Subject:</td>
                    <td style="font-size: 14px; font-weight: bold; padding: 4px 0; color: #107C41;">{subj}</td>
                </tr>
            </table>
        </div>
        """
        
        final_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: letter;
                    margin: 0.5in;
                }}
                body {{
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 12px;
                    color: #333;
                    line-height: 1.4;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 10px 0;
                }}
                table {{
                    max-width: 100%;
                }}
            </style>
        </head>
        <body>
            {header_html}
            <div style="width: 100%;">
                {str(soup)}
            </div>
        </body>
        </html>
        """
        
        out_default = os.path.splitext(email_path)[0] + "_Reproduced.pdf"
        out_pdf = filedialog.asksaveasfilename(
            title="Save Reproduced Email PDF As",
            initialfile=os.path.basename(out_default),
            filetypes=[("PDF Document", "*.pdf")]
        )
        
        if not out_pdf:
            print("[Status]: File save cancelled by user.")
            return
            
        print(f"[Writing]: Delivering PDF binary matrices to {out_pdf}...")
        with open(out_pdf, "wb") as f:
            pisa_status = pisa.CreatePDF(final_html, dest=f)
            
        if pisa_status.err:
            print(f"[Warning]: PDF rendering finished with {pisa_status.err} engine anomalies.")
            
        print("[Success]: Email fully reproduced!")
        
        if messagebox.askyesno("Success", f"Email successfully reproduced to PDF!\n\nFile: {os.path.basename(out_pdf)}\n\nOpen the PDF now?"):
            try: os.startfile(out_pdf)
            except: pass
            
    except Exception as e:
        print(f"[Error]: {e}")
        messagebox.showerror("Failed", f"Email reproduction routine failed:\n\n{str(e)}")
        
    finally:
        if ext_low == '.msg' and msg_obj:
            try: msg_obj.close()
            except: pass
        for tf_path in temp_files:
            try: os.remove(tf_path)
            except: pass
        print("[Finished]: Local environment cache successfully purged.")

if __name__ == "__main__":
    convert_email_to_pdf()
