import json
import os

class IdentityManager:
    def __init__(self, registry_path="data/registry.json"):
        self.registry_path = registry_path
        self.registry = {} # name -> {"group": G, "item": I}
        self.next_ids = {} # group_int -> next_item_int
        self.load_registry()

    def load_registry(self):
        """Loads the registry from disk or initializes it."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    self.registry = json.load(f)
            except Exception as e:
                print(f"[IdentityManager] Error loading registry: {e}")
                self.registry = {}
        
        # Calculate next available IDs based on loaded data
        self._recalc_next_ids()

    def _recalc_next_ids(self):
        """Scans registry to find the highest item ID for each group."""
        self.next_ids = {}
        for name, id_data in self.registry.items():
            grp = id_data.get("group")
            itm = id_data.get("item")
            if grp is not None and itm is not None:
                current_max = self.next_ids.get(grp, 0)
                if itm >= current_max:
                    self.next_ids[grp] = itm + 1
        
        # Ensure we have defaults for standard groups if empty
        # 20-39 Physical, 40-49 Math, 50-59 Abstract, 60-69 Social
        ranges = list(range(20, 70))
        for r in ranges:
            if r not in self.next_ids:
                self.next_ids[r] = 1

    def get_id(self, name):
        """Returns existing ID dict or None."""
        return self.registry.get(name.lower())

    def mint_id(self, name, group_id):
        """
        Creates a new ID for the name in the specified group.
        If name already exists, returns existing ID.
        """
        name_key = name.lower()
        if name_key in self.registry:
            return self.registry[name_key]

        # Get next item ID
        group_id = int(group_id)
        next_item = self.next_ids.get(group_id, 1)
        
        new_id = {"group": group_id, "item": next_item}
        self.registry[name_key] = new_id
        
        # Update state
        self.next_ids[group_id] = next_item + 1
        self._save_registry()
        
        return new_id

    def _save_registry(self):
        try:
            with open(self.registry_path, 'w') as f:
                json.dump(self.registry, f, indent=4)
        except Exception as e:
            print(f"[IdentityManager] Error saving registry: {e}")
