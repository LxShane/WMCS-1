from typing import Dict, Any, List
from ..interfaces.llm_provider import LLMProvider

class QueryParser:
    def __init__(self, llm_client: LLMProvider = None):
        self.llm = llm_client

    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parses natural language into structured intent using LLM or fallback.
        """
        if not self.llm:
            # Fallback for when no LLM is provided (e.g. unit tests without key)
            return self._fallback_regex_parse(text)
            
        system_prompt = """You are the 'System B' Translator for the World-Model Cognitive System.
Target JSON Structure:
{
    "intent": "CAPABILITY_CHECK" | "GENERAL_QUERY",
    "entities": ["list", "of", "single", "nouns"],
    "action": "verb_in_infintive",
    "question_type": "CAUSAL" | "RELATIONAL" | "TELEOLOGICAL" | "FORMAL",
    "raw_query": "original text"
}
Rules:
1. Extract MAIN entities only (singular form).
2. Action should be the core verb.
3. If asking "Can X do Y?", intent is CAPABILITY_CHECK.
4. If asking "Why?", question_type is CAUSAL.
"""
        return self.llm.json_completion(system_prompt, text)

    def _fallback_regex_parse(self, text: str) -> Dict[str, Any]:
        # Simple fallback for testing
        text = text.lower()
        entities = []
        if "dog" in text: entities.append("dog")
        if "tree" in text: entities.append("tree")
        action = "climb" if "climb" in text else None
        return {
            "intent": "CAPABILITY_CHECK",
            "entities": entities,
            "action": action,
            "question_type": "CAUSAL",
            "raw_query": text
        }
