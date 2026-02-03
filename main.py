import json
import os
from termcolor import colored
from server.telemetry import telemetry

def tprint(text, color="white"):
    """Helper to print to stdout AND telemetry."""
    print(colored(text, color))
    telemetry.log(text, color=color)

# Import Systems
from system_a_cognitive.logic.models import ConceptBlock, ConceptID
from system_a_cognitive.epistemic.gate import EpistemicGate
from system_b_llm.parsers.query_parser import QueryParser
from system_b_llm.generators.response_generator import ResponseGenerator

from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient

class LazyBlockDict:
    """Proxy to handle legacy self.blocks access lazily."""
    def __init__(self, kernel):
        self.kernel = kernel
        
    def __getitem__(self, key):
        val = self.kernel.get_block(key)
        if val is None: raise KeyError(key)
        return val
        
    def get(self, key, default=None):
        val = self.kernel.get_block(key)
        return val if val is not None else default
        
    def __contains__(self, key):
        return self.kernel.block_exists(key)
        
    def __len__(self):
        return len(self.kernel.file_map)
        
    def keys(self):
        return self.kernel.file_map.keys()
        
    def values(self):
        # Scan all
        for key in self.kernel.file_map:
            yield self.kernel.get_block(key)

    def items(self):
        for key in self.kernel.file_map:
            yield (key, self.kernel.get_block(key))

class WMCS_Kernel:
    def __init__(self):
        self.block_cache = {} # Lazy Loaded Blocks (RAM)
        self.file_map = {}    # Name -> FilePath Map
        self.blocks = LazyBlockDict(self) # Backward Compatibility Proxy
        
        # Initialize LLM Client
        try:
            self.llm_client = GeminiClient(
                api_key=Config.LLM_API_KEY,
                model=Config.LLM_MODEL
            )
            print(colored(f"Gemini Client Connected: {Config.LLM_MODEL}", "green"))
        except Exception as e:
            print(colored(f"Gemini Client Failed: {e}. Using Fallback.", "red"))
            self.llm_client = None

        self.parser = QueryParser(self.llm_client)
        self.gate = EpistemicGate()
        self.generator = ResponseGenerator(self.llm_client)
        
        from system_a_cognitive.logic.functional_search import FunctionalSearcher
        self.func_search = FunctionalSearcher()
        
        # VECTOR MEMORY
        from system_a_cognitive.memory.chroma_store import ChromaStore
        self.vector_store = ChromaStore()

        # INGESTION & IDENTITY
        from system_a_cognitive.ingestion.ingestor import ContentIngestor
        from system_a_cognitive.logic.identity import IdentityManager
        
        self.identity_manager = IdentityManager()
        self.ingestor = ContentIngestor(identity_manager=self.identity_manager)
        self.memory_path = "data"
        self.status = "Idle" # UI Feedback Loop

    def load_data(self, force=False):
        tprint("Step 0: Mapping Concept Blocks (Lazy Load)...", "cyan")
        
        # 1. Map Files (No content reading)
        base_path = "data/concepts"
        if not os.path.exists(base_path): return

        count = 0
        self.file_map = {}
        for filename in os.listdir(base_path):
            if not filename.endswith(".json"): continue
            # Heuristic: filename 'cat_paw.json' -> key 'cat_paw'
            # This matches our ingestion sanitization: name.lower().replace(' ', '_')
            key = filename.replace(".json", "")
            self.file_map[key] = os.path.join(base_path, filename)
            count += 1
        
        tprint(f"  Mapped {count} Concept Files.", "green")

        # 2. Vector Indexing
        tprint("Step 0.5: Checking Vector Index...", "cyan")
        # Chroma is persistent. Check count.
        db_count = self.vector_store.count()
        file_count = count
        
        print(colored(f"  > DB has {db_count} vectors. Disk has {file_count} JSONs.", "white"))
        
        if force or db_count < file_count:
            print(colored(f"  > Index Outdated (DB:{db_count} vs Disk:{file_count}). Syncing JSONs...", "yellow"))
            # Optimized: ContentIngestor handles the heavy lifting
            self.ingestor.ingest_all(self.memory_path, self.vector_store)
            print(colored("  > Sync Complete.", "green"))
            print(colored("  > Vector DB ready (Persistent).", "green"))
    
    def get_block(self, name_or_key: str):
        """Lazy load a block by name."""
        if not name_or_key: return None
        
        # Normalize: 'Cat Paw' -> 'cat_paw'
        key = name_or_key.lower().replace(" ", "_")
        
        # 1. Check RAM Cache
        if key in self.block_cache:
            return self.block_cache[key]
            
        # 2. Check File Map
        if key in self.file_map:
            try:
                with open(self.file_map[key], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.block_cache[key] = data # Cache it
                    return data
            except Exception as e:
                print(colored(f"  [Error] Failed to lazy load {key}: {e}", "red"))
                return None
        
        return None

    def block_exists(self, name_or_key: str):
        key = name_or_key.lower().replace(" ", "_")
        return (key in self.block_cache) or (key in self.file_map)
    
    def _trigger_reflex(self, text):
        """Helper to run Deep Research and return new blocks."""
        tprint("\n[!] GAP DETECTED: Insufficient knowledge.", "red")
        tprint("Step 2.X (Reflex): Triggering DEEP Autonomous Research...", "magenta")
        
        self.status = "Researching unknown concept..."
        telemetry.log(self.status, "magenta")
        
        from system_a_cognitive.meta.deep_researcher import DeepResearchAgent
        agent = DeepResearchAgent()
        new_concepts = agent.conduct_deep_research(text, max_depth=1)
        
        self.status = f"Ingesting {len(new_concepts)} new facts..."
        print(colored(f"Step 2.X: Targeted Ingest of {len(new_concepts)} new blocks...", "green"))
        
        new_real_blocks = []
        base_path = os.path.join(self.memory_path, "concepts")
        
        if new_concepts:
            import time
            time.sleep(0.5) 
            for name in new_concepts:
                # Robust sanitization
                safe_name = name.lower().replace(' ', '_')
                for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                    safe_name = safe_name.replace(char, '-')

                fname = f"{safe_name}.json"
                fpath = os.path.join(base_path, fname)
                msg = f"DEBUG: Reflex looking for file: {fpath}"
                print(colored(msg, "magenta"))
                with open("server_debug.log", "a") as log:
                    log.write(msg + "\n")
                
                if os.path.exists(fpath):
                    with open("server_debug.log", "a") as log: log.write(f"  > FOUND: {fname}\n")
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            block = json.load(f)
                            # UPDATE LAZY MAPS
                            key = block["name"].lower().replace(' ', '_')
                            self.block_cache[key] = block
                            self.file_map[key] = fpath
                            # self.vector_store.add_concept_block(block) # Should be handled by Ingestor or done once
                            new_real_blocks.append(block)
                    except Exception as e:
                        print(colored(f"  > Failed to ingest {fname}: {e}", "red"))
                        
        print(colored("Step 2.X: Retrying Query...", "cyan"))
        return new_real_blocks

    def process_query(self, text: str, allow_research: bool = True, injected_blocks: list = None):
        self.status = "Thinking (" + text[:20] + "...)"
        telemetry.log(f"Processing: {text}", "cyan")

        # COMMAND INTERCEPTION
        if text.startswith("/teach "):
            try:
                proposition = text.replace("/teach ", "").strip()
                tprint(f"Teaching Mode: Learning '{proposition}'...", "magenta")
                created = self.ingestor.ingest_proposition(proposition)
                
                # HOT LOAD
                for name in created:
                    key = name.lower().replace(' ', '_')
                    fname = f"{key}.json"
                    fpath = os.path.join(self.memory_path, "concepts", fname)
                    if os.path.exists(fpath):
                        with open(fpath, "r", encoding="utf-8") as f:
                             block = json.load(f)
                             self.blocks.kernel.block_cache[key] = block
                             self.blocks.kernel.file_map[key] = fpath
                             tprint(f"  > Hot-Loaded learned concept: {name}", "green")
                
                return {
                    "text": f"I have learned {len(created)} new concept(s): {', '.join(created)}.",
                    "visited_nodes": []
                }
            except Exception as e:
                return {"text": f"Teaching Failed: {str(e)}", "visited_nodes": []}

        # 1. Parse (System B)
        intent = self.parser.parse(text)
        
        # 2. Reasoning (System A)
        contract = None
        
        # AGENTIC NAVIGATION
        tprint("Step 2 (Reasoning): Launching Agentic Navigator...", "cyan")
        
        from system_a_cognitive.logic.navigator import ConceptNavigator
        navigator = ConceptNavigator(self)
        
        # 1. Semantic Entry Point
        start_blocks = []
        tprint(f"  > Semantic Search for: '{text}'...", "cyan")
        hits = self.vector_store.search(text, top_k=3, threshold=0.45)
        
        for hit in hits:
            name = hit['metadata'].get('name', '')
            # Use Helper (auto-normalizes)
            if self.block_exists(name):
                block = self.get_block(name)
                if block:
                    start_blocks.append(block)
                    print(colored(f"    - Found Entry: {name} (Score: {hit['score']:.2f})", "green"))
        
        if not start_blocks:
            print(colored("  > No semantic entry points found.", "red"))

        # INJECTION (Robustness Fix)
        if injected_blocks:
            print(colored(f"  > Injecting {len(injected_blocks)} newly learned blocks directly.", "cyan"))
            start_blocks.extend(injected_blocks)
            
        # CURIOSITY REFLEX: If we know NOTHING (and no injection), research immediately.
        if not start_blocks and allow_research:
            injected = self._trigger_reflex(text)
            return self.process_query(text, allow_research=False, injected_blocks=injected)

        # 2. Agentic Traversal
        final_blocks = navigator.navigate(start_blocks, text, max_steps=3)
        
        # BLENDING: Ensure injected blocks are present in final context (if Navigator didn't pick them up)
        if injected_blocks:
             if not final_blocks:
                 final_blocks = []
             existing_ids = {b.get('name') for b in final_blocks}
             for b in injected_blocks:
                 if b.get('name') not in existing_ids:
                     final_blocks.append(b)
            
        # GAP DETECTION & REFLEX (Epistemic Curiosity)
        if not final_blocks and allow_research:
            injected = self._trigger_reflex(text)
            return self.process_query(text, allow_research=False, injected_blocks=injected)
        
        found_info = []
        if final_blocks:
            print(colored(f"  > Context Path: {[b.get('name') for b in final_blocks]}", "yellow"))
            for b in final_blocks:
                concept_name = b.get('name', 'Unknown')
                concept_id = b.get('id', {'group': 0, 'item': 0})
                # INCLUDE claims AND facets (backward compatibility)
                # EXTRACT METADATA ROBUSTLY
                sl = b.get("surface_layer", {})
                dl = b.get("deep_layer", {})
                
                definition = b.get("definition") or sl.get("definition", "")
                mechanism = dl.get("mechanism", "")
                origin = dl.get("origin", "")
                
                content_dump = {
                    "definition": definition,
                    "mechanism": mechanism,
                    "origin": origin,
                    "claims": b.get("claims", []),
                    "facets": b.get("facets", {})
                }
                # Extract computed confidence from Navigator (default 1.0)
                path_conf = b.get('_computed_confidence', 1.0)
                
                context_str = f"Concept: {concept_name} (ID: {concept_id}, Conf: {path_conf:.2f}). Content: {json.dumps(content_dump, default=str)}"
                found_info.append(context_str)
        else:
            found_info = ["No specific internal concepts found."]

        # STEP 3: COGNITIVE PROCESSING (Synthesizing Logic)
        tprint("Step 3 (Cognitive Processing): Synthesizing Logic...", "cyan")
        
        # META-LEARNING INJECTION
        reasoning_prompt_header = "SYSTEM ROLE: You are the Logic Engine (System A).\\n"
        
        # 1. Recall relevant strategies
        try:
             from system_a_cognitive.memory.strategy_store import StrategyStore
             # Dirty hack: We need a singleton or to init it in __init__
             # Ideally validation happens in init.
             if not hasattr(self, 'strategy_store'):
                  try:
                      self.strategy_store = StrategyStore()
                  except:
                      self.strategy_store = None
             
             if self.strategy_store:
                  strategies = self.strategy_store.recall_strategies(text, top_k=2)
                  if strategies:
                      print(colored(f"  > [Meta-Learning] Applying Strategies: {strategies}", "magenta"))
                      reasoning_prompt_header += f"ADAPTIVE STRATEGIES (LEARNED FROM PAST):\\n"
                      for s in strategies:
                           reasoning_prompt_header += f"- {s}\\n"
                      reasoning_prompt_header += "\\n"
        except Exception as e:
             print(f"Strategy Injection Failed: {e}")

        reasoning_prompt = (
            f"{reasoning_prompt_header}"
            f"YOUR GOAL: Answer the User Query using ONLY the provided Memory Blocks.\\n\\n"
            f"MEMORY BLOCKS:\\n{json.dumps(found_info, indent=2)}\\n\\n"
            f"USER QUERY: \"{text}\"\\n\\n"
            "INSTRUCTIONS:\\n"
            "1. ID Identification: Extract key terms from the USER QUERY and match them to Concept IDs in Memory.\\n"
            "2. Missing Entity Check: If the USER QUERY asks about a concept NOT in Memory, you MUST output \"Missing Concept: [Term]\" and STOP.\\n"
            "3. Logical Synthesis: Use the claims in Memory to construct an answer.\\n"
            "4. Conflict Detection: Report any contradictions.\\n\\n"
            "FORMAT REQURIED:\\n"
            f"| Query: \"{text}\"\\n"
            "| 1. ID Identification: [Match results]\\n"
            "| 2. Missing Entity Check: [Found/Missing]\\n"
            "| 3. Logic Check: [Analysis]\\n"
            "| 4. Conclusion: [Final Answer]\\n"
            "| 5. CONFIDENCE_SCORE: [0-100]"
        )
        # DEBUG: Show what we are feeding the LLM
        # print(colored(f"  DEBUG: Feeding {len(found_info)} blocks to Logic Engine.", "magenta"))

        # We use the raw completion here to get the "Thought Process"
        reasoning_trace = self.llm_client.completion(
            "You are a Logic Engine. Output clear, step-by-step reasoning.", 
            reasoning_prompt
        )
        
        # ACTIVE LEARNING LOOP
        # Check if the Logic Engine identified a specific gap
        if "Missing Concept" in reasoning_trace and allow_research:
            import re
            # Try to extract the missing term. Heuristic: "Missing Concept: Dog" or "Missing Concept: 'Dog'"
            # We look for the line
            missing_term = None
            for line in reasoning_trace.split('\\n'):
                if "Missing Concept" in line:
                     # Extract the last word or quoted word
                    try:
                        missing_term = line.split(":")[-1].strip().strip("'").strip('"').strip(".").strip()
                    except: pass
                    
            if missing_term and len(missing_term) > 2 and missing_term.lower() != "none":
                print(colored(f"\\n[!] LOGIC GAP DETECTED: Unknown Concept '{missing_term}'", "magenta", attrs=['bold']))
                
                # Use Helper
                injected = []
                try:
                    injected = self._trigger_reflex(missing_term)
                except Exception as e:
                    print(colored(f"  > Reflex Failed: {e}", "red"))

                print(colored("Step 2.X: Retrying Query with new Brain...", "cyan"))
                return self.process_query(text, allow_research=False, injected_blocks=injected) # Recursion

        
        # Print the Thought Process
        tprint("  REASONING TRACE:", "yellow")
        for line in reasoning_trace.split('\n'):
            tprint(f"    | {line}", "yellow")

        # EXTRACT CONFIDENCE SCORE (Self-Reflection)
        import re
        calculated_confidence = 0.8 if final_blocks else 0.1
        match = re.search(r"CONFIDENCE_SCORE:\s*(\d+)", reasoning_trace)
        if match:
            score = int(match.group(1))
            calculated_confidence = score / 100.0
            print(colored(f"  > Self-Corrected Confidence: {calculated_confidence}", "magenta"))

        # Pass the reasoning to the Gate/Generator
        combined_context = found_info + [f"Logic Synthesis: {reasoning_trace}"]
        
        contract = self.gate.generate_contract(
            confidence=calculated_confidence, 
            assumptions=combined_context,
            positive_assertions=[], 
            negative_assertions=[]
        )

        # 3. Gate
        tprint("Step 3 (Epistemic Gate): Contract Generated.", "cyan")
        tprint(f"  > Grade: {contract.grade.grade}", "magenta")
        
        # 4. Generate
        tprint("Step 4 (Generate): Response...", "cyan")
        # Ensure raw_query is available even if parser result is strictly structured
        if isinstance(intent, dict):
            intent['raw_query'] = text
        else:
            intent = {'raw_query': text} # Fallback if parser failed or returns obj
            
        response_text = self.generator.generate(contract, intent)
        
        # Extract Visited IDs for Visualization
        visited_ids = []
        if final_blocks:
            for b in final_blocks:
                # Construct Vector Store ID from block ID: "Group,Item"
                gid = f"{b.get('id',{}).get('group',0)},{b.get('id',{}).get('item',0)}"
                visited_ids.append(gid)
        
        # LATE BINDING REFLEX:
        if contract.grade.grade in ["CANNOT_CONCLUDE", "UNCERTAIN"] and allow_research:
            print(colored("\\n[!] LATE GATING REFLEX: Answer deemed insufficient. Triggering Research.", "magenta"))
            injected = self._trigger_reflex(text)
            # Recursively process with new info
            return self.process_query(text, allow_research=False, injected_blocks=injected)

        return {
            "text": response_text,
            "visited_nodes": visited_ids
        }

if __name__ == "__main__":
    pass
