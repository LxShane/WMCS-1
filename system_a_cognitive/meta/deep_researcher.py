import json
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.identity import IdentityManager
from system_a_cognitive.meta.researcher import ResearchAgent
from config import Config

class DeepResearchAgent(ResearchAgent):
    """
    The Scientific Method Agent.
    Unlike the basic ResearchAgent, this agent:
    1. Formulates a Hypothesis.
    2. Recursively investigates gaps (Depth First Search).
    3. Critiques its own findings for completeness.
    """
    def __init__(self):
        super().__init__()
        # We reuse self.client, self.ingestor from parent

    def conduct_deep_research(self, topic: str, max_depth=2):
        print(colored(f"\n╔═══ DEEP RESEARCH SCIENTIST: '{topic}' ═══╗", "magenta", attrs=['bold']))
        
        # Phase 1: Hypothesis & breakdown
        print(colored("Step 1: Formulating Hypothesis & Taxonomy...", "yellow"))
        hypothesis_plan = self._formulate_hypothesis(topic)
        print(colored(f"  > Hierarchy: {json.dumps(hypothesis_plan, indent=2)}", "cyan"))
        
        # Phase 2: Recursive Investigation
        print(colored("\nStep 2: Recursive Investigation Loop...", "yellow"))
        
        knowledge_graph = []
        
        # Queue of distinct topics to investigate
        # We start with the breakdown items
        investigation_queue = []
        if isinstance(hypothesis_plan, list):
            investigation_queue = hypothesis_plan
        elif isinstance(hypothesis_plan, dict):
            # Flatten keys/values if complex
            investigation_queue = list(hypothesis_plan.values())
        else:
            investigation_queue = [topic] # Fallback

        # Iterate through the initial plan
        all_new_concepts = []
        for sub_topic in investigation_queue:
            concepts = self._investigate_node(sub_topic, current_depth=0, max_depth=max_depth)
            all_new_concepts.extend(concepts)
            
        print(colored(f"\n╚═══ DEEP RESEARCH COMPLETE: '{topic}' ═══╝", "magenta", attrs=['bold']))
        return all_new_concepts

    def _investigate_node(self, topic, current_depth, max_depth):
        indent = "  " * (current_depth + 1)
        print(colored(f"{indent}> Investigating: '{topic}' (Depth {current_depth})", "yellow"))
        
        created_concepts = [] # Track what we learn
        
        # 1. Search
        if Config.SERPAPI_KEY:
            results = self._search_real(topic)
            # FALLBACK: If Real Search fails (Rate Limit), use Simulation
            if results is None: 
                print(colored(f"{indent}  [!] Real Search failed. Falling back to Simulation.", "magenta"))
                results = self._search_simulated(topic)
        else:
            results = self._search_simulated(topic)
            
        # 2. Ingest Immediate Findings
        print(colored(f"{indent}  > Ingesting {len(results)} chars...", "cyan"))
        new_names = self.ingestor.ingest_text(results, source_name=f"deep_research_d{current_depth}")
        created_concepts.extend(new_names)
        
        # 3. Stop Condition
        if current_depth >= max_depth:
            return created_concepts

        # 4. Critique & Expand (The Recursive Step)
        critique = self._critique_completeness(topic, results)
        
        if critique['status'] == 'INCOMPLETE':
            print(colored(f"{indent}  [!] CRITIQUE: Missing concept '{critique['missing_term']}'", "red"))
            print(colored(f"{indent}  --> Recursively researching '{critique['missing_term']}'...", "magenta"))
            
            # Recursive Call
            sub_concepts = self._investigate_node(critique['missing_term'], current_depth + 1, max_depth)
            created_concepts.extend(sub_concepts)
        else:
            print(colored(f"{indent}  [OK] Concept definition satisfies rigor.", "green"))
            
        return created_concepts

    def _formulate_hypothesis(self, topic):
        prompt = f"""
        You are a Lead Scientist.
        Topic: "{topic}"
        Goal: Break this topic down into its 3 critical constituent mechanisms.
        Output: A JSON list of strings (e.g. ["Combustion Cycle", "Fuel Injection", "Transmission"]).
        """
        response = self.client.completion("You are a Scientist. Output JSON list.", prompt)
        try:
            return json.loads(response.strip().strip("`json").strip("`"))
        except:
            return [f"Mechanism of {topic}", f"History of {topic}", f"Applications of {topic}"]

    def _critique_completeness(self, topic, text_content):
        """
        Asks LLM: Did we define the core terms? Or did we find a new term that is undefined?
        """
        prompt = f"""
        You are an Epistemic Critic.
        Topic: "{topic}"
        Content Found: "{text_content[:2000]}..."
        
        Task:
        1. Did this content explain the core concept sufficiently for a general understanding?
        2. Are there any CRITICAL technical terms mentioned that are NOT defined?
        
        CRITICAL RULES:
        - Do NOT nitpick. If the general idea is clear, mark as COMPLETE.
        - Only mark INCOMPLETE if a key mechanism is completely partially unexplained.
        - Ignore "nice to have" details (history, trivia). Focus on MECHANISM.
        
        Output JSON:
        {{
            "status": "COMPLETE" or "INCOMPLETE",
            "missing_term": "Term to research" (or null)
        }}
        """
        response = self.client.completion("You are a Critic. Output JSON.", prompt)
        try:
            data = json.loads(response.strip().strip("`json").strip("`"))
            # Safety check
            if "status" not in data: data["status"] = "COMPLETE"
            return data
        except:
            return {"status": "COMPLETE", "missing_term": None}
