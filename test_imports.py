print("Testing Imports...")
try:
    from duckduckgo_search import DDGS
    print("SUCCESS: from duckduckgo_search import DDGS")
except ImportError:
    print("FAILED: from duckduckgo_search import DDGS")

try:
    from ddgs import DDGS
    print("SUCCESS: from ddgs import DDGS")
except ImportError:
    print("FAILED: from ddgs import DDGS")
except Exception as e:
    print(f"ERROR: {e}")
