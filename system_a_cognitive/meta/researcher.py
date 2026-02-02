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
            
            # A. Search (Real or Sim)
            if Config.SERPAPI_KEY:
                results = self._search_real(question)
                mode = "LIVE WEB"
            else:
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
        EXECUTING REAL SEARCH via SERPAPI
        """
        try:
            import urllib.parse
            import urllib.request
            
            if not Config.SERPAPI_KEY:
                return "Error: No SERPAPI_KEY found in Config."

            print(colored(f"  > Pinging SerpAPI for: '{query}'...", "cyan"))
            
            params = {
                "engine": "google",
                "q": query,
                "api_key": Config.SERPAPI_KEY,
                "num": 3
            }
            query_string = urllib.parse.urlencode(params)
            url = f"https://serpapi.com/search?{query_string}"
            
            with urllib.request.urlopen(url) as response:
                if response.status != 200:
                    print(colored(f"  [!] SerpAPI Error: {response.status}", "red"))
                    return None
                
                data = json.loads(response.read().decode('utf-8'))
                
                # Check for error in JSON body
                if "error" in data:
                     print(colored(f"  [!] SerpAPI JSON Error: {data['error']}", "red"))
                     return None

                # Extract Snippets
                snippets = []
                if "organic_results" in data:
                    for result in data["organic_results"]:
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")
                        link = result.get("link", "")
                        snippets.append(f"SOURCE: {title}\nURL: {link}\nCONTENT: {snippet}\n")
                
                combined_text = "\n".join(snippets)
                return combined_text if combined_text else None

        except Exception as e:
            print(colored(f"  [!] Search Exception: {str(e)}", "red"))
            return None




    def _generate_report(self, topic):
        # We'd fetch all relevant blocks from the DB to synthesize
        # For now, we just acknowledge the completion
        print(colored(f"Research on '{topic}' complete. Blocks are stored in /data/concepts.", "green"))

if __name__ == "__main__":
    agent = ResearchAgent()
    agent.conduct_research("Nuclear Fusion Tokamak")
