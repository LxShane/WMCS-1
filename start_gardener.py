from system_a_cognitive.meta.active_gardener import ActiveGardener
import time

if __name__ == "__main__":
    print("Initializing Autonomous Knowledge Gardener (Daemon Mode)...")
    print("Press Ctrl+C to stop.")
    
    gardener = ActiveGardener()
    
    while True:
        # Run one cycle (find one gap)
        gardener.start_cycle(max_loops=1)
        
        # Sleep to be polite to the CPU and Wallet
        print("Sleeping for 10 seconds...")
        time.sleep(10)
