"""
Graph Navigation Engine (WMCS v1.0)
Multi-hop traversal over concept relationships.
Finds paths, implications, and dependencies.
"""
import json
import os
from collections import deque
from typing import Dict, List, Optional, Set, Tuple


class GraphEngine:
    def __init__(self, concepts_dir: str = "data/concepts"):
        self.concepts_dir = concepts_dir
        self._concept_cache = {}
        self._relation_index = {}  # {source_id: [(relation, target_id), ...]}
        self._reverse_index = {}   # {target_id: [(relation, source_id), ...]}
        self._build_index()
    
    def _build_index(self):
        """Build relationship index from all concepts."""
        if not os.path.exists(self.concepts_dir):
            return
        
        for fname in os.listdir(self.concepts_dir):
            if not fname.endswith(".json"):
                continue
            
            path = os.path.join(self.concepts_dir, fname)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    concept = json.load(f)
                
                name = concept.get("CORE", {}).get("name", fname.replace(".json", ""))
                self._concept_cache[name.lower()] = concept
                
                # Index CONNECTIONS
                if "CONNECTIONS" in concept:
                    conns = concept["CONNECTIONS"]
                    
                    # Relational links
                    for rel in conns.get("relational", []):
                        if isinstance(rel, dict):
                            relation = rel.get("relation", "related_to")
                            target = rel.get("target", "")
                        else:
                            relation = "related_to"
                            target = str(rel)
                        
                        if target:
                            self._add_edge(name, relation, target)
                    
                    # Part-of links
                    for part in conns.get("part_of", []):
                        self._add_edge(name, "part_of", part)
                    
                    # Similar-to links
                    for sim in conns.get("similar_to", []):
                        self._add_edge(name, "similar_to", sim)
                    
                    # Contrasts-with links
                    for con in conns.get("contrasts_with", []):
                        self._add_edge(name, "contrasts_with", con)
                
                # Index CAUSATION
                if "CAUSATION" in concept:
                    caus = concept["CAUSATION"]
                    
                    for req in caus.get("requires", []):
                        self._add_edge(name, "requires", req)
                    
                    for prod in caus.get("produces", []):
                        self._add_edge(name, "produces", prod)
                    
                    for cause in caus.get("caused_by", []):
                        self._add_edge(name, "caused_by", cause)
                
            except Exception as e:
                pass  # Skip invalid files
    
    def _add_edge(self, source: str, relation: str, target: str):
        """Add edge to indices."""
        source_key = source.lower()
        target_key = target.lower() if isinstance(target, str) else str(target).lower()
        
        if source_key not in self._relation_index:
            self._relation_index[source_key] = []
        self._relation_index[source_key].append((relation, target_key))
        
        if target_key not in self._reverse_index:
            self._reverse_index[target_key] = []
        self._reverse_index[target_key].append((relation, source_key))
    
    def get_concept(self, name: str) -> Optional[Dict]:
        """Load concept by name."""
        return self._concept_cache.get(name.lower())
    
    def walk(self, start: str, relation_type: str = None, depth: int = 2, direction: str = "forward") -> List[Dict]:
        """
        BFS walk from start concept following relations.
        direction: "forward" = follow outgoing, "backward" = follow incoming
        Returns list of {name, relation, depth}
        """
        start_key = start.lower()
        visited = set([start_key])
        results = []
        queue = deque([(start_key, 0)])
        
        while queue:
            current, current_depth = queue.popleft()
            
            if current_depth >= depth:
                continue
            
            # Get edges
            if direction == "forward":
                edges = self._relation_index.get(current, [])
            else:
                edges = self._reverse_index.get(current, [])
            
            for relation, target in edges:
                if relation_type and relation != relation_type:
                    continue
                
                if target not in visited:
                    visited.add(target)
                    results.append({
                        "name": target,
                        "relation": relation,
                        "depth": current_depth + 1,
                        "from": current
                    })
                    queue.append((target, current_depth + 1))
        
        return results
    
    def find_path(self, from_name: str, to_name: str, max_depth: int = 5) -> Optional[List[Dict]]:
        """
        Find shortest path between two concepts.
        Returns list of {name, relation} or None if no path.
        """
        start_key = from_name.lower()
        end_key = to_name.lower()
        
        if start_key == end_key:
            return [{"name": start_key, "relation": "self"}]
        
        visited = {start_key: None}  # {node: (parent, relation)}
        queue = deque([start_key])
        
        while queue:
            current = queue.popleft()
            
            # Check depth
            depth = 0
            node = current
            while visited.get(node):
                depth += 1
                node = visited[node][0]
            if depth >= max_depth:
                continue
            
            # Get neighbors
            for relation, target in self._relation_index.get(current, []):
                if target not in visited:
                    visited[target] = (current, relation)
                    
                    if target == end_key:
                        # Reconstruct path
                        path = []
                        node = target
                        while node:
                            if visited[node]:
                                parent, rel = visited[node]
                                path.append({"name": node, "relation": rel})
                                node = parent
                            else:
                                path.append({"name": node, "relation": "start"})
                                break
                        return list(reversed(path))
                    
                    queue.append(target)
        
        return None
    
    def get_implications(self, concept_name: str, depth: int = 3) -> List[str]:
        """What does this concept causally lead to?"""
        results = self.walk(concept_name, "produces", depth)
        return [r["name"] for r in results]
    
    def get_dependencies(self, concept_name: str, depth: int = 3) -> List[str]:
        """What does this concept require?"""
        results = self.walk(concept_name, "requires", depth)
        return [r["name"] for r in results]
    
    def get_related(self, concept_name: str, depth: int = 2) -> Dict[str, List[str]]:
        """Get all related concepts grouped by relation type."""
        results = self.walk(concept_name, None, depth)
        
        grouped = {}
        for r in results:
            rel = r["relation"]
            if rel not in grouped:
                grouped[rel] = []
            grouped[rel].append(r["name"])
        
        return grouped
    
    def get_stats(self) -> Dict:
        """Return index statistics."""
        return {
            "concepts": len(self._concept_cache),
            "forward_edges": sum(len(v) for v in self._relation_index.values()),
            "reverse_edges": sum(len(v) for v in self._reverse_index.values()),
            "relation_types": list(set(
                rel for edges in self._relation_index.values() 
                for rel, _ in edges
            ))
        }


# Singleton
_engine = None

def get_graph_engine(concepts_dir: str = "data/concepts") -> GraphEngine:
    global _engine
    if _engine is None:
        _engine = GraphEngine(concepts_dir)
    return _engine


if __name__ == "__main__":
    # Quick test
    engine = GraphEngine()
    print("Graph Stats:")
    print(json.dumps(engine.get_stats(), indent=2))
    
    print("\nWalk from 'earth':")
    results = engine.walk("earth", depth=2)
    for r in results[:5]:
        print(f"  {r['from']} --{r['relation']}--> {r['name']}")
