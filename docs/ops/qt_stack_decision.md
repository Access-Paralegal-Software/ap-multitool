# Qt UI Stack Choice & Decision Record

**Product**: APMultitool  
**Decision**: PySide6 with Qt Widgets (with custom QSS and Tablet-First Layout Doctrine)

---

## 🏛️ 1. Technical Choice Context

APMultitool is transitioning from a Tkinter/CustomTkinter desktop interface to a cross-platform foundation targeting:
1. **Desktop**: Windows, macOS, Linux.
2. **Mobile**: Android tablets and iPads (iOS tablets).

The choice of UI stack must balance visual fluidity on tablets, complex tool capabilities on desktops, ease of local packaging (PyInstaller), and low development overhead.

---

## 📊 2. Evaluated Options

### Option A: PySide6 with Qt Widgets (Classic C++ Style API)
- **Description**: Standard UI framework utilizing standard system-drawn widgets styled via Qt Style Sheets (QSS).
- **Pros**:
  - Robust table widgets (`QTableWidget`) and layout trees.
  - Straightforward python-only development; no secondary language or markup languages needed.
  - Compiles flawlessly with PyInstaller into single-file standalone binaries without missing DLLs or plugin imports.
  - Low memory footprint.
- **Cons**:
  - Fluid gestures (swipes, dynamic transitions) require manual layout manipulation.
  - Layouts are pixel-perfect but require conscious design to scale gracefully to touch interfaces.

### Option B: PySide6 with QML / Qt Quick (Declarative Styling)
- **Description**: Fluid, GPU-accelerated engine using QML markup to build dynamic animations and responsive layouts.
- **Pros**:
  - Native touch-centric gestures, fluid scaling, and modern mobile app aesthetics.
  - Extremely responsive design out-of-the-box.
- **Cons**:
  - Highly complex compilation pipelines. PyInstaller has historically struggled to analyze QML runtime imports, frequently resulting in broken static binaries.
  - Bridging QML signals with Python operations adds integration overhead.
  - Higher learning curve for maintenance.

---

## 🎯 3. Final Decision: PySide6 with Qt Widgets + Tablet-First Layout Doctrine

We have chosen **PySide6 with Qt Widgets** as the foundation. 

### Rationale:
1. **Packaging Security**: The product must compile cleanly using the existing `build_windows.ps1` and future macOS/Linux automated packagers. Using Qt Widgets eliminates the runtime plugin-resolution failures typical of QML bundles.
2. **Responsive Layout Doctrine**: By leveraging `QSplitter`, `QStackedLayout`, and structural layout grids with custom sizing policies, we can achieve responsive UI reflows for both desktop monitors and landscape/portrait tablet orientations.
3. **QSS Touch Targets**: QSS (Qt Style Sheets) allows us to style widgets globally. We will enforce a minimum touch target size of **48x48 pixels** for all buttons, menus, and checkboxes.
4. **Decoupled Architecture**: By keeping the GUI views decoupled from the core Python engine via Qt Signals/Slots, we ensure that if we decide to wrap the app in QML or a native mobile shell (e.g. PySide6 on Android) in the future, the backend logic remains completely untouched.
