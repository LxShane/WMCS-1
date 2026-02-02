import threading
import time
import random
import os
import json
from termcolor import colored
from system_a_cognitive.meta.auditor import RelationAuditor

class SubconsciousLoop(threading.Thread):
    """
    The 'Subconscious' processing unit.
    Runs in the background to Audit, Repair, and Consolidate memory.
    Logs activity to data/logs/subconscious_events.json instead of stdout.
    """
    def __init__(self, interval_seconds=30):
        super().__init__()
        self.interval = interval_seconds
        self.running = False
        self.auditor = RelationAuditor()
        self.daemon = True # Kill when main exits
        self.name = "SubconsciousMind"
        
        self.log_dir = "data/logs"
        self.log_file = os.path.join(self.log_dir, "subconscious_events.json")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Initialize log if not exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def log_event(self, event_type, message, details=None):
        entry = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "details": details or {}
        }
        try:
            # Simple file append logic (read-modify-write)
            # In production, use a rotating log handler or DB
            logs = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = []
            
            logs.append(entry)
            if len(logs) > 50: logs = logs[-50:] # Keep last 50
            
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            # Fail silently to avoid interrupting main thread
            pass

    def run(self):
        self.running = True
        # Silent startup
        # print(colored("\n[SUBCONSCIOUS] Online and Dreaming...", "magenta", attrs=['bold']))
        self.log_event("SYSTEM", "Subconscious Mind Online")
        
        while self.running:
            try:
                # 1. Sleep first
                time.sleep(self.interval)
                
                if not self.running: break

                # 2. Pick a random task
                task = random.choice(["AUDIT", "CONSOLIDATE"])
                
                if task == "AUDIT":
                    # Silent Audit
                    issues = self.auditor.audit(interactive=False)
                    if issues:
                        self.log_event("AUDIT_ALERT", f"Found {len(issues)} logic errors.", {"issues": issues})
                        # Optional: Auto-fix if high confidence? For now, just log.
                    else:
                        self.log_event("AUDIT_PASS", "Routine scan complete. No anomalies.")
                    
                elif task == "CONSOLIDATE":
                    # Placeholder
                    self.log_event("CONSOLIDATE", "Consolidation cycle skipped (Not implemented yet).")

            except Exception as e:
                self.log_event("ERROR", f"Subconscious Exception: {str(e)}")
                
    def stop(self):
        self.running = False
        self.log_event("SYSTEM", "Subconscious Shutting Down")
