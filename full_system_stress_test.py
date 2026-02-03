import time
import os
from termcolor import colored
from main import WMCS_Kernel
from system_a_cognitive.logic.models import MetaLesson

def print_section(title):
    print(colored(f"\n{'='*60}", "magenta"))
    print(colored(f"  TEST SCENARIO: {title}", "white", attrs=['bold']))
    print(colored(f"{'='*60}\n", "magenta"))

def full_stress_test():
    print(colored(">>> INITIALIZING FULL SYSTEM STRESS TEST <<<", "green", attrs=['bold', 'blink']))
    
    # Initialize Kernel
    kernel = WMCS_Kernel()
    kernel.load_data() # Ensure indexes are ready
    
    # =========================================================================
    # SCENARIO 1: THE VOID (Autonomous Research)
    # Goal: Ask about a term definitely NOT in memory, verify it goes and gets it.
    # =========================================================================
    print_section("1. AUTONOMOUS RESEARCH RECOVERY")
    
    target_unknown = "Gloxnark Theory" # Totally fake, but let's see if it tries to research it or admits ignorance.
    # Actually, let's use a real but obscure thing so research *succeeds* in finding content.
    # "Zorkmid currency" (from Zork).
    target_concept = "Zorkmid" 
    
    print(colored(f"Query: 'What is the exchange rate of a {target_concept}?'", "cyan"))
    
    if kernel.block_exists(target_concept):
        print(colored(f"WARNING: '{target_concept}' already exists. Skipping research trigger test.", "yellow"))
    else:
        print(colored(f"Confirmed '{target_concept}' is unknown. Expecting 'Research' trigger...", "yellow"))
    
    # We expect the kernel to print "Triggering DEEP Autonomous Research..."
    # We can't easily capture stdout here without redirecting, but the user will see it.
    # We will check RESULT confidence.
    
    start = time.time()
    response_1 = kernel.process_query(f"What is the historical value of a {target_concept}?")
    duration = time.time() - start
    
    print(colored(f"Response: {response_1['text'][:200]}...", "white"))
    print(colored(f"Duration: {duration:.2f}s", "cyan"))
    
    # Verification: Did it learn it?
    if kernel.block_exists(target_concept):
        print(colored("[PASS] System learned new concept autonomously.", "green"))
    else:
        # It might have found it but just answered without saving, or failed to find data.
        print(colored("[INFO] Concept not persisted (maybe just used in context).", "yellow"))


    # =========================================================================
    # SCENARIO 2: SPATIAL REASONING
    # Goal: Verify it uses the 'Secondary Immune Response' spatial data we verified earlier.
    # =========================================================================
    print_section("2. SPATIAL LOGIC SYNTHESIS")
    
    query_2 = "Where precisely does the Secondary Immune Response occur?"
    print(colored(f"Query: '{query_2}'", "cyan"))
    
    response_2 = kernel.process_query(query_2)
    text_2 = response_2['text'].lower()
    
    expected_keywords = ["spleen", "lymph", "systemic", "body"]
    matches = [w for w in expected_keywords if w in text_2]
    
    if len(matches) >= 2:
        print(colored(f"[PASS] Spatial Nuance Detected. Keywords found: {matches}", "green"))
    else:
        print(colored(f"[FAIL] Missing spatial detail. Response: {text_2[:100]}...", "red"))


    # =========================================================================
    # SCENARIO 3: META-LEARNING (STRATEGY APPLICATION)
    # Goal: Inject a specific strategy and see if it changes behavior.
    # =========================================================================
    print_section("3. META-LEARNING (STRATEGY INJECTION)")
    
    # 3.1 Teach the strategy
    strategy_content = "When explaining 'Light', you MUST mention it behaves as both a particle and a wave."
    strategy_trigger = "nature of light"
    
    print(colored(f"Injecting Strategy: '{strategy_content}' for trigger '{strategy_trigger}'", "yellow"))
    
    try:
        from system_a_cognitive.memory.strategy_store import StrategyStore
        store = StrategyStore()
        import uuid
        lesson = MetaLesson(
            id=str(uuid.uuid4())[:8],
            lesson_type="STRATEGY",
            content=strategy_content,
            trigger=strategy_trigger,
            confidence=1.0
        )
        store.add_lesson(lesson)
        print(colored("[OK] Strategy Stored.", "green"))
    except Exception as e:
        print(colored(f"[FAIL] Strategy Store Error: {e}", "red"))

    # 3.2 Query
    query_3 = "Explain the fundamental nature of light."
    print(colored(f"Query: '{query_3}' (Expect mention of 'particle' and 'wave')", "cyan"))
    
    response_3 = kernel.process_query(query_3)
    text_3 = response_3['text'].lower()
    
    if "particle" in text_3 and "wave" in text_3:
        print(colored("[PASS] Strategy Successfully Applied.", "green"))
        # We can also check logs strictly to see if "Applying Strategies" printed.
    else:
        print(colored(f"[FAIL] Strategy ignored. Response: {text_3[:100]}...", "red"))

    print(colored("\n>>> STRESS TEST COMPLETE <<<", "green", attrs=['bold']))

if __name__ == "__main__":
    full_stress_test()
