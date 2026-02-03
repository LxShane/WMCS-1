from duckduckgo_search import DDGS
import json

print("Testing DuckDuckGo Search...")
try:
    with DDGS() as ddgs:
        results = list(ddgs.text("Nuclear Fusion Tokamak", max_results=3))
        print(f"Results found: {len(results)}")
        for r in results:
            print(f"- {r.get('title')}: {r.get('href')}")
except Exception as e:
    print(f"Error: {e}")
