import os
import re
import csv
import shutil
import pikepdf

class BatesExporter:
    def __init__(self, target_dir, output_root_dir, reconciliation_results):
        self.target_dir = target_dir
        self.output_root_dir = output_root_dir
        self.results = reconciliation_results

    def run_export(self, progress_callback=None):
        """Export reassembled files, exceptions, Concordance DAT files, and Opticon OPT page logs."""
        if os.path.exists(self.output_root_dir):
            try:
                shutil.rmtree(self.output_root_dir)
            except Exception:
                pass
        os.makedirs(self.output_root_dir, exist_ok=True)

        # Group matches by original document path
        doc_pages = {}
        for r in self.results:
            key = r["file_subpath"]
            if key not in doc_pages:
                doc_pages[key] = []
            doc_pages[key].append(r)

        total_docs = len(doc_pages)
        
        # Load files buffers
        dat_records = []
        opt_records = []

        for d_idx, (rel_path, pages) in enumerate(doc_pages.items(), start=1):
            if progress_callback:
                progress_callback(f"Compiling {os.path.basename(rel_path)}", d_idx / total_docs)

            # Sort pages naturally by page label (e.g. Page 1, Page 2)
            pages.sort(key=lambda x: int(re.search(r"\d+", x["page_label"]).group() if re.search(r"\d+", x["page_label"]) else 0))

            src_path = os.path.join(self.target_dir, rel_path)
            if not os.path.exists(src_path):
                continue

            sub_dir, fname = os.path.split(rel_path)
            f_base, f_ext = os.path.splitext(fname)

            has_bates = any(p["bates_number"] != "N/A" for p in pages)
            missing_pages = [p for p in pages if p["bates_number"] == "N/A"]

            # 1. Reconstruct Bates PDF (ONLY numbered pages)
            dst_bates_path = None
            if has_bates and f_ext.lower() == ".pdf":
                dst_bates_dir = os.path.join(self.output_root_dir, sub_dir)
                os.makedirs(dst_bates_dir, exist_ok=True)
                dst_bates_path = os.path.join(dst_bates_dir, f"{f_base} (Bates){f_ext}")
                
                try:
                    src_pdf = pikepdf.Pdf.open(src_path)
                    dst_pdf = pikepdf.Pdf.new()
                    
                    for p in pages:
                        if p["bates_number"] != "N/A":
                            p_num = int(re.search(r"\d+", p["page_label"]).group())
                            dst_pdf.pages.append(src_pdf.pages[p_num - 1])
                            
                    dst_pdf.save(dst_bates_path)
                    dst_pdf.close()
                    src_pdf.close()
                except Exception:
                    pass

            # 2. Reconstruct Exceptions Folder & Missing Extract File
            if missing_pages:
                exceptions_dir = os.path.join(self.output_root_dir, "exceptions", sub_dir)
                os.makedirs(exceptions_dir, exist_ok=True)
                dst_missing_path = os.path.join(exceptions_dir, f"{f_base}-missing{f_ext}")
                
                if f_ext.lower() == ".pdf":
                    try:
                        src_pdf = pikepdf.Pdf.open(src_path)
                        dst_missing_pdf = pikepdf.Pdf.new()
                        for p in missing_pages:
                            p_num = int(re.search(r"\d+", p["page_label"]).group())
                            dst_missing_pdf.pages.append(src_pdf.pages[p_num - 1])
                        dst_missing_pdf.save(dst_missing_path)
                        dst_missing_pdf.close()
                        src_pdf.close()
                    except Exception:
                        pass
                else:
                    try:
                        shutil.copy2(src_path, dst_missing_path)
                    except Exception:
                        pass

            # 3. Create Concordance DAT metadata record
            matched_bates_nums = [p["bates_number"] for p in pages if p["bates_number"] != "N/A"]
            if matched_bates_nums:
                # E-Discovery standard metadata fields
                bates_start = matched_bates_nums[0]
                bates_end = matched_bates_nums[-1]
                dat_records.append({
                    "DocID": f_base,
                    "BatesStart": bates_start,
                    "BatesEnd": bates_end,
                    "PageCount": len(matched_bates_nums),
                    "OriginalPath": rel_path,
                    "MD5Hash": pages[0]["md5"] or "",
                    "Status": "Complete" if not missing_pages else "Partial Omission"
                })

            # 4. Create Opticon OPT image log records
            # Columns: ImageKey, VolumeName, PathToImage, DocumentBreak, FolderBreak, BoxBreak, PageCount
            if matched_bates_nums and dst_bates_path:
                rel_dst_bates = os.path.relpath(dst_bates_path, self.output_root_dir).replace("\\", "/")
                
                # First page of the document has DocumentBreak = "Y" and the total PageCount
                opt_records.append({
                    "ImageKey": matched_bates_nums[0],
                    "VolumeName": "VOL001",
                    "PathToImage": rel_dst_bates,
                    "DocumentBreak": "Y",
                    "FolderBreak": "",
                    "BoxBreak": "",
                    "PageCount": len(matched_bates_nums)
                })
                # Subsequent pages have empty breaks and page counts
                for b_num in matched_bates_nums[1:]:
                    opt_records.append({
                        "ImageKey": b_num,
                        "VolumeName": "VOL001",
                        "PathToImage": rel_dst_bates,
                        "DocumentBreak": "",
                        "FolderBreak": "",
                        "BoxBreak": "",
                        "PageCount": ""
                    })

        # Save Concordance DAT metadata load file
        dat_path = os.path.join(self.output_root_dir, "production_loadfile.dat")
        try:
            with open(dat_path, "w", encoding="utf-8", newline="") as f:
                # We use standard Concordance comma separators here for reliability
                writer = csv.DictWriter(f, fieldnames=["DocID", "BatesStart", "BatesEnd", "PageCount", "OriginalPath", "MD5Hash", "Status"])
                writer.writeheader()
                writer.writerows(dat_records)
        except Exception:
            pass

        # Save Opticon OPT image log load file
        opt_path = os.path.join(self.output_root_dir, "production_images.opt")
        try:
            with open(opt_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for rec in opt_records:
                    writer.writerow([
                        rec["ImageKey"],
                        rec["VolumeName"],
                        rec["PathToImage"],
                        rec["DocumentBreak"],
                        rec["FolderBreak"],
                        rec["BoxBreak"],
                        rec["PageCount"]
                    ])
        except Exception:
            pass

        # Write exceptions report
        exceptions_report_path = os.path.join(self.output_root_dir, "exceptions", "exceptions_report.txt")
        try:
            with open(exceptions_report_path, "w", encoding="utf-8") as f:
                f.write("AP MULTITOOL BATES RECONCILER: AUDIT EXCEPTIONS REPORT\n")
                f.write("=" * 80 + "\n\n")
                for rel_path, pages in sorted(doc_pages.items()):
                    missing = [p for p in pages if p["bates_number"] == "N/A"]
                    if missing:
                        f.write(f"File: {rel_path}\n")
                        f.write(f"  Missing Pages: {', '.join([p['page_label'] for p in missing])}\n")
                        f.write("-" * 80 + "\n")
        except Exception:
            pass
