# test_gui_integration.py
"""Integration test for testing the new email compilation loop in gui_apmultitool.py."""

import os
import sys
import tempfile
import time
from pathlib import Path
import pikepdf

# Add current workspace to path
sys.path.append(str(Path(__file__).parent.parent))
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import email_processing

def main():
    print("=== APMultitool GUI Email Harvester Integration Test ===")
    
    # 1. Setup paths
    workspace = Path(__file__).parent.parent
    mock_eml = workspace / "scratch" / "test_temp" / "test_email.eml"
    
    if not mock_eml.exists():
        print("Error: Mock EML file not found! Please run test_email_processing.py first.")
        sys.exit(1)
        
    temp_dir = workspace / "scratch" / "test_temp" / "gui_integration_output"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_extract_dir = temp_dir / "_volta_temp_attachments"
    temp_extract_dir.mkdir(parents=True, exist_ok=True)
    
    final_dest = temp_dir / f"Access_Merged_Master_Test_{int(time.time())}.pdf"
    
    print(f"2. Simulating gui_apmultitool.py merger loop...")
    print(f"   Target file: {mock_eml.name}")
    print(f"   Temp extract dir: {temp_extract_dir}")
    print(f"   Output master PDF: {final_dest}")
    
    # Simulate UI settings
    var_bookmark = True
    var_grayscale = True  # Enable Grayscale compression!
    var_compress = True
    var_fit_view = True
    
    merged_pdf = pikepdf.Pdf.new()
    if var_fit_view:
        merged_pdf.Root.ViewerPreferences = pikepdf.Dictionary(FitWindow=True, CenterWindow=True, DisplayDocTitle=True)
        merged_pdf.Root.PageLayout = pikepdf.Name("/SinglePage")
        
    outline_nodes = []
    curr_pg = 0
    idx = 1
    file_path = str(mock_eml)
    low_fn = mock_eml.name.lower()
    
    # Execute identical unified compiler logic
    try:
        if low_fn.endswith(('.eml', '.msg')):
            email_path = Path(file_path)
            
            # 1. Parse unified email
            print("   - Parsing email via UnifiedEmail...")
            email_obj = email_processing.UnifiedEmail(email_path)
            print(f"     Subject: {email_obj.subject}")
            print(f"     Sender: {email_obj.sender}")
            
            # 2. Render cover PDF
            print("   - Rendering branded cover page via ReportLab...")
            cover_pdf_path = os.path.join(temp_extract_dir, f"email_cover_{int(time.time())}_{idx}.pdf")
            email_processing.email_to_pdf(email_obj, Path(cover_pdf_path), grayscale=var_grayscale)
            
            email_start_pg = curr_pg
            with pikepdf.open(cover_pdf_path) as cover:
                merged_pdf.pages.extend(cover.pages)
                curr_pg += len(cover.pages)
                
            subj = email_obj.subject or "No Subject"
            email_type_str = "Email" if low_fn.endswith('.eml') else "Outlook"
            email_outline = pikepdf.OutlineItem(f"📧 {email_type_str}: {subj[:50]}", destination=email_start_pg, page_location="Fit")
            
            # 3. Process attachments
            print("   - Process attachments & convert to PDF...")
            extracted_attachments = []
            a_idx = 0
            for fname, data, ct in email_processing.get_email_attachments(email_obj, keep_inline=True):
                raw_p = os.path.join(temp_extract_dir, f"raw_{idx}_{a_idx}_{fname}")
                with open(raw_p, 'wb') as raw_f:
                    raw_f.write(data)
                    
                pdf_p = os.path.join(temp_extract_dir, f"conv_{idx}_{a_idx}_{fname}.pdf")
                att_low = str(fname).lower()
                
                # First try the offline email_processing converter
                success = email_processing.attachment_to_pdf(
                    data, fname, Path(pdf_p), ct, grayscale=var_grayscale
                )
                
                # Check for standard Word/Excel/Txt fallbacks if ReportLab fails
                if not success or not os.path.exists(pdf_p):
                    if att_low.endswith('.txt'):
                        # Using text conversion logic
                        with open(raw_p, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read()
                        doc = email_processing._new_doc(Path(pdf_p))
                        story = [email_processing.Paragraph(email_processing.xml_escape(content), email_processing.BODY_STYLE)]
                        doc.build(story)
                        success = True
                        
                if success and os.path.exists(pdf_p):
                    extracted_attachments.append((fname, pdf_p))
                a_idx += 1
                
            print(f"     Found and converted {len(extracted_attachments)} attachments.")
            
            for o_name, p_path in extracted_attachments:
                a_start = curr_pg
                with pikepdf.open(p_path) as src:
                    merged_pdf.pages.extend(src.pages)
                    curr_pg += len(src.pages)
                email_outline.children.append(pikepdf.OutlineItem(f"📎 {o_name}", destination=a_start, page_location="Fit"))
                
            if var_bookmark:
                outline_nodes.append(email_outline)
                
        # Save master portfolio
        if var_bookmark and outline_nodes:
            with merged_pdf.open_outline() as outline:
                outline.root.extend(outline_nodes)
                
        merged_pdf.save(str(final_dest), linearize=True, compress_streams=var_compress)
        merged_pdf.close()
        
        print("\n3. Verifying output master PDF...")
        assert final_dest.exists(), "Final merged PDF was not saved!"
        
        # Open final and verify pages and structure
        with pikepdf.open(final_dest) as final:
            total_pages = len(final.pages)
            print(f"   -> Final PDF Pages: {total_pages}")
            assert total_pages >= 3, f"Expected at least 3 pages (Cover + 2 attachments), found {total_pages}"
            
            # Verify outline structure
            outline = final.open_outline()
            assert len(outline.root) == 1, "Expected exactly 1 main email bookmark"
            email_node = outline.root[0]
            print(f"   -> Bookmark Title: {email_node.title}")
            assert "Email: Access Paralegal Test Subject" in email_node.title, f"Unexpected title: {email_node.title}"
            
            print(f"   -> Children Bookmarks Count: {len(email_node.children)}")
            assert len(email_node.children) == 3, f"Expected 3 attachment bookmarks, found {len(email_node.children)}"
            print(f"      - Child 1: {email_node.children[0].title}")
            print(f"      - Child 2: {email_node.children[1].title}")
            print(f"      - Child 3: {email_node.children[2].title}")
            assert "test_inline.png" in email_node.children[0].title
            assert "test_att.png" in email_node.children[1].title
            assert "test_att.txt" in email_node.children[2].title
            
        print("\n=== SUCCESS: Integration compile & validation test passed! ===")
        
        # Cleanup temporary files
        for f in os.listdir(temp_extract_dir):
            try: os.remove(os.path.join(temp_extract_dir, f))
            except: pass
        try: os.rmdir(temp_extract_dir)
        except: pass
        
    except Exception as e:
        print(f"\nERROR: Integration loop failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
