import os
import subprocess
import time
import sys
import re

def get_pid_by_port(port):
    """Returns the PID of the process listening on the given port."""
    try:
        # Run netstat to find the PID
        result = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        # Parse the output: TCP 0.0.0.0:8000 ... LISTENING 1234
        for line in result.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                return parts[-1] # PID is the last element
    except:
        return None
    return None

def kill_pid(pid):
    if pid:
        print(f"  > Killing PID {pid}...")
        os.system(f"taskkill /F /PID {pid}")

def boot():
    print("=== WESTWORLD COGNITIVE SYSTEM BOOTLOADER ===")
    
    # 1. Cleanup Ports
    print("\n[1] Cleaning Ports...")
    for port in [8000, 3000]:
        pid = get_pid_by_port(port)
        if pid:
            print(f"  > Port {port} is busy (PID {pid}). Killing...")
            kill_pid(pid)
        else:
            print(f"  > Port {port} is free.")

    # 2. Launch API
    print("\n[2] Launching Matrix Kernel (API)...")
    # We use subprocess.Popen to launch in separate Shells so they persist
    subprocess.Popen("start cmd /k python server/api.py", shell=True)
    
    # 3. Launch UI
    print("[3] Launching Holodeck (UI)...")
    subprocess.Popen("start cmd /k python server/serve_ui.py", shell=True)
    
    print("\n==================================")
    print("   SYSTEM BOOTING IN NEW WINDOWS")
    print("==================================")
    print("1. Wait 10 seconds.")
    print("2. Open COMMAND CENTER: http://127.0.0.1:3000/ultimate.html")
    print("3. Verify 'SYSTEM ONLINE' indicator.")

if __name__ == "__main__":
    boot()
