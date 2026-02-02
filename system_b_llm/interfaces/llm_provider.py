from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    def completion(self, system_prompt: str, user_prompt: str) -> str:
        """Returns raw text response"""
        pass

    @abstractmethod
    def json_completion(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Returns parsed JSON response"""
        pass
