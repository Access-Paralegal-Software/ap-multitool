import subprocess
import os

ssh_key = os.path.expandvars(r"%USERPROFILE%\.ssh\id_ed25519")
sparky_ip = "aewoodyard@192.168.0.176"

# 1. Clean standard Windows paths (no extended prefix for SCP!)
sewing_local = r"C:\Users\aewoo\Desktop\Evernote-Backup\ENEX\Sewing.enex"
recipes_local = r"C:\Users\aewoo\Desktop\Evernote-Backup\ENEX\Recipes.enex"
core_dir_local = r"C:\Users\aewoo\Desktop\Antigravity Workspace\adventures-of-sparky-and-claw\archivist-core"
test_script_local = r"C:\Users\aewoo\Desktop\Antigravity Workspace\adventures-of-sparky-and-claw\remote_test.py"

# Sparky Paths
remote_warehouse = "/home/aewoodyard/DataWarehouse/EvernoteRaw"
remote_core = "/home/aewoodyard/archivist-core"

print("--- STEP 1: Beaming Target Notebooks to Sparky ---")
for local_file in [sewing_local, recipes_local]:
    filename = os.path.basename(local_file)
    scp_cmd = ["scp", "-o", "StrictHostKeyChecking=accept-new", "-i", ssh_key, local_file, f"{sparky_ip}:{remote_warehouse}/{filename}"]
    try:
        subprocess.run(scp_cmd, check=True, text=True, capture_output=True)
        print(f"[OK] Streamed {filename} to warehouse.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to stream {filename}: {e.stderr}")
        exit(1)

print("\n--- STEP 2: Deploying 'archivist-core' Source to Sparky ---")
# Clean old remote code first
ssh_clean_cmd = ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-i", ssh_key, sparky_ip, f"rm -rf {remote_core} && mkdir -p {remote_core}"]
try:
    subprocess.run(ssh_clean_cmd, check=True, text=True)
except Exception as e:
    print("[WARNING] Remote cleanup failed:", e)

# Beam files recursive
scp_core_cmd = ["scp", "-o", "StrictHostKeyChecking=accept-new", "-i", ssh_key, "-r", f"{core_dir_local}", f"{sparky_ip}:/home/aewoodyard/"]
try:
    subprocess.run(scp_core_cmd, check=True, text=True, capture_output=True)
    print("[OK] Python core codebase successfully synced to Sparky.")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Codebase sync failed: {e.stderr}")
    exit(1)

print("\n--- STEP 3: Deploying and Triggering Remote Test Orchestrator ---")
# Send remote_test.py
scp_test_cmd = ["scp", "-o", "StrictHostKeyChecking=accept-new", "-i", ssh_key, test_script_local, f"{sparky_ip}:~/remote_test.py"]
try:
    subprocess.run(scp_test_cmd, check=True, text=True)
except Exception as e:
    print("[ERROR] Test script transfer failed:", e)
    exit(1)

# Execute on Sparky
ssh_exec_cmd = ["ssh", "-o", "StrictHostKeyChecking=accept-new", "-i", ssh_key, sparky_ip, "python ~/remote_test.py && rm ~/remote_test.py"]
try:
    result = subprocess.run(ssh_exec_cmd, check=True, text=True, capture_output=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("[CRITICAL ERROR DURING EXECUTION]:")
    print(e.stderr)
    print(e.stdout)
