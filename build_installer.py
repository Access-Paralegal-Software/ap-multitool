import os
import subprocess
import sys

def build():
    print("🚀 ACCESS PARALEGAL - SINGLE INSTALLER BUILDER")
    print("---------------------------------------------")
    
    # 0. Clean up previous builds to prevent PermissionError
    import shutil
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"🧹 Cleaning up old '{folder}' folder...")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"⚠️ Warning: Could not delete {folder}. Make sure the app is closed! ({e})")

    # 1. Check for PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller detected.")
    except ImportError:
        print("❌ PyInstaller not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Define the build command
    # Use sys.executable -m PyInstaller for better compatibility on Windows
    main_script = "gui_apmultitool.py"
    icon_file = "logo_small.png"
    
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--noconsole",
        f"--icon={icon_file}",
        "--name=AccessParalegalMultitool",
        "--hidden-import=reportlab.graphics.barcode.code128",
        "--hidden-import=reportlab.graphics.barcode.code39",
        "--hidden-import=reportlab.graphics.barcode.usps",
        "--collect-submodules=reportlab",
        main_script
    ]

    print(f"📦 Bundling {main_script} into a single EXE...")
    try:
        subprocess.run(cmd, check=True)
        print("\n✨ SUCCESS! Your single installer is ready in the 'dist' folder.")
        print(f"   File: {os.path.join(script_dir, 'dist', 'AccessParalegalMultitool.exe')}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ BUILD FAILED: {e}")

if __name__ == "__main__":
    build()
