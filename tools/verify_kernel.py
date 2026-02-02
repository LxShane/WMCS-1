import sys
import os
sys.path.append(os.getcwd())

print("Attempting to import WMCS_Kernel...")
try:
    from main import WMCS_Kernel
    print("Import SUCCESS.")
except Exception as e:
    print(f"Import FAILED: {e}")
    import traceback
    traceback.print_exc()
