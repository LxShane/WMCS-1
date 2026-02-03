import os

target = "main.py"
if os.path.exists(target):
    with open(target, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        # Expand tabs to 4 spaces
        new_line = line.replace("\t", "    ")
        # Ensure consistent right-strip for cleanliness (optional, but good)
        new_lines.append(new_line)
    
    with open(target, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Normalized {len(lines)} lines in {target}.")
else:
    print(f"Target {target} not found.")
