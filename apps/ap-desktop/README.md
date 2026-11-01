# AP-Desktop

Cross-platform desktop application for AP-Suite powered by Tauri v2.

## Structure
- `src-tauri/`: Rust backend, system tray, window management, and native IPC.
- `src/` & `index.html`: Web-based modern UI shell communicating with `ap-appliance` and Tauri core.
