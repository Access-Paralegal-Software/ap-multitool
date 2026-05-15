import os
import re
import sys
import time
import threading
import email
from email import policy
from email.parser import BytesParser
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pikepdf
import urllib.request
import json
import webbrowser
from datetime import datetime

# Application Metadata
VERSION = "1.2.0"
GITHUB_REPO = "woodyardae/Access_Paralegal_PDF_Merger" # Change this to your repo path!

# UI Aesthetic Branding Colors (Access Paralegal Light/Silver Concept)
BRAND_ACCENT_GREEN = "#288F4F"
BRAND_DEEP_ACCENT = "#1E6C3A"
BRAND_SILVER_BG = "#F3F4F6"
BRAND_DARK_TEXT = "#1F2937"
BRAND_WHITE_PANEL = "#FFFFFF"
BRAND_BORDER_LIGHT = "#E5E7EB"

# Mode and Theme Config
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

EULA_TEXT = """ACCESS PARALEGAL SERVICES — END USER LICENSE AGREEMENT (EULA)

1. SOFTWARE LICENSE AND OWNERSHIP
This software ("Access Paralegal PDF Merger") and all accompanying documentation are licensed, not sold, by Access Paralegal Services. 

2. 100% OFFLINE DATA GUARANTEE
Privacy is paramount in legal tech. This software operates entirely on your local machine. No document content, metadata, or identifying metrics are collected, stored, or transmitted to any remote server or third party. 

3. NO WARRANTY ("AS-IS")
Access Paralegal Services provides this software "AS IS" without any warranties. You are solely responsible for reviewing and validating the accuracy of all output files for legal filings.

4. LIMITATION OF LIABILITY
In no event shall Access Paralegal Services or its developers (Alan Woodyard) be liable for any special, direct, indirect, consequential, or incidental damages.

5. COPYRIGHT & TRADEMARKS
Copyright © 2026 Alan Woodyard & Access Paralegal Services. All rights reserved.
"""

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AccessMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Path Bindings
        self.app_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
        self.default_input = os.path.join(self.app_dir, "Source_Files")
        self.default_output = os.path.join(self.app_dir, "Merged_Output")
        
        os.makedirs(self.default_input, exist_ok=True)
        os.makedirs(self.default_output, exist_ok=True)

        self.detected_files = []
        self.total_audit_pages = 0
        self.scan_in_progress = False

        # Window Config
        self.title("Access Paralegal PDF Merger")
        self.geometry("880x690")
        self.resizable(False, False)
        self.configure(fg_color=BRAND_SILVER_BG)

        self._setup_menu()
        self._setup_ui()
        
        # Scan current landing folder
        self.trigger_async_folder_scan(self.default_input)

    def _setup_menu(self):
        self.menubar = tk.Menu(self)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Open Source Folder", command=self.browse_folder)
        filemenu.add_command(label="View Merged Output", command=lambda: os.startfile(self.default_output))
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="Check for Updates...", command=self.check_updates)
        helpmenu.add_command(label="About Software...", command=self.show_about_window)
        helpmenu.add_command(label="View License Terms", command=self.show_eula_window)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=self.menubar)

    def _setup_ui(self):
        # --- HEADER BAR (SILVER WITH PROMINENT LOGO) ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=BRAND_WHITE_PANEL, border_width=0, height=140)
        self.header_frame.pack(fill="x", pady=0)
        self.header_frame.pack_propagate(False)

        # Load Bundled Company Logo
        logo_path = resource_path("logo_small.png")
        if os.path.exists(logo_path):
            try:
                pil_img = Image.open(logo_path)
                w, h = pil_img.size
                aspect = w / h
                new_h = 70
                new_w = int(new_h * aspect)
                
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(new_w, new_h))
                self.logo_lbl = ctk.CTkLabel(self.header_frame, image=self.logo_img, text="")
                self.logo_lbl.pack(pady=(20, 5))
            except Exception as e:
                self._fallback_logo()
        else:
            self._fallback_logo()

        self.sub_title = ctk.CTkLabel(
            self.header_frame, 
            text="PROFESSIONAL PDF & EMAIL BUNDLE MERGER", 
            font=ctk.CTkFont(family="Inter", size=10, weight="bold", tracking=True),
            text_color="#4B5563"
        )
        self.sub_title.pack(pady=(0, 15))

        self.line = ctk.CTkFrame(self, height=1, fg_color=BRAND_BORDER_LIGHT)
        self.line.pack(fill="x")

        # --- DUAL-MODULE TABBED DASHBOARD ---
        self.tab_view = ctk.CTkTabview(
            self, fg_color="transparent", segmented_button_selected_color=BRAND_ACCENT_GREEN,
            segmented_button_selected_hover_color=BRAND_DEEP_ACCENT, text_color=BRAND_DARK_TEXT
        )
        self.tab_view.pack(fill="both", expand=True, padx=25, pady=(10, 10))
        
        self.tab_merger = self.tab_view.add("📦 Document Merger")
        self.tab_bates = self.tab_view.add("⚖️ Bates Stamping & Locking")

        # ==========================================
        # TAB 1: DOCUMENT MERGER (MOUNTED CODEBASE)
        # ==========================================
        self.merger_container = ctk.CTkFrame(self.tab_merger, fg_color="transparent")
        self.merger_container.pack(fill="both", expand=True)

        # Left Config Panel
        self.left_frame = ctk.CTkFrame(
            self.merger_container, width=320, fg_color=BRAND_WHITE_PANEL, 
            corner_radius=12, border_width=1, border_color=BRAND_BORDER_LIGHT
        )
        self.left_frame.pack(side="left", fill="both", padx=(0, 15))
        self.left_frame.pack_propagate(False)

        # Right Queue Panel
        self.right_frame = ctk.CTkFrame(self.merger_container, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # --- POPULATE LEFT (SETTINGS) ---
        ctk.CTkLabel(self.left_frame, text="🛠️ COMPILER SETTINGS", font=ctk.CTkFont(weight="bold", size=13), text_color=BRAND_DARK_TEXT).pack(pady=(15, 10))

        self.var_bookmark = tk.BooleanVar(value=True)
        self.chk_bookmark = ctk.CTkCheckBox(
            self.left_frame, text="Create Bookmarks per file", variable=self.var_bookmark, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=12), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_bookmark.pack(anchor="w", padx=20, pady=6)

        self.var_fit_view = tk.BooleanVar(value=True)
        self.chk_fit_view = ctk.CTkCheckBox(
            self.left_frame, text="Enforce Single-Page Layout", variable=self.var_fit_view, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=12), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_fit_view.pack(anchor="w", padx=20, pady=6)

        self.var_compress = tk.BooleanVar(value=False)
        self.chk_compress = ctk.CTkCheckBox(
            self.left_frame, text="Optimize Output Size", variable=self.var_compress, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=12), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_compress.pack(anchor="w", padx=20, pady=6)

        self.var_email = tk.BooleanVar(value=True)
        self.chk_email = ctk.CTkCheckBox(
            self.left_frame, text="Extract Email Attachments", variable=self.var_email, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=12), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_email.pack(anchor="w", padx=20, pady=6)

        self.var_grayscale = tk.BooleanVar(value=False)
        self.chk_grayscale = ctk.CTkCheckBox(
            self.left_frame, text="📉 Grayscale (Huge File Save!)", variable=self.var_grayscale, 
            text_color="#B45309", font=ctk.CTkFont(size=12, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_grayscale.pack(anchor="w", padx=20, pady=6)

        ctk.CTkLabel(self.left_frame, text="Target Standard Page Size:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=20, pady=(10, 2))
        self.paper_dropdown = ctk.CTkOptionMenu(
            self.left_frame, values=["US Letter (8.5 x 11 in)", "US Legal (8.5 x 14 in)", "A4 (International)"], width=260, 
            fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN, button_hover_color=BRAND_DEEP_ACCENT
        )
        self.paper_dropdown.pack(padx=20, pady=(0, 10))

        # AUDIT STATUS CARD
        self.audit_panel = ctk.CTkFrame(self.left_frame, fg_color=BRAND_SILVER_BG, corner_radius=8, border_width=1, border_color=BRAND_BORDER_LIGHT)
        self.audit_panel.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        ctk.CTkLabel(self.audit_panel, text="📄 QUEUE PREVIEW", font=ctk.CTkFont(weight="bold", size=11), text_color=BRAND_ACCENT_GREEN).pack(pady=(10, 5))
        self.audit_files_lbl = ctk.CTkLabel(self.audit_panel, text="Documents: Scanning...", font=ctk.CTkFont(size=12), text_color=BRAND_DARK_TEXT)
        self.audit_files_lbl.pack(anchor="w", padx=15, pady=2)
        self.audit_pages_lbl = ctk.CTkLabel(self.audit_panel, text="Total Pages: Calculating...", font=ctk.CTkFont(size=12), text_color=BRAND_DARK_TEXT)
        self.audit_pages_lbl.pack(anchor="w", padx=15, pady=2)

        # --- POPULATE RIGHT (VISUAL QUEUE & MERGER) ---
        self.dir_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.dir_frame.pack(fill="x", pady=(0, 15))

        self.dir_entry = ctk.CTkEntry(
            self.dir_frame, height=36, fg_color=BRAND_WHITE_PANEL, 
            text_color=BRAND_DARK_TEXT, border_color=BRAND_BORDER_LIGHT
        )
        self.dir_entry.insert(0, self.default_input)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dir_btn = ctk.CTkButton(
            self.dir_frame, text="Change Folder", width=110, height=36, 
            fg_color="#4B5563", hover_color="#374151", command=self.browse_folder
        )
        self.dir_btn.pack(side="right")

        self.queue_frame = ctk.CTkScrollableFrame(
            self.right_frame, fg_color=BRAND_WHITE_PANEL, 
            border_width=1, border_color=BRAND_BORDER_LIGHT, corner_radius=8
        )
        self.queue_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.status_bar_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.status_bar_frame.pack(fill="x", pady=(0, 10))
        
        self.processing_lbl = ctk.CTkLabel(
            self.status_bar_frame, text="Status: Standing By", 
            font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_DARK_TEXT
        )
        self.processing_lbl.pack(side="left")

        self.count_lbl = ctk.CTkLabel(
            self.status_bar_frame, text="", font=ctk.CTkFont(size=12, weight="normal"), text_color="#4B5563"
        )
        self.count_lbl.pack(side="right")

        self.action_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.action_frame.pack(fill="x")
        
        self.p_bar = ctk.CTkProgressBar(self.action_frame, height=12, progress_color=BRAND_ACCENT_GREEN)
        self.p_bar.set(0)
        self.p_bar.pack(fill="x", pady=(0, 15))

        self.run_btn = ctk.CTkButton(
            self.action_frame, text="🚀 COMBINE & MERGE FILES", height=52, 
            font=ctk.CTkFont(size=16, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT,
            command=self.start_merge_thread
        )
        self.run_btn.pack(fill="x")

        # ==========================================
        # TAB 2: BATES STAMPING & LOCKING SYSTEM
        # ==========================================
        self.bates_container = ctk.CTkFrame(self.tab_bates, fg_color="transparent")
        self.bates_container.pack(fill="both", expand=True)

        # Left Bates Config Panel
        self.bates_left = ctk.CTkFrame(
            self.bates_container, width=350, fg_color=BRAND_WHITE_PANEL, 
            corner_radius=12, border_width=1, border_color=BRAND_BORDER_LIGHT
        )
        self.bates_left.pack(side="left", fill="both", padx=(0, 15))
        self.bates_left.pack_propagate(False)

        # Populate Left Bates Controls
        ctk.CTkLabel(self.bates_left, text="🔢 BATES CONFIGURATION", font=ctk.CTkFont(weight="bold", size=13), text_color=BRAND_DARK_TEXT).pack(pady=(15, 10))
        
        ctk.CTkLabel(self.bates_left, text="Alpha-Numeric Prefix:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=20, pady=(5, 2))
        self.bates_prefix = ctk.CTkEntry(self.bates_left, placeholder_text="e.g., EXHIBIT-A-", width=310)
        self.bates_prefix.pack(padx=20, pady=(0, 10))
        self.bates_prefix.insert(0, "AP-")

        # Dual columns for start index and padding
        self.num_grid = ctk.CTkFrame(self.bates_left, fg_color="transparent")
        self.num_grid.pack(fill="x", padx=20, pady=(0, 10))
        
        # Start # Column
        self.col1 = ctk.CTkFrame(self.num_grid, fg_color="transparent")
        self.col1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(self.col1, text="Starting Index:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w")
        self.bates_start = ctk.CTkEntry(self.col1, placeholder_text="1", width=140)
        self.bates_start.pack(anchor="w")
        self.bates_start.insert(0, "1")

        # Padding Column
        self.col2 = ctk.CTkFrame(self.num_grid, fg_color="transparent")
        self.col2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(self.col2, text="Digit Padding:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w")
        self.bates_padding = ctk.CTkOptionMenu(self.col2, values=["4 digits (0001)", "6 digits (000001)", "8 digits (00000001)"], width=140, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN)
        self.bates_padding.pack(anchor="w")
        self.bates_padding.set("6 digits (000001)")

        ctk.CTkLabel(self.bates_left, text="Stamp Positioning:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=20, pady=(5, 2))
        self.bates_pos = ctk.CTkOptionMenu(self.bates_left, values=["Bottom Right (Court Standard)", "Bottom Center", "Bottom Left", "Top Right"], width=310, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN)
        self.bates_pos.pack(padx=20, pady=(0, 10))

        ctk.CTkLabel(self.bates_left, text="Universal Font Selector:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=20, pady=(5, 2))
        self.bates_font = ctk.CTkOptionMenu(self.bates_left, values=["Arial Bold (Standard)", "Courier Prime (Monospaced)", "Times New Roman", "Georgia"], width=310, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN)
        self.bates_font.pack(padx=20, pady=(0, 15))

        # Sequencer Toggles
        self.var_bates_seq = tk.BooleanVar(value=True)
        self.chk_bates_seq = ctk.CTkCheckBox(
            self.bates_left, text="Continue Sequential Count Across Files", variable=self.var_bates_seq, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=12), fg_color=BRAND_ACCENT_GREEN
        )
        self.chk_bates_seq.pack(anchor="w", padx=20, pady=6)

        self.var_bates_csv = tk.BooleanVar(value=True)
        self.chk_bates_csv = ctk.CTkCheckBox(
            self.bates_left, text="💾 Generate eDiscovery CSV Load File", variable=self.var_bates_csv, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=12), fg_color=BRAND_ACCENT_GREEN
        )
        self.chk_bates_csv.pack(anchor="w", padx=20, pady=6)

        self.var_ocr = tk.BooleanVar(value=False)
        self.chk_ocr = ctk.CTkCheckBox(
            self.bates_left, text="👁️ Execute OCR Searchable Text Layers", variable=self.var_ocr, 
            text_color="#B45309", font=ctk.CTkFont(size=12, weight="bold"), fg_color=BRAND_ACCENT_GREEN
        )
        self.chk_ocr.pack(anchor="w", padx=20, pady=6)

        # Right Bates Panel (Info & Dynamic Portal)
        self.bates_right = ctk.CTkFrame(self.bates_container, fg_color="transparent")
        self.bates_right.pack(side="right", fill="both", expand=True)

        self.bates_info_box = ctk.CTkFrame(
            self.bates_right, fg_color=BRAND_WHITE_PANEL, corner_radius=12, border_width=1, border_color=BRAND_BORDER_LIGHT
        )
        self.bates_info_box.pack(fill="both", expand=True, pady=(0, 15))

        ctk.CTkLabel(self.bates_info_box, text="⛓️ LEGAL AUTHENTICITY REPORT", font=ctk.CTkFont(weight="bold", size=13), text_color=BRAND_ACCENT_GREEN).pack(pady=(20, 10))
        
        exp_text = (
            "Bates Stamping securely vector-locks serialization directly into the page content stream. "
            "This physically 'flattens' the document metadata to prevent post-filing manipulation.\n\n"
            "Generating an eDiscovery Load File (CSV) exports a court-ready directory mapping filenames "
            "to exact Bates ranges, perfectly compatible with enterprise databases like Concordance or Relativity."
        )
        ctk.CTkLabel(self.bates_info_box, text=exp_text, font=ctk.CTkFont(size=12), text_color=BRAND_DARK_TEXT, wraplength=400, justify="left").pack(padx=25, pady=10)

        # ❓ DYNAMIC ONLINE FAQ PORTAL
        self.faq_btn = ctk.CTkButton(
            self.bates_info_box, text="❓ OPEN FAQ & COMPLIANCE PORTAL (LIVE)", 
            fg_color="#F3F4F6", text_color=BRAND_ACCENT_GREEN, border_width=1, border_color=BRAND_ACCENT_GREEN,
            hover_color="#E5E7EB", height=40, font=ctk.CTkFont(weight="bold"),
            command=lambda: webbrowser.open("https://www.accessparalegalservices.com/software-faq")
        )
        self.faq_btn.pack(fill="x", padx=30, pady=(20, 10))

        self.bates_run_btn = ctk.CTkButton(
            self.bates_right, text="✨ FLATTEN & APPLY BATES STAMPS", height=60, 
            font=ctk.CTkFont(size=16, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT,
            command=lambda: messagebox.showinfo("Coming Soon", "The Secure Bates Flattening system is staged!\n\nComplete structural module rollout pending in V1.3 Hotfix!")
        )
        self.bates_run_btn.pack(fill="x")

        # --- FOOTER COPYRIGHT ---
        self.footer_frame = ctk.CTkFrame(self, fg_color=BRAND_WHITE_PANEL, corner_radius=0, height=30)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)

        self.copy_lbl = ctk.CTkLabel(
            self.footer_frame, 
            text="Copyright © 2026 Alan Woodyard & Access Paralegal Services. All rights reserved.", 
            font=ctk.CTkFont(family="Inter", size=9),
            text_color="#6B7280"
        )
        self.copy_lbl.pack(pady=4)

    def _fallback_logo(self):
        ctk.CTkLabel(self.header_frame, text="ACCESS PARALEGAL", font=ctk.CTkFont(size=24, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(25, 0))
        ctk.CTkLabel(self.header_frame, text="SERVICES", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=0)

    def clear_queue_visual(self):
        for widget in self.queue_frame.winfo_children():
            widget.destroy()

    def add_queue_item(self, filename, status="Pending", text_color="#4B5563"):
        item_row = ctk.CTkFrame(self.queue_frame, fg_color="transparent")
        item_row.pack(fill="x", pady=4, padx=5)
        icon = "📧" if filename.lower().endswith('.eml') else "📄"
        
        lbl_name = ctk.CTkLabel(item_row, text=f"{icon} {filename[:50]}", anchor="w", text_color=BRAND_DARK_TEXT)
        lbl_name.pack(side="left", fill="x", expand=True)
        
        lbl_status = ctk.CTkLabel(item_row, text=status, font=ctk.CTkFont(size=11, weight="bold"), text_color=text_color)
        lbl_status.pack(side="right")
        return lbl_status

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.dir_entry.get() or self.default_input)
        if folder:
            folder = os.path.normpath(folder)
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, folder)
            self.trigger_async_folder_scan(folder)

    def natural_sort_key(self, s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

    def check_updates(self):
        """Future-proof GitHub Release Checker Hook."""
        def check():
            try:
                url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    latest_version = data.get("tag_name", "").replace("v", "")
                    if latest_version and latest_version != VERSION:
                        if messagebox.askyesno("Update Available", f"An updated version (v{latest_version}) is available!\n\nWould you like to download it now?"):
                            webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases")
                    else:
                        messagebox.showinfo("Up to Date", "You are running the latest version!")
            except Exception:
                messagebox.showinfo("Check Updates", "Could not reach the server. Please ensure you are online or visit the website for updates.")
        threading.Thread(target=check, daemon=True).start()

    def _generate_email_cover(self, msg, out_path):
        # Dynamically set dimensions based on paper dropdown
        paper = self.paper_dropdown.get()
        if "Legal" in paper:
            w, h = 2550, 4200 # 300 DPI Legal
        elif "Letter" in paper:
            w, h = 2550, 3300 # 300 DPI Letter
        else:
            w, h = 2480, 3508 # 300 DPI A4

        img = Image.new("RGB", (w, h), "white")
        draw = ImageDraw.Draw(img)
        
        # Attempt Native Windows Fonts fallback to default
        try:
            font_bold = ImageFont.truetype("arialbd.ttf", 60)
            font_reg = ImageFont.truetype("arial.ttf", 45)
            font_title = ImageFont.truetype("arialbd.ttf", 80)
        except:
            font_bold = font_reg = font_title = ImageFont.load_default()

        # 🏢 Draw Executive Branding Top Bar
        draw.rectangle([0, 0, w, 220], fill="#F3F4F6")
        draw.text((120, 70), "ACCESS PARALEGAL — DOCUMENTATION RECORD", fill="#1F2937", font=font_title)
        draw.rectangle([0, 215, w, 220], fill="#288F4F")

        # Header Metadata Extraction
        headers = {
            "From": str(msg.get('From', 'Unknown Sender')),
            "To": str(msg.get('To', 'Unknown Recipient')),
            "Date": str(msg.get('Date', 'Unknown Date')),
            "Subject": str(msg.get('Subject', 'No Subject'))
        }
        
        y = 340
        for k, v in headers.items():
            draw.text((120, y), f"{k.upper()}:", fill="#111827", font=font_bold)
            # Wrap header values
            words = v.split(' ')
            line = ""
            for word in words:
                if len(line + " " + word) * 28 < (w - 850):
                    line += " " + word
                else:
                    draw.text((450, y), line.strip(), fill="#374151", font=font_reg)
                    y += 70
                    line = word
            draw.text((450, y), line.strip(), fill="#374151", font=font_reg)
            y += 110

        draw.line([120, y, w-120, y], fill="#E5E7EB", width=5)
        y += 70
        
        draw.text((120, y), "MESSAGE CORRESPONDENCE EXTRACT:", fill="#111827", font=font_bold)
        y += 90
        
        # Safely parse Text Body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode(errors='replace')
                    except:
                        pass
                    break
        else:
            try:
                body = msg.get_payload(decode=True).decode(errors='replace')
            except:
                pass
        
        if not body.strip():
            body = "[This email contains no plain text content or is an HTML-only document.]"
            
        body = re.sub(r'\s+', ' ', body)[:2000] # Restrict to first 2000 chars for cover page
        
        # Draw Wrapped Body Content
        line = ""
        for word in body.split(' '):
            if len(line + " " + word) * 24 < (w - 380):
                line += " " + word
            else:
                draw.text((120, y), line.strip(), fill="#4B5563", font=font_reg)
                y += 60
                line = word
                if y > h - 250: break
        if y < h - 200:
            draw.text((120, y), line.strip(), fill="#4B5563", font=font_reg)
            
        # Convert to grayscale matrix if checked by paralegal
        if self.var_grayscale.get():
            img = img.convert("L")
            
        img.save(out_path, "PDF")

    def trigger_async_folder_scan(self, folder_path):
        if self.scan_in_progress: return
        self.clear_queue_visual()
        self.audit_files_lbl.configure(text="Documents: Counting...")
        self.audit_pages_lbl.configure(text="Pages: Auditing...")
        threading.Thread(target=self.perform_scan, args=(folder_path,), daemon=True).start()

    def perform_scan(self, folder_path):
        self.scan_in_progress = True
        try:
            if not os.path.exists(folder_path):
                return
            # Expanded to detect Legacy Image Formats and Emails
            legal_exts = ('.pdf', '.eml', '.tif', '.tiff', '.jpg', '.jpeg', '.png') if self.var_email.get() else ('.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png')
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(legal_exts)]
            files.sort(key=self.natural_sort_key)
            self.detected_files = files
            
            total_p = 0
            for idx, fn in enumerate(files):
                self.after(0, lambda name=fn: self.add_queue_item(name, "Ready"))
                try:
                    p_path = os.path.join(folder_path, fn)
                    low_fn = fn.lower()
                    if low_fn.endswith('.pdf'):
                        with pikepdf.open(p_path) as p:
                            total_p += len(p.pages)
                    elif low_fn.endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png')):
                        total_p += 1 # Represents 1 page converted image
                    elif low_fn.endswith('.eml'):
                        total_p += 1 # Cover page
                except:
                    pass
            
            self.total_audit_pages = total_p
            self.after(0, lambda: self.audit_files_lbl.configure(text=f"Files Found: {len(files)}"))
            self.after(0, lambda: self.audit_pages_lbl.configure(text=f"Total Pages Estimated: {total_p}"))
            self.after(0, lambda: self.processing_lbl.configure(text="Status: Ready to Combine"))
        except:
            pass
        finally:
            self.scan_in_progress = False

    def start_merge_thread(self):
        self.run_btn.configure(state="disabled", text="Processing...")
        self.p_bar.set(0)
        self.clear_queue_visual()
        threading.Thread(target=self.execute_audit_merge, daemon=True).start()

    def execute_audit_merge(self):
        source = self.dir_entry.get()
        if not os.path.exists(source):
            self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))
            return
        
        legal_exts = ('.pdf', '.eml', '.tif', '.tiff', '.jpg', '.jpeg', '.png') if self.var_email.get() else ('.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png')
        files = [f for f in os.listdir(source) if f.lower().endswith(legal_exts)]
        if not files:
            self.after(0, lambda: self.processing_lbl.configure(text="Status: Error - No files found!"))
            self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))
            return
        files.sort(key=self.natural_sort_key)

        start_t = time.time()
        merged_pdf = pikepdf.Pdf.new()
        
        if self.var_fit_view.get():
            merged_pdf.Root.ViewerPreferences = pikepdf.Dictionary(FitWindow=True, CenterWindow=True, DisplayDocTitle=True)
            merged_pdf.Root.PageLayout = pikepdf.Name("/SinglePage")

        outline_nodes = []
        curr_pg = 0
        success_count = 0
        
        temp_extract_dir = os.path.join(source, "_volta_temp_attachments")
        os.makedirs(temp_extract_dir, exist_ok=True)
        total_items = len(files)

        for idx, fn in enumerate(files, 1):
            self.after(0, lambda p=idx/total_items: self.p_bar.set(p))
            self.after(0, lambda f=fn: self.processing_lbl.configure(text=f"Compiling: {f[:30]}..."))
            self.after(0, lambda: self.count_lbl.configure(text=f"Item {idx} of {total_items}"))
            
            status_ref = []
            self.after(0, lambda: status_ref.append(self.add_queue_item(fn, "Processing...", BRAND_ACCENT_GREEN)))
            
            time.sleep(0.05)
            
            try:
                file_path = os.path.join(source, fn)
                low_fn = fn.lower()
                
                # --- SCENARIO 1: NATIVE PDF ---
                if low_fn.endswith('.pdf'):
                    with pikepdf.open(file_path) as src:
                        cnt = len(src.pages)
                        merged_pdf.pages.extend(src.pages)
                        if self.var_bookmark.get():
                            clean_n, _ = os.path.splitext(fn)
                            dest = pikepdf.Destination(merged_pdf.pages[curr_pg], pikepdf.Name("/Fit"))
                            outline_nodes.append(pikepdf.OutlineItem(clean_n, dest))
                        curr_pg += cnt
                        success_count += 1
                        if status_ref: self.after(0, lambda: status_ref[0].configure(text="✅ Combined", text_color=BRAND_ACCENT_GREEN))
                
                # --- SCENARIO 2: LEGACY IMAGE (TIFF, JPG, PNG) ---
                elif low_fn.endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png')):
                    temp_pdf = os.path.join(temp_extract_dir, f"img_{int(time.time())}_{idx}.pdf")
                    with Image.open(file_path) as img:
                        # Convert to grayscale matrix if enabled to reduce byte-size drastically
                        target_mode = "L" if self.var_grayscale.get() else "RGB"
                        img.convert(target_mode).save(temp_pdf, "PDF")
                    
                    with pikepdf.open(temp_pdf) as src:
                        merged_pdf.pages.extend(src.pages)
                        if self.var_bookmark.get():
                            clean_n, _ = os.path.splitext(fn)
                            dest = pikepdf.Destination(merged_pdf.pages[curr_pg], pikepdf.Name("/Fit"))
                            outline_nodes.append(pikepdf.OutlineItem(f"📷 {clean_n}", dest))
                        curr_pg += 1
                        success_count += 1
                        if status_ref: self.after(0, lambda: status_ref[0].configure(text="✅ Converted & Combined", text_color=BRAND_ACCENT_GREEN))

                # --- SCENARIO 3: EMAIL RECORDS (.EML) ---
                elif low_fn.endswith('.eml') and self.var_email.get():
                    with open(file_path, 'rb') as f:
                        msg = BytesParser(policy=policy.default).parse(f)
                    
                    # A. Generate Visual Email Record Page (Cover)
                    cover_pdf_path = os.path.join(temp_extract_dir, f"eml_cover_{int(time.time())}_{idx}.pdf")
                    self._generate_email_cover(msg, cover_pdf_path)
                    
                    email_start_pg = curr_pg
                    
                    # Insert Cover Page
                    with pikepdf.open(cover_pdf_path) as cover:
                        merged_pdf.pages.extend(cover.pages)
                        curr_pg += len(cover.pages)
                    
                    # Prepare Outline/Bookmark Node
                    subj = str(msg.get('Subject', 'No Subject'))
                    email_dest = pikepdf.Destination(merged_pdf.pages[email_start_pg], pikepdf.Name("/Fit"))
                    email_outline = pikepdf.OutlineItem(f"📧 Email: {subj[:50]}", email_dest)
                    
                    # B. Rip Attachments
                    extracted_pdfs = []
                    for part in msg.iter_attachments():
                        att_filename = part.get_filename()
                        if att_filename and att_filename.lower().endswith('.pdf'):
                            out_path = os.path.join(temp_extract_dir, f"extracted_{idx}_{att_filename}")
                            with open(out_path, 'wb') as out_f:
                                out_f.write(part.get_payload(decode=True))
                            extracted_pdfs.append((att_filename, out_path))
                    
                    # C. Append Ripped Attachments to merged document & NEST Bookmarks!
                    if extracted_pdfs:
                        for orig_name, pdf_path in extracted_pdfs:
                            att_start_pg = curr_pg
                            with pikepdf.open(pdf_path) as src:
                                cnt = len(src.pages)
                                merged_pdf.pages.extend(src.pages)
                                curr_pg += cnt
                            
                            # Nest Bookmark directly under the parent email!
                            att_dest = pikepdf.Destination(merged_pdf.pages[att_start_pg], pikepdf.Name("/Fit"))
                            email_outline.children.append(pikepdf.OutlineItem(f"📎 Attachment: {orig_name}", att_dest))
                        
                        if status_ref: self.after(0, lambda: status_ref[0].configure(text=f"✅ Rendered Body & Ripped {len(extracted_pdfs)} PDF(s)", text_color=BRAND_ACCENT_GREEN))
                    else:
                        if status_ref: self.after(0, lambda: status_ref[0].configure(text="✅ Rendered Body (No Attachments)", text_color=BRAND_ACCENT_GREEN))
                    
                    if self.var_bookmark.get():
                        outline_nodes.append(email_outline)
                    success_count += 1

            except Exception as e:
                if status_ref: self.after(0, lambda err=str(e): status_ref[0].configure(text="❌ Failed", text_color="#DC2626"))
            time.sleep(0.01)

        if self.var_bookmark.get() and outline_nodes:
            with merged_pdf.open_outline() as outline: 
                outline.root.extend(outline_nodes)

        self.after(0, lambda: self.processing_lbl.configure(text="Compiling Final Corporate Portfolio..."))
        out_name = f"Access_Merged_Master_{int(time.time())}.pdf"
        final_dest = os.path.join(self.default_output, out_name)

        try:
            merged_pdf.save(final_dest, linearize=True, compress_streams=self.var_compress.get())
            merged_pdf.close()
            elapsed = time.time() - start_t
            
            # Clean extraction directories
            for f in os.listdir(temp_extract_dir):
                try: os.remove(os.path.join(temp_extract_dir, f))
                except: pass
            try: os.rmdir(temp_extract_dir)
            except: pass

            self.after(0, lambda: self.processing_lbl.configure(text="🎉 Portfolio Complete!"))
            self.after(0, lambda: self.count_lbl.configure(text=""))
            self.after(0, lambda: messagebox.showinfo("Success", f"Successfully combined {success_count} items into a single master PDF!\n\nDuration: {elapsed:.1f}s"))
            os.startfile(self.default_output)
        except Exception as e:
            self.after(0, lambda: self.processing_lbl.configure(text="Error: Compile failed!"))
            self.after(0, lambda err=str(e): messagebox.showerror("Fatal Error", f"Failed saving: {err}"))

        self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))

    def show_about_window(self):
        about = ctk.CTkToplevel(self)
        about.title("About Access PDF Merger")
        about.geometry("460x320")
        about.configure(fg_color=BRAND_WHITE_PANEL)
        about.resizable(False, False)
        about.grab_set()
        about.lift()
        ctk.CTkLabel(about, text="Access Paralegal PDF Merger", font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(25, 5))
        ctk.CTkLabel(about, text=f"Version {VERSION} (Production)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4B5563").pack(pady=2)
        desc = "Secure, enterprise-grade document compiler developed for Access Paralegal Services by Alan Woodyard."
        ctk.CTkLabel(about, text=desc, font=ctk.CTkFont(size=11), wraplength=380, justify="center", text_color=BRAND_DARK_TEXT).pack(pady=15)
        ctk.CTkLabel(about, text="Copyright © 2026 Alan Woodyard & Access Paralegal Services.", font=ctk.CTkFont(size=9), text_color="#6B7280").pack(pady=5)
        ctk.CTkButton(about, text="Dismiss", width=120, fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, command=about.destroy).pack(pady=15)

    def show_eula_window(self):
        eula = ctk.CTkToplevel(self)
        eula.title("License & EULA")
        eula.geometry("580x480")
        eula.configure(fg_color=BRAND_WHITE_PANEL)
        eula.resizable(False, False)
        eula.grab_set()
        eula.lift()
        ctk.CTkLabel(eula, text="End User License Agreement", font=ctk.CTkFont(size=16, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=15)
        txt = ctk.CTkTextbox(eula, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(family="Consolas", size=10))
        txt.pack(fill="both", expand=True, padx=20, pady=10)
        txt.insert("end", EULA_TEXT)
        txt.configure(state="disabled")
        ctk.CTkButton(eula, text="Close Terms", width=140, fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, command=eula.destroy).pack(pady=15)

if __name__ == "__main__":
    app = AccessMergerApp()
    app.mainloop()
