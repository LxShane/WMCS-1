import time
from collections import deque
import threading

class TelemetryBuffer:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TelemetryBuffer, cls).__new__(cls)
                    cls._instance.logs = deque(maxlen=1000) # Keep last 1000 lines
        return cls._instance

    def log(self, message: str, level: str = "INFO", color: str = "white"):
        """
        Add a log entry. 
        Level: INFO, WARN, ERROR, DEBUG, TRACE
        Color: hex or css name, can be used by frontend
        """
        entry = {
            "timestamp": time.time(),
            "time_str": time.strftime("%H:%M:%S"),
            "message": message,
            "level": level,
            "color": color
        }
        self.logs.append(entry)

    def get_logs(self, since: float = 0):
        """Return logs newer than timestamp 'since'."""
        return [l for l in self.logs if l["timestamp"] > since]

# Global Instance
telemetry = TelemetryBuffer()
