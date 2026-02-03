import subprocess
import time
from termcolor import colored
import sys

SCRIPTS = [
    ("test_macgyver.py", "Universal Physics Layer"),
    ("test_dynamic_causality.py", "Dynamic Causal Learning"),
    ("test_social_causality.py", "Social Theory of Mind"),
    ("test_gardener_physics.py", "Autonomous Maintenance"),
    ("test_rebuild_registry.py", "Registry Integrity"),
    ("full_system_stress_test.py", "Meta-Learning & Research Loop")
]

def run_audit():
    print(colored("\n╔════════════════════════════════════════════════════╗", "cyan"))
    print(colored("║       FINAL SYSTEM AUDIT: THE GOD-MACHINE          ║", "cyan", attrs=['bold']))
    print(colored("╚════════════════════════════════════════════════════╝\n", "cyan"))
    
    results = []
    
    for script, name in SCRIPTS:
        print(colored(f"Target: {name} ({script})...", "yellow"))
        start = time.time()
        try:
            # Run without capturing output first to let user see progress, 
            # but for a cleaner report we might want to capture. 
            # I will let it stream so user sees the 'matrix' scrolling.
            result = subprocess.run([sys.executable, script], 
                                    check=False) # Don't crash on fail, just record
            
            duration = time.time() - start
            status = "PASS" if result.returncode == 0 else "FAIL"
            color = "green" if status == "PASS" else "red"
            
            print(colored(f"Result: [{status}] in {duration:.2f}s\n", color, attrs=['bold']))
            results.append((name, status))
            
        except Exception as e:
            print(colored(f"CRITICAL ERROR: {e}\n", "red"))
            results.append((name, "ERROR"))

    # FINAL REPORT
    print(colored("\n════════ AUDIT SUMMARY ════════", "white", attrs=['bold']))
    all_pass = True
    for name, status in results:
        color = "green" if status == "PASS" else "red"
        print(f"{name.ljust(30)}: {colored(status, color)}")
        if status != "PASS": all_pass = False
        
    if all_pass:
        print(colored("\n>>> SYSTEM STATUS: OPERATIONALLY READY (FLYING COLORS) <<<", "green", attrs=['bold', 'blink']))
        sys.exit(0)
    else:
        print(colored("\n>>> SYSTEM STATUS: FAILURE DETECTED <<<", "red", attrs=['bold']))
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
