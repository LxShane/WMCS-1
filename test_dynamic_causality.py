from system_a_cognitive.logic.causal_simulator import CausalSimulator
from system_a_cognitive.logic.models import ConceptBlock, MetaLesson
from system_a_cognitive.memory.strategy_store import StrategyStore
from termcolor import colored
import time

def test_dynamic_learning():
    print(colored("╔═══ TEST: DYNAMIC CAUSALITY ═══╗", "magenta", attrs=['bold']))
    
    # 1. Setup Mock Data
    store = StrategyStore()
    sim = CausalSimulator(strategy_store=store)
    
    # Subject: User (Abstract)
    subject = ConceptBlock(name="User", primary_type="LIVING_SYSTEM", id={"group": 0, "item": 1})
    
    # Target: Frobnosticator (Unknown Object)
    target = ConceptBlock(name="Frobnosticator", primary_type="INANIMATE_OBJECT", id={"group": 99, "item": 1})
    target.facets["STRUCTURAL"] = {"material_properties": {"state": "SOLID"}}
    
    # Action: Glorp (Unknown Action)
    action = ConceptBlock(name="Glorp", primary_type="ACTION", id={"group": 60, "item": 1})
    
    # 2. Baseline Test (Should Fail/No Change)
    print(colored("\nStep 1: Baseline (Before Learning)", "cyan"))
    outcome = sim.simulate_interaction(subject, action, target)
    print(f"Outcome: {outcome}")
    
    if outcome == "NO_CHANGE":
        print(colored("[PASS] Baseline correct (No knowledge).", "green"))
    else:
        print(colored("[FAIL] Baseline hallucinated.", "red"))

    # 3. Teach the Rule (The "Matrix" Upload)
    print(colored("\nStep 2: Learning Rule 'Glorp -> Purple'...", "cyan"))
    lesson = MetaLesson(
        id="lesson_glorp_01",
        lesson_type="MECHANISM",
        content="Glorping causes objects to turn purple.",
        trigger="Action: Glorp"
    )
    store.add_lesson(lesson)
    time.sleep(1) # Wait for DB sync
    
    # 4. Usage Test (Should Succeed)
    print(colored("\nStep 3: Dynamic Application (After Learning)", "cyan"))
    outcome_2 = sim.simulate_interaction(subject, action, target)
    print(f"Outcome: {outcome_2}")
    
    if isinstance(outcome_2, dict) and outcome_2.get("color") == "PURPLE":
        print(colored("[PASS] Dynamic Logic Learned! System predicts PERCEPTION_CHANGE.", "green"))
    else:
        print(colored(f"[FAIL] Did not apply learned rule. Got: {outcome_2}", "red"))

if __name__ == "__main__":
    test_dynamic_learning()
