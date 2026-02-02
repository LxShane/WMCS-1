from system_a_cognitive.logic.functional_search import FunctionalSearcher

searcher = FunctionalSearcher()
print(f"Loaded {len(searcher.graph)} concepts.")

print("\nSearching for 'Medieval Shield'...")
results = searcher.find_equivalents("Medieval Shield")

if results.get("equivalents"):
    print("SUCCESS: Equivalents found!")
    for role, items in results["equivalents"].items():
        print(f"Role: {role}")
        for item in items:
            print(f"  - {item['name']} ({item['id']})")
else:
    print("FAILURE: No equivalents found.")
    # Debug: Check if the concepts exist
    shield = searcher.graph.get(searcher.resolve_name("medieval_shield"))
    firewall = searcher.graph.get(searcher.resolve_name("network_firewall"))
    print(f"Shield Data: {shield}")
    print(f"Firewall Data: {firewall}")
