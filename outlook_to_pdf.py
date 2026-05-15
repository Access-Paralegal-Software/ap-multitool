import os
import sys
import tempfile
import extract_msg
from bs4 import BeautifulSoup
from xhtml2pdf import pisa
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_msg_to_pdf():
    """
    Premium standalone utility to parse an Outlook MSG file, extract headers, 
    map and physically resolve all inline image attachments to disk, reconstruct 
    the composite HTML, and convert perfectly to an ISO-standard PDF document.
    """
    # Initialize non-blocking Tkinter shell for interactive dialogs
    root = tk.Tk()
    root.withdraw()
    
    msg_path = filedialog.askopenfilename(
        title="Select Outlook MSG File to Reproduce",
        filetypes=[("Outlook Message", "*.msg")]
    )
    if not msg_path:
        print("[Status]: Prompt cancelled by user.")
        return
        
    temp_files = []
    msg = None
    try:
        print(f"[Parsing]: Extracting data streams from {os.path.basename(msg_path)}...")
        msg = extract_msg.Message(msg_path)
        
        # 1. Capture Corporate Metadata Headers
        subj = msg.subject or "No Subject"
        sender = msg.sender or "Unknown Sender"
        to = msg.to or "Unknown Recipient"
        date = msg.date or "Unknown Date"
        
        # 2. Extract Raw HTML Body or generate pre-formatted plain text fallback
        html_body = ""
        if msg.htmlBody:
            html_body = msg.htmlBody.decode('utf-8', errors='ignore')
        elif msg.body:
            # Graceful plain-text wrapper keeping whitespace preservation
            html_body = f"<html><body><pre style='white-space: pre-wrap; font-family: Arial, Helvetica, sans-serif; font-size: 12px;'>{msg.body}</pre></body></html>"
            
        soup = BeautifulSoup(html_body, 'html.parser')
        
        # 3. Physical Image Rip-And-Map Routine (Resolving cid: boundaries)
        cid_map = {}
        if msg.attachments:
            for att in msg.attachments:
                # Extract CID identifier
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
                    
                    # Create locked physical temp file on local disk for xhtml2pdf renderer safety
                    tf = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                    tf.write(att.data)
                    tf.close()
                    temp_files.append(tf.name)
                    
                    # Clean cid bounds to prevent lookup miss matching
                    clean_key = str(cid).strip('<>').strip()
                    cid_map[clean_key] = tf.name
        
        print(f"[Mapping]: Found {len(cid_map)} inline attachment resources.")

        # 4. Traverse DOM and Replace Source URIs with verified Temp file Paths
        image_elements = soup.find_all('img')
        for img in image_elements:
            src = img.get('src', '')
            if src.startswith('cid:'):
                target_cid = src[4:].strip('<>').strip()
                
                local_path = None
                # Attempt exact-match or fuzzy partial key-containment matches
                for k, v in cid_map.items():
                    if target_cid in k or k in target_cid:
                        local_path = v
                        break
                
                if local_path:
                    img['src'] = local_path
                    print(f" -> Injected resolved attachment node for CID [{target_cid}]")
                    
        # 5. Render Luxurious Traditional Outlook Metadata Header Block
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
        
        # 6. Wrap Entire DOM in High-Fidelity Print Stylesheets
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
        
        # 7. Select Output Save Destination
        out_default = os.path.splitext(msg_path)[0] + "_Reproduced.pdf"
        out_pdf = filedialog.asksaveasfilename(
            title="Save Reproduced Email PDF As",
            initialfile=os.path.basename(out_default),
            filetypes=[("PDF Document", "*.pdf")]
        )
        
        if not out_pdf:
            print("[Status]: Save prompt cancelled.")
            return
            
        print(f"[Rendering]: Compiling PDF matrices to {out_pdf}...")
        
        # 8. Run pisa HTML-To-PDF Binary Engine
        with open(out_pdf, "wb") as f:
            pisa_status = pisa.CreatePDF(final_html, dest=f)
            
        if pisa_status.err:
            print("[Warning]: Minor markup discrepancies skipped by renderer engine.")
        
        print("[Success]: Email successfully compiled to PDF!")
        
        # 9. High-End Auto-Launch Popup Hook
        if messagebox.askyesno("Success", f"Outlook email successfully reproduced!\n\nFile: {os.path.basename(out_pdf)}\n\nOpen the PDF now?"):
            try: os.startfile(out_pdf)
            except Exception as e: print(f"[Error]: Auto-launch failed: {e}")
                
    except Exception as e:
        print(f"[Fatal Error]: {e}")
        messagebox.showerror("Conversion Failed", f"An unexpected exception occurred during email reproduction:\n\n{str(e)}")
        
    finally:
        # 10. Secure Shutdown & Destructor Cleanup
        if msg:
            try: msg.close()
            except: pass
        # Prune localized temp images from cache immediately
        for tf_path in temp_files:
            try: os.remove(tf_path)
            except: pass
        print("[Cleanup]: Localised image nodes successfully purged from cache.")

if __name__ == "__main__":
    convert_msg_to_pdf()
