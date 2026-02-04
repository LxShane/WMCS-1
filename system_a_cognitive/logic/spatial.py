"""
Spatial Engine (v1.0)
Handles 3D spatial reasoning, coordinate transformations, and fit calculations.
"""
import math
from typing import Dict, List, Optional, Tuple

class SpatialEngine:
    def __init__(self):
        pass

    def get_dimensions(self, spatial_data: Dict) -> Tuple[float, float, float]:
        """Returns (width, height, depth) from spatial data."""
        # Check overall size first
        if "overall" in spatial_data and "size" in spatial_data["overall"]:
            s = spatial_data["overall"]["size"]
            shape = spatial_data["overall"].get("shape", "").lower()
            
            # Case 1: Spherical / Single Value (assume diameter if "value")
            if "value" in s:
                val = self._extract_val(s["value"])
                # If shape implies sphere, it's diameter. W=H=D=val
                return val, val, val
                
            # Case 2: Explicit Dimensions
            w = self._extract_val(s.get("width", 0))
            h = self._extract_val(s.get("height", 0))
            d = self._extract_val(s.get("depth", 0)) # or length
            
            # If depth missing, check length
            if d == 0: d = self._extract_val(s.get("length", 0))
            if w == 0 and "radius" in s:
                 r = self._extract_val(s["radius"])
                 return r*2, r*2, r*2

            return w, h, d
            
        # Fallback: Calculate bounding box from parts?
        return 0, 0, 0

    def _extract_val(self, val_obj):
        if isinstance(val_obj, dict):
            return float(val_obj.get("value", 0))
        try:
            return float(val_obj)
        except:
            return 0

    def calculate_volume_cm3(self, spatial_data: Dict) -> float:
        """Calculates volume in cubic centimeters."""
        # Simple box approximation for now
        w, h, d = self.get_dimensions(spatial_data)
        
        # Refine for spheres if shape known? 
        # For now, box volume is acceptable upper bound, 
        # or we check shape.
        shape = spatial_data.get("overall", {}).get("shape", "").lower()
        if "sphere" in shape or "spheroid" in shape:
             r = w / 2.0
             return (4/3) * math.pi * (r**3)
             
        return w * h * d

    def check_fit(self, object_spatial: Dict, container_spatial: Dict) -> Dict:
        """
        Calculates if object fits in container.
        Returns: { "fits": bool, "margin": float, "reason": str }
        """
        o_w, o_h, o_d = self.get_dimensions(object_spatial)
        c_w, c_h, c_d = self.get_dimensions(container_spatial)
        
        # Sort dimensions to find best fit (rotation allowed)
        obj_dims = sorted([o_w, o_h, o_d])
        cont_dims = sorted([c_w, c_h, c_d])
        
        # Check for zero dims (invalid data)
        if o_w == 0 or c_w == 0:
             return {"fits": False, "margin": 0, "reason": "Invalid dimensions (0)"}

        fits = all(o <= c for o, c in zip(obj_dims, cont_dims))
        
        if fits:
            # simple margin approximation
            margin = (c_w*c_h*c_d) - (o_w*o_h*o_d)
            return {"fits": True, "margin": margin, "reason": "Object dimensions are smaller than container"}
        else:
            return {"fits": False, "margin": -1, "reason": f"Object {obj_dims} exceeds Container {cont_dims}"}

    def get_part_position(self, spatial_data: Dict, part_name: str) -> Optional[Dict]:
        """Returns absolute position {x,y,z} of a named part relative to center."""
        parts = spatial_data.get("structure_spatial", {}).get("parts", []) # Fixed key: was 'relative_parts', seed gen uses 'parts'
        
        # Direct lookup
        for p in parts:
            if p.get("name") == part_name:
                return {
                    "x": self._extract_val(p.get("position", {}).get("x", 0)), # Handle nested Position object or direct x
                    "y": self._extract_val(p.get("position", {}).get("y", 0)),
                    "z": self._extract_val(p.get("position", {}).get("z", 0))
                }
            # Also check flat keys if seed gen output flat x,y,z
            if p.get("name") == part_name and "x" in p:
                 return {
                    "x": self._extract_val(p.get("x", 0)),
                    "y": self._extract_val(p.get("y", 0)),
                    "z": self._extract_val(p.get("z", 0))
                }
        return None

    def distance_between_parts(self, spatial_data: Dict, part_a: str, part_b: str) -> float:
        """Calculates Euclidean distance between two named parts."""
        pos_a = self.get_part_position(spatial_data, part_a)
        pos_b = self.get_part_position(spatial_data, part_b)
        
        if not pos_a or not pos_b:
            return -1.0
            
        return math.sqrt(
            (pos_a["x"] - pos_b["x"])**2 +
            (pos_a["y"] - pos_b["y"])**2 +
            (pos_a["z"] - pos_b["z"])**2
        )
