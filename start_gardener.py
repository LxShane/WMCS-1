from system_a_cognitive.meta.active_gardener import ActiveGardener

if __name__ == "__main__":
    print("Initializing Autonomous Knowledge Gardener...")
    gardener = ActiveGardener()
    # Force it to run until it hits Printing Press (or just 1 loop if lucky/mocked)
    # But to ensure demo success, I will hint it towards Printing Press if possible?
    # No, the code randomizes. I will run it and see.
    # Actually, to save time for the user, let's hardcode the 'Printing Press' target in the script logic 
    # OR just rely on probability (there are only ~300 files, many not physical).
    
    gardener.start_cycle(max_loops=1)
