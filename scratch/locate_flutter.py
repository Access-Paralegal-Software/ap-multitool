import os

def find_flutter():
    skip_dirs = ["Windows", "Program Files", "Program Files (x86)", "ProgramData", "AppData", "System Volume Information", "$Recycle.Bin", "Python314"]
    for root, dirs, files in os.walk("C:\\"):
        # Remove restricted system dirs in place to skip traversal
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        if "flutter.bat" in files:
            path = os.path.join(root, "flutter.bat")
            print(f"FOUND_FLUTTER_PATH: {path}")
            return
    print("FLUTTER_NOT_FOUND")

if __name__ == "__main__":
    find_flutter()
