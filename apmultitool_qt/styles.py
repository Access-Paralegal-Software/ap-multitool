# apmultitool_qt/styles.py

"""Centralized style variables and QSS template for APMultitool Qt."""

# Color tokens
BRAND_JADE = "#67BE5E"
BRAND_JADE_HOVER = "#4C9945"
BRAND_CHARCOAL = "#1E2222"
BRAND_SURFACE_DARK = "#2D3232"
BRAND_LIGHT_GREY = "#F3F4F6"
BRAND_WHITE = "#FFFFFF"
BRAND_BORDER = "#E5E7EB"
BRAND_TEXT_DARK = "#111827"
BRAND_TEXT_MUTED = "#6B7280"
BRAND_ALERT = "#E11D48"
BRAND_ALERT_HOVER = "#BE123C"

# Global Stylesheet QSS
GLOBAL_STYLE = f"""
QMainWindow {{
    background-color: {BRAND_LIGHT_GREY};
}}

/* Sidebar Styling */
QFrame#SidebarFrame {{
    background-color: {BRAND_CHARCOAL};
    border: none;
    min-width: 250px;
    max-width: 250px;
}}

QLabel#SidebarHeader {{
    color: {BRAND_JADE};
    font-size: 16px;
    font-weight: bold;
    padding: 20px 10px;
}}

QPushButton#SidebarButton {{
    background-color: transparent;
    color: #9CA3AF;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 12px 15px;
    font-size: 13px;
    font-weight: bold;
    margin: 4px 10px;
}}

QPushButton#SidebarButton:hover {{
    background-color: #2D3748;
    color: {BRAND_WHITE};
}}

QPushButton#SidebarButton:checked {{
    background-color: {BRAND_JADE};
    color: {BRAND_WHITE};
}}

/* Main Content Panel */
QStackedWidget {{
    background-color: {BRAND_LIGHT_GREY};
    padding: 15px;
}}

/* Styled Panel Group Boxes */
QFrame#GroupBoxContainer {{
    background-color: {BRAND_WHITE};
    border: 1px solid {BRAND_BORDER};
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
}}

QLabel#GroupHeader {{
    color: {BRAND_TEXT_DARK};
    font-size: 13px;
    font-weight: bold;
    padding-bottom: 5px;
}}

/* Buttons */
QPushButton#PrimaryButton {{
    background-color: {BRAND_JADE};
    color: {BRAND_WHITE};
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 20px;
    min-height: 40px;
}}

QPushButton#PrimaryButton:hover {{
    background-color: {BRAND_JADE_HOVER};
}}

QPushButton#DangerButton {{
    background-color: {BRAND_ALERT};
    color: {BRAND_WHITE};
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 20px;
    min-height: 40px;
}}

QPushButton#DangerButton:hover {{
    background-color: {BRAND_ALERT_HOVER};
}}

QPushButton#SecondaryButton {{
    background-color: #E5E7EB;
    color: {BRAND_TEXT_DARK};
    border: 1px solid {BRAND_BORDER};
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    padding: 6px 12px;
}}

QPushButton#SecondaryButton:hover {{
    background-color: #D1D5DB;
}}

/* Inputs */
QLineEdit {{
    border: 1px solid {BRAND_BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    background-color: {BRAND_WHITE};
    color: {BRAND_TEXT_DARK};
    font-size: 12px;
}}

QLineEdit:focus {{
    border: 2px solid {BRAND_JADE};
}}

QCheckBox {{
    font-size: 12px;
    color: {BRAND_TEXT_DARK};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {BRAND_BORDER};
    border-radius: 4px;
    background-color: {BRAND_WHITE};
}}

QCheckBox::indicator:checked {{
    background-color: {BRAND_JADE};
    border-color: {BRAND_JADE};
    image: url(check_mark.png); /* Fallback to standard check drawing if no image */
}}

/* Text Console Output */
QPlainTextEdit#ConsoleOutput {{
    background-color: #111827;
    color: #10B981;
    font-family: 'Consolas', 'JetBrains Mono', monospace;
    font-size: 11px;
    border-radius: 6px;
    border: 1px solid {BRAND_BORDER};
    padding: 10px;
}}

/* Header Bar Banner */
QFrame#HeaderBanner {{
    background-color: {BRAND_WHITE};
    border-bottom: 1px solid {BRAND_BORDER};
    padding: 15px 25px;
    min-height: 60px;
}}

QLabel#BannerTitle {{
    color: {BRAND_TEXT_DARK};
    font-size: 18px;
    font-weight: bold;
}}

QLabel#BannerSub {{
    color: {BRAND_TEXT_MUTED};
    font-size: 12px;
}}

/* Statusbar */
QStatusBar {{
    background-color: {BRAND_WHITE};
    color: {BRAND_TEXT_MUTED};
    border-top: 1px solid {BRAND_BORDER};
    font-size: 11px;
}}
"""
