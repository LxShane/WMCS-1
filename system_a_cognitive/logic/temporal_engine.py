"""
Temporal Engine (WMCS v1.0)
Handles time-based structures: songs, events, processes.
"""
from typing import Dict, List, Optional, Tuple


class TemporalEngine:
    def __init__(self):
        pass
    
    def get_duration(self, temporal_data: Dict) -> Dict:
        """
        Get total duration from temporal structure.
        Returns {value: float, unit: str}
        """
        if "structure_temporal" in temporal_data:
            temp = temporal_data["structure_temporal"]
        else:
            temp = temporal_data
        
        duration = temp.get("duration", {})
        if isinstance(duration, dict):
            return {
                "value": duration.get("value", 0),
                "unit": duration.get("unit", "seconds")
            }
        return {"value": float(duration) if duration else 0, "unit": "seconds"}
    
    def get_sequence(self, temporal_data: Dict) -> List[Dict]:
        """
        Get ordered list of temporal segments.
        Returns [{name, start, end, duration}, ...]
        """
        if "structure_temporal" in temporal_data:
            temp = temporal_data["structure_temporal"]
        else:
            temp = temporal_data
        
        segments = temp.get("segments", [])
        phases = temp.get("phases", [])
        steps = temp.get("steps", [])
        
        # Combine all temporal elements
        all_segments = segments + phases + steps
        
        result = []
        for seg in all_segments:
            if isinstance(seg, dict):
                result.append({
                    "name": seg.get("name", "unnamed"),
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "duration": seg.get("duration", seg.get("end", 0) - seg.get("start", 0)),
                    "description": seg.get("description", "")
                })
            else:
                result.append({
                    "name": str(seg),
                    "start": 0,
                    "end": 0,
                    "duration": 0,
                    "description": ""
                })
        
        # Sort by start time
        result.sort(key=lambda x: x.get("start", 0))
        
        return result
    
    def get_segment_at(self, temporal_data: Dict, timestamp: float) -> Optional[Dict]:
        """
        Get the segment active at a given timestamp.
        """
        segments = self.get_sequence(temporal_data)
        
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", start + seg.get("duration", 0))
            
            if start <= timestamp <= end:
                return seg
        
        return None
    
    def get_timeline(self, temporal_data: Dict) -> str:
        """
        Generate ASCII timeline visualization.
        """
        segments = self.get_sequence(temporal_data)
        if not segments:
            return "No temporal segments found"
        
        lines = ["Timeline:"]
        for i, seg in enumerate(segments):
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            name = seg.get("name", "unnamed")
            lines.append(f"  [{start}] ─── {name} ─── [{end}]")
        
        return "\n".join(lines)
    
    def get_overlapping(self, temporal_data: Dict) -> List[Tuple[Dict, Dict]]:
        """
        Find segments that overlap in time.
        Returns list of (segment1, segment2) tuples.
        """
        segments = self.get_sequence(temporal_data)
        overlaps = []
        
        for i, seg1 in enumerate(segments):
            for seg2 in segments[i+1:]:
                s1_start = seg1.get("start", 0)
                s1_end = seg1.get("end", s1_start + seg1.get("duration", 0))
                s2_start = seg2.get("start", 0)
                s2_end = seg2.get("end", s2_start + seg2.get("duration", 0))
                
                # Check overlap
                if s1_start < s2_end and s2_start < s1_end:
                    overlaps.append((seg1, seg2))
        
        return overlaps
    
    def convert_timestamp(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between time units."""
        # Normalize to seconds first
        to_seconds = {
            "milliseconds": 0.001,
            "seconds": 1,
            "minutes": 60,
            "hours": 3600,
            "days": 86400,
            "years": 31536000
        }
        
        seconds = value * to_seconds.get(from_unit, 1)
        return seconds / to_seconds.get(to_unit, 1)


# Singleton
_engine = None

def get_temporal_engine() -> TemporalEngine:
    global _engine
    if _engine is None:
        _engine = TemporalEngine()
    return _engine
