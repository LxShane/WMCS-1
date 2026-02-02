import json
import os
from termcolor import colored

# Import Systems
from system_a_cognitive.logic.models import ConceptBlock, ConceptID
from system_a_cognitive.epistemic.gate import EpistemicGate
from system_b_llm.parsers.query_parser import QueryParser
from system_b_llm.generators.response_generator import ResponseGenerator

from config import Config
from system_b_llm.interfaces.gemini_client import GeminiClient

class WMCS_Kernel:
    def __init__(self):
        self.blocks = {}
        
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
        print(colored("Step 0: Loading Concept Blocks...", "cyan"))
        
        # 1. Load JSONs
        base_path = "data/concepts"
        if not os.path.exists(base_path): return

        count = 0
        blocks_list = []
        for filename in os.listdir(base_path):
            if not filename.endswith(".json"): continue
            try:
                with open(os.path.join(base_path, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "name" not in data: continue
                    self.blocks[data["name"].lower()] = data
                    blocks_list.append(data)
                    count += 1
            except: pass
        
        print(colored(f"  Loaded {count} Concept Blocks.", "green"))

        # 2. Vector Indexing
        # 2. Vector Indexing
        print(colored("Step 0.5: Checking Vector Index...", "cyan"))
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
    
    def _trigger_reflex(self, text):
        """Helper to run Deep Research and return new blocks."""
        print(colored("\n[!] GAP DETECTED: Insufficient knowledge.", "red"))
        print(colored("Step 2.X (Reflex): Triggering DEEP Autonomous Research...", "magenta"))
        
        self.status = "Researching unknown concept..."
        
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
                            self.blocks[block["name"].lower()] = block
                            self.vector_store.add_concept_block(block)
                            new_real_blocks.append(block)
                    except Exception as e:
                        print(colored(f"  > Failed to ingest {fname}: {e}", "red"))
                        
        print(colored("Step 2.X: Retrying Query...", "cyan"))
        return new_real_blocks

    def process_query(self, text: str, allow_research: bool = True, injected_blocks: list = None):
        self.status = "Thinking (" + text[:20] + "...)"
        # 1. Parse (System B)
        intent = self.parser.parse(text)
        
        # 2. Reasoning (System A)
        contract = None
        
        # AGENTIC NAVIGATION
        print(colored("Step 2 (Reasoning): Launching Agentic Navigator...", "cyan"))
        
        from system_a_cognitive.logic.navigator import ConceptNavigator
        navigator = ConceptNavigator(self)
        
        # 1. Semantic Entry Point
        start_blocks = []
        print(colored(f"  > Semantic Search for: '{text}'...", "cyan"))
        hits = self.vector_store.search(text, top_k=3, threshold=0.45)
        
        for hit in hits:
            name = hit['metadata'].get('name', '').lower()
            if name in self.blocks:
                start_blocks.append(self.blocks[name])
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

            final_blocks = []
            # Create a fallback contract for "I don't know"
            from system_a_cognitive.epistemic.gate import Contract, AnswerGrade
            grade = AnswerGrade("CANNOT_CONCLUDE", 0.0, False, "No memory found.")
            contract = Contract(grade, 0.0, [], [], ["No relevant concepts found in memory."], False)
        else:
             # 2. Agentic Traversal
             final_blocks = navigator.navigate(start_blocks, text, max_steps=3)
             
             # FALLBACK: If Navigator found nothing, but we INJECTED data, use the injection.
             if not final_blocks and injected_blocks:
                 print(colored("  > Navigation yielded 0 results. Reverting to Injected Blocks.", "cyan"))
                 final_blocks = list(injected_blocks)
             elif injected_blocks:
                 # ALWAYS include injected blocks to prevent "Noise" from crowding out "Signal"
                 print(colored(f"  > Merging {len(injected_blocks)} injected blocks into context.", "cyan"))
                 # Avoid duplicates
                 existing_ids = {b['name'] for b in final_blocks}
                 for b in injected_blocks:
                     if b['name'] not in existing_ids:
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
             print(colored("Step 3 (Cognitive Processing): Synthesizing Logic...", "cyan"))
             
             reasoning_prompt = f"""SYSTEM ROLE: You are the Logic Engine (System A).
YOUR GOAL: Answer the User Query using ONLY the provided Memory Blocks.

MEMORY BLOCKS:
{json.dumps(found_info, indent=2)}

USER QUERY: "{text}"

INSTRUCTIONS:
1. ID Identification: Extract key terms from the USER QUERY and match them to Concept IDs in Memory.
2. Missing Entity Check: If the USER QUERY asks about a concept NOT in Memory, you MUST output "Missing Concept: [Term]" and STOP.
3. Logical Synthesis: Use the claims in Memory to construct an answer.
4. Conflict Detection: Report any contradictions.

FORMAT REQURIED:
| Query: "{text}"
| 1. ID Identification: [Match results]
| 2. Missing Entity Check: [Found/Missing]
| 3. Logic Check: [Analysis]
| 4. Conclusion: [Final Answer]
| 5. CONFIDENCE_SCORE: [0-100]
"""
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
                for line in reasoning_trace.split('\n'):
                    if "Missing Concept" in line:
                         # Extract the last word or quoted word
                        try:
                            missing_term = line.split(":")[-1].strip().strip("'").strip('"').strip(".").strip()
                        except: pass
                        
                if missing_term and len(missing_term) > 2 and missing_term.lower() != "none":
                    print(colored(f"\n[!] LOGIC GAP DETECTED: Unknown Concept '{missing_term}'", "magenta", attrs=['bold']))
                    
                    # Use Helper
                    injected = []
                    try:
                        injected = self._trigger_reflex(missing_term)
                    except Exception as e:
                        print(colored(f"  > Reflex Failed: {e}", "red"))

                    print(colored("Step 2.X: Retrying Query with new Brain...", "cyan"))
                    return self.process_query(text, allow_research=False, injected_blocks=injected) # Recursion

             
             # Print the Thought Process
             print(colored("  REASONING TRACE:", "yellow"))
             for line in reasoning_trace.split('\n'):
                 print(colored(f"    | {line}", "yellow"))

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
        print(colored("Step 3 (Epistemic Gate): Contract Generated.", "cyan"))
        print(colored(f"  > Grade: {contract.grade.grade}", "magenta"))
        print(colored(f"  > Must Say: {contract.can_assert}", "magenta"))
        print(colored(f"  > Conflicts: {contract.cannot_assert}", "magenta"))
        
        # 4. Generate
        print(colored("Step 4 (Generate): Response...", "cyan"))
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
             print(colored("\n[!] LATE GATING REFLEX: Answer deemed insufficient. Triggering Research.", "magenta"))
             injected = self._trigger_reflex(text)
             # Recursively process with new info
             return self.process_query(text, allow_research=False, injected_blocks=injected)

        return {
            "text": response_text,
            "visited_nodes": visited_ids
        }

    def interactive_mode(self):
        print(colored("\n╔════════════════════════════════════════════╗", "magenta"))
        print(colored("║        WMCS INTERACTIVE TERMINAL v1.1      ║", "magenta"))
        print(colored("╚════════════════════════════════════════════╝", "magenta"))
        print("Commands:")
        print("  /learn <text>  -> Teach the system a new fact (raw text)")
        print("  /ingest <path> -> Teach the system from a file")
        print("  /trust         -> (After Query) Auto-ingest Verifier correction")
        print("  /consolidate   -> Auto-link unidirectional concepts")
        print("  /diagnose      -> Run system self-check")
        print("  /audit         -> Verify Knowledge Graph Logic")
        print("  /subconscious  -> Toggle Background Mind (on/off)")
        print("  /quit          -> Exit")
        print("  <message>      -> Chat with the system")
        
        from system_a_cognitive.meta.store import MetaReasoningStore
        from system_a_cognitive.meta.reflection import ReflectionEngine
        from system_a_cognitive.meta.verifier import ExternalVerifier
        from system_a_cognitive.logic.models import ReasoningTrace, Outcome
        
        # Ingestor is now self.ingestor
        meta_store = MetaReasoningStore()
        reflector = ReflectionEngine()
        verifier = ExternalVerifier(self.llm_client)

        while True:
            try:
                user_input = input(colored("\nYOU > ", "yellow")).strip()
                print(f"DEBUG: Input received: '{user_input}'")
                if not user_input: continue
                
                if user_input.lower() in ["/quit", "/exit"]:
                    print("Goodbye.")
                    break
                
                if user_input.startswith("/learn "):
                    text_to_learn = user_input[7:].strip()
                    print(colored("SYSTEM: Ingesting knowledge...", "cyan"))
                    new_concepts = ingestor.ingest_text(text_to_learn, source_name="user_chat")
                    
                    if new_concepts:
                        print(colored(f"SYSTEM: Learned {len(new_concepts)} new concepts: {new_concepts}", "green"))
                        print("SYSTEM: Reloading memory...")
                        self.load_data() 
                    else:
                        print(colored("SYSTEM: No clear concepts found to learn.", "red"))

                elif user_input.startswith("/ingest "):
                    path_to_learn = user_input[8:].strip()
                    # Handle quotes if present
                    if path_to_learn.startswith('"') and path_to_learn.endswith('"'):
                        path_to_learn = path_to_learn[1:-1]
                        
                    print(colored(f"SYSTEM: Ingesting file: {path_to_learn}...", "cyan"))
                    
                    # Fix for relative paths if needed
                    if not os.path.isabs(path_to_learn):
                        path_to_learn = os.path.abspath(path_to_learn)
                        
                    new_concepts = ingestor.ingest_file(path_to_learn)
                    
                    if new_concepts and not new_concepts[0].startswith("Error"):
                        print(colored(f"SYSTEM: Learned {len(new_concepts)} new concepts from file.", "green"))
                        print(f"Concepts: {new_concepts}")
                        print("SYSTEM: Reloading memory...")
                        self.load_data() 
                    else:
                        print(colored(f"SYSTEM: Ingestion failed. {new_concepts}", "red"))

                elif user_input.lower() == "/consolidate":
                    from system_a_cognitive.meta.consolidator import KnowledgeConsolidator
                    consolidator = KnowledgeConsolidator()
                    consolidator.consolidate()
                    self.load_data() # Reload

                elif user_input.lower() == "/diagnose":
                    from system_a_cognitive.meta.diagnostic import SystemDiagnostic
                    diag = SystemDiagnostic()
                    diag.run_diagnostics()

                elif user_input.lower() == "/audit":
                    from system_a_cognitive.meta.auditor import RelationAuditor
                    auditor = RelationAuditor()
                    auditor.audit()

                elif user_input.startswith("/analogy"):
                    # /analogy "concept" [group]
                    parts = user_input.split('"')
                    if len(parts) < 2:
                        print(colored("Usage: /analogy \"Concept Name\" [Optional: Target Group No]", "red"))
                        continue
                    
                    concept_name = parts[1]
                    target_group = None
                    if len(parts) > 2 and parts[2].strip():
                        try:
                            target_group = int(parts[2].strip())
                        except:
                            print(colored("Target Group must be an integer (e.g. 20, 60)", "red"))
                            continue

                    print(colored(f"SYSTEM: Searching for functional equivalents of '{concept_name}'...", "cyan"))
                    
                    # 1. Try Direct Lookup
                    results = self.func_search.find_equivalents(concept_name, target_group)
                    
                    # 2. If not found, try LLM Resolution (The "Smart" Search)
                    if "error" in results and "not found" in results["error"].lower():
                        print(colored(f"  > Direct lookup failed. Asking System B to resolve '{concept_name}'...", "yellow"))
                        
                        # Get list of all known names
                        known_names = list(self.func_search.id_to_name.values())
                        
                        resolution_prompt = f"""
                        Task: Map the user's term to a specific Concept Name from the database.
                        User Term: "{concept_name}"
                        Database: {json.dumps(known_names)}
                        
                        Rules:
                        1. If the term refers to the same thing (synonym), return the Database Name.
                        2. If uncertain, return "None".
                        3. Output ONLY the Name or "None".
                        """
                        resolved_name = self.llm_client.completion(
                            "You are a Concept Resolver. Be strict.", 
                            resolution_prompt
                        ).strip().strip('"')
                        
                        if resolved_name and resolved_name != "None" and resolved_name in known_names:
                            print(colored(f"  > Resolved '{concept_name}' identified as: '{resolved_name}'", "green"))
                            results = self.func_search.find_equivalents(resolved_name, target_group)
                    
                    if "error" in results:
                        print(colored(f"Error: {results['error']}", "red"))
                    else:
                        print(colored(f"\n══ FUNCTIONAL EQUIVALENCE REPORT: {results['source']} ══", "green"))
                        print(colored(f"Roles identified: {', '.join(results['roles_found'])}", "cyan"))
                        
                        if not results['equivalents']:
                            print("No equivalents found in known memory.")
                        else:
                            for role, equivalents in results['equivalents'].items():
                                print(f"\nRole: {role}")
                                for eq in equivalents:
                                    print(f"  • {eq['name']} (ID: {eq['id']['group']},{eq['id']['item']})")
                        print("\n")

                elif user_input.startswith("/subconscious"):
                    cmd = user_input.split(" ")[1] if " " in user_input else ""
                    if hasattr(self, 'subconscious') and self.subconscious.running:
                        if cmd == "off":
                            self.subconscious.stop()
                            self.subconscious = None
                        else:
                            print("Subconscious is ALREADY ONLINE.")
                    else:
                        if cmd == "on":
                            from system_a_cognitive.meta.subconscious import SubconsciousLoop
                            self.subconscious = SubconsciousLoop(interval_seconds=15)
                            self.subconscious.start()
                        else:
                            print("Usage: /subconscious [on|off]")
                        
                else:
                    # START TRACE
                    trace = ReasoningTrace(query=user_input)
                    trace.outcome = Outcome.SUCCESS # Assume success until flagged
                    
                    # 4. Process
                    result = self.process_query(user_input)
                    response_text = result["text"]
                    
                    print(colored("\nWMCS >", "green"))
                    print(f"{response_text}")

                    # STEP 5: EXTERNAL VERIFICATION (The "Smart AI")
                    print(colored("\nStep 5 (External Verifier): Assessing Truth...", "cyan"))
                    verification = verifier.verify(user_input, response_text)
                    
                    # Pretty Print
                    score = verification.get('score', 0)
                    status = verification.get('status', 'UNKNOWN')
                    correction = verification.get('correction', '')
                    
                    print(colored(f"[VERIFICATION REPORT]", "magenta", attrs=['bold']))
                    print(colored(f"  Status: {status} (Score: {score}/10)", "magenta"))
                    print(colored(f"  Critique: {verification.get('missing_context', 'None')}", "magenta"))
                    print(colored(f"  Trusted Correction: {correction[:100]}...", "magenta"))
                    
                    print(colored("\n------------------------------------------------", "white"))
                    print("Options:")
                    print("  /trust  -> Auto-learn from the Verifier's correction")
                    print("  /learn  -> Write your own fact")
                    print("  [Enter] -> Pass/Ignore")
                    
                    feedback = input(colored("Action > ", "yellow")).strip()

                    if feedback.lower() == "/trust":
                         print(colored(f"SYSTEM: trusting the Verifier. Ingesting correction...", "green"))
                         # Feed the correction back into the Ingestor
                         new_concepts = ingestor.ingest_text(correction, source_name="verified_correction")
                         print(colored(f"SYSTEM: Updated Knowledge Base with {len(new_concepts)} concepts.", "green"))
                         self.load_data()
                         
                    elif feedback.lower() == "/learn":
                         # The standard /learn command loop is handled at top of loop, 
                         # but we can prompt here for convenience
                         text = input("Enter fact to learn: ")
                         ingestor.ingest_text(text, source_name="user_manual")
                         self.load_data()

                    elif feedback.lower() == "/consolidate":
                        # Run the cross-linker
                        from system_a_cognitive.meta.consolidator import KnowledgeConsolidator
                        consolidator = KnowledgeConsolidator()
                        consolidator.consolidate()
                        self.load_data() # Reload to see new links

                    elif feedback.lower() in ['n', 'no']:
                        print(colored("SYSTEM: Reflecting on failure...", "cyan"))
                        trace.outcome = Outcome.FAILURE
                        # Analyze why
                        trace.outcome = Outcome.FAILURE
                        # Analyze why
                        lesson = reflector.analyze_trace(trace, feedback)
                        if lesson:
                            meta_store.add_lesson(lesson)
                            print(colored(f"META-LESSON LEARNED: {lesson.content}", "green", attrs=['bold']))
                            print(f"Trigger: {lesson.trigger}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break
            except Exception as e:
                print(colored(f"SYSTEM ERROR: {e}", "red"))

if __name__ == "__main__":
    wmcs = WMCS_Kernel()
    wmcs.load_data()
    
    # Check for CLI args for single-shot mode (testing)
    import sys
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        print(f"\nSingle-Shot Query: {q}")
        resp = wmcs.process_query(q)
        print(colored(f"\nFINAL OUTPUT:\n{resp}", "white", attrs=['bold', 'reverse']))
    else:
        wmcs.interactive_mode()
