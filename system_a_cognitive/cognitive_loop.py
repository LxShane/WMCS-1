"""
Cognitive Loop (WMCS v1.0)
The full retrieve→reason→detect_gap→retrieve_more→synthesize loop.
This is the core cognitive cycle that ties all engines together.
"""
import json
from typing import Dict, List, Optional
from termcolor import colored

# Import all engines
from system_a_cognitive.logic.graph_engine import get_graph_engine
from system_a_cognitive.logic.type_engine import get_type_engine
from system_a_cognitive.logic.analogy_engine import get_analogy_engine
from system_a_cognitive.logic.inference_engine import get_inference_engine
from system_a_cognitive.logic.spatial import SpatialEngine
from system_a_cognitive.logic.composition import CompositionEngine
from system_a_cognitive.logic.grounding import GroundingEngine
from system_a_cognitive.epistemic_gate import get_epistemic_gate


class CognitiveLoop:
    """
    Implements the full cognitive cycle from Spec Section 14.
    
    The loop:
    1. RETRIEVE: Gather all relevant concepts
    2. REASON: Use engines to derive insights
    3. DETECT_GAP: Identify missing information
    4. RESEARCH: If critical gaps, trigger deep research
    5. RETRIEVE_MORE: Fill gaps with additional data
    6. SYNTHESIZE: Generate final answer
    """
    
    def __init__(self, llm_client=None, max_iterations: int = 3, auto_research: bool = True):
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.auto_research = auto_research  # Enable/disable auto-research
        
        # Initialize engines
        self.graph = get_graph_engine()
        self.type_engine = get_type_engine()
        self.analogy = get_analogy_engine()
        self.inference = get_inference_engine()
        self.spatial = SpatialEngine()
        self.composition = CompositionEngine()
        self.grounding = GroundingEngine()
        self.epistemic = get_epistemic_gate()
        
        # Logging
        self.trace = []
    
    def process(self, query: str) -> Dict:
        """
        Main entry point. Process a query through the full cognitive loop.
        Returns {
            answer: str,
            confidence: float,
            trace: [step descriptions],
            concepts_used: [names],
            engines_used: [names]
        }
        """
        self.trace = []
        concepts_used = set()
        engines_used = set()
        context = {"concepts": {}, "derived_facts": [], "gaps": []}
        
        self._log("Starting cognitive loop", query)
        
        # Parse query to understand intent
        query_type = self._classify_query(query)
        self._log("Query classification", query_type)
        
        for iteration in range(self.max_iterations):
            self._log(f"Iteration {iteration + 1}", f"max={self.max_iterations}")
            
            # 1. RETRIEVE
            retrieved = self._retrieve(query, context)
            for name in retrieved:
                concepts_used.add(name)
            context["concepts"].update({n: self.graph.get_concept(n) for n in retrieved if self.graph.get_concept(n)})
            self._log("Retrieved concepts", list(retrieved)[:5])
            
            # 2. REASON with appropriate engines
            reasoning_result = self._reason(query, query_type, context)
            context["derived_facts"].extend(reasoning_result.get("facts", []))
            engines_used.update(reasoning_result.get("engines", []))
            self._log("Reasoning complete", reasoning_result.get("summary", ""))
            
            # 3. DETECT GAP
            gaps = self._detect_gaps(query, context)
            context["gaps"] = gaps
            self._log("Gaps detected", gaps[:3] if gaps else "None")
            
            if not gaps:
                # No gaps, we can synthesize
                break
            
            # 3.5. AUTO-RESEARCH if no concepts found
            if "No relevant concepts found" in gaps and self.auto_research:
                self._log("Triggering auto-research", query)
                engines_used.add("DeepResearchAgent")
                new_concepts = self._trigger_research(query)
                if new_concepts:
                    # Reload graph engine to pick up new data
                    self._reload_engines()
                    context["research_triggered"] = True
                    continue  # Retry with new data
            
            # 4. RETRIEVE MORE
            for gap in gaps[:3]:  # Limit gap filling per iteration
                additional = self._retrieve_for_gap(gap, context)
                for name in additional:
                    concepts_used.add(name)
                context["concepts"].update({n: self.graph.get_concept(n) for n in additional if self.graph.get_concept(n)})
        
        # 5. SYNTHESIZE
        answer = self._synthesize(query, query_type, context)
        confidence = self._calculate_confidence(context)
        
        # Apply Epistemic Gate
        trust_score = self.epistemic.get_trust_score(answer)
        if trust_score < 0.5:
            answer, _ = self.epistemic.enforce(answer)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "trust_score": trust_score,
            "trace": self.trace,
            "concepts_used": list(concepts_used),
            "engines_used": list(engines_used),
            "iterations": iteration + 1
        }
    
    def _log(self, step: str, detail: any):
        """Add to trace log."""
        self.trace.append({
            "step": step,
            "detail": str(detail)[:200]
        })
    
    def _classify_query(self, query: str) -> str:
        """Classify query to determine which engines to use."""
        query_lower = query.lower()
        
        if "fit" in query_lower or "inside" in query_lower or "size" in query_lower:
            return "spatial"
        if "made of" in query_lower or "contain" in query_lower or "component" in query_lower:
            return "composition"
        if "like" in query_lower and ("how" in query_lower or "similar" in query_lower):
            return "analogy"
        if "what if" in query_lower or "would happen" in query_lower:
            return "counterfactual"
        if "cause" in query_lower or "why" in query_lower or "because" in query_lower:
            return "causal"
        if "path" in query_lower or "connect" in query_lower or "related" in query_lower:
            return "graph"
        
        return "general"
    
    def _retrieve(self, query: str, context: Dict) -> List[str]:
        """Retrieve relevant concepts for the query."""
        retrieved = set()
        
        # Extract concept names from query
        for name in self.graph._concept_cache.keys():
            if name in query.lower():
                retrieved.add(name)
        
        # Also get related concepts
        for name in list(retrieved):
            related = self.graph.walk(name, depth=1)
            for r in related[:5]:
                retrieved.add(r["name"])
        
        return list(retrieved)
    
    def _reason(self, query: str, query_type: str, context: Dict) -> Dict:
        """Apply appropriate engines based on query type."""
        result = {"facts": [], "engines": [], "summary": ""}
        
        concepts = context.get("concepts", {})
        if not concepts:
            return result
        
        concept_list = list(concepts.values())
        
        if query_type == "spatial":
            result["engines"].append("SpatialEngine")
            for c in concept_list[:2]:
                if "ARRANGEMENT" in c:
                    vol = self.spatial.calculate_volume_cm3(c["ARRANGEMENT"].get("structure_spatial", {}))
                    result["facts"].append(f"{c['CORE']['name']} volume: {vol:.2e} cm³")
            result["summary"] = "Calculated spatial properties"
        
        elif query_type == "composition":
            result["engines"].append("CompositionEngine")
            for c in concept_list[:2]:
                if "SUBSTANCE" in c:
                    parts = self.composition.get_all_components(c["SUBSTANCE"].get("composition", {}))
                    result["facts"].append(f"{c['CORE']['name']} contains: {parts[:5]}")
            result["summary"] = "Analyzed composition"
        
        elif query_type == "analogy":
            result["engines"].append("AnalogyEngine")
            if len(concept_list) >= 2:
                explanation = self.analogy.explain_analogy(
                    concept_list[0]["CORE"]["name"],
                    concept_list[1]["CORE"]["name"]
                )
                result["facts"].append(explanation)
            result["summary"] = "Generated analogy"
        
        elif query_type == "counterfactual":
            result["engines"].append("InferenceEngine")
            for c in concept_list[:1]:
                name = c["CORE"]["name"]
                cf = self.inference.counterfactual(name, query)
                result["facts"].extend(cf.get("effects", [])[:5])
            result["summary"] = "Traced counterfactual effects"
        
        elif query_type == "causal":
            result["engines"].append("InferenceEngine")
            for c in concept_list[:1]:
                name = c["CORE"]["name"]
                deps = self.inference.backward_chain(name)
                result["facts"].append(f"{name} requires: {deps.get('required', [])[:3]}")
            result["summary"] = "Analyzed causation"
        
        elif query_type == "graph":
            result["engines"].append("GraphEngine")
            for c in concept_list[:2]:
                name = c["CORE"]["name"]
                related = self.graph.get_related(name, depth=1)
                result["facts"].append(f"{name} relations: {dict(list(related.items())[:3])}")
            result["summary"] = "Explored graph"
        
        else:
            result["engines"].append("General")
            result["summary"] = "General reasoning"
        
        return result
    
    def _detect_gaps(self, query: str, context: Dict) -> List[str]:
        """Identify what information is still missing."""
        gaps = []
        
        # If we have no concepts, that's a gap
        if not context.get("concepts"):
            gaps.append("No relevant concepts found")
            return gaps
        
        # Check for missing required fields
        for name, concept in context["concepts"].items():
            validation = self.type_engine.validate_concept(concept)
            for warning in validation.get("warnings", []):
                gaps.append(f"{name}: {warning}")
        
        return gaps[:5]  # Limit gaps
    
    def _retrieve_for_gap(self, gap: str, context: Dict) -> List[str]:
        """Retrieve additional concepts to fill a gap."""
        # Extract concept name from gap
        for name in self.graph._concept_cache.keys():
            if name in gap.lower():
                return [name]
        
        return []
    
    def _trigger_research(self, query: str) -> List[str]:
        """
        Trigger deep research to acquire new knowledge.
        Returns list of newly created concept names.
        """
        self._log("Deep Research", "Starting autonomous research...")
        
        try:
            from system_a_cognitive.meta.deep_researcher import DeepResearchAgent
            agent = DeepResearchAgent()
            new_concepts = agent.conduct_deep_research(query, max_depth=1)
            self._log("Research complete", f"Learned {len(new_concepts)} new concepts")
            return new_concepts
        except ImportError:
            self._log("Research unavailable", "DeepResearchAgent not found")
            return []
        except Exception as e:
            self._log("Research failed", str(e))
            return []
    
    def _reload_engines(self):
        """Reload engines to pick up newly researched data."""
        global _loop
        from system_a_cognitive.logic.graph_engine import GraphEngine
        self.graph = GraphEngine()  # Fresh instance
        self.epistemic = get_epistemic_gate()  # Refresh claims index
    
    def _synthesize(self, query: str, query_type: str, context: Dict) -> str:
        """Generate final answer from context."""
        lines = []
        
        # Summarize what we found
        concepts = context.get("concepts", {})
        facts = context.get("derived_facts", [])
        
        if concepts:
            lines.append(f"**Based on {len(concepts)} concepts:**")
            for name in list(concepts.keys())[:5]:
                c = concepts[name]
                defn = c.get("CORE", {}).get("definition", "")[:100]
                lines.append(f"- **{name.title()}**: {defn}")
        
        if facts:
            lines.append(f"\n**Derived facts:**")
            for fact in facts[:5]:
                lines.append(f"- {fact}")
        
        if not concepts and not facts:
            lines.append("I don't have enough information to answer this query.")
        
        return "\n".join(lines)
    
    def _calculate_confidence(self, context: Dict) -> float:
        """Calculate overall confidence in the answer."""
        concepts = context.get("concepts", {})
        
        if not concepts:
            return 0.1
        
        # Average grounding confidence
        confidences = []
        for c in concepts.values():
            grounding = c.get("GROUNDING", {})
            conf = grounding.get("confidence", 0.5)
            confidences.append(conf)
        
        if confidences:
            return sum(confidences) / len(confidences)
        
        return 0.5


# Singleton
_loop = None

def get_cognitive_loop(llm_client=None) -> CognitiveLoop:
    global _loop
    if _loop is None:
        _loop = CognitiveLoop(llm_client)
    return _loop


if __name__ == "__main__":
    loop = CognitiveLoop()
    
    print(colored("=== WMCS Cognitive Loop Demo ===", "magenta", attrs=['bold']))
    
    queries = [
        "How is Earth like Mars?",
        "What is Earth made of?",
        "What would happen if the Sun disappeared?"
    ]
    
    for q in queries:
        print(colored(f"\nQuery: {q}", "cyan"))
        result = loop.process(q)
        print(f"Confidence: {result['confidence']*100:.0f}%")
        print(f"Engines: {result['engines_used']}")
        print(result["answer"][:300])
