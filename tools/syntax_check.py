import ast
import traceback

filename = "main.py"
try:
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()
    ast.parse(source)
    print("Syntax OK")
except SyntaxError as e:
    print(f"SYNTAX_ERROR_FOUND_ON_LINE: {e.lineno}")
    # print(f"Text: {repr(e.text)}")
    print(f"Msg: {e.msg}")
except Exception as e:
    traceback.print_exc()
