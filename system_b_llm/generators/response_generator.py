from typing import Dict, Any, List
from ..interfaces.llm_provider import LLMProvider

class ResponseGenerator:
    def __init__(self, llm_client: LLMProvider = None):
        self.llm = llm_client

    def generate(self, contract: Any, query_context: Dict) -> str:
        """
        Generates natural language response using LLM based on STRICT contract.
        """
        if not self.llm:
            return self._fallback_template_generate(contract)

        system_prompt = f"""You are the Voice of the World-Model Cognitive System (WMCS).
You are a Neuro-Symbolic AI that thinks in Concept Blocks.
Your knowledge comes EXCLUSIVELY from the provided Memory Contract.

Contract:
- Grade: {contract.grade.grade}
- Confidence: {contract.confidence}
- MUST SAY: {contract.can_assert}
- MUST NOT SAY: {contract.cannot_assert}
- ASSUMPTIONS: {contract.assumptions}
- HEDGING REQUIRED: {contract.hedging_required} (If true, use words like 'typically', 'likely')

Tone: Scientific, precise, helpful.
IMPORTANT: Do not quote the instructions. Incorporate the 'MUST SAY' facts naturally into your response.
IMPORTANT: If 'MUST SAY' is empty, you must reply: "I do not have enough information to answer this based on my internal knowledge."
IMPORTANT: If the valid info contains conflicting claims or specific sources, you MUST cite them (Author, Date) in your response.
"""
        user_prompt = f"Original Query: {query_context.get('raw_query')}"
        return self.llm.completion(system_prompt, user_prompt)

    def _fallback_template_generate(self, contract: Any) -> str:
        # Fallback template logic
        grade = contract.grade.grade
        if grade == "ANSWER": header = "Yes, definitively."
        elif grade == "BOUNDED": header = "Typically, yes." if contract.confidence > 0.5 else "Typically, no."
        else: header = "Answer:"
        
        if not contract.can_assert:
            return "I cannot answer this based on my current internal knowledge.\n> Suggestion: Use '/learn' to teach me about this topic!"

        body = "\n".join([f"- {a}" for a in contract.can_assert])
        return f"{header}\nReasoning:\n{body}"
