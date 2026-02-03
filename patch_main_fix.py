
import os

target_file = "main.py"
old_line = '                           reasoning_prompt_header += f"- {s}\\n"'
new_block = '''                           if hasattr(s, 'content'):
                               reasoning_prompt_header += f"- [{s.lesson_type}] {s.content} (Trigger: {s.trigger})\\\\n"
                           else:
                               reasoning_prompt_header += f"- {s}\\\\n"'''

with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

if old_line in content:
    print("Found exact line match!")
    # Proceed (simple replace might fail if multiple, but we check)
else:
    print("Exact match failed. Trying stripped match.")
    # Fallback: line by line
    lines = content.split('\n')
    new_lines = []
    patched = False
    for line in lines:
        if 'reasoning_prompt_header += f"- {s}\\n"' in line and not patched:
             # Preserve indentation
             indent = line[:line.find('reasoning_prompt_header')]
             new_lines.append(f'{indent}if hasattr(s, "content"):')
             new_lines.append(f'{indent}    s_str = f"[{s.lesson_type}] {{s.content}} (Trigger: {{s.trigger}})"')
             new_lines.append(f'{indent}    reasoning_prompt_header += f"- {{s_str}}\\\\n"')
             new_lines.append(f'{indent}else:')
             new_lines.append(f'{indent}    reasoning_prompt_header += f"- {{s}}\\\\n"')
             patched = True
        else:
             new_lines.append(line)
    
    if patched:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print("Patched main.py successfully.")
    else:
        print("Could not find line to patch.")
