import os
import re
import hashlib
import json
import random
import fitz
import numpy as np
import pytesseract
from PIL import Image as PILImage

# Set default Tesseract path for Windows local installations
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class BatesReconciler:
    def __init__(self, target_dir, master_dir, ocr_cache_path=None):
        self.target_dir = target_dir
        self.master_dir = master_dir
        self.ocr_cache_path = ocr_cache_path or os.path.join(target_dir, "ocr_cache.json")
        self.ocr_cache = {}
        self.load_ocr_cache()

    def load_ocr_cache(self):
        if os.path.exists(self.ocr_cache_path):
            try:
                with open(self.ocr_cache_path, "r", encoding="utf-8") as f:
                    self.ocr_cache = json.load(f)
            except Exception:
                self.ocr_cache = {}

    def save_ocr_cache(self):
        try:
            with open(self.ocr_cache_path, "w", encoding="utf-8") as f:
                json.dump(self.ocr_cache, f, indent=4)
        except Exception:
            pass

    def compute_md5(self, file_path):
        """Generate MD5 hash of file content for exact duplicate matching."""
        hasher = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None

    def get_normalized_thumbnail(self, page, size=128):
        """Render grayscale normalized matrix signature for layout matching."""
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(size/page.rect.width, size/page.rect.height), colorspace=fitz.csGRAY)
            arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape((size, size)).astype(float)
            mean = np.mean(arr)
            std = np.std(arr)
            if std > 0:
                arr = (arr - mean) / std
            else:
                arr = arr - mean
            return arr
        except Exception:
            return np.zeros((size, size))

    def get_normalized_thumbnail_variants(self, page, size=128):
        """Generates rotated layout variant matrices."""
        variants = []
        for rotation in [0, 90, 180, 270]:
            try:
                matrix = fitz.Matrix(size/page.rect.width, size/page.rect.height).prerotate(rotation)
                pix = page.get_pixmap(matrix=matrix, colorspace=fitz.csGRAY)
                arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape((size, size)).astype(float)
                mean = np.mean(arr)
                std = np.std(arr)
                arr = (arr - mean) / (std if std > 0 else 1.0)
                variants.append((rotation, arr))
            except Exception:
                pass
        return variants

    def ocr_page_content(self, file_path, page_num, dpi=150):
        """Extract text layer or run PyTesseract OCR if image-only."""
        cache_key = f"{os.path.basename(file_path)}_p{page_num}"
        if cache_key in self.ocr_cache:
            return self.ocr_cache[cache_key]

        text = ""
        try:
            doc = fitz.open(file_path)
            page = doc[page_num - 1]
            text = page.get_text().strip()
            
            # If empty or minimal text layer, run OCR
            if len(text) <= 25:
                zoom = dpi / 72
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                img = PILImage.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img).strip()
            doc.close()
        except Exception:
            pass

        self.ocr_cache[cache_key] = text
        return text

    def extract_numbers(self, text):
        if not text:
            return set()
        # Find alphanumeric identifiers or currency codes
        pattern = re.compile(r"\b[A-Za-z-]*\d{2,}[A-Za-z0-9,-]*\b")
        nums = pattern.findall(text)
        filtered = set()
        ignore = {"2024", "2025", "2026", "0.00", "000"}
        for n in nums:
            clean = n.replace(",", "").replace(".", "").strip().lower()
            if len(clean) >= 3 and clean not in ignore:
                filtered.add(n.lower())
        return filtered

    def run_reconciliation(self, progress_callback=None):
        """Headless reconciliation loop scanning targets vs master court productions."""
        results = []
        
        # 1. Index Master Production PDFs
        master_configs = []
        for f in os.listdir(self.master_dir):
            if f.lower().endswith(".pdf") and not f.startswith("."):
                master_configs.append(os.path.join(self.master_dir, f))
                
        master_index = []
        for m_path in master_configs:
            m_filename = os.path.basename(m_path)
            try:
                doc = fitz.open(m_path)
                for idx in range(len(doc)):
                    page = doc[idx]
                    # Read Bates stamp if OCR/text layer exists
                    bates_guess = "N/A"
                    txt = page.get_text()
                    m = re.search(r"\b[A-Za-z]{3,10}_[A-Za-z0-9_-]*\d{3,8}\b", txt)
                    if m:
                        bates_guess = m.group(0)
                        
                    master_index.append({
                        "master_file": m_filename,
                        "master_path": m_path,
                        "master_page": idx + 1,
                        "bates_label": bates_guess,
                        "thumb": self.get_normalized_thumbnail(page)
                    })
                doc.close()
            except Exception:
                pass
                
        if not master_index:
            return []

        m_thumbs = np.array([m["thumb"] for m in master_index])

        # 2. Walk Target Files
        target_files = []
        master_filenames = {os.path.basename(m_path).lower() for m_path in master_configs}
        for root, dirs, files in os.walk(self.target_dir):
            parts = [p.lower() for p in root.replace("\\", "/").split("/")]
            if any(p in parts for p in ["exceptions", "identified-bates", "identified-bates-test", "reconciled_production", "bates_proof_images", "roqui_chunks", "undefined"]):
                continue
            for f in files:
                if f.lower() in master_filenames:
                    continue
                ext = os.path.splitext(f)[1].lower()
                if ext in [".pdf", ".png", ".jpg", ".jpeg"] and not f.startswith("."):
                    target_files.append(os.path.join(root, f))

        total_files = len(target_files)
        
        # 3. Match Target Pages
        for f_idx, t_path in enumerate(target_files, start=1):
            if progress_callback:
                progress_callback(f"Analyzing {os.path.basename(t_path)}", f_idx / total_files)
                
            file_basename = os.path.basename(t_path)
            rel_path = os.path.relpath(t_path, self.target_dir)
            md5_hash = self.compute_md5(t_path)
            
            try:
                doc = fitz.open(t_path)
                pages_count = len(doc)
                
                for p_idx in range(pages_count):
                    page = doc[p_idx]
                    page_label = f"Page {p_idx + 1}"
                    
                    # Generate layout variants for rotation invariance
                    variants = self.get_normalized_thumbnail_variants(page)
                    
                    # Find closest visual matches
                    best_match_idx = -1
                    best_mse = float("inf")
                    best_rot = 0
                    
                    for rot, t_thumb in variants:
                        mses = np.mean((m_thumbs - t_thumb) ** 2, axis=(1, 2))
                        min_idx = np.argmin(mses)
                        min_mse = mses[min_idx]
                        if min_mse < best_mse:
                            best_mse = min_mse
                            best_match_idx = min_idx
                            best_rot = rot
                            
                    # Match Decision
                    bates = "N/A"
                    master_info = "N/A"
                    status = "Omitted"
                    confidence = 0.0
                    
                    # Threshold check: MSE <= 0.05 is an exact layout match
                    if best_mse <= 0.05:
                        match_item = master_index[best_match_idx]
                        bates = match_item["bates_label"] if match_item["bates_label"] != "N/A" else f"Reconstructed (Page {match_item['master_page']})"
                        master_info = f"{match_item['master_file']} (Page {match_item['master_page']})"
                        status = "Matched"
                        confidence = 1.0 - best_mse
                    
                    results.append({
                        "file_subpath": rel_path.replace("\\", "/"),
                        "page_label": page_label,
                        "bates_number": bates,
                        "master_info": master_info,
                        "status": status,
                        "mse": float(best_mse),
                        "rotation": best_rot,
                        "md5": md5_hash,
                        "confidence": confidence
                    })
                doc.close()
            except Exception:
                pass
                
        self.save_ocr_cache()
        return results

    def get_random_audit_sample(self, match_list, confidence=0.95, margin=0.05):
        """
        Calculates statistically valid sample size using Cochran's formula.
        N = Total population size
        n0 = (Z^2 * p * (1-p)) / e^2
        n = n0 / (1 + (n0 - 1)/N)
        """
        N = len(match_list)
        if N == 0:
            return []
            
        # Z-score lookup based on confidence level
        z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        Z = z_scores.get(confidence, 1.96)
        p = 0.5  # Max variability (standard assumption)
        e = margin
        
        n0 = (Z**2 * p * (1-p)) / (e**2)
        n = int(np.ceil(n0 / (1 + (n0 - 1) / N)))
        n = min(n, N)
        
        # Pull a random sample
        sample_indices = random.sample(range(N), n)
        return [match_list[i] for i in sample_indices]
