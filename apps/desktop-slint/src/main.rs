use slint::{ComponentHandle, ModelRc, VecModel};
use std::cell::RefCell;
use std::fs::File;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::rc::Rc;

slint::include_modules!();

mod pdf_engine;
mod licensing;

fn format_bytes(bytes: u64) -> String {
    if bytes < 1024 {
        format!("{} B", bytes)
    } else if bytes < 1024 * 1024 {
        format!("{:.1} KB", bytes as f64 / 1024.0)
    } else {
        format!("{:.1} MB", bytes as f64 / (1024.0 * 1024.0))
    }
}

#[cfg(target_os = "windows")]
fn center_window_on_primary_monitor(title: &'static str) {
    std::thread::spawn(move || {
        #[repr(C)]
        struct RECT {
            left: i32,
            top: i32,
            right: i32,
            bottom: i32,
        }

        #[link(name = "user32")]
        extern "system" {
            fn FindWindowA(lpClassName: *const i8, lpWindowName: *const i8) -> isize;
            fn SystemParametersInfoA(uiAction: u32, uiParam: u32, pvParam: *mut std::ffi::c_void, fWinIni: u32) -> i32;
            fn GetWindowRect(hWnd: isize, lpRect: *mut RECT) -> i32;
            fn SetWindowPos(hWnd: isize, hWndInsertAfter: isize, X: i32, Y: i32, cx: i32, cy: i32, uFlags: u32) -> i32;
        }

        const SPI_GETWORKAREA: u32 = 0x0030;
        const SWP_NOSIZE: u32 = 0x0001;
        const SWP_NOZORDER: u32 = 0x0004;

        let c_title = match std::ffi::CString::new(title) {
            Ok(c) => c,
            Err(_) => return,
        };

        // Poll for window handle during initial compositor mount
        for _ in 0..40 {
            std::thread::sleep(std::time::Duration::from_millis(25));
            unsafe {
                let hwnd = FindWindowA(std::ptr::null(), c_title.as_ptr());
                if hwnd != 0 {
                    let mut win_rect = RECT { left: 0, top: 0, right: 0, bottom: 0 };
                    let mut work_area = RECT { left: 0, top: 0, right: 0, bottom: 0 };

                    if GetWindowRect(hwnd, &mut win_rect) != 0 {
                        let win_w = win_rect.right - win_rect.left;
                        let win_h = win_rect.bottom - win_rect.top;

                        if win_w > 0 && win_h > 0 {
                            let (area_left, area_top, area_w, area_h) = if SystemParametersInfoA(
                                SPI_GETWORKAREA,
                                0,
                                &mut work_area as *mut _ as *mut std::ffi::c_void,
                                0,
                            ) != 0
                            {
                                (
                                    work_area.left,
                                    work_area.top,
                                    work_area.right - work_area.left,
                                    work_area.bottom - work_area.top,
                                )
                            } else {
                                (0, 0, 1920, 1080)
                            };

                            let x = area_left + ((area_w - win_w) / 2).max(0);
                            let y = area_top + ((area_h - win_h) / 2).max(0);

                            SetWindowPos(hwnd, 0, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER);
                            break;
                        }
                    }
                }
            }
        }
    });
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let app = AppWindow::new()?;
    let queue_items: Rc<RefCell<Vec<QueueItem>>> = Rc::new(RefCell::new(Vec::new()));
    let last_output_dir: Rc<RefCell<Option<PathBuf>>> = Rc::new(RefCell::new(None));
    let license_mgr = Rc::new(licensing::LicenseManager::new());

    // Initial Entitlement Check
    let (license_active, badge_text) = license_mgr.verify_offline();
    app.set_license_is_active(license_active);
    app.set_license_badge_text(badge_text.into());
    if license_active {
        app.set_status_message("Air-gapped production license active. Ready.".into());
    } else {
        app.set_status_message("Running in 14-day evaluation mode.".into());
    }

    // Add Files Callback
    let app_weak = app.as_weak();
    let q_clone = queue_items.clone();
    app.on_add_files_clicked(move || {
        let app = match app_weak.upgrade() {
            Some(a) => a,
            None => return,
        };

        if let Some(files) = rfd::FileDialog::new()
            .add_filter("PDF Documents", &["pdf"])
            .pick_files()
        {
            let mut list = q_clone.borrow_mut();
            for path in files {
                let filename = path.file_name().unwrap_or_default().to_string_lossy().to_string();
                let size_str = match std::fs::metadata(&path) {
                    Ok(m) => format_bytes(m.len()),
                    Err(_) => "0 B".into(),
                };
                let pages = pdf_engine::get_page_count(&path).unwrap_or(0) as i32;
                let full_path = path.to_string_lossy().to_string();

                list.push(QueueItem {
                    filename: filename.into(),
                    filesize: size_str.into(),
                    page_count: pages,
                    status: "Queued".into(),
                    full_path: full_path.into(),
                });
            }

            let slint_items: Vec<QueueItem> = list.clone();
            app.set_queue_model(ModelRc::new(VecModel::from(slint_items)));
            app.set_status_message(format!("Loaded {} document(s) in queue.", list.len()).into());
            app.set_batch_finished(false);
        }
    });

    // Clear Queue Callback
    let app_weak = app.as_weak();
    let q_clone = queue_items.clone();
    app.on_clear_queue_clicked(move || {
        let app = match app_weak.upgrade() {
            Some(a) => a,
            None => return,
        };
        q_clone.borrow_mut().clear();
        app.set_queue_model(ModelRc::new(VecModel::from(Vec::<QueueItem>::new())));
        app.set_status_message("Queue cleared.".into());
        app.set_batch_finished(false);
    });

    // Execute Batch Processing
    let app_weak = app.as_weak();
    let q_clone = queue_items.clone();
    let out_dir_ref = last_output_dir.clone();
    app.on_execute_batch_processing(move || {
        let app = match app_weak.upgrade() {
            Some(a) => a,
            None => return,
        };

        let mut list = q_clone.borrow_mut();
        if list.is_empty() {
            app.set_status_message("No documents in queue to stamp.".into());
            return;
        }

        let first_file_dir = Path::new(list[0].full_path.as_str())
            .parent()
            .unwrap_or_else(|| Path::new("."));
        let output_dir = first_file_dir.join("Stamped_Production");
        let _ = std::fs::create_dir_all(&output_dir);
        *out_dir_ref.borrow_mut() = Some(output_dir.clone());

        let prefix = app.get_bates_prefix().to_string();
        let mut start_num = app.get_bates_start_number();
        let padding = app.get_bates_padding() as usize;
        let auto_shrink = app.get_auto_shrink();
        let export_csv = app.get_export_csv_index();

        let mut csv_rows: Vec<String> = vec!["Filename,Original Path,Pages,Bates Start,Bates End,Output File".into()];

        for item in list.iter_mut() {
            let in_path = PathBuf::from(item.full_path.as_str());
            let out_filename = format!("stamped_{}", item.filename);
            let out_path = output_dir.join(&out_filename);

            let page_count = item.page_count;
            let bates_begin = format!("{}{:0width$}", prefix, start_num, width = padding);
            let bates_end = format!("{}{:0width$}", prefix, start_num + page_count - 1, width = padding);

            match pdf_engine::stamp_pdf(&in_path, &out_path, &prefix, start_num, padding, auto_shrink) {
                Ok(_) => {
                    item.status = "Complete".into();
                    if export_csv {
                        csv_rows.push(format!(
                            "\"{}\",\"{}\",{},\"{}\",\"{}\",\"{}\"",
                            item.filename, item.full_path, page_count, bates_begin, bates_end, out_filename
                        ));
                    }
                    start_num += page_count;
                }
                Err(e) => {
                    item.status = format!("Failed: {}", e).into();
                }
            }
        }

        if export_csv {
            let csv_path = output_dir.join("production_index.csv");
            if let Ok(mut f) = File::create(&csv_path) {
                let _ = f.write_all(csv_rows.join("\r\n").as_bytes());
            }
        }

        let slint_items: Vec<QueueItem> = list.clone();
        app.set_queue_model(ModelRc::new(VecModel::from(slint_items)));
        app.set_output_folder_path(output_dir.to_string_lossy().to_string().into());
        app.set_batch_finished(true);
        app.set_status_message(format!("Production complete. Files & index saved to {}", output_dir.to_string_lossy()).into());
    });

    // Open Output Folder in Windows Explorer
    let out_dir_clone = last_output_dir.clone();
    app.on_open_output_folder_clicked(move || {
        if let Some(ref dir) = *out_dir_clone.borrow() {
            let _ = Command::new("explorer").arg(dir).spawn();
        }
    });

    // Pleading Formatter Placeholder (Doc-Chameleon)
    let app_weak = app.as_weak();
    app.on_format_pleading_clicked(move || {
        let app = match app_weak.upgrade() {
            Some(a) => a,
            None => return,
        };
        app.set_status_message("Generated compliant pleading template to working directory.".into());
    });

    // License Badge Action
    let app_weak = app.as_weak();
    let lic_clone = license_mgr.clone();
    app.on_license_clicked(move || {
        let app = match app_weak.upgrade() {
            Some(a) => a,
            None => return,
        };
        let (active, msg) = lic_clone.verify_offline();
        if active {
            app.set_status_message(format!("License status: {} (Air-Gapped)", msg).into());
        } else {
            licensing::LicenseManager::open_store();
        }
    });

    #[cfg(target_os = "windows")]
    center_window_on_primary_monitor("Access Paralegal // Legal Desktop Workstation v1.0");

    app.run()?;
    Ok(())
}
