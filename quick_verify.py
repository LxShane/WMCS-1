from main import WMCS_Kernel
from termcolor import colored
from system_a_cognitive.logic.models import MetaLesson

def quick_verify():
    kernel = WMCS_Kernel()
    kernel.load_data(force=True)
    
    # SCENARIO 2: SPATIAL
    print(colored("\n--- SCENARIO 2: SPATIAL ---", "magenta"))
    # Secondary_Immune_Response we know is good.
    resp = kernel.process_query("Where is the Secondary Immune Response located?", allow_research=False)
    print(f"Resp: {resp['text']}")
    if "spleen" in resp['text'].lower():
        print(colored("[PASS] Spatial Data Used.", "green"))
    else:
        print(colored("[FAIL] Spatial keywords missing.", "red"))

    # SCENARIO 3: META-LEARNING
    print(colored("\n--- SCENARIO 3: META-LEARNING ---", "magenta"))
    # Inject Strategy
    import uuid
    from system_a_cognitive.memory.strategy_store import StrategyStore
    store = StrategyStore()
    lesson = MetaLesson(
        id=str(uuid.uuid4())[:8],
        lesson_type="STRATEGY",
        content="When explaining 'Light', mention it is a particle and a wave.",
        trigger="nature of light",
        confidence=1.0
    )
    store.add_lesson(lesson)
    print("Strategy Injected.")
    
    resp = kernel.process_query("Explain the fundamental nature of light.", allow_research=False)
    print(f"Resp: {resp['text']}")
    if "particle" in resp['text'].lower() and "wave" in resp['text'].lower():
        print(colored("[PASS] Strategy Applied.", "green"))
    else:
        print(colored("[FAIL] Strategy Ignored.", "red"))

if __name__ == "__main__":
    quick_verify()
