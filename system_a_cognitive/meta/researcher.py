import json
from termcolor import colored
from system_b_llm.interfaces.gemini_client import GeminiClient
from system_a_cognitive.ingestion.ingestor import ContentIngestor
from system_a_cognitive.logic.identity import IdentityManager
from config import Config

class ResearchAgent:
    """
    An autonomous agent that conducts 'Deep Research'.
    Loop:
    1. Analyze Topic -> Create Questions
    2. Search (Mock/Real) -> Get Text
    3. Ingest -> KB
    4. Review KB -> Are questions answered?
    5. Iterate or Finish
    """
    def __init__(self):
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)
        self.identity_manager = IdentityManager()
        self.ingestor = ContentIngestor(identity_manager=self.identity_manager)
        self.memory = [] # Short term history
        
    def conduct_research(self, topic: str, max_steps=3):
        print(colored(f"\n╔════ RESEARCH AGENT STARTED: '{topic}' ════╗", "cyan", attrs=['bold']))
        
        # Phase 1: Planning
        print(colored("Step 1: Planning Research Strategy...", "yellow"))
        plan = self._generate_plan(topic)
        print(colored(f"  > Generated {len(plan)} sub-questions.", "green"))
        for i, q in enumerate(plan):
            print(f"    {i+1}. {q}")
            
        # Phase 2: Execution Loop
        for i, question in enumerate(plan):
            if i >= max_steps: break
            print(colored(f"\nStep 2.{i+1}: Investigating '{question}'...", "yellow"))
            
            # A. Search (Real)
            # We now use DuckDuckGo which is free, so we always try real search first.
            results = self._search_real(question)
            mode = "LIVE WEB (DDG)"
            
            # Fallback check
            if not results:
                results = self._search_simulated(question)
                mode = "SIMULATION"

            print(colored(f"  > [{mode}] Found info source ({len(results)} chars).", "green"))
            
            # B. Ingest
            print(colored("  > Ingesting into Knowledge Base...", "cyan"))
            new_concepts = self.ingestor.ingest_text(results, source_name=f"research_step_{i}")
            print(colored(f"  > Learned {len(new_concepts)} blocks: {new_concepts}", "green"))
            
            # C. Reflection (Optional expansion)
            # We could check if we need more info here
            
        # Phase 3: Synthesis
        print(colored("\nStep 3: Synthesizing Final Report...", "magenta"))
        self._generate_report(topic)
        
    def _generate_plan(self, topic):
        prompt = f"""
        You are a Research Director.
        Topic: {topic}
        Goal: Break this down into 3 specific, distinct scientific questions to investigate mechanisms.
        Output: A JSON list of strings.
        Example: ["What is the chemical fuel?", "How does the containment work?", "What are the waste products?"]
        """
        response = self.client.completion("You are a Planner. Output JSON list only.", prompt)
        try:
            return json.loads(response.strip().strip("`json").strip("`"))
        except:
            # Fallback (Simplified for Speed)
            return [f"Key mechanism of {topic}"]

    def _search_simulated(self, query):
        """
        FALLBACK: Simulates a search result if no API key is present.
        """
        # ... (Existing simulation logic) ...
        return self.client.completion("You are a Simulator.", f"Simulate a search snippet for: {query}")

    def _search_real(self, query):
        """
        EXECUTING REAL SEARCH via DUCKDUCKGO (Free & Unlimited)
        """
        try:
            # Try new package name first
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            
            print(colored(f"  > Searching (DDG): '{query}'...", "cyan"))
            
            # Using DuckDuckGo Search (new syntax)
            results = []
            with DDGS() as ddgs:
                # 'text' method is standard for search
                gen_results = ddgs.text(query, max_results=3)
                if gen_results:
                    results = list(gen_results)
            
            if not results:
                print(colored("  [!] No results found.", "red"))
                return None
                
            snippets = []
            for r in results:
                title = r.get("title", "")
                link = r.get("href", "")
                body = r.get("body", "")
                snippets.append(f"SOURCE: {title}\nURL: {link}\nCONTENT: {body}\n")
            
            combined_text = "\n".join(snippets)
            return combined_text if combined_text else None

        except Exception as e:
            print(colored(f"  [!] Search Exception: {str(e)}", "red"))
            # Fallback to simulation if network fails
            return self._search_simulated(query)


    def _generate_report(self, topic):
        # We'd fetch all relevant blocks from the DB to synthesize
        # For now, we just acknowledge the completion
        print(colored(f"Research on '{topic}' complete. Blocks are stored in /data/concepts.", "green"))

if __name__ == "__main__":
    agent = ResearchAgent()
    agent.conduct_research("Nuclear Fusion Tokamak")
