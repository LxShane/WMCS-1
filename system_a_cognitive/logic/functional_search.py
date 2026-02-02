import json
import os
from termcolor import colored

class FunctionalSearcher:
    def __init__(self, concepts_dir="data/concepts"):
        self.concepts_dir = concepts_dir
        self.graph = {} # id_str -> concept_data
        self.role_index = {} # role_name -> [concept_ids]
        self.id_to_name = {} # id_str -> name
        self.autoload()

    def autoload(self):
        """Loads all concept blocks and builds the functional index."""
        self.graph = {}
        self.role_index = {}
        
        if not os.path.exists(self.concepts_dir):
            return

        for filename in os.listdir(self.concepts_dir):
            if not filename.endswith(".json"): continue
            
            try:
                path = os.path.join(self.concepts_dir, filename)
                with open(path, 'r') as f:
                    data = json.load(f)
                    
                # Store by ID string "Group,Item"
                if "id" in data:
                    grp = data["id"].get("group")
                    itm = data["id"].get("item")
                    id_str = f"{grp},{itm}"
                    
                    self.graph[id_str] = data
                    self.id_to_name[id_str] = data.get("name", "Unknown")
                    
                    # Index Functional Roles
                    # Look in facets -> FUNCTION -> roles
                    facets = data.get("facets", {})
                    # Handle both dict and list format of facets (legacy vs new)
                    # We heavily prefer dict format now
                    if isinstance(facets, dict):
                        func_facet = facets.get("FUNCTION", {})
                        roles = func_facet.get("roles", [])
                        for role in roles:
                            self._add_to_index(role, id_str)
                            
                        # Also check EQUIVALENCE -> fills_role
                        equiv_facet = facets.get("EQUIVALENCE", {})
                        filled = equiv_facet.get("fills_role", [])
                        for role in filled:
                            self._add_to_index(role, id_str)

            except Exception as e:
                print(f"[FuncSearch] Error loading {filename}: {e}")
        
        print(f"[FuncSearch] Indexed {len(self.graph)} concepts and {len(self.role_index)} functional roles.")

    def _add_to_index(self, role, id_str):
        role = role.upper()
        if role not in self.role_index:
            self.role_index[role] = set()
        self.role_index[role].add(id_str)

    def find_by_role(self, role_name):
        """Returns all concepts that fill a specific role."""
        role_name = role_name.upper()
        ids = self.role_index.get(role_name, [])
        return [self.graph[i] for i in ids]

    def find_equivalents(self, source_name_or_id, target_group=None):
        """
        Finds functional equivalents for a concept.
        
        Args:
            source_name_or_id: The name or "G,I" string of the source concept.
            target_group: (Optional) The specific Group ID to look in (e.g. 60 for Human/Social).
                          If None, looks in ALL groups.
        """
        source_id = self._resolve_id(source_name_or_id)
        if not source_id:
            return {"error": f"Concept '{source_name_or_id}' not found."}

        source_data = self.graph[source_id]
        results = {}

        # 1. Identify Roles of Source
        roles = set()
        facets = source_data.get("facets", {})
        if isinstance(facets, dict):
             roles.update(facets.get("FUNCTION", {}).get("roles", []))
             roles.update(facets.get("EQUIVALENCE", {}).get("fills_role", []))
        
        if not roles:
            return {"error": f"Concept '{source_data['name']}' has no defined functional roles."}

        # 2. Find siblings for each role
        for role in roles:
            siblings = self.find_by_role(role)
            for sib in siblings:
                sib_id_str = f"{sib['id']['group']},{sib['id']['item']}"
                
                # Skip self
                if sib_id_str == source_id: continue
                
                # Filter by Target Group if specified
                sib_group = sib['id']['group']
                if target_group is not None:
                    # Allow fuzzy match (e.g. 20s, 60s) or exact match
                    # User might pass "23" or just "20" (for physical). 
                    # For strictness, let's assume exact integer or None.
                    try:
                        tgt = int(target_group)
                        if sib_group != tgt: continue
                    except:
                        pass # Ignore filter if invalid

                # Add to results
                if role not in results: results[role] = []
                results[role].append({
                    "name": sib["name"],
                    "id": sib["id"],
                    "reason": f"Both fill role {role}"
                })

        return {
            "source": source_data["name"],
            "roles_found": list(roles),
            "equivalents": results
        }

    def _resolve_id(self, query):
        # 1. Check if it's already an ID string "21,61"
        if query in self.graph:
            return query
            
        # 2. Search by name (case-insensitive)
        q_lower = query.lower()
        for id_str, data in self.graph.items():
            if data.get("name", "").lower() == q_lower:
                return id_str
            # Check aliases
            for alias in data.get("aliases", []):
                if alias.lower() == q_lower:
                    return id_str
        return None
