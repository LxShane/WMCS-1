import os
import ast
import sys
from termcolor import colored

class SystemDiagnostic:
    """
    Performs self-checks on the WMCS codebase.
    """
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        self.ignore_dirs = [".git", "__pycache__", "venv", ".gemini", "node_modules"]

    def run_diagnostics(self):
        print(colored("SYSTEM: Initiating Self-Diagnostic Sequence...", "cyan"))
        
        errors = []
        checked_count = 0
        
        # 1. Syntax Check (AST Parse)
        print(colored("Phase 1: Static Code Analysis...", "yellow"))
        for root, dirs, files in os.walk(self.root_dir):
            # Skip ignored
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    checked_count += 1
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            source = f.read()
                        ast.parse(source)
                    except SyntaxError as e:
                        print(colored(f"  [X] SYNTAX ERROR: {path}", "red"))
                        print(colored(f"      Line {e.lineno}: {e.msg}", "red"))
                        errors.append(f"SyntaxError in {file}: Line {e.lineno}")
                    except Exception as e:
                        print(colored(f"  [X] READ ERROR: {path} ({str(e)})", "red"))
        
        print(f"  > Scanned {checked_count} python files.")

        # 2. Dependency Check (Critical Imports)
        print(colored("Phase 2: Core Dependency Verification...", "yellow"))
        critical_modules = [
            "system_a_cognitive.ingestion.ingestor",
            "system_a_cognitive.meta.verifier",
            "system_a_cognitive.meta.consolidator",
            "system_b_llm.interfaces.gemini_client"
        ]
        
        for mod in critical_modules:
            try:
                __import__(mod)
                print(f"  [OK] {mod}")
            except ImportError as e:
                print(colored(f"  [X] MISSING MODULE: {mod} ({str(e)})", "red"))
                errors.append(f"ImportError: {mod}")
            except Exception as e:
                print(colored(f"  [?] LOAD ERROR: {mod} ({str(e)})", "red"))
                errors.append(f"LoadError: {mod}")

        # Summary
        print(colored("\n════════ DIAGNOSTIC REPORT ════════", "white", attrs=['bold']))
        if not errors:
            print(colored("SYSTEM STATUS: NOMINAL (100% HEALTHY)", "green"))
            print(colored("  - No syntax errors detected.", "green"))
            print(colored("  - All core modules loaded.", "green"))
            return True
        else:
            print(colored(f"SYSTEM STATUS: CRITICAL ({len(errors)} ERRORS)", "red"))
            for err in errors:
                print(f"  - {err}")
            return False

if __name__ == "__main__":
    diag = SystemDiagnostic()
    diag.run_diagnostics()
