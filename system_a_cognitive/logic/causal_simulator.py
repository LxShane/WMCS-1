import json
from termcolor import colored
from system_a_cognitive.logic.models import ConceptBlock, MetaLesson
from system_a_cognitive.memory.strategy_store import StrategyStore

class CausalSimulator:
    """
    The Event Engine for Phase 5 (General Causality).
    Predicts State Transitions: Action(Subject, Object) -> New State.
    """
    def __init__(self, strategy_store: StrategyStore = None):
        self.store = strategy_store
        
    def simulate_interaction(self, subject: ConceptBlock, action: ConceptBlock, target: ConceptBlock):
        """
        Main entry point. Returns a prediction string.
        """
        print(colored(f"\n⚡ CAUSAL SIM: {action.name}({target.name})", "yellow"))
        
        # 1. Get the Rules (From Action Definition OR Strategy Store)
        rules = self._get_causal_rules(action)
        
        # 2. Check Logic
        for rule in rules:
            outcome = self._evaluate_rule(rule, subject, target)
            if outcome:
                return outcome
                
        return "NO_CHANGE"

    def _get_causal_rules(self, action: ConceptBlock):
        """
        Retrieves rules from:
        1. The Action's own 'mechanics' facet (Static Definition).
        2. The StrategyStore (Learned Dynamic Rules).
        """
        rules = []
        
        # Static
        if "ACTION_SCHEMA" in action.facets:
            schema = action.facets["ACTION_SCHEMA"]
            rules.append({
                "source": "DEFINITION",
                "mechanics": schema.get("mechanics", ""),
                "postconditions": schema.get("postconditions", {})
            })
            
        # Dynamic (Learning)
        if self.store:
            # We treat 'MECHANISM' lessons as causal rules
            # Query format: "Action: Drop"
            lessons = self.store.recall_strategies(f"Action: {action.name}")
            for l in lessons:
                if l.lesson_type == "MECHANISM":
                    rules.append({
                        "source": "LEARNED",
                        "mechanics": l.content,
                        "postconditions": self._parse_learned_postcondition(l.content)
                    })
                    
        return rules

    def _evaluate_rule(self, rule, subject, target):
        """
        The Universal Logic Engine.
        Currently handles: "Impact > Resilience" (Physics)
        Future: "Insult > Patience" (Social)
        """
        mech = rule["mechanics"].lower()
        
        # PHYSICS: "Impact > Brittleness"
        if "impact" in mech:
            # 1. Estimate Impact Force (from Subject/Action)
            impact_force = 5 # Default Medium
            if "high_energy" in mech: impact_force = 8
            
            # 2. Estimate Resistance (Target Properties)
            resistance = 5
            props = target.facets.get("STRUCTURAL", {}).get("material_properties", {})
            
            # Simple Physics Heuristic
            rigidity = props.get("rigidity", "MEDIUM").upper()
            state = props.get("state", "SOLID").upper()
            
            if rigidity == "HIGH" and "BRITTLE" in mech: 
                # Glass is Rigid but Brittle -> Low Resilience to Shock
                resistance = 2 
            elif rigidity == "LOW": 
                # Rubber -> High Resilience
                resistance = 8
                
            print(f"  > Physics Calc: Force({impact_force}) vs Resistance({resistance})")
            
            if impact_force > resistance:
                return rule["postconditions"]
                
            if impact_force > resistance:
                return rule["postconditions"]

        # SOCIAL: "Status Attack" (Insult, Intimidate)
        if "status" in mech or "insult" in mech:
            # 1. Get Social Profile
            profile = target.facets.get("SOCIAL_PROFILE", {})
            rels = profile.get("relationships", [])
            
            # 2. Determine Relationship to Subject
            # Simple string matching for now
            is_friend = any("Friend" in r for r in rels)
            is_enemy = any("Enemy" in r for r in rels)
            
            print(f"  > Social Calc: Agent({subject.name}) vs Target({target.name}) [Friend={is_friend}, Enemy={is_enemy}]")
            
            # 3. Calculate Emotional Outcome
            if is_friend:
                return {"mental_state": "HURT", "trust": "-10"}
            elif is_enemy:
                return {"mental_state": "ANGRY", "trust": "-5"}
            else:
                return {"mental_state": "ANNOYED", "trust": "-2"}
                
        # GENERIC / LEARNED (The Catch-All)
        # If we learned "X causes Y", and we are doing X, just do Y.
        if rule.get("source") == "LEARNED":
             print(f"  > Applying Learned Rule: '{mech}'")
             return rule["postconditions"]

        return None

    def _parse_learned_postcondition(self, content):
        """
        Extracts the 'Effect' from a natural language lesson string.
        Simple heuristic for now.
        """
        if "breaks" in content: return {"state": "BROKEN"}
        if "purple" in content: return {"color": "PURPLE"}
        return {"state": "CHANGED"}
