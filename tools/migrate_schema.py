import os
import json
import shutil
from termcolor import colored

DATA_DIR = os.path.join("data", "concepts")
BACKUP_DIR = os.path.join("data", "concepts_backup_v1")

def migrate_schema():
    print(colored("Starting Schema Migration...", "cyan"))
    
    # 1. Create Backup
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(colored(f"Created backup directory: {BACKUP_DIR}", "yellow"))
    
    count_migrated = 0
    count_skipped = 0
    
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    print(f"Found {len(files)} concept files.")
    
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # CHECK: Does it need migration?
            if "claims" in data and len(data["claims"]) > 0:
                # Already has claims (or is a new file)
                # But we might want to ensure old facets are migrated if they exist and aren't in claims?
                # For safety, if 'claims' exists, we assume it's compliant-ish. 
                # Better: simple check if it ONLY has facets and NO claims.
                count_skipped += 1
                continue
                
            print(f"Migrating {filename}...")
            
            # Backup first
            shutil.copy2(filepath, os.path.join(BACKUP_DIR, filename))
            
            new_claims = []
            facets = data.get("facets", {})
            
            # MAPPER LOGIC: Convert Facets -> Claims
            
            # 1. STRUCTURAL
            structural = facets.get("STRUCTURAL", {})
            for key, values in structural.items():
                if isinstance(values, list):
                    for v in values:
                        new_claims.append({
                            "predicate": key, # e.g. "visual_features", "composition"
                            "object": v,
                            "epistemic": {"confidence": 1.0, "status": "SETTLED", "source_type": "MIGRATE_LEGACY"}
                        })
            
            # 2. FUNCTION
            function = facets.get("FUNCTION", {})
            for key, values in function.items():
                if isinstance(values, list):
                    for v in values:
                        new_claims.append({
                            "predicate": f"functional_{key}", # e.g. "functional_roles"
                            "object": v,
                             "epistemic": {"confidence": 1.0, "status": "SETTLED", "source_type": "MIGRATE_LEGACY"}
                        })

            # 3. MECHANISM
            mechanisms = facets.get("MECHANISM", [])
            for m in mechanisms:
                 new_claims.append({
                    "predicate": "mechanism",
                    "object": m,
                    "epistemic": {"confidence": 1.0, "status": "SETTLED", "source_type": "MIGRATE_LEGACY"}
                })
            
            # 4. INSTANCE LAYER (Move examples to claims too?) 
            # Ideally keep 'instance_layer' as a high-level summary, but examples are IS_A claims inverse?
            # Let's leave instance_layer alone for now, it's distinct from claims about the concept itself.
            
            data["claims"] = new_claims
            
            # Save
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            count_migrated += 1
            
        except Exception as e:
            print(colored(f"Error migrating {filename}: {e}", "red"))

    print(colored(f"\nMigration Complete.", "green"))
    print(f"Migrated: {count_migrated}")
    print(f"Skipped (Already compliant): {count_skipped}")
    print(f"Backups stored in {BACKUP_DIR}")

if __name__ == "__main__":
    migrate_schema()
