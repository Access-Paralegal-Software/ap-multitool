# Qt File Room & Trees Parity Map

This document establishes the direct mappings between the legacy CustomTkinter-based `gui_apmultitool.py` File Room tab and the new PySide6 implementation in `apmultitool_qt/views/fileroom.py`.

## UI Element & Option Mapping

| Legacy Tkinter (CTk) Control | PySide6 equivalent | Mapping Details & Option Defaults |
| :--- | :--- | :--- |
| `self.case_num_entry` | `self.txt_case_id` | Text field storing active Case ID / Matter Reference. |
| `self.tree_dropdown` | `self.cb_blueprints` | Dropdown choosing folder archetypes: `"⭐ Custom User Blueprint"`, `"Standard Civil Litigation"`, `"Trial Notebook Model"`, `"Solo / Freelance Core"`. |
| `self.tree_preview` | `self.tree_widget` | Visual preview area. Tkinter used a basic Text widget showing text/ascii drawings; PySide6 uses a dynamic, hierarchical `QTreeWidget`. |
| `self.btn_tree` | `self.btn_run` | Execution trigger initiating folder structure creations on disk. |
| `self.org_left` / Renaming | Deferred / Out of Scope | Batch renaming and dynamic renaming formula inputs are deferred from File Room View to keep focus on tree architectures. |

## Operations & Methods Mapping

| Legacy Python Method | PySide6/Core Method | Parity Mapping Details |
| :--- | :--- | :--- |
| `self.update_tree_preview` | `self.rebuild_preview` | Triggered when combo selection changes or Matter ID changes, updates hierarchy layout in tree view. |
| `self.execute_tree_builder` | `self.run_spinup` | Launches standard `os.makedirs` directory loops (with dynamic `{Date}` variable substitution support). |
| `self.custom_case_structure` | `self.custom_structure` | Session list tracking customized user folders (resets to legal standard defaults on request). |
