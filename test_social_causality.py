from system_a_cognitive.logic.causal_simulator import CausalSimulator
from system_a_cognitive.logic.models import ConceptBlock
from termcolor import colored

def test_social_theory():
    print(colored("╔═══ TEST: THEORY OF MIND ═══╗", "magenta", attrs=['bold']))
    
    sim = CausalSimulator()
    
    # 1. Subject
    me = ConceptBlock(name="User", primary_type="LIVING_SYSTEM", id={"group": 0, "item": 1})
    
    # 2. Action: Insult
    insult = ConceptBlock(name="Insult", primary_type="ACTION", id={"group": 60, "item": 5})
    # We define the action mechanism statically here to simulate a known concept
    insult.facets["ACTION_SCHEMA"] = {
        "mechanics": "Attack on status/ego. Reduces trust.",
        "postconditions": {"mental_state": "NEGATIVE"}
    }
    
    # 3. Scenario A: Insulting a Friend
    print(colored("\nStep 1: Insulting a FRIEND...", "cyan"))
    friend = ConceptBlock(name="Alice", primary_type="LIVING_SYSTEM", id={"group": 20, "item": 50})
    friend.facets["SOCIAL_PROFILE"] = {
        "relationships": ["Friend of User"],
        "traits": {"agreeableness": "HIGH"}
    }
    
    outcome_friend = sim.simulate_interaction(me, insult, friend)
    print(f"Outcome: {outcome_friend}")
    
    # 4. Scenario B: Insulting an Enemy
    print(colored("\nStep 2: Insulting an ENEMY...", "cyan"))
    enemy = ConceptBlock(name="Bob", primary_type="LIVING_SYSTEM", id={"group": 20, "item": 51})
    enemy.facets["SOCIAL_PROFILE"] = {
        "relationships": ["Enemy of User"],
        "traits": {"agreeableness": "LOW"}
    }
    
    outcome_enemy = sim.simulate_interaction(me, insult, enemy)
    print(f"Outcome: {outcome_enemy}")

    # 5. Verification
    if outcome_friend.get("mental_state") == "HURT" and outcome_enemy.get("mental_state") == "ANGRY":
        print(colored("[PASS] System understands Contextual Emotion.", "green"))
    else:
        print(colored("[FAIL] Emotional logic is flat.", "red"))

if __name__ == "__main__":
    test_social_theory()
