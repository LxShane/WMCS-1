"""
Hierarchy Engine (WMCS v1.0)
Handles hierarchical structures: organizations, power flow, role trees.
"""
from typing import Dict, List, Optional


class HierarchyEngine:
    def __init__(self):
        pass
    
    def get_root(self, hierarchy_data: Dict) -> Optional[Dict]:
        """
        Get the root/top of the hierarchy (e.g., CEO, President).
        """
        if "structure_hierarchical" in hierarchy_data:
            hier = hierarchy_data["structure_hierarchical"]
        else:
            hier = hierarchy_data
        
        return hier.get("root", hier.get("top", hier.get("leader", None)))
    
    def get_children(self, hierarchy_data: Dict, node_name: str) -> List[Dict]:
        """
        Get direct children/reports of a node.
        """
        if "structure_hierarchical" in hierarchy_data:
            hier = hierarchy_data["structure_hierarchical"]
        else:
            hier = hierarchy_data
        
        nodes = hier.get("nodes", [])
        
        for node in nodes:
            if isinstance(node, dict):
                if node.get("name", "").lower() == node_name.lower():
                    return node.get("children", node.get("reports", []))
        
        return []
    
    def get_parent(self, hierarchy_data: Dict, node_name: str) -> Optional[str]:
        """
        Get parent/manager of a node.
        """
        if "structure_hierarchical" in hierarchy_data:
            hier = hierarchy_data["structure_hierarchical"]
        else:
            hier = hierarchy_data
        
        nodes = hier.get("nodes", [])
        
        for node in nodes:
            if isinstance(node, dict):
                children = node.get("children", node.get("reports", []))
                for child in children:
                    child_name = child.get("name", "") if isinstance(child, dict) else str(child)
                    if child_name.lower() == node_name.lower():
                        return node.get("name")
        
        return None
    
    def get_power_chain(self, hierarchy_data: Dict, node_name: str) -> List[str]:
        """
        Get chain from node up to root (who reports to whom).
        """
        chain = [node_name]
        current = node_name
        
        for _ in range(20):  # Max depth
            parent = self.get_parent(hierarchy_data, current)
            if parent:
                chain.append(parent)
                current = parent
            else:
                break
        
        return chain
    
    def get_depth(self, hierarchy_data: Dict, node_name: str) -> int:
        """
        Get depth of node from root (root = 0).
        """
        chain = self.get_power_chain(hierarchy_data, node_name)
        return len(chain) - 1
    
    def get_all_descendants(self, hierarchy_data: Dict, node_name: str) -> List[str]:
        """
        Get all nodes below a given node (recursive).
        """
        descendants = []
        to_process = [node_name]
        
        while to_process:
            current = to_process.pop(0)
            children = self.get_children(hierarchy_data, current)
            
            for child in children:
                child_name = child.get("name", "") if isinstance(child, dict) else str(child)
                if child_name:
                    descendants.append(child_name)
                    to_process.append(child_name)
        
        return descendants
    
    def get_decision_path(self, hierarchy_data: Dict, decision_source: str) -> List[Dict]:
        """
        How decisions flow from source down.
        Returns [{node: str, action: str}, ...]
        """
        path = [{"node": decision_source, "action": "originates"}]
        
        descendants = self.get_children(hierarchy_data, decision_source)
        for desc in descendants:
            desc_name = desc.get("name", "") if isinstance(desc, dict) else str(desc)
            if desc_name:
                path.append({
                    "node": desc_name,
                    "action": "receives from " + decision_source
                })
        
        return path
    
    def flatten(self, hierarchy_data: Dict) -> List[Dict]:
        """
        Flatten hierarchy to list of {name, parent, depth}.
        """
        result = []
        
        root = self.get_root(hierarchy_data)
        if root:
            root_name = root.get("name", "") if isinstance(root, dict) else str(root)
            result.append({"name": root_name, "parent": None, "depth": 0})
            
            # BFS
            to_process = [(root_name, 0)]
            while to_process:
                current, depth = to_process.pop(0)
                children = self.get_children(hierarchy_data, current)
                
                for child in children:
                    child_name = child.get("name", "") if isinstance(child, dict) else str(child)
                    if child_name:
                        result.append({
                            "name": child_name,
                            "parent": current,
                            "depth": depth + 1
                        })
                        to_process.append((child_name, depth + 1))
        
        return result


# Singleton
_engine = None

def get_hierarchy_engine() -> HierarchyEngine:
    global _engine
    if _engine is None:
        _engine = HierarchyEngine()
    return _engine
