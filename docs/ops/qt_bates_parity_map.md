# Qt Bates View Parity Map

This document establishes the direct mappings between the legacy Tkinter-based `gui_apmultitool.py` Bates Stamping controls and their PySide6 equivalents in `apmultitool_qt/views/bates.py`.

## UI Element & Option Mapping

| Legacy Tkinter (CTk) Control | PySide6 equivalent | Mapping Details & Option Defaults |
| :--- | :--- | :--- |
| `self.bates_target_entry` | `self.txt_target` | Line entry storing the path to the target PDF for Bates stamping. |
| `self.btn_bates_target` | `self.btn_browse` | Browse button calling `file_dialogs.get_open_file` to select PDF. |
| `self.bates_prefix` | `self.txt_prefix` | Line entry for the alphanumeric Bates prefix (defaults to `"AP"`). |
| `self.bates_start` | `self.txt_start` | Line entry for the starting Bates serial number index (defaults to `"1"`). |
| `self.bates_sep_menu` | `self.cb_sep` | Option dropdown selecting separator: `_`, `-`, or `(None)` (maps to `""`). |
| `self.btn_bates_options` | `self.btn_options` | Button launching advanced settings modal (`BatesOptionsDialog`). |
| `self.bates_console` | `self.console` | Console text terminal displaying run outputs and warnings. |
| `self.bates_p_bar` | Shell `progress_bar` | Progress bar reflecting the current page count processing state. |
| `self.bates_run_btn` | `self.btn_run` | Execution trigger, transforms into Cancellation trigger during running. |

## Advanced Option Modal Mapping

| Legacy Option Variable | Dialog Component | BatesParams Mapping |
| :--- | :--- | :--- |
| `self.font_opt` | `self.cb_font` | `font_name` (Arial, Times New Roman, Calibri, Helvetica, Courier) |
| `self.size_opt` | `self.cb_size` | `font_size` (10, 11, 12, 14) |
| `self.pos_opt` | `self.cb_pos` | `position` (e.g. "Bottom Right (Outside Margin)") |
| `self.chk_shrink` | `self.chk_shrink` | `shrink_conflict` (True/False) |
| `self.name_policy` | `self.cb_naming` | `naming` ("Prefix_Start-End" or "Prefix_StartOnly") |
| `self.out_policy` | `self.cb_output` | Directory resolution policy ("Nested Folder", "Same as Source", "Custom") |
