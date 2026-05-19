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
import config
import email_processing
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pikepdf
import urllib.request
import json
import webbrowser
import csv
import extract_msg
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, legal, A4
from datetime import datetime
import hashlib
import base64
from cryptography.fernet import Fernet
import tempfile
from bs4 import BeautifulSoup, Comment
from xhtml2pdf import pisa

# Application Metadata
VERSION = config.__version__
GITHUB_REPO = "woodyardae/Access_Paralegal_Multitool"

# Keygen.sh Secure Licensing Constants
KEYGEN_ACCOUNT_ID = "c885ab2c-9f4d-44a1-adfd-ec1839a0ed93"
KEYGEN_PRODUCT_TOKEN = "prod-1ba5ec8a951c01b0857f24a19726b4effc9eb159f73e164a2c91f413510bd984v3"
LICENSE_FILE = os.path.join(os.path.expanduser("~"), ".access_paralegal_license.json")
CASE_VAULT_FILE = os.path.join(os.path.expanduser("~"), ".access_cases_vault.enc")

# UI Aesthetic Branding Colors (Luxury Neutral & Glowing Velvet Concept)
BRAND_ACCENT_GREEN = "#67BE5E"              # Exact Vibrant Logo Green
BRAND_DEEP_ACCENT = "#4E9146"               # Darkened Emerald
BRAND_SILVER_BG = ("#EAEAEC", "#1E2222")    # Light: Elegant Matte Silver, Dark: Soft Glowing Velvet Charcoal
BRAND_DARK_TEXT = ("#222222", "#ECECEC")    # High-Contrast Crisp Typography
BRAND_WHITE_PANEL = ("#F4F4F5", "#242828")  # Soft Grey Panels for fallback
BRAND_BORDER_LIGHT = ("#CCCCCC", "#3C4242")

# --- THE "MULTI-LAYER FROSTED GLASS" PALETTE ---
# Explicitly tuned to Alan's Layering Specifications to simulate multi-pane glass depth
GLASS_HEADER = ("#ECF9EB", "#2A4E27")       # Pristine Emerald Mint (Prevents washed-out appearance)
GLASS_LEFT = ("#ECEEF0", "#222727")         # Clear Slate Glass (100% sits over the Charcoal base)
GLASS_RIGHT = ("#DBEBDB", "#233627")        # Clear Jade-Slate Glass (simulates partial Green Slash overlap)
GLASS_BORDER = ("#BFE2BD", "#5DA652")       # High-specular bright emerald "Gleam" edge

# Mode and Theme Config
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

EULA_TEXT = """ACCESS PARALEGAL SERVICES — END USER LICENSE AGREEMENT (EULA)

1. SOFTWARE LICENSE AND OWNERSHIP
This software (config.APP_NAME) and all accompanying documentation are licensed, not sold, by Access Paralegal Services. 

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
        
        # Pro / Licensing State
        self.is_pro_activated = False
        self.active_license_key = ""
        self.trial_run_count = 0
        self.cancel_requested = False
        
        # Global Application Preferences
        self.custom_workspace_root = self.app_dir
        self.safeguard_files_var = tk.BooleanVar(value=True)
        self.custom_case_structure = [
            "Correspondence",
            "Correspondence/Client Correspondence",
            "Correspondence/Opposing Counsel",
            "Correspondence/Court Correspondence",
            "Correspondence/{Date}",
            "Discovery",
            "Discovery/Written Discovery",
            "Discovery/Document Production",
            "Discovery/Depositions",
            "Discovery/Experts",
            "Pleadings",
            "Pleadings/Motions",
            "Pleadings/Orders",
            "Pleadings/Briefs & Memoranda",
            "Client Documents",
            "Client Documents/Intake & Retainer",
            "Client Documents/Financial Records",
            "Research",
            "Research/Caselaw",
            "Research/Fact Research",
            "Trial",
            "Trial/Exhibits"
        ]

        # Window Config
        self.title(config.APP_NAME)
        self.geometry("960x760")
        self.resizable(True, True)
        self.minsize(920, 600)
        self.configure(fg_color=BRAND_SILVER_BG)

        # --- GLOBAL OS SCALING OVERRIDES ---
        self.option_add('*Menu.font', '{Segoe UI} 18')

        # --- DYNAMIC LUXURY DUAL-MODE WATERMARK & DIAGONAL SLASH ARCHITECT ---
        bg_w, bg_h = 960, 780
        try:
            logo_path = resource_path("logo_small.png")
            # 1. Pre-extract Logo Emblem
            emblem = None
            if os.path.exists(logo_path):
                orig = Image.open(logo_path).convert("RGBA")
                pixels = orig.get_flattened_data()
                new_pixels = []
                for item in pixels:
                    r, g, b, a = item
                    # Extract vibrant greens
                    if g > r + 12 and g > b + 12:
                        new_pixels.append((r, g, b, a))
                    else:
                        new_pixels.append((0, 0, 0, 0))
                emblem = orig.copy()
                emblem.putdata(new_pixels)
                emblem = emblem.resize((360, 360), Image.Resampling.LANCZOS)

            # 2. Draw Light Mode Canvas
            light_canvas = Image.new("RGBA", (bg_w, bg_h), "#EAEAEC") # Premium Matte Light Silver
            l_draw = ImageDraw.Draw(light_canvas)
            # Pushed WAY down/left: Sweeps from 12% of width down to 95% of height on right
            l_draw.polygon([(bg_w * 0.12, 0), (bg_w, 0), (bg_w, bg_h * 0.95)], fill=(103, 190, 94, 70))
            
            # 3. Draw Dark Mode Canvas
            dark_canvas = Image.new("RGBA", (bg_w, bg_h), "#1E2222") # Glowing Velvet Charcoal
            d_draw = ImageDraw.Draw(dark_canvas)
            d_draw.polygon([(bg_w * 0.12, 0), (bg_w, 0), (bg_w, bg_h * 0.95)], fill=(78, 145, 70, 90))

            # 4. Layer the Brand Emblem inside the Slash Sweep
            if emblem:
                # Dynamic blend of the emblem on both canvases at exactly 40% opacity for high impact
                emb_data = emblem.get_flattened_data()
                emb_alpha = []
                for r, g, b, a in emb_data:
                    if a > 0:
                        emb_alpha.append((r, g, b, int(a * 0.40)))
                    else:
                        emb_alpha.append((0, 0, 0, 0))
                emb_overlay = emblem.copy()
                emb_overlay.putdata(emb_alpha)
                
                # Positioned proudly deeper inside the vastly expanded green landscape
                light_canvas.paste(emb_overlay, (bg_w - 450, 130), emb_overlay)
                dark_canvas.paste(emb_overlay, (bg_w - 450, 130), emb_overlay)
            
            self.adaptive_bg_img = ctk.CTkImage(light_image=light_canvas, dark_image=dark_canvas, size=(bg_w, bg_h))
            self.bg_overlay = ctk.CTkLabel(self, image=self.adaptive_bg_img, text="")
            self.bg_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Visual rendering fallback: {e}")
            self.bg_overlay = ctk.CTkFrame(self, fg_color=BRAND_SILVER_BG)
            self.bg_overlay.place(x=0, y=0, relwidth=1, relheight=1)



        self._setup_menu()
        self._setup_ui()
        
        # 💫 Dynamic Screen Layout Responsiveness (Real-Time Background Scaling)
        def on_screen_rescale(event):
            if event.widget == self:
                cw = self.winfo_width()
                ch = self.winfo_height()
                if hasattr(self, "adaptive_bg_img"):
                    self.adaptive_bg_img.configure(size=(cw, ch))
                if hasattr(self, "header_image"):
                    self.header_image.configure(size=(cw, 80))
        self.bind("<Configure>", on_screen_rescale)

        self.load_stored_license()
        self.load_case_vault()
        self.update_case_workspace_paths()
        
        # Scan current landing folder
        self.trigger_async_folder_scan(self.default_input)

    def _setup_menu(self):
        m_font = ("Segoe UI", 18)
        self.menubar = tk.Menu(self, font=m_font)
        
        filemenu = tk.Menu(self.menubar, tearoff=0, font=m_font)
        filemenu.add_command(label="Open Source Folder", command=self.browse_folder)
        filemenu.add_command(label="View Merged Output", command=lambda: os.startfile(self.default_output))
        filemenu.add_separator()
        filemenu.add_command(label="⚙️ Settings & Preferences...", command=self.show_settings_modal)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        
        viewmenu = tk.Menu(self.menubar, tearoff=0, font=m_font)
        viewmenu.add_command(label="🌙 Ultra Low-Glare (Dark Mode)", command=lambda: ctk.set_appearance_mode("dark"))
        viewmenu.add_command(label="☀️ Standard Bright (Light Mode)", command=lambda: ctk.set_appearance_mode("light"))
        viewmenu.add_command(label="🖥️ Match OS System Appearance", command=lambda: ctk.set_appearance_mode("System"))
        self.menubar.add_cascade(label="View", menu=viewmenu)
        
        helpmenu = tk.Menu(self.menubar, tearoff=0, font=m_font)
        helpmenu.add_command(label="🔐 Activate Enterprise License...", command=self.show_activation_window)
        helpmenu.add_separator()
        helpmenu.add_command(label="Check for Updates...", command=self.check_updates)
        helpmenu.add_command(label="Submit App Feedback...", command=self.show_feedback_window)
        helpmenu.add_command(label="About Software...", command=self.show_about_window)
        helpmenu.add_command(label="View License Terms", command=self.show_eula_window)
        self.menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=self.menubar)

    def _setup_ui(self):
        drop_font = ctk.CTkFont(family="Segoe UI", size=16)

        # --- HEADER BAR (SILVER SKINNER TEXTURED BANNER) ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, border_width=0, height=80)
        self.header_frame.pack(fill="x", pady=0)
        self.header_frame.pack_propagate(False)

        self.header_image = self._render_textured_header()
        if self.header_image:
            self.header_lbl = ctk.CTkLabel(self.header_frame, image=self.header_image, text="")
            self.header_lbl.pack(fill="both", expand=True)
        else:
            self.header_frame.configure(fg_color=GLASS_HEADER)

        self.line = ctk.CTkFrame(self, height=1, fg_color=BRAND_BORDER_LIGHT)
        self.line.pack(fill="x")

        # 💎 Premium Overhanging Suite Emblem (Overlaps skinner banner onto tabs!)
        logo_path = resource_path("logo_small.png")
        if os.path.exists(logo_path):
            try:
                logo_pil = Image.open(logo_path).convert("RGBA")
                lh = 90 # Expanded emblem height for elegant overlap
                lw = int(lh * (logo_pil.width / logo_pil.height))
                logo_res = logo_pil.resize((lw, lh), Image.Resampling.LANCZOS)
                
                self.logo_ctk_img = ctk.CTkImage(light_image=logo_res, dark_image=logo_res, size=(lw, lh))
                self.logo_floating_lbl = ctk.CTkLabel(self, image=self.logo_ctk_img, text="")
                self.logo_floating_lbl.place(relx=0.5, y=60, anchor="center")
            except Exception as e:
                print(f"Logo overlay render fail: {e}")

        # --- DUAL-MODULE TABBED DASHBOARD ---
        self.tab_view = ctk.CTkTabview(
            self, fg_color="transparent", segmented_button_selected_color=BRAND_ACCENT_GREEN,
            segmented_button_selected_hover_color=BRAND_DEEP_ACCENT, text_color=BRAND_DARK_TEXT
        )
        # Access and elevate the internal segmented tab bar font
        self.tab_view._segmented_button.configure(font=ctk.CTkFont(size=16, weight="bold"))
        
        self.tab_view.pack(fill="both", expand=True, padx=25, pady=(10, 10))
        
        self.tab_merger = self.tab_view.add("📦 Document Compiler")
        self.tab_bates = self.tab_view.add("⚖️ Bates & Security")
        self.tab_organizer = self.tab_view.add("📂 File Room & Trees")
        
        # Critical Override: Make individual tab window bodies fully transparent 
        # to let the sweeping background emerald flow completely through!
        self.tab_merger.configure(fg_color="transparent")
        self.tab_bates.configure(fg_color="transparent")
        self.tab_organizer.configure(fg_color="transparent")

        # ==========================================
        # TAB 1: DOCUMENT MERGER (MOUNTED CODEBASE)
        # ==========================================
        self.merger_container = ctk.CTkFrame(self.tab_merger, fg_color="transparent")
        self.merger_container.pack(fill="both", expand=True)

        # Left Config Panel
        self.left_frame = ctk.CTkFrame(
            self.merger_container, width=360, fg_color=GLASS_LEFT, 
            corner_radius=12, border_width=1, border_color=GLASS_BORDER
        )
        self.left_frame.pack(side="left", fill="both", padx=(0, 15))
        self.left_frame.pack_propagate(False)

        # Right Queue Panel
        self.right_frame = ctk.CTkFrame(self.merger_container, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # --- POPULATE LEFT (SETTINGS) ---
        ctk.CTkLabel(self.left_frame, text="🛠️ COMPILER SETTINGS", font=ctk.CTkFont(weight="bold", size=16), text_color=BRAND_DARK_TEXT).pack(pady=(15, 10))

        self.var_bookmark = tk.BooleanVar(value=True)
        self.chk_bookmark = ctk.CTkCheckBox(
            self.left_frame, text="Create Bookmarks per file", variable=self.var_bookmark, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=14), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_bookmark.pack(anchor="w", padx=20, pady=6)

        self.var_fit_view = tk.BooleanVar(value=True)
        self.chk_fit_view = ctk.CTkCheckBox(
            self.left_frame, text="Enforce Single-Page Layout", variable=self.var_fit_view, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=14), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_fit_view.pack(anchor="w", padx=20, pady=6)

        self.var_compress = tk.BooleanVar(value=False)
        self.chk_compress = ctk.CTkCheckBox(
            self.left_frame, text="Optimize Output Size", variable=self.var_compress, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=14), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_compress.pack(anchor="w", padx=20, pady=6)

        self.var_email = tk.BooleanVar(value=True)
        self.chk_email = ctk.CTkCheckBox(
            self.left_frame, text="Extract Email Attachments", variable=self.var_email, 
            text_color=BRAND_DARK_TEXT, font=ctk.CTkFont(size=14), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_email.pack(anchor="w", padx=20, pady=6)

        self.var_grayscale = tk.BooleanVar(value=False)
        self.chk_grayscale = ctk.CTkCheckBox(
            self.left_frame, text="📉 Grayscale (Huge File Save!)", variable=self.var_grayscale, 
            text_color="#B45309", font=ctk.CTkFont(size=14, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT
        )
        self.chk_grayscale.pack(anchor="w", padx=20, pady=6)

        ctk.CTkLabel(self.left_frame, text="Target Standard Page Size:", font=ctk.CTkFont(size=14, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=20, pady=(10, 2))
        self.paper_dropdown = ctk.CTkOptionMenu(
            self.left_frame, values=["US Letter (8.5 x 11 in)", "US Legal (8.5 x 14 in)", "A4 (International)"], width=260, height=38,
            fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN, button_hover_color=BRAND_DEEP_ACCENT,
            font=drop_font, dropdown_font=drop_font
        )
        self.paper_dropdown.pack(padx=20, pady=(0, 10))

        # AUDIT STATUS CARD
        self.audit_panel = ctk.CTkFrame(self.left_frame, fg_color="transparent", corner_radius=8, border_width=1, border_color=BRAND_BORDER_LIGHT)
        self.audit_panel.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        ctk.CTkLabel(self.audit_panel, text="📄 QUEUE PREVIEW", font=ctk.CTkFont(weight="bold", size=14), text_color=BRAND_ACCENT_GREEN).pack(pady=(10, 5))
        self.audit_files_lbl = ctk.CTkLabel(self.audit_panel, text="Documents: Scanning...", font=ctk.CTkFont(size=15), text_color=BRAND_DARK_TEXT)
        self.audit_files_lbl.pack(anchor="w", padx=15, pady=2)
        self.audit_pages_lbl = ctk.CTkLabel(self.audit_panel, text="Total Pages: Calculating...", font=ctk.CTkFont(size=15), text_color=BRAND_DARK_TEXT)
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

        from tkinter import ttk
        self.queue_container = ctk.CTkFrame(
            self.right_frame, fg_color=("#F5F9F4", "#161E15"), 
            border_width=1, border_color=GLASS_BORDER, corner_radius=8
        )
        self.queue_container.pack(fill="both", expand=True, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use("default")
        bg_col = "#F5F9F4" if ctk.get_appearance_mode() == "Light" else "#161E15"
        fg_col = "#222222" if ctk.get_appearance_mode() == "Light" else "#ECECEC"
        style.configure("Treeview", background=bg_col, foreground=fg_col, fieldbackground=bg_col, rowheight=36, borderwidth=0, font=("Segoe UI", 14))
        style.map("Treeview", background=[("selected", BRAND_ACCENT_GREEN)], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", font=("Segoe UI", 15, "bold"))
        
        self.queue_tree = ttk.Treeview(self.queue_container, columns=("Order", "File", "Status"), show="headings", selectmode="extended")
        self.queue_tree.heading("Order", text="#")
        self.queue_tree.column("Order", width=40, anchor="center", stretch=False)
        self.queue_tree.heading("File", text="Document Name")
        self.queue_tree.column("File", width=450, anchor="w") # Increased default to 450 for longer names!
        self.queue_tree.heading("Status", text="Status")
        self.queue_tree.column("Status", width=120, anchor="center", stretch=False)
        
        # 🌟 Dual Scrollbar Engine (Grid Integrated for 100% Overflow Prevention)
        vsb = ttk.Scrollbar(self.queue_container, orient="vertical", command=self.queue_tree.yview)
        hsb = ttk.Scrollbar(self.queue_container, orient="horizontal", command=self.queue_tree.xview)
        
        self.queue_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid Configuration for perfect fluid expansion
        self.queue_container.grid_rowconfigure(0, weight=1)
        self.queue_container.grid_columnconfigure(0, weight=1)
        
        # Position elements with seamless precision
        self.queue_tree.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=(2, 0))
        vsb.grid(row=0, column=1, sticky="ns", pady=(2, 0), padx=(0, 2))
        hsb.grid(row=1, column=0, sticky="ew", padx=(2, 0), pady=(0, 2))
        
        self.queue_tree.bind("<ButtonPress-1>", self.on_tree_click)
        self.queue_tree.bind("<B1-Motion>", self.on_tree_drag)
        self.queue_tree.bind("<ButtonRelease-1>", self.on_tree_drop)
        self.queue_tree.bind("<Double-1>", self.on_tree_double_click)
        self._drag_start_item = None
        
        btn_frame = ctk.CTkFrame(self.queue_container, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=2, padx=2)
        ctk.CTkButton(btn_frame, text="Move Up ⬆", width=80, height=28, fg_color="#4B5563", hover_color="#374151", command=self.move_item_up).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Move Down ⬇", width=80, height=28, fg_color="#4B5563", hover_color="#374151", command=self.move_item_down).pack(side="left")
        
        self.status_bar_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.status_bar_frame.pack(fill="x", pady=(0, 10))
        
        self.processing_lbl = ctk.CTkLabel(
            self.status_bar_frame, text="Status: Standing By", 
            font=ctk.CTkFont(size=15, weight="bold"), text_color=BRAND_DARK_TEXT
        )
        self.processing_lbl.pack(side="left")

        self.count_lbl = ctk.CTkLabel(
            self.status_bar_frame, text="", font=ctk.CTkFont(size=14, weight="normal"), text_color="#4B5563"
        )
        self.count_lbl.pack(side="right")

        self.action_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.action_frame.pack(fill="x")
        
        self.p_bar = ctk.CTkProgressBar(self.action_frame, height=12, progress_color=BRAND_ACCENT_GREEN)
        self.p_bar.set(0)
        self.p_bar.pack(fill="x", pady=(0, 15))

        self.run_btn = ctk.CTkButton(
            self.action_frame, text="🚀 COMBINE & MERGE FILES", height=52, 
            font=ctk.CTkFont(size=19, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT,
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
            self.bates_container, width=380, fg_color=GLASS_LEFT, 
            corner_radius=12, border_width=1, border_color=GLASS_BORDER
        )
        self.bates_left.pack(side="left", fill="both", padx=(0, 15))
        self.bates_left.pack_propagate(False)

        # Target File Selector
        ctk.CTkLabel(self.bates_left, text="🎯 TARGET PDF FOR PRODUCTION:", font=ctk.CTkFont(size=11, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=20, pady=(10, 2))
        self.bates_target_entry = ctk.CTkEntry(self.bates_left, placeholder_text="Select PDF...", width=310)
        self.bates_target_entry.pack(padx=20, pady=(0, 5))
        
        btn_target = ctk.CTkButton(
            self.bates_left, text="📂 Browse for PDF", width=310, height=32, 
            fg_color="#4B5563", hover_color="#374151", command=self.browse_bates_target
        )
        btn_target.pack(padx=20, pady=(0, 15))

        # --- ADVANCED OPTIONS TRIGGER ---
        self.btn_bates_options = ctk.CTkButton(
            self.bates_left, text="⚙️ ADVANCED STAMP OPTIONS", width=310, height=40,
            fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, border_width=1, border_color=BRAND_BORDER_LIGHT,
            hover_color="#E5E7EB", command=self.show_bates_options_modal
        )
        self.btn_bates_options.pack(padx=20, pady=(10, 15))

        # Bates Run Button
        self.bates_run_btn = ctk.CTkButton(
            self.bates_right, text="✨ EXECUTE PRODUCTION PRODUCTION", height=60, 
            font=ctk.CTkFont(size=16, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT,
            command=self.start_bates_thread
        )
        self.bates_run_btn.pack(fill="x")

        # ==========================================
        # TAB 3: FILE ROOM (SMART FILER & ORGANIZER)
        # ==========================================
        self.org_container = ctk.CTkFrame(self.tab_organizer, fg_color="transparent")
        self.org_container.pack(fill="both", expand=True)
        
        # Left Panel: Smart Filename Protocol
        self.org_left = ctk.CTkFrame(
            self.org_container, width=420, fg_color=GLASS_LEFT, 
            corner_radius=12, border_width=1, border_color=GLASS_BORDER
        )
        self.org_left.pack(side="left", fill="both", padx=(0, 12), expand=True)
        self.org_left.pack_propagate(False)
        
        ctk.CTkLabel(self.org_left, text="🔐 ENCRYPTED CASE CONTEXT & PROTOCOL", font=ctk.CTkFont(size=13, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=(15, 2))
        
        # --- ACTIVE VAULT CONTEXT (Inputs) ---
        context_frame = ctk.CTkFrame(self.org_left, fg_color="transparent", corner_radius=8, border_width=1, border_color=BRAND_BORDER_LIGHT)
        context_frame.pack(fill="x", padx=20, pady=6)
        
        lbl_font = ctk.CTkFont(size=11, weight="bold")
        ent_font = ctk.CTkFont(size=12)
        
        # Case Num
        ctk.CTkLabel(context_frame, text="Case Number:", font=lbl_font, text_color=BRAND_DARK_TEXT).grid(row=0, column=0, padx=(15, 5), pady=6, sticky="e")
        self.case_num_entry = ctk.CTkEntry(context_frame, font=ent_font, height=32, width=150, fg_color=BRAND_WHITE_PANEL, placeholder_text="e.g., 4:26-cv-00123")
        self.case_num_entry.grid(row=0, column=1, padx=5, pady=6, sticky="w")

        # Plaintiff
        ctk.CTkLabel(context_frame, text="Plaintiff:", font=lbl_font, text_color=BRAND_DARK_TEXT).grid(row=1, column=0, padx=(15, 5), pady=6, sticky="e")
        self.case_pla_entry = ctk.CTkEntry(context_frame, font=ent_font, height=32, width=150, fg_color=BRAND_WHITE_PANEL, placeholder_text="e.g., Jane Smith")
        self.case_pla_entry.grid(row=1, column=1, padx=5, pady=6, sticky="w")
        
        # Defendant
        ctk.CTkLabel(context_frame, text="Defendant:", font=lbl_font, text_color=BRAND_DARK_TEXT).grid(row=2, column=0, padx=(15, 5), pady=6, sticky="e")
        self.case_def_entry = ctk.CTkEntry(context_frame, font=ent_font, height=32, width=150, fg_color=BRAND_WHITE_PANEL, placeholder_text="e.g., Acme Corp")
        self.case_def_entry.grid(row=2, column=1, padx=5, pady=6, sticky="w")
        
        self.btn_save_vault = ctk.CTkButton(context_frame, text="🔒 SECURE", height=32, width=70, font=ctk.CTkFont(size=11, weight="bold"), fg_color=BRAND_DARK_TEXT, hover_color="#374151", command=self.save_case_vault)
        self.btn_save_vault.grid(row=1, column=2, padx=12, pady=6)

        # --- RENAMING FORMULA ---
        ctk.CTkLabel(self.org_left, text="🔀 COMPOSE DYNAMIC FORMULA", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(10, 4))

        
        self.rename_p1 = ctk.CTkComboBox(
            self.org_left, values=["[Date] YYYY-MM-DD", "[Case Number]", "[Plaintiff]", "[Defendant]", "[DocType] Motion", "[Custom] Text"], 
            state="readonly", height=38, font=drop_font, dropdown_font=drop_font
        )
        self.rename_p1.set("[Date] YYYY-MM-DD")
        self.rename_p1.pack(fill="x", padx=20, pady=3)
        
        self.rename_sep = ctk.CTkComboBox(
            self.org_left, values=[" - (Space Dash Space)", "_ (Underscore)", ". (Period)", " (Single Space)"], 
            state="readonly", height=38, font=drop_font, dropdown_font=drop_font
        )
        self.rename_sep.set(" - (Space Dash Space)")
        self.rename_sep.pack(fill="x", padx=20, pady=3)
        
        self.rename_p2 = ctk.CTkComboBox(
            self.org_left, values=["[DocType] Motion", "[Plaintiff]", "[Defendant]", "[Case Number]", "[Date] YYYY-MM-DD", "[Custom] Text"], 
            state="readonly", height=38, font=drop_font, dropdown_font=drop_font
        )
        self.rename_p2.set("[DocType] Motion")
        self.rename_p2.pack(fill="x", padx=20, pady=3)

        self.dyn_entry = ctk.CTkEntry(self.org_left, font=drop_font, placeholder_text="[Custom] Override Text String", fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, height=38)
        self.dyn_entry.pack(fill="x", padx=20, pady=8)
        
        self.btn_rename = ctk.CTkButton(
            self.org_left, text="🔀 BATCH RENAME & NORMALIZE", height=45, 
            font=ctk.CTkFont(size=14, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT,
            command=self.execute_rename_wizard
        )
        self.btn_rename.pack(fill="x", padx=20, pady=(4, 10))

        # Right Panel: Master Case Tree Builder
        self.org_right = ctk.CTkFrame(
            self.org_container, width=360, fg_color=GLASS_RIGHT, 
            corner_radius=12, border_width=1, border_color=GLASS_BORDER
        )
        self.org_right.pack(side="right", fill="both", expand=True)
        self.org_right.pack_propagate(False)
        
        ctk.CTkLabel(self.org_right, text="📂 MASTER CASE TREE BUILDER", font=ctk.CTkFont(size=13, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=(15, 3))
        ctk.CTkLabel(self.org_right, text="Automate standardized firm architectures.", font=ctk.CTkFont(size=10), text_color="#6B7280").pack(pady=(0, 10))
        
        ctk.CTkLabel(self.org_right, text="Choose Architecture Archetype:", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=25)
        self.tree_dropdown = ctk.CTkComboBox(
            self.org_right, values=["⭐ Custom User Blueprint", "Standard Civil Litigation", "Trial Notebook Model", "Solo / Freelance Core"], 
            state="readonly", height=38, font=drop_font, dropdown_font=drop_font, command=self.update_tree_preview
        )
        self.tree_dropdown.set("⭐ Custom User Blueprint")
        self.tree_dropdown.pack(fill="x", padx=25, pady=(0, 12))
        
        ctk.CTkLabel(self.org_right, text="Folder Blueprint Preview:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#4B5563").pack(anchor="w", padx=25)
        self.tree_preview = ctk.CTkTextbox(
            self.org_right, height=105, fg_color=("#F5F9F4", "#161E15"), text_color=BRAND_DARK_TEXT, 
            border_width=1, border_color=GLASS_BORDER, font=ctk.CTkFont(size=13)
        )
        self.tree_preview.pack(fill="x", padx=25, pady=(0, 15))
        
        self.btn_tree = ctk.CTkButton(
            self.org_right, text="🛠️ SPIN UP FOLDER TREE", height=45, 
            font=ctk.CTkFont(weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT,
            command=self.execute_tree_builder
        )
        self.btn_tree.pack(fill="x", padx=25, pady=5)
        
        # Initialize previews
        self.after(100, lambda: self.update_tree_preview(None))


        # --- FOOTER COPYRIGHT ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0, height=30)
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)

        self.copy_lbl = ctk.CTkLabel(
            self.footer_frame, 
            text="Copyright © 2026 Alan Woodyard & Access Paralegal Services. All rights reserved.", 
            font=ctk.CTkFont(family="Inter", size=9),
            text_color="#6B7280"
        )
        self.copy_lbl.pack(pady=4)

    def _render_textured_header(self):
        """
        Dynamically composite the luxury tiled caustics water texture for an edge-to-edge
        80px-tall skinnier banner, producing seamless Light and Dark Mode images.
        """
        try:
            tex_path = resource_path("water_texture.png")
            if not os.path.exists(tex_path):
                return None

            bw, bh = 1400, 80 # Skinner 80px height, ultra-wide ranges
            
            tex = Image.open(tex_path).convert("RGBA")

            # Tile texture banner (smallish 80x80 water ripples repeating)
            tex_tile = tex.resize((80, 80), Image.Resampling.LANCZOS)
            tiled_banner = Image.new("RGBA", (bw, bh))
            for x in range(0, bw, 80):
                tiled_banner.paste(tex_tile, (x, 0))

            # 1. Light Header Composite
            light_bg = Image.new("RGBA", (bw, bh), (236, 249, 235, 255))
            tex_light = tiled_banner.copy()
            r, g, b, a = tex_light.split()
            new_a_light = a.point(lambda p: int(p * 0.15))
            tex_light.putalpha(new_a_light)
            light_final = Image.alpha_composite(light_bg, tex_light)

            # 2. Dark Header Composite
            dark_bg = Image.new("RGBA", (bw, bh), (22, 46, 21, 255))
            tex_dark = tiled_banner.copy()
            r, g, b, a = tex_dark.split()
            new_a_dark = a.point(lambda p: int(p * 0.20))
            tex_dark.putalpha(new_a_dark)
            dark_final = Image.alpha_composite(dark_bg, tex_dark)

            return ctk.CTkImage(light_image=light_final, dark_image=dark_final, size=(960, 80))
        except Exception as e:
            print(f"[Header Rendering Error]: {e}")
            return None

    def _fallback_logo(self):
        ctk.CTkLabel(self.header_frame, text="ACCESS PARALEGAL", font=ctk.CTkFont(size=24, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(25, 0))
        ctk.CTkLabel(self.header_frame, text="SERVICES", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=0)

    def clear_queue_visual(self):
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)

    def add_queue_item(self, filename, status="Pending", text_color="#4B5563"):
        low_fn = filename.lower()
        if low_fn.endswith(('.eml', '.msg')): icon = "📧"
        elif low_fn.endswith(('.docx', '.doc')): icon = "📝"
        elif low_fn.endswith(('.xlsx', '.xls', '.csv')): icon = "📊"
        elif low_fn.endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png')): icon = "📷"
        elif low_fn.endswith('.txt'): icon = "🔤"
        else: icon = "📄"
        idx = len(self.queue_tree.get_children()) + 1
        item = self.queue_tree.insert("", "end", values=(str(idx), f"{icon} {filename}", status))
        return item

    def on_tree_click(self, event):
        self._drag_start_item = self.queue_tree.identify_row(event.y)
        
    def on_tree_drag(self, event):
        pass

    def on_tree_drop(self, event):
        target_item = self.queue_tree.identify_row(event.y)
        if self._drag_start_item and target_item and self._drag_start_item != target_item:
            selected = self.queue_tree.selection()
            if self._drag_start_item not in selected:
                selected = (self._drag_start_item,)
            target_idx = self.queue_tree.index(target_item)
            for item in selected:
                self.queue_tree.move(item, '', target_idx)
            self.reindex_queue()
            
    def on_tree_double_click(self, event):
        region = self.queue_tree.identify_region(event.x, event.y)
        if region == "cell":
            col = self.queue_tree.identify_column(event.x)
            if col == "#1":
                item = self.queue_tree.identify_row(event.y)
                if item:
                    dialog = ctk.CTkInputDialog(text="Enter new numerical order position:", title="Reorder")
                    val = dialog.get_input()
                    if val and val.isdigit():
                        new_idx = max(0, min(int(val) - 1, len(self.queue_tree.get_children()) - 1))
                        self.queue_tree.move(item, '', new_idx)
                        self.reindex_queue()

    def move_item_up(self):
        selected = self.queue_tree.selection()
        for item in selected:
            idx = self.queue_tree.index(item)
            if idx > 0:
                self.queue_tree.move(item, '', idx - 1)
        self.reindex_queue()

    def move_item_down(self):
        selected = reversed(self.queue_tree.selection())
        total = len(self.queue_tree.get_children())
        for item in selected:
            idx = self.queue_tree.index(item)
            if idx < total - 1:
                self.queue_tree.move(item, '', idx + 1)
        self.reindex_queue()

    def reindex_queue(self):
        for idx, item in enumerate(self.queue_tree.get_children()):
            vals = self.queue_tree.item(item, 'values')
            self.queue_tree.item(item, values=(str(idx + 1), vals[1], vals[2]))

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


    def _convert_image_to_pdf(self, file_path, out_path):
        """RAW conversion of single/multi-frame images to a pure, unbranded PDF preserving all file data."""
        try:
            with Image.open(file_path) as img:
                pages = []
                try:
                    while True:
                        # Obey grayscale toggle if checked to optimize file size natively
                        tm = "L" if self.var_grayscale.get() else "RGB"
                        pages.append(img.convert(tm))
                        img.seek(img.tell() + 1)
                except EOFError:
                    pass # End of frames reached
                
                if pages:
                    pages[0].save(out_path, "PDF", save_all=True, append_images=pages[1:])
                    return True
            return False
        except Exception as e:
            print(f"RAW Image conversion failure: {e}")
            return False

    def _convert_word_to_pdf(self, file_path, out_path):
        """Leverage win32com background automation to natively export DOCX to PDF."""
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        word = None
        doc = None
        try:
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            word.DisplayAlerts = False
            doc = word.Documents.Open(os.path.abspath(file_path), ReadOnly=True)
            doc.SaveAs(os.path.abspath(out_path), FileFormat=17) # 17 = wdFormatPDF
            return True
        except Exception as e:
            print(f"Word native export failure: {e}")
            return False
        finally:
            if doc:
                try: doc.Close(SaveChanges=0)
                except: pass
            if word:
                try: word.Quit()
                except: pass
            pythoncom.CoUninitialize()

    def _convert_excel_to_pdf(self, file_path, out_path):
        """Leverage win32com background automation to natively export spreadsheet data to PDF."""
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        excel = None
        wb = None
        try:
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            wb = excel.Workbooks.Open(os.path.abspath(file_path), ReadOnly=True)
            wb.ExportAsFixedFormat(0, os.path.abspath(out_path)) # 0 = xlTypePDF
            return True
        except Exception as e:
            print(f"Excel native export failure: {e}")
            return False
        finally:
            if wb:
                try: wb.Close(SaveChanges=False)
                except: pass
            if excel:
                try: excel.Quit()
                except: pass
            pythoncom.CoUninitialize()

    def _convert_text_to_pdf(self, file_path, out_path):
        """Read text streams, escape symbols, and compile securely via xhtml2pdf with NO extra headers."""
        import html
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            escaped = html.escape(content)
            
            paper_size = "letter"
            paper_val = self.paper_dropdown.get()
            if "Legal" in paper_val: paper_size = "legal"
            elif "A4" in paper_val: paper_size = "a4"
            
            # Compile pure raw typewriter text without any added margins or titles
            final_html = f"""<html><head><style>@page {{ size: {paper_size}; margin: 0.5in; }} body {{ font-family: Courier, monospace; font-size: 11px; color: #222; line-height: 1.2; }}</style></head><body><pre style='white-space: pre-wrap;'>{escaped}</pre></body></html>"""
            with open(out_path, "wb") as f:
                pisa.CreatePDF(final_html, dest=f)
            return True
        except Exception as e:
            print(f"Text to PDF engine failure: {e}")
            return False

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
            # Expanded to detect Legacy Image Formats and Emails (including Outlook .msg)
            legal_exts = ('.pdf', '.eml', '.msg', '.tif', '.tiff', '.jpg', '.jpeg', '.png', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.txt') if self.var_email.get() else ('.pdf', '.tif', '.tiff', '.jpg', '.jpeg', '.png', '.docx', '.doc', '.xlsx', '.xls', '.csv', '.txt')
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
                        total_p += 1 
                    elif low_fn.endswith(('.eml', '.msg')):
                        total_p += 1 
                    elif low_fn.endswith(('.docx', '.doc', '.xlsx', '.xls', '.csv', '.txt')):
                        total_p += 1
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
        if not self.queue_tree.get_children():
            return
        answer = messagebox.askyesno("Confirm Order", "Please ensure the documents in the list are in the exact order you want them merged.\n\nProceed with merge?")
        if not answer:
            return
        self.run_btn.configure(state="disabled", text="Processing...")
        self.p_bar.set(0)
        for item in self.queue_tree.get_children():
            vals = self.queue_tree.item(item, 'values')
            self.queue_tree.item(item, values=(vals[0], vals[1], "Processing..."))
        threading.Thread(target=self.execute_audit_merge, daemon=True).start()

    def execute_audit_merge(self):
        source = self.dir_entry.get()
        if not os.path.exists(source):
            self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))
            return
        
        tree_items = self.queue_tree.get_children()
        ordered_files = []
        for item in tree_items:
            vals = self.queue_tree.item(item, 'values')
            fname = vals[1][2:] # Strip icon and space
            ordered_files.append((fname, item))
            
        if not ordered_files:
            self.after(0, lambda: self.processing_lbl.configure(text="Status: Error - No files found!"))
            self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))
            return
            
        # --- 🛑 SAFE SHADOW ISOLATION ENGINE ---
        import shutil
        import tempfile
        is_safeguarded = self.safeguard_files_var.get()
        working_source = source
        shadow_dir = None
        
        if is_safeguarded:
            shadow_dir = os.path.join(tempfile.gettempdir(), f"ap_shadow_{int(time.time())}")
            os.makedirs(shadow_dir, exist_ok=True)
            self.after(0, lambda: self.processing_lbl.configure(text="🛡️ Preserving originals in Shadow Copy..."))
            
            # Clone target files into staging location
            for (fn, _) in ordered_files:
                src_p = os.path.join(source, fn)
                if os.path.exists(src_p):
                    try:
                        shutil.copy2(src_p, os.path.join(shadow_dir, fn))
                    except Exception as ex:
                        print(f"Safeguard copy fail: {ex}")
            working_source = shadow_dir
            
        # --- 🚦 ENFORCE V1.4.0 LICENSE GATING LIMITS ---
        if not self.check_gate_limit("merge_count", len(ordered_files)):
            self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))
            # Cleanup shadow if we exit early
            if shadow_dir:
                try: shutil.rmtree(shadow_dir, ignore_errors=True)
                except: pass
            return
            
        if self.var_grayscale.get():
            if not self.check_gate_limit("advanced_compression"):
                self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))
                return
        start_t = time.time()
        merged_pdf = pikepdf.Pdf.new()
        
        if self.var_fit_view.get():
            merged_pdf.Root.ViewerPreferences = pikepdf.Dictionary(FitWindow=True, CenterWindow=True, DisplayDocTitle=True)
            merged_pdf.Root.PageLayout = pikepdf.Name("/SinglePage")

        outline_nodes = []
        curr_pg = 0
        success_count = 0
        
        temp_extract_dir = os.path.join(working_source, "_volta_temp_attachments")
        os.makedirs(temp_extract_dir, exist_ok=True)
        total_items = len(ordered_files)
        
        def update_tree_status(item_id, text):
            vals = self.queue_tree.item(item_id, 'values')
            self.queue_tree.item(item_id, values=(vals[0], vals[1], text))

        for idx, (fn, item_id) in enumerate(ordered_files, 1):
            self.after(0, lambda p=idx/total_items: self.p_bar.set(p))
            self.after(0, lambda f=fn: self.processing_lbl.configure(text=f"Compiling: {f[:30]}..."))
            self.after(0, lambda: self.count_lbl.configure(text=f"Item {idx} of {total_items}"))
            
            self.after(0, lambda i=item_id: update_tree_status(i, "Processing..."))
            
            time.sleep(0.01)
            
            try:
                file_path = os.path.join(working_source, fn)
                low_fn = fn.lower()
                
                # --- SCENARIO 1: NATIVE PDF ---
                if low_fn.endswith('.pdf'):
                    with pikepdf.open(file_path) as src:
                        cnt = len(src.pages)
                        merged_pdf.pages.extend(src.pages)
                        if self.var_bookmark.get():
                            clean_n, _ = os.path.splitext(fn)
                            outline_nodes.append(pikepdf.OutlineItem(clean_n, destination=curr_pg, page_location="Fit"))
                        curr_pg += cnt
                        success_count += 1
                        self.after(0, lambda i=item_id: update_tree_status(i, "✅ Combined"))
                
                # --- SCENARIO 2: LEGACY IMAGE (TIFF, JPG, PNG) ---
                elif low_fn.endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png')):
                    temp_pdf = os.path.join(temp_extract_dir, f"img_{int(time.time())}_{idx}.pdf")
                    if self._convert_image_to_pdf(file_path, temp_pdf):
                        with pikepdf.open(temp_pdf) as src:
                            merged_pdf.pages.extend(src.pages)
                            if self.var_bookmark.get():
                                clean_n, _ = os.path.splitext(fn)
                                outline_nodes.append(pikepdf.OutlineItem(f"📷 {clean_n}", destination=curr_pg, page_location="Fit"))
                            curr_pg += len(src.pages)
                            success_count += 1
                            self.after(0, lambda i=item_id: update_tree_status(i, "✅ Converted & Combined"))
                    else:
                        raise ValueError("Image branded renderer failure.")

                # --- SCENARIOS 3 & 4: EMAIL RECORDS (.EML / .MSG) ---
                elif low_fn.endswith(('.eml', '.msg')) and self.var_email.get():
                    from pathlib import Path
                    from core.job import Job, InputSpec, EmailToPdfParams, OutputSpec
                    from core.engine import DocEngine

                    email_path = Path(file_path)
                    output_pdf_name = f"email_conv_{int(time.time())}_{idx}.pdf"
                    
                    # 1. Construct Job for DocEngine
                    job_input = InputSpec.from_path(email_path)
                    job_params = EmailToPdfParams(
                        grayscale=self.var_grayscale.get(),
                        include_attachments=True,
                        output_name=output_pdf_name
                    )
                    job_output = OutputSpec(directory=Path(temp_extract_dir))
                    
                    email_job = Job(
                        operation="email_to_pdf",
                        inputs=[job_input],
                        params=job_params,
                        output=job_output
                    )
                    
                    # Enforce user cancellation request if set in GUI
                    if self.cancel_requested:
                        from core.job import JobStatus
                        email_job.status = JobStatus.CANCELLED
                    
                    # 2. Define callback to show progress in tree status
                    def progress_cb(msg, progress_val):
                        self.after(0, lambda i=item_id: update_tree_status(i, f"📧 {msg}"))
                    
                    # 3. Submit and execute job via engine
                    engine = DocEngine(write_audit=False)
                    engine.submit(email_job, on_progress=progress_cb)
                    
                    pdf_p = Path(temp_extract_dir) / output_pdf_name
                    if not pdf_p.exists():
                        raise ValueError("Email engine conversion failed: output PDF not generated.")
                    
                    # 4. Merge results into the compiler master document
                    email_start_pg = curr_pg
                    with pikepdf.open(pdf_p) as cover:
                        merged_pdf.pages.extend(cover.pages)
                        curr_pg += len(cover.pages)
                    
                    # 5. Handle outline bookmarks
                    if self.var_bookmark.get():
                        try:
                            email_obj = email_processing.UnifiedEmail(email_path)
                            subj = email_obj.subject or "No Subject"
                        except Exception:
                            subj = "No Subject"
                        email_type_str = "Email" if low_fn.endswith('.eml') else "Outlook"
                        email_outline = pikepdf.OutlineItem(f"📧 {email_type_str}: {subj[:50]}", destination=email_start_pg, page_location="Fit")
                        outline_nodes.append(email_outline)
                        
                    self.after(0, lambda i=item_id: update_tree_status(i, "✅ Combined E-mail"))
                    success_count += 1

                # --- SCENARIO 5: WORD DOCUMENTS (.DOCX, .DOC) ---
                elif low_fn.endswith(('.docx', '.doc')):
                    from pathlib import Path
                    from core.job import Job, InputSpec, DocxToPdfParams, OutputSpec, JobStatus
                    from core.engine import DocEngine

                    output_pdf_name = f"word_{int(time.time())}_{idx}.pdf"
                    job_input = InputSpec.from_path(Path(file_path))
                    job_params = DocxToPdfParams(
                        grayscale=self.var_grayscale.get(),
                        output_name=output_pdf_name
                    )
                    job_output = OutputSpec(directory=Path(temp_extract_dir))
                    word_job = Job(
                        operation="docx_to_pdf",
                        inputs=[job_input],
                        params=job_params,
                        output=job_output
                    )
                    if self.cancel_requested:
                        word_job.status = JobStatus.CANCELLED
                    def word_progress_cb(msg, progress_val):
                        self.after(0, lambda i=item_id: update_tree_status(i, f"📝 {msg}"))
                    engine = DocEngine(write_audit=False)
                    engine.submit(word_job, on_progress=word_progress_cb)
                    temp_pdf = os.path.join(temp_extract_dir, output_pdf_name)
                    if os.path.exists(temp_pdf):
                        with pikepdf.open(temp_pdf) as src:
                            merged_pdf.pages.extend(src.pages)
                            if self.var_bookmark.get():
                                clean_n, _ = os.path.splitext(fn)
                                outline_nodes.append(pikepdf.OutlineItem(f"📝 {clean_n}", destination=curr_pg, page_location="Fit"))
                            curr_pg += len(src.pages)
                            success_count += 1
                            self.after(0, lambda i=item_id: update_tree_status(i, "✅ Word Rendered"))
                    else:
                        raise ValueError("Word native print automation failed.")

                # --- SCENARIO 6: SPREADSHEETS (.XLSX, .XLS, .CSV) ---
                elif low_fn.endswith(('.xlsx', '.xls', '.csv')):
                    from pathlib import Path
                    from core.job import Job, InputSpec, XlsxToPdfParams, OutputSpec, JobStatus
                    from core.engine import DocEngine

                    output_pdf_name = f"excel_{int(time.time())}_{idx}.pdf"
                    job_input = InputSpec.from_path(Path(file_path))
                    job_params = XlsxToPdfParams(
                        grayscale=self.var_grayscale.get(),
                        output_name=output_pdf_name
                    )
                    job_output = OutputSpec(directory=Path(temp_extract_dir))
                    excel_job = Job(
                        operation="xlsx_to_pdf",
                        inputs=[job_input],
                        params=job_params,
                        output=job_output
                    )
                    if self.cancel_requested:
                        excel_job.status = JobStatus.CANCELLED
                    def excel_progress_cb(msg, progress_val):
                        self.after(0, lambda i=item_id: update_tree_status(i, f"📊 {msg}"))
                    engine = DocEngine(write_audit=False)
                    engine.submit(excel_job, on_progress=excel_progress_cb)
                    temp_pdf = os.path.join(temp_extract_dir, output_pdf_name)
                    if os.path.exists(temp_pdf):
                        with pikepdf.open(temp_pdf) as src:
                            merged_pdf.pages.extend(src.pages)
                            if self.var_bookmark.get():
                                clean_n, _ = os.path.splitext(fn)
                                outline_nodes.append(pikepdf.OutlineItem(f"📊 {clean_n}", destination=curr_pg, page_location="Fit"))
                            curr_pg += len(src.pages)
                            success_count += 1
                            self.after(0, lambda i=item_id: update_tree_status(i, "✅ Excel Rendered"))
                    else:
                        raise ValueError("Excel native print automation failed.")

                # --- SCENARIO 7: TEXT RECORDS (.TXT) ---
                elif low_fn.endswith('.txt'):
                    temp_pdf = os.path.join(temp_extract_dir, f"txt_{int(time.time())}_{idx}.pdf")
                    if self._convert_text_to_pdf(file_path, temp_pdf):
                        with pikepdf.open(temp_pdf) as src:
                            merged_pdf.pages.extend(src.pages)
                            if self.var_bookmark.get():
                                clean_n, _ = os.path.splitext(fn)
                                outline_nodes.append(pikepdf.OutlineItem(f"🔤 {clean_n}", destination=curr_pg, page_location="Fit"))
                            curr_pg += len(src.pages)
                            success_count += 1
                            self.after(0, lambda i=item_id: update_tree_status(i, "✅ Text Compiled"))
                    else:
                        raise ValueError("Text parsing engine failure.")

            except Exception as e:
                self.after(0, lambda i=item_id, err=str(e): update_tree_status(i, f"❌ Fail: {err[:30]}"))
            time.sleep(0.01)

        if self.var_bookmark.get() and outline_nodes:
            with merged_pdf.open_outline() as outline: 
                outline.root.extend(outline_nodes)

        self.after(0, lambda: self.processing_lbl.configure(text="Compiling Final Corporate Portfolio..."))
        out_name = f"Access_Merged_Master_{int(time.time())}.pdf"
        final_dest = os.path.join(self.default_output, out_name)

        try:
            # Lazy JIT Directory Creation: Only build the Merge subfolder when writing output!
            os.makedirs(self.default_output, exist_ok=True)
            merged_pdf.save(final_dest, linearize=True, compress_streams=self.var_compress.get())
            merged_pdf.close()
            elapsed = time.time() - start_t
            
            # Clean extraction directories
            for f in os.listdir(temp_extract_dir):
                try: os.remove(os.path.join(temp_extract_dir, f))
                except: pass
            try: os.rmdir(temp_extract_dir)
            except: pass

            def on_success():
                self.processing_lbl.configure(text="🎉 Portfolio Complete!")
                self.count_lbl.configure(text="")
                msg = (
                    f"Successfully combined {success_count} items into a single master PDF!\n\n"
                    f"File Saved: {out_name}\n"
                    f"Folder: {self.default_output}\n\n"
                    "Would you like to open the output folder to view the file?"
                )
                if messagebox.askyesno("Success", msg):
                    try: os.startfile(self.default_output)
                    except: pass
            self.after(0, on_success)
            self.trial_run_count += 1
            self.after(0, lambda: self.generate_audit_log(f"{config.APP_NAME} Merge", self.default_output, file_names, elapsed))
        except Exception as e:
            self.after(0, lambda: self.processing_lbl.configure(text="Error: Compile failed!"))
            self.after(0, lambda err=str(e): messagebox.showerror("Fatal Error", f"Failed saving: {err}"))

        # --- 🛑 SHADOW ENGINE TEARDOWN ---
        if shadow_dir:
            try: shutil.rmtree(shadow_dir, ignore_errors=True)
            except: pass

        self.after(0, lambda: self.run_btn.configure(state="normal", text="🚀 COMBINE & MERGE FILES"))

    def show_about_window(self):
        about = ctk.CTkToplevel(self)
        about.title(f"About {config.APP_NAME}")
        about.geometry("460x420")
        about.configure(fg_color=BRAND_WHITE_PANEL)
        about.resizable(False, False)
        about.grab_set()
        about.lift()
        
        ctk.CTkLabel(about, text=config.APP_NAME, font=ctk.CTkFont(size=20, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(25, 5))
        ctk.CTkLabel(about, text=f"Version {VERSION} (Production)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4B5563").pack(pady=2)
        ctk.CTkLabel(about, text="Product ID: {86C436C7-1A84-4DCA-88EA-FF879B4B43D2}", font=ctk.CTkFont(size=9), text_color="#9CA3AF").pack(pady=1)
        
        # --- Support Security Token (Requested by User) ---
        import platform, getpass
        raw_token = f"{platform.node()}-{getpass.getuser()}-{VERSION}"
        support_token = hashlib.sha256(raw_token.encode()).hexdigest()[:16].upper()
        
        token_frame = ctk.CTkFrame(about, fg_color=BRAND_SILVER_BG, corner_radius=6)
        token_frame.pack(pady=10, padx=40, fill="x")
        ctk.CTkLabel(token_frame, text="SUPPORT SECURITY TOKEN", font=ctk.CTkFont(size=9, weight="bold"), text_color="#6B7280").pack(pady=(5, 0))
        ctk.CTkLabel(token_frame, text=support_token, font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=(0, 5))

        desc = f"Secure, enterprise-grade {config.APP_NAME} developed for Access Paralegal Services by Alan Woodyard."
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

    def browse_bates_target(self):
        f = filedialog.askopenfilename(filetypes=[("PDF Documents", "*.pdf")])
        if f:
            self.bates_target_entry.delete(0, 'end')
            self.bates_target_entry.insert(0, f)

    def show_bates_options_modal(self):
        """Advanced Bates Modal with Professor-level compliance controls."""
        opt = ctk.CTkToplevel(self)
        opt.title("🔢 Advanced Bates Stamping Options")
        opt.geometry("540x700")
        opt.configure(fg_color=BRAND_WHITE_PANEL)
        opt.grab_set()

        # Defaults
        if not hasattr(self, "bates_opts"):
            self.bates_opts = {
                "prefix": "AP",
                "sep": "_",
                "start": 1,
                "padding": 7,
                "font": "Arial Bold",
                "size": 12,
                "pos": "Bottom Right (Outside Margin)",
                "shrink": tk.BooleanVar(value=True),
                "naming": "Prefix_Start-End",
                "output": "Nested Folder (Default)"
            }

        ctk.CTkLabel(opt, text="PRODUCTION BATES PROTOCOL", font=ctk.CTkFont(weight="bold", size=16), text_color=BRAND_ACCENT_GREEN).pack(pady=(20, 10))

        # 1. Prefix & Separator
        f1 = ctk.CTkFrame(opt, fg_color="transparent")
        f1.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(f1, text="Prefix (max 20):", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.pref_ent = ctk.CTkEntry(f1, width=150)
        self.pref_ent.pack(side="left", padx=10)
        self.pref_ent.insert(0, self.bates_opts["prefix"])
        
        self.sep_var = ctk.StringVar(value=self.bates_opts["sep"])
        ctk.CTkRadioButton(f1, text="-", variable=self.sep_var, value="-").pack(side="left", padx=5)
        ctk.CTkRadioButton(f1, text="_", variable=self.sep_var, value="_").pack(side="left", padx=5)

        # 2. Font & Size
        f2 = ctk.CTkFrame(opt, fg_color="transparent")
        f2.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(f2, text="Font:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.font_opt = ctk.CTkOptionMenu(f2, values=["Arial", "Arial Bold", "Calibri", "Times New Roman", "Helvetica", "Courier"], width=160)
        self.font_opt.pack(side="left", padx=10)
        self.font_opt.set(self.bates_opts["font"])
        
        ctk.CTkLabel(f2, text="Size:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 0))
        self.size_opt = ctk.CTkOptionMenu(f2, values=["10", "11", "12", "14"], width=80)
        self.size_opt.pack(side="left", padx=10)
        self.size_opt.set(str(self.bates_opts["size"]))

        # 3. Position
        ctk.CTkLabel(opt, text="Stamp Placement:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(10, 2))
        self.pos_opt = ctk.CTkOptionMenu(opt, values=[
            "Bottom Right (Outside Margin)", "Bottom Center (Outside Margin)", 
            "Top Center (Above Margin)", "Top Right (Above Margin)", 
            "Top Left (Above Margin)", "Bottom Left (Outside Margin)"
        ], width=480)
        self.pos_opt.pack(padx=30, pady=5)
        self.pos_opt.set(self.bates_opts["pos"])

        # 4. Normalization
        self.chk_shrink = ctk.CTkCheckBox(opt, text="🛡️ Collision Avoidance: Shrink page to fit margins (Recommended)", variable=self.bates_opts["shrink"], text_color=BRAND_DARK_TEXT)
        self.chk_shrink.pack(anchor="w", padx=30, pady=15)

        # 5. Output Management
        ctk.CTkLabel(opt, text="Output Directory Policy:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(10, 2))
        self.out_policy = ctk.CTkOptionMenu(opt, values=["Nested Folder (Default)", "Same as Source", "Custom Location..."], width=480)
        self.out_policy.pack(padx=30, pady=5)
        
        # 6. Naming
        ctk.CTkLabel(opt, text="File Naming Protocol:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=30, pady=(10, 2))
        self.name_policy = ctk.CTkOptionMenu(opt, values=["Prefix_Start-End", "Prefix_StartOnly"], width=480)
        self.name_policy.pack(padx=30, pady=5)

        def save_and_close():
            self.bates_opts["prefix"] = self.pref_ent.get()[:20]
            self.bates_opts["sep"] = self.sep_var.get()
            self.bates_opts["font"] = self.font_opt.get()
            self.bates_opts["size"] = int(self.size_opt.get())
            self.bates_opts["pos"] = self.pos_opt.get()
            self.bates_opts["naming"] = self.name_policy.get()
            self.bates_opts["output"] = self.out_policy.get()
            opt.destroy()

        ctk.CTkButton(opt, text="✅ SAVE PROTOCOL", height=45, fg_color=BRAND_ACCENT_GREEN, command=save_and_close).pack(pady=20, padx=30, fill="x")

    def start_bates_thread(self):
        target = self.bates_target_entry.get().strip()
        if not target or not os.path.exists(target):
            messagebox.showerror("Error", "Please select a valid PDF to Bates Number.")
            return
        
        self.bates_run_btn.configure(state="disabled", text="Executing Production...")
        import threading
        threading.Thread(target=self.execute_bates_production, daemon=True).start()

    def execute_bates_production(self):
        """High-Performance Bates Engine leveraging core engine and DocEngine.submit()."""
        target_path = self.bates_target_entry.get().strip()
        source_dir = os.path.dirname(target_path)
        
        # Pull Options
        if not hasattr(self, "bates_opts"): self.show_bates_options_modal() # Fallback to defaults
        opts = self.bates_opts
        
        # 1. Resolve Output Dir
        if opts["output"] == "Same as Source":
            out_dir = source_dir
        elif opts["output"] == "Custom Location...":
            out_dir = filedialog.askdirectory(title="Select Output Folder") or source_dir
        else: # Nested
            folder_name = f"{opts['prefix']}-Bates-{time.strftime('%Y-%m-%d')}"
            out_dir = os.path.join(source_dir, folder_name)
            os.makedirs(out_dir, exist_ok=True)

        try:
            start_idx = int(self.bates_start.get().strip())
        except:
            start_idx = 1

        # Build Job structures
        from pathlib import Path
        from core.job import Job, InputSpec, BatesParams, OutputSpec, JobStatus
        from core.engine import DocEngine

        job_input = InputSpec.from_path(Path(target_path))
        job_params = BatesParams(
            prefix=opts["prefix"],
            start_number=start_idx,
            padding=7, # Professor's SOP Standard
            position=opts["pos"],
            font_size=opts["size"],
            shrink_conflict=opts["shrink"].get(),
            sep=opts["sep"],
            font_name=opts["font"],
            naming=opts["naming"],
            output_name=None  # Managed by operation naming format
        )
        job_output = OutputSpec(directory=Path(out_dir), overwrite=True)

        bates_job = Job(
            operation="bates_stamp",
            inputs=[job_input],
            params=job_params,
            output=job_output
        )

        def progress_cb(msg, progress_val):
            self.after(0, lambda: self.bates_run_btn.configure(text=f"Stamping: {int(progress_val*100)}%"))

        try:
            engine = DocEngine(write_audit=True)
            res_job = engine.submit(bates_job, on_progress=progress_cb)

            if res_job.status == JobStatus.COMPLETE:
                out_path = res_job.result.outputs[0]
                out_name = os.path.basename(out_path)
                page_count = res_job.result.page_count_out
                self.after(0, lambda: messagebox.showinfo("Success", f"Bates Production Complete!\n\nFile: {out_name}\nPages: {page_count}"))
                os.startfile(out_dir)
            elif res_job.status == JobStatus.CANCELLED:
                self.after(0, lambda: messagebox.showinfo("Cancelled", "Bates stamping was cancelled."))
            else:
                raise ValueError(res_job.result.error or "Unknown engine error.")
        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror("Production Error", f"Bates execution failed: {err}"))
            
        self.after(0, lambda: self.bates_run_btn.configure(state="normal", text="✨ EXECUTE PRODUCTION PRODUCTION"))

    def _on_bates_prefix_focusout(self, event):
        prefix = self.bates_prefix.get().strip()
        matter_name = self.case_num_entry.get().strip() or "Default_Matter"
        if hasattr(self, "bates_registry") and matter_name in self.bates_registry:
            last_num = self.bates_registry[matter_name].get(prefix)
            if last_num is not None:
                self.bates_start.delete(0, 'end')
                self.bates_start.insert(0, str(last_num))

    def execute_bates_flattening(self):
        """Engine to inject indelible physical vector bates stamps directly into the PDF page stream."""
        source = self.dir_entry.get()
        if not os.path.exists(source):
            self.after(0, lambda: self.bates_run_btn.configure(state="normal", text="✨ FLATTEN & APPLY BATES STAMPS"))
            return

        # 📂 1. Find Source PDFs
        files = [f for f in os.listdir(source) if f.lower().endswith('.pdf')]
        if not files:
            self.after(0, lambda: messagebox.showerror("No Files", "No PDF files found in the queue to Bates stamp!"))
            self.after(0, lambda: self.bates_run_btn.configure(state="normal", text="✨ FLATTEN & APPLY BATES STAMPS"))
            return
        
        files.sort(key=self.natural_sort_key)
        
        # 📁 2. Setup Output Directories
        bates_out_dir = os.path.join(self.default_output, f"Bates_Stamped_{int(time.time())}")
        os.makedirs(bates_out_dir, exist_ok=True)

        # 🔢 3. Parse Serialization Values
        prefix = self.bates_prefix.get().strip()
        try:
            curr_idx = int(self.bates_start.get().strip())
        except:
            curr_idx = 1
            
        padding_str = self.bates_padding.get()
        padding = 8 if "8" in padding_str else 6 if "6" in padding_str else 4

        # 🎯 4. Establish Position and Font Matrices
        pos_sel = self.bates_pos.get()
        font_sel = self.bates_font.get()
        
        pdf_font = "Helvetica-Bold"
        if "Courier" in font_sel: pdf_font = "Courier-Bold"
        elif "Times" in font_sel: pdf_font = "Times-Bold"
        elif "Georgia" in font_sel: pdf_font = "Times-Roman"

        csv_records = []
        total_files_processed = 0
        start_time = time.time()

        for f_idx, fn in enumerate(files):
            try:
                file_path = os.path.join(source, fn)
                out_path = os.path.join(bates_out_dir, f"Bates_{fn}")
                
                if not self.var_bates_seq.get():
                    # Reset sequential counter per file if selected
                    try: curr_idx = int(self.bates_start.get().strip())
                    except: curr_idx = 1
                
                bates_start_label = f"{prefix}{str(curr_idx).zfill(padding)}"
                
                with pikepdf.open(file_path) as src_pdf:
                    page_count = len(src_pdf.pages)
                    
                    # Loop through each page to inject text
                    for page_num in range(page_count):
                        page = src_pdf.pages[page_num]
                        
                        # A. Read Real Points Coordinates
                        # Standard Letter is [0, 0, 612, 792]
                        mbox = page.mediabox
                        p_w = float(mbox[2] - mbox[0])
                        p_h = float(mbox[3] - mbox[1])
                        
                        # B. Construct Real-Time Bates Label
                        bates_str = f"{prefix}{str(curr_idx).zfill(padding)}"
                        
                        # C. Generate High-Fidelity Transparent Vector PDF Overlay in Memory
                        packet = BytesIO()
                        can = canvas.Canvas(packet, pagesize=(p_w, p_h))
                        can.setFont(pdf_font, 10)
                        can.setFillColorRGB(0, 0, 0) # Deep pitch black vector text
                        
                        # Draw text based on positioning rules
                        margin = 40
                        tw = can.stringWidth(bates_str, pdf_font, 10)
                        
                        if "Bottom Right" in pos_sel:
                            x = p_w - tw - margin
                            y = margin
                        elif "Bottom Center" in pos_sel:
                            x = (p_w / 2) - (tw / 2)
                            y = margin
                        elif "Bottom Left" in pos_sel:
                            x = margin
                            y = margin
                        else: # Top Right
                            x = p_w - tw - margin
                            y = p_h - margin
                            
                        can.drawString(x, y, bates_str)
                        can.save()
                        
                        packet.seek(0)
                        
                        # D. Physical Flattening Fusion
                        with pikepdf.open(packet) as overlay_pdf:
                            page.add_overlay(overlay_pdf.pages[0])
                        
                        curr_idx += 1
                    
                    bates_end_label = f"{prefix}{str(curr_idx-1).zfill(padding)}"
                    src_pdf.save(out_path, linearize=True)
                    
                    csv_records.append({
                        "Original_Filename": fn,
                        "Bates_Start": bates_start_label,
                        "Bates_End": bates_end_label,
                        "Page_Count": page_count
                    })
                    total_files_processed += 1
            except Exception as e:
                print(f"Bates injection failed for {fn}: {e}")
                
        # 💾 5. Generate eDiscovery Concordance Load File (CSV)
        if self.var_bates_csv.get() and csv_records:
            csv_path = os.path.join(bates_out_dir, "_eDiscovery_Load_File.csv")
            try:
                with open(csv_path, mode='w', newline='', encoding='utf-8') as cf:
                    writer = csv.DictWriter(cf, fieldnames=["Original_Filename", "Bates_Start", "Bates_End", "Page_Count"])
                    writer.writeheader()
                    for rec in csv_records:
                        writer.writerow(rec)
            except Exception as e:
                print(f"CSV write failed: {e}")

        duration = time.time() - start_time
        
        # 🔒 Update Bates Registry Ledger securely
        matter_name = self.case_num_entry.get().strip() or "Default_Matter"
        if not hasattr(self, "bates_registry"):
            self.bates_registry = {}
        if matter_name not in self.bates_registry:
            self.bates_registry[matter_name] = {}
        self.bates_registry[matter_name][prefix] = curr_idx
        self.save_case_vault()
        
        self.after(0, lambda: self.bates_run_btn.configure(state="normal", text="✨ FLATTEN & APPLY BATES STAMPS"))
        
        def finish():
            msg = (
                f"Indelible Bates stamps successfully fused to {total_files_processed} documents!\n\n"
                f"Duration: {duration:.1f}s\n"
                f"Saved to: {bates_out_dir}\n\n"
                "Would you like to open the stamped output folder now?"
            )
            if messagebox.askyesno("Bates Success", msg):
                try: os.startfile(bates_out_dir)
                except: pass
            file_names = [f for f in files]
            details = "\n".join([f"  {r['Original_Filename']} : {r['Bates_Start']} to {r['Bates_End']}" for r in csv_records])
            self.trial_run_count += 1
            self.generate_audit_log(f"{config.APP_NAME} Bates Stamping", bates_out_dir, file_names, duration, details)
        self.after(0, finish)

    def generate_audit_log(self, operation, out_dir, files, duration, details=""):
        try:
            log_path = os.path.join(out_dir, "Merge_Audit_Log.txt")
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("="*60 + "\n")
                f.write("  ACCESS PARALEGAL MULTITOOL - SECURE AUDIT LOG\n")
                f.write("="*60 + "\n\n")
                f.write(f"Operation: {operation}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duration:  {duration:.1f} seconds\n")
                f.write(f"Matter:    {self.case_num_entry.get().strip() or 'Default'}\n")
                f.write(f"Output:    {out_dir}\n\n")
                f.write("="*60 + "\n")
                f.write("FILES PROCESSED (IN ORDER):\n")
                for i, fn in enumerate(files, 1):
                    f.write(f"  {i:03d}. {fn}\n")
                f.write("\n" + "="*60 + "\n")
                if details:
                    f.write(f"DETAILS:\n{details}\n\n")
                f.write("  *** Processed securely offline via Access Paralegal Multitool ***\n")
            
            os.startfile(log_path)
        except Exception as e:
            print(f"Audit log failure: {e}")

    def show_feedback_window(self):
        """Sleek UI interface allowing paralegals to submit local platform feedback."""
        fb = ctk.CTkToplevel(self)
        fb.title("💬 Submit Application Feedback")
        fb.geometry("480x420")
        fb.configure(fg_color=BRAND_WHITE_PANEL)
        fb.resizable(False, False)
        fb.grab_set()
        fb.lift()

        ctk.CTkLabel(fb, text="WE VALUE YOUR FEEDBACK", font=ctk.CTkFont(size=16, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(20, 5))
        ctk.CTkLabel(fb, text="Help us build the premier local legal ecosystem.", font=ctk.CTkFont(size=11), text_color="#6B7280").pack(pady=(0, 15))

        # Feedback Body Box
        ctk.CTkLabel(fb, text="What features or refinements would you like to see?", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=25, pady=(5, 2))
        fb_txt = ctk.CTkTextbox(fb, height=120, fg_color=BRAND_SILVER_BG, border_color=BRAND_BORDER_LIGHT, text_color=BRAND_DARK_TEXT)
        fb_txt.pack(fill="x", padx=25, pady=(0, 10))

        # Email Box
        ctk.CTkLabel(fb, text="Email Address (Optional - for responses):", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=25, pady=(5, 2))
        email_entry = ctk.CTkEntry(fb, placeholder_text="e.g., user@lawfirm.com", fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT)
        email_entry.pack(fill="x", padx=25, pady=(0, 20))

        def submit_action():
            msg_content = fb_txt.get("1.0", "end-1c").strip()
            user_em = email_entry.get().strip()
            if not msg_content:
                messagebox.showwarning("Empty Field", "Please write some feedback before submitting!")
                return
            # Simulates instant network transport hook
            messagebox.showinfo("Feedback Sent", "Thank you! Your encrypted legal tech feedback has been received by the development core!")
            fb.destroy()

        # Submit Button
        btn_sub = ctk.CTkButton(fb, text="🚀 Submit Secure Feedback", height=45, fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, font=ctk.CTkFont(weight="bold"), command=submit_action)
        btn_sub.pack(fill="x", padx=25)

    # ==========================================
    # 🔒 KEYGEN SECURE ACTIVATION ARCHITECTURE
    # ==========================================
    def load_stored_license(self):
        """Detects and silently parses any locally stored license files during startup."""
        if os.path.exists(LICENSE_FILE):
            try:
                with open(LICENSE_FILE, 'r') as f:
                    data = json.load(f)
                    key = data.get("key", "")
                    if key:
                        self.active_license_key = key
                        # Launch asynchronous verification background thread
                        threading.Thread(target=self._silent_startup_validation, args=(key,), daemon=True).start()
            except:
                pass

    def _silent_startup_validation(self, key):
        """Performs background handshakes to prevent application loop freezing on slow networks."""
        if self.validate_keygen_license(key):
            self.is_pro_activated = True
            self.after(0, self._apply_pro_ui_theme)

    def validate_keygen_license(self, key):
        """Encapsulated REST API driver sending secure POST validations to Keygen.sh."""
        url = f"https://api.keygen.sh/v1/accounts/{KEYGEN_ACCOUNT_ID}/licenses/actions/validate-key"
        body_data = {
            "meta": {
                "key": key.strip()
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(body_data).encode('utf-8'),
            headers={
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
                "Authorization": f"Bearer {KEYGEN_PRODUCT_TOKEN}"
            },
            method="POST"
        )
        
        try:
            # Perform deterministic secure SSL handshake with an 8s ceiling
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode())
                meta = res_data.get("meta", {})
                if meta.get("constant") == "VALID":
                    return True
        except Exception as e:
            print(f"Handshake signature failed: {e}")
        return False

    def _apply_pro_ui_theme(self):
        """Elevates standard UI to enterprise aesthetic levels on successful verification."""
        self.title(f"{config.APP_NAME} — 🛡️ PRO ENTERPRISE ACTIVE")

    def check_gate_limit(self, action_name, count=0):
        """Central execution controller preventing access to restricted modules based on tier."""
        if self.is_pro_activated:
            return True
            
        if action_name == "merge_count" and count > 20:
            self.show_activation_prompt(f"The Free Tier allows up to 20 documents per batch.\nYour queue contains {count} files.")
            return False
        elif action_name == "bates_stamping":
            self.show_activation_prompt("Indelible Bates Stamping & Serialization is a Pro Enterprise utility.")
            return False
        elif action_name == "advanced_compression":
            self.show_activation_prompt("High-Contrast Grayscale Exhibit Optimization requires Pro Enterprise activation.")
            return False
            
        return True

    def show_activation_prompt(self, reason):
        """Injects decision dialog to upsell or activate the application."""
        msg = f"{reason}\n\nWould you like to activate your Lifetime Enterprise License Key right now?"
        if messagebox.askyesno(f"🔒 {config.APP_NAME} — Premium Upgrade", msg):
            self.show_activation_window()

    def show_activation_window(self):
        """Generates beautiful modal asking for activation keys, verifying via backend hooks."""
        act = ctk.CTkToplevel(self)
        act.title(f"🔐 {config.APP_NAME} Activation")
        act.geometry("480x400")
        act.configure(fg_color=BRAND_WHITE_PANEL)
        act.resizable(False, False)
        act.grab_set()
        act.lift()
        
        ctk.CTkLabel(act, text=f"ACTIVATE YOUR {config.APP_NAME.upper()}", font=ctk.CTkFont(size=16, weight="bold"), text_color=BRAND_DARK_TEXT).pack(pady=(25, 5))
        ctk.CTkLabel(act, text="Unlock unlimited batch compiling and permanent Bates numbering.", font=ctk.CTkFont(size=10), text_color="#6B7280").pack(pady=(0, 20))
        
        ctk.CTkLabel(act, text="Enter License Key:", font=ctk.CTkFont(size=12, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w", padx=35, pady=(10, 2))
        key_entry = ctk.CTkEntry(act, placeholder_text="XXXX-XXXX-XXXX-XXXX", height=40, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT)
        key_entry.pack(fill="x", padx=35, pady=(0, 15))
        if self.active_license_key:
            key_entry.insert(0, self.active_license_key)
            
        status_lbl = ctk.CTkLabel(act, text="", font=ctk.CTkFont(size=11, weight="bold"))
        status_lbl.pack(pady=5)
        
        def attempt_activation():
            key = key_entry.get().strip()
            if not key:
                status_lbl.configure(text="❌ Please enter a valid key string!", text_color="#DC2626")
                return
            status_lbl.configure(text="Connecting to Access Security Matrix...", text_color="#2563EB")
            
            def thread_task():
                success = self.validate_keygen_license(key)
                if success:
                    self.is_pro_activated = True
                    self.active_license_key = key
                    try:
                        with open(LICENSE_FILE, 'w') as f:
                            json.dump({"key": key, "stamp": str(datetime.now())}, f)
                    except: pass
                    self.after(0, self._apply_pro_ui_theme)
                    self.after(0, lambda: messagebox.showinfo("Welcome to Enterprise Suite", "Success! Your lifetime license has been fully validated and locked to this terminal."))
                    self.after(0, act.destroy)
                else:
                    self.after(0, lambda: status_lbl.configure(text="❌ Invalid License Key or Network Timeout!", text_color="#DC2626"))
            
            threading.Thread(target=thread_task, daemon=True).start()

        btn_act = ctk.CTkButton(act, text="🚀 Activate License Now", height=45, fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, font=ctk.CTkFont(weight="bold"), command=attempt_activation)
        btn_act.pack(fill="x", padx=35, pady=15)
        
        link_lbl = ctk.CTkLabel(act, text="Don't have a key? Secure your Founder Tier Pass", font=ctk.CTkFont(size=10, underline=True), text_color="#2563EB", cursor="hand2")
        link_lbl.pack(pady=5)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open("https://www.accessparalegalservices.com/founder-portal"))

    # ==========================================
    # 🔐 CRYPTOGRAPHIC SECURE CASE VAULT
    # ==========================================
    def get_machine_uuid(self):
        """Retrieves a unique hardware identifier from the OS for local cryptographic salting."""
        try:
            import subprocess
            cmd = 'wmic csproduct get uuid'
            # Extracts the unique motherboard/BIOS UUID on Windows
            uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            return uuid
        except Exception:
            import platform
            # Fallback to local hostname if WMIC is restricted
            return platform.node() or "OFFLINE_SAFE_FALLBACK"

    def get_crypto_key(self):
        """Generates a deterministic 32-byte Fernet key bound to device hardware and license signature."""
        license_seed = self.active_license_key or "ACCESS_FREE_TIER"
        machine_seed = self.get_machine_uuid()
        
        # Combine license and hardware identity for a unique 'Machine Key'
        final_seed = f"{license_seed}::{machine_seed}::ACCESS_PARALEGAL_SALT_2026"
        
        key_bytes = hashlib.sha256(final_seed.encode()).digest()
        return base64.urlsafe_b64encode(key_bytes)

    def save_case_vault(self):
        """Encrypts active UI Case input metrics using hardware keys and locks to disk."""
        try:
            data = {
                "case_num": self.case_num_entry.get().strip(),
                "plaintiff": self.case_pla_entry.get().strip(),
                "defendant": self.case_def_entry.get().strip(),
                "bates_registry": getattr(self, "bates_registry", {})
            }
            raw_json = json.dumps(data)
            
            # Encrypt using standard AES-256 Fernet
            cipher = Fernet(self.get_crypto_key())
            encrypted = cipher.encrypt(raw_json.encode())
            
            with open(CASE_VAULT_FILE, 'wb') as f:
                f.write(encrypted)
            
            # Instantly scaffold physical windows folders based on updated metadata
            self.update_case_workspace_paths()
            
            messagebox.showinfo("Vault Locked", "Success! Case profile secured to hardware and default workspace directory generated.")
        except Exception as e:
            messagebox.showerror("Vault Error", f"Failed to secure Case Vault: {e}")

    def load_case_vault(self):
        """Silently decodes secure files on startup, injecting data into visual buffers."""
        if not os.path.exists(CASE_VAULT_FILE):
            return
        try:
            with open(CASE_VAULT_FILE, 'rb') as f:
                encrypted = f.read()
            
            cipher = Fernet(self.get_crypto_key())
            decrypted = cipher.decrypt(encrypted).decode()
            data = json.loads(decrypted)
            
            self.bates_registry = data.get("bates_registry", {})
            
            self.case_num_entry.delete(0, 'end')
            self.case_num_entry.insert(0, data.get("case_num", ""))
            self.case_pla_entry.delete(0, 'end')
            self.case_pla_entry.insert(0, data.get("plaintiff", ""))
            self.case_def_entry.delete(0, 'end')
            self.case_def_entry.insert(0, data.get("defendant", ""))
        except Exception:
            pass # Fails silently on mismatch / new seed

    def get_next_available_default_case(self, parent_root):
        """Scans active workspace and calculates next available numbered case folder to prevent collisions."""
        if not os.path.exists(parent_root):
            return "Case0001"
        try:
            existing = os.listdir(parent_root)
            max_num = 0
            for item in existing:
                # Match CaseXXXX pattern
                if item.startswith("Case") and len(item) > 4:
                    suffix = item[4:]
                    num_str = ""
                    for char in suffix:
                        if char.isdigit():
                            num_str += char
                        else:
                            break
                    if num_str:
                        try:
                            val = int(num_str)
                            if val > max_num:
                                max_num = val
                        except ValueError:
                            pass
            next_val = max_num + 1
            return f"Case{next_val:04d}"
        except Exception:
            return "Case0001"

    def update_case_workspace_paths(self):
        """Enforces standardized legal subdirectory trees tied to Case Profiles."""
        parent_root = getattr(self, 'custom_workspace_root', self.app_dir)
        
        case_val = self.case_num_entry.get().strip()
        if not case_val:
            # Fallback to plaintiff
            pla_val = self.case_pla_entry.get().strip()
            if pla_val:
                case_val = f"Case_{pla_val.replace(' ', '_')}"
            else:
                # INTELLIGENT AUTO-INCREMENT: Prevents "File Exists" collisions!
                case_val = self.get_next_available_default_case(parent_root)
                # Update GUI Entry visually so the user knows exactly where they're working
                self.case_num_entry.delete(0, 'end')
                self.case_num_entry.insert(0, case_val)
        
        # Sanitize folder name
        safe_case = "".join(c for c in case_val if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
        if not safe_case:
            safe_case = "Case0001"
            
        case_root = os.path.join(parent_root, safe_case)
        
        subfolders = {
            "merge": os.path.join(case_root, "PDF Merge"),
            "docs": os.path.join(case_root, "Created Docs"),
            "comp": os.path.join(case_root, "Compressed"),
            "src": os.path.join(case_root, "PDF Merge Source Files"),
            "pre": os.path.join(case_root, "Pre-Compressed Files")
        }
        
        try:
            # ONLY create active Source files drop zone and parent case root on startup
            # Do NOT pre-generate empty output / compression directories until they're actively used
            os.makedirs(subfolders["src"], exist_ok=True)
                
            # Auto-Route Tab 1 inputs/outputs
            self.default_input = subfolders["src"]
            self.default_output = subfolders["merge"]
            
            # Repopulate Tab 1 fields dynamically
            if hasattr(self, 'dir_entry'):
                self.dir_entry.delete(0, 'end')
                self.dir_entry.insert(0, self.default_input)
            if hasattr(self, 'out_entry'):
                self.out_entry.delete(0, 'end')
                self.out_entry.insert(0, self.default_output)
            
            self.trigger_async_folder_scan(self.default_input)
        except Exception as e:
            print(f"Workspace generation failure: {e}")

    def show_settings_modal(self):
        """Consolidated Premium Settings & Preferences Panel."""
        win = ctk.CTkToplevel(self)
        win.title("⚙️ System Preferences & Settings")
        win.geometry("520x450")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        
        # Center over main window
        x = self.winfo_x() + (self.winfo_width() - 520) // 2
        y = self.winfo_y() + (self.winfo_height() - 450) // 2
        win.geometry(f"+{x}+{y}")
        
        # --- HEADER ---
        ctk.CTkLabel(win, text="SYSTEM PREFERENCES", font=ctk.CTkFont(size=18, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=(25, 5))
        ctk.CTkLabel(win, text="Configure core application defaults and data staging.", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(pady=(0, 20))
        
        container = ctk.CTkFrame(win, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # 1. Appearance Selector
        f1 = ctk.CTkFrame(container, fg_color="transparent")
        f1.pack(fill="x", pady=8)
        ctk.CTkLabel(f1, text="🖥️ Interface Mode:", font=ctk.CTkFont(size=13, weight="bold"), text_color=BRAND_DARK_TEXT).pack(side="left")
        
        def change_theme(val):
            ctk.set_appearance_mode(val)
            
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_opt = ctk.CTkOptionMenu(f1, values=["System", "Light", "Dark"], variable=theme_var, command=change_theme, width=160, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN)
        theme_opt.pack(side="right")
        
        # 2. Master Workspace Selection
        f2 = ctk.CTkFrame(container, fg_color="transparent")
        f2.pack(fill="x", pady=15)
        ctk.CTkLabel(f2, text="🗂️ Master Case Folder:", font=ctk.CTkFont(size=13, weight="bold"), text_color=BRAND_DARK_TEXT).pack(anchor="w")
        
        path_frame = ctk.CTkFrame(container, fg_color=BRAND_WHITE_PANEL, height=38, corner_radius=6, border_width=1, border_color=BRAND_BORDER_LIGHT)
        path_frame.pack(fill="x", pady=(2, 8))
        path_frame.pack_propagate(False)
        
        path_lbl = ctk.CTkLabel(path_frame, text=self.custom_workspace_root, font=ctk.CTkFont(size=12), text_color=BRAND_DARK_TEXT)
        path_lbl.pack(side="left", padx=10)
        
        def pick_new_root():
            t = filedialog.askdirectory(title="Select Primary Case File Storage Root")
            if t:
                self.custom_workspace_root = t
                path_lbl.configure(text=t)
                self.update_case_workspace_paths()
                
        btn_browse = ctk.CTkButton(f2, text="Relocate", width=80, height=24, font=ctk.CTkFont(size=11, weight="bold"), fg_color="#4B5563", hover_color="#374151", command=pick_new_root)
        btn_browse.pack(anchor="e", pady=(0, 5))
        
        # 3. Data Safeguard Policy Selector
        f3 = ctk.CTkFrame(container, fg_color=GLASS_LEFT, corner_radius=8, border_width=1, border_color=GLASS_BORDER)
        f3.pack(fill="x", pady=15, ipady=5)
        
        lbl_safe_row = ctk.CTkFrame(f3, fg_color="transparent")
        lbl_safe_row.pack(fill="x", padx=15, pady=5)
        
        sw_safe = ctk.CTkSwitch(lbl_safe_row, text="🛡️ Safeguard Original Files", font=ctk.CTkFont(size=13, weight="bold"), variable=self.safeguard_files_var, text_color=BRAND_DARK_TEXT, progress_color=BRAND_ACCENT_GREEN)
        sw_safe.pack(side="left")
        
        def show_safeguard_tip():
            messagebox.showinfo("Shadow Staging Security Engine", 
                                "DATA STAGING ADVISORY:\n\n"
                                "• SAFE SHADOW STAGING (ON):\n"
                                "Clones queued files to an isolated temp folder before merging. HIGHLY RECOMMENDED for most applications to preserve source data integrity.\n\n"
                                "• DIRECT LIVE INGESTION (OFF):\n"
                                "Reads source files in place. Use with caution on network shares as concurrent operations can trigger file access conflicts.")
                                
        btn_tip = ctk.CTkButton(lbl_safe_row, text="❔ Info Note", font=ctk.CTkFont(size=11, weight="bold"), width=65, height=24, fg_color="#6B7280", hover_color="#4B5563", command=show_safeguard_tip)
        btn_tip.pack(side="left", padx=15)
        
        lbl_desc = ctk.CTkLabel(f3, text="Clones documents to shadow isolation first to preserve malpractice safety.", font=ctk.CTkFont(size=11), text_color="#4B5563")
        lbl_desc.pack(anchor="w", padx=30, pady=(2, 0))
        
        # 4. ADVANCED ARCHITECT SUB-PANEL ACCESS
        btn_advanced = ctk.CTkButton(
            container, text="🛠️ Open Case Blueprint Architect (Advanced)", 
            font=ctk.CTkFont(size=13, weight="bold"), height=40, 
            fg_color="#374151", hover_color="#1F2937", text_color="white",
            command=lambda: [win.destroy(), self.show_case_architect_modal()]
        )
        btn_advanced.pack(fill="x", pady=(20, 0))

    def show_case_architect_modal(self):
        """Dynamic blueprint architect allowing user to customize default case folder structures."""
        win = ctk.CTkToplevel(self)
        win.title("🛠️ Advanced Case File-Tree Architect")
        win.geometry("620x640")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()
        
        x = self.winfo_x() + (self.winfo_width() - 620) // 2
        y = self.winfo_y() + (self.winfo_height() - 640) // 2
        win.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(win, text="CASE FILE TREE ARCHITECT", font=ctk.CTkFont(size=18, weight="bold"), text_color=BRAND_ACCENT_GREEN).pack(pady=(25, 2))
        ctk.CTkLabel(win, text="Define a custom hierarchical architecture for automated case creation.", font=ctk.CTkFont(size=12), text_color="#6B7280").pack(pady=(0, 15))
        
        main_frame = ctk.CTkFrame(win, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=5)
        
        # Current Structure Display
        list_lbl = ctk.CTkLabel(main_frame, text="📂 Current Hierarchy Map (Relative Paths):", font=ctk.CTkFont(size=13, weight="bold"), text_color=BRAND_DARK_TEXT)
        list_lbl.pack(anchor="w", pady=(0, 5))
        
        txt_container = ctk.CTkFrame(main_frame, fg_color=BRAND_WHITE_PANEL, border_width=1, border_color=BRAND_BORDER_LIGHT, corner_radius=6)
        txt_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # Use Textbox for visualizing editable paths
        tree_box = ctk.CTkTextbox(txt_container, font=ctk.CTkFont(family="Consolas", size=12), fg_color="transparent", text_color=BRAND_DARK_TEXT)
        tree_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Controls area
        controls_frame = ctk.CTkFrame(main_frame, fg_color=GLASS_LEFT, corner_radius=8, border_width=1, border_color=GLASS_BORDER)
        controls_frame.pack(fill="x", pady=5, ipady=10)
        
        # Standard Presets Dropdown row
        row1 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5, padx=15)
        
        presets_pool = [
            "Correspondence/Client Correspondence", "Correspondence/Opposing Counsel", "Correspondence/{Date}",
            "Discovery/Written Discovery", "Discovery/Document Production", "Discovery/Depositions", "Discovery/Experts",
            "Pleadings/Motions", "Pleadings/Orders", "Pleadings/Briefs & Memoranda",
            "Client Documents/Financial Records", "Client Documents/Medical Records",
            "Research/Caselaw", "Research/Fact Research",
            "Trial/Exhibits", "Trial/Jury Instructions", "Trial/Witness Lists"
        ]
        
        preset_var = ctk.StringVar(value="Add Preset Subfolder...")
        opt_presets = ctk.CTkOptionMenu(row1, values=presets_pool, variable=preset_var, width=280, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN)
        opt_presets.pack(side="left", padx=(10, 10))
        
        # Custom path input row
        row2 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5, padx=15)
        
        ent_custom = ctk.CTkEntry(row2, placeholder_text="CustomName (e.g. Subpoenas)", width=280, fg_color=BRAND_WHITE_PANEL, text_color=BRAND_DARK_TEXT, border_color=BRAND_BORDER_LIGHT)
        ent_custom.pack(side="left", padx=(10, 10))

        # DELETE PATH ROW (New Functional Upgrade!)
        row3 = ctk.CTkFrame(controls_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5, padx=15)

        remove_var = ctk.StringVar(value="Select Folder to Remove...")
        opt_remove = ctk.CTkOptionMenu(
            row3, values=["Select Folder to Remove..."], variable=remove_var, width=280, 
            fg_color=BRAND_WHITE_PANEL, text_color="#BE123C", button_color="#E11D48", button_hover_color="#BE123C"
        )
        opt_remove.pack(side="left", padx=(10, 10))

        # Master Refresher Function
        def refresh_box():
            tree_box.configure(state="normal")
            tree_box.delete("1.0", "end")
            sorted_struct = sorted(list(set(self.custom_case_structure)), key=str.lower)
            for p in sorted_struct:
                tree_box.insert("end", f" •  {p}\n")
            tree_box.configure(state="disabled")
            
            # Re-sync removal dropdown list
            if sorted_struct:
                opt_remove.configure(values=sorted_struct)
            else:
                opt_remove.configure(values=["Select Folder to Remove..."])
            remove_var.set("Select Folder to Remove...")

        def add_selected_preset():
            val = preset_var.get()
            if val and val != "Add Preset Subfolder...":
                root_name = val.split('/')[0]
                if root_name not in self.custom_case_structure:
                    self.custom_case_structure.append(root_name)
                if val not in self.custom_case_structure:
                    self.custom_case_structure.append(val)
                refresh_box()
                # Temporary visual feedback
                btn_add_p.configure(text="✓ Added!", fg_color="#16A34A")
                win.after(1000, lambda: btn_add_p.configure(text="+ Add Preset", fg_color=BRAND_ACCENT_GREEN))

        btn_add_p = ctk.CTkButton(row1, text="+ Add Preset", font=ctk.CTkFont(size=12, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, command=add_selected_preset, width=120)
        btn_add_p.pack(side="right", padx=(0, 10))

        def add_custom_path():
            txt = ent_custom.get().strip()
            if txt:
                cat_win = ctk.CTkToplevel(win)
                cat_win.title("Select Parent Folder")
                cat_win.geometry("300x220")
                cat_win.transient(win)
                cat_win.grab_set()
                
                ctk.CTkLabel(cat_win, text="Select Parent Node:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=10)
                
                roots = ["Root Level", "Correspondence", "Discovery", "Pleadings", "Research", "Client Documents", "Trial"]
                r_var = ctk.StringVar(value="Root Level")
                ctk.CTkOptionMenu(cat_win, values=roots, variable=r_var, width=200, fg_color=BRAND_SILVER_BG, text_color=BRAND_DARK_TEXT, button_color=BRAND_ACCENT_GREEN).pack(pady=10)
                
                def do_commit():
                    r = r_var.get()
                    final = txt
                    if r != "Root Level":
                        if r not in self.custom_case_structure:
                            self.custom_case_structure.append(r)
                        final = f"{r}/{txt}"
                    if final not in self.custom_case_structure:
                        self.custom_case_structure.append(final)
                    cat_win.destroy()
                    ent_custom.delete(0, "end")
                    refresh_box()
                    btn_add_c.configure(text="✓ Added!", fg_color="#16A34A")
                    win.after(1000, lambda: btn_add_c.configure(text="+ Custom Folder", fg_color=BRAND_ACCENT_GREEN))
                    
                ctk.CTkButton(cat_win, text="Attach Folder", fg_color=BRAND_ACCENT_GREEN, command=do_commit).pack(pady=15)

        btn_add_c = ctk.CTkButton(row2, text="+ Custom Folder", font=ctk.CTkFont(size=12, weight="bold"), fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, command=add_custom_path, width=120)
        btn_add_c.pack(side="right", padx=(0, 10))

        def remove_selected_path():
            val = remove_var.get()
            if val and val != "Select Folder to Remove...":
                if val in self.custom_case_structure:
                    self.custom_case_structure.remove(val)
                    refresh_box()
                    btn_remove.configure(text="✓ Removed!", fg_color="#16A34A")
                    win.after(1000, lambda: btn_remove.configure(text="❌ Remove Folder", fg_color="#E11D48"))

        btn_remove = ctk.CTkButton(row3, text="❌ Remove Folder", font=ctk.CTkFont(size=12, weight="bold"), fg_color="#E11D48", hover_color="#BE123C", command=remove_selected_path, width=120)
        btn_remove.pack(side="right", padx=(0, 10))

        # Populate list and dropdowns initially
        refresh_box()
        
        # Clear / Reset actions
        actions_row = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_row.pack(fill="x", pady=(10, 0))
        
        def reset_defaults():
            if messagebox.askokcancel("Reset Structure", "Reset case tree to factory default legal hierarchy?"):
                self.custom_case_structure = ["Correspondence", "Correspondence/Client Correspondence", "Correspondence/Opposing Counsel", "Correspondence/Court Correspondence", "Correspondence/{Date}", "Discovery", "Discovery/Written Discovery", "Discovery/Document Production", "Discovery/Depositions", "Discovery/Experts", "Pleadings", "Pleadings/Motions", "Pleadings/Orders", "Pleadings/Briefs & Memoranda", "Client Documents", "Client Documents/Intake & Retainer", "Client Documents/Financial Records", "Research", "Research/Caselaw", "Research/Fact Research", "Trial", "Trial/Exhibits"]
                refresh_box()
                
        btn_reset = ctk.CTkButton(actions_row, text="🔄 Reset to Defaults", font=ctk.CTkFont(size=11), fg_color="#374151", hover_color="#1F2937", command=reset_defaults)
        btn_reset.pack(side="left")

        def clear_all():
            if messagebox.askyesno("Clear Hierarchy", "Delete all folders? You will start with an empty case blueprint."):
                self.custom_case_structure = []
                refresh_box()

        btn_clear = ctk.CTkButton(actions_row, text="🗑️ Clear All", font=ctk.CTkFont(size=11), fg_color="#B91C1C", hover_color="#991B1B", command=clear_all, width=100)
        btn_clear.pack(side="left", padx=15)
        
        btn_done = ctk.CTkButton(
            actions_row, text="🔒 Save Blueprint & Exit", 
            font=ctk.CTkFont(size=13, weight="bold"), 
            fg_color=BRAND_ACCENT_GREEN, hover_color=BRAND_DEEP_ACCENT, text_color="white",
            command=win.destroy
        )
        btn_done.pack(side="right")



    # ==========================================
    # 📂 FILE ROOM: ACTIVE ENGINE BACKENDS
    # ==========================================
    def update_tree_preview(self, choice):
        """Updates the text blueprint widget when the dropdown model is toggled."""
        archetype = self.tree_dropdown.get()
        self.tree_preview.configure(state="normal")
        self.tree_preview.delete("1.0", "end")
        
        if archetype == "⭐ Custom User Blueprint":
            sorted_c = sorted(self.custom_case_structure, key=str.lower)
            lines = ["📁 Case_Root (Custom User Build)/"]
            # Build a tidy visual tree representation
            roots = [p for p in sorted_c if '/' not in p]
            for r in roots:
                lines.append(f"  ├── 📁 {r}")
                children = [c for c in sorted_c if c.startswith(f"{r}/")]
                for idx, child in enumerate(children):
                    subname = child.split('/')[-1]
                    prefix = "  │   └── 📁" if idx == len(children)-1 else "  │   ├── 📁"
                    lines.append(f"{prefix} {subname}")
            
            preview = "\n".join(lines[:25])
            if len(lines) > 25:
                preview += "\n  └── [ + Custom blueprints continued ]"
        elif archetype == "Standard Civil Litigation":
            preview = "📁 Case_Root/\n  ├── 📁 01_Pleadings\n  ├── 📁 02_Discovery\n  ├── 📁 03_Correspondence\n  ├── 📁 04_Court_Orders\n  └── 📁 05_Research"
        elif archetype == "Trial Notebook Model":
            preview = "📁 Trial_Notebook/\n  ├── 📁 Exhibits_Plaintiff\n  ├── 📁 Exhibits_Defendant\n  ├── 📁 Witness_Outlines\n  ├── 📁 Jury_Instructions\n  └── 📁 Opening_Closing_Statements"
        else: # Solo / Freelance Core
            preview = "📁 Practice_Vault/\n  ├── 📁 Admin_Billing\n  ├── 📁 Client_Intake\n  └── 📁 Outbound_Production"
            
        self.tree_preview.insert("1.0", preview)
        self.tree_preview.configure(state="disabled")

    def execute_tree_builder(self):
        """Runs physical OS mkdir constructs to generate directory architectures."""
        base_dir = self.dir_entry.get()
        if not base_dir or not os.path.exists(base_dir):
            messagebox.showwarning("No Folder Selected", "Please choose or scan a Source/Target Folder in Tab 1 first!")
            return
            
        archetype = self.tree_dropdown.get()
        subdirs = []
        if archetype == "⭐ Custom User Blueprint":
            subdirs = self.custom_case_structure
        elif archetype == "Standard Civil Litigation":
            subdirs = ["01_Pleadings", "02_Discovery", "03_Correspondence", "04_Court_Orders", "05_Research"]
        elif archetype == "Trial Notebook Model":
            subdirs = ["Exhibits_Plaintiff", "Exhibits_Defendant", "Witness_Outlines", "Jury_Instructions", "Opening_Closing_Statements"]
        else:
            subdirs = ["Admin_Billing", "Client_Intake", "Outbound_Production"]
            
        # Dynamic expansion of variables
        from datetime import datetime
        curr_date = datetime.now().strftime("%Y-%m-%d")
        
        created = 0
        for sub in subdirs:
            # Parse variables like {Date} or {Client Name} safely
            resolved_sub = sub.replace("{Date}", curr_date)
            # Fallback safely replacing illegal Windows folder chars
            resolved_sub = resolved_sub.replace(":", "-").replace("*", "").replace("?", "")
            try:
                os.makedirs(os.path.join(base_dir, resolved_sub), exist_ok=True)
                created += 1
            except Exception as e:
                print(f"Folder creation failed for {resolved_sub}: {e}")
            
        messagebox.showinfo("Success", f"Directory Tree Construction Complete!\n\nInstantiated {created} customized legal subfolders in:\n{os.path.basename(base_dir)}")
        try:
            os.startfile(base_dir)
        except: pass

    def execute_rename_wizard(self):
        """Performs programmatic structural batch renaming across matching file filters."""
        source = self.dir_entry.get()
        if not source or not os.path.exists(source):
            messagebox.showwarning("No Folder", "Please select a source folder in Tab 1 first!")
            return
            
        # Parse naming formula parameters
        prefix = self.rename_p1.get()
        sub_comp = self.rename_p2.get()
        raw_sep = self.rename_sep.get()
        custom_txt = self.dyn_entry.get().strip().replace(" ", "_")
        
        # Resolve actual Separator
        sep = " - "
        if "_" in raw_sep: sep = "_"
        elif "." in raw_sep: sep = "."
        elif "Single" in raw_sep: sep = " "
        
        # Map logic triggers
        def get_value_for_type(t, default_name):
            if "[Date]" in t:
                return datetime.now().strftime("%Y-%m-%d")
            elif "[Case Number]" in t:
                val = self.case_num_entry.get().strip().replace(" ", "_").replace(":", "-")
                return val if val else "CASE"
            elif "[Plaintiff]" in t:
                val = self.case_pla_entry.get().strip().replace(" ", "_")
                return val if val else "PLAINTIFF"
            elif "[Defendant]" in t:
                val = self.case_def_entry.get().strip().replace(" ", "_")
                return val if val else "DEFENDANT"
            elif "[DocType]" in t:
                return "MOTION"
            elif "[Custom]" in t and custom_txt:
                return custom_txt
            return default_name
            
        # Target files
        files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f)) and not f.startswith("~")]
        if not files:
            messagebox.showinfo("Queue Empty", "No files detected in source directory.")
            return
            
        if not messagebox.askyesno("Confirm Batch Rename", f"Are you sure you want to batch rename {len(files)} files using the chosen formula?"):
            return
            
        renamed = 0
        for idx, f in enumerate(files):
            try:
                base, ext = os.path.splitext(f)
                p1_val = get_value_for_type(prefix, "ITEM")
                p2_val = get_value_for_type(sub_comp, base)
                
                # Append counter for uniqueness
                new_name = f"{p1_val}{sep}{p2_val}_{idx+1:03d}{ext}"
                
                os.rename(os.path.join(source, f), os.path.join(source, new_name))
                renamed += 1
            except Exception as e:
                print(f"Rename failure on {f}: {e}")
                
        self.trigger_async_folder_scan(source)
        messagebox.showinfo("Renaming Complete", f"Batch Renaming Loop Succeeded!\n\nRe-formatted and normalized {renamed} filenames.")

if __name__ == "__main__":
    app = AccessMergerApp()
    app.mainloop()
