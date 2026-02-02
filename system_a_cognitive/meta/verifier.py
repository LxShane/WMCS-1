from system_b_llm.interfaces.llm_provider import LLMProvider

class ExternalVerifier:
    def __init__(self, llm_client: LLMProvider):
        self.llm = llm_client

    def verify(self, query: str, system_response: str) -> dict:
        """
        Uses the LLM in 'Unconstrained Mode' to check the truthfulness
        of the Constrained System's answer. Returns structured JSON.
        """
        prompt = f"""
You are the "External Smart Verifier". 
You are the "External Smart Verifier". 
You have access to REAL-TIME WEB SEARCH and general knowledge.

CONTEXT:
- User Query: "{query}"
- WMCS (Constrained System) Answer: "{system_response}"

YOUR TASK:
1. CHECK the accuracy of the WMCS Answer. Is it true? Is it missing key details?
2. PROVIDE additional context or corrections from your general knowledge.
3. RATING: Rate the WMCS answer from 0 to 10.

OUTPUT JSON FORMAT:
{{
  "status": "CONFIRMED" | "PARTIAL" | "INCORRECT",
  "score": <integer 0-10>,
  "missing_context": "<what is missing>",
  "correction": "<The ideal, fact-filled answer>"
}}
"""
        # We manually call the new search method
        # Note: We need to parse the JSON manually since json_completion logic is not in search method yet
        raw_response = self.llm.completion_with_search("You are a smart Verifier. Output Valid JSON.", prompt)
        
        # Robust JSON Cleanup
        text = raw_response.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        # Remove any leading/trailing chars that aren't brackets (sometimes happens)
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            text = text[start:end]
            
        try:
            return __import__('json').loads(text)
        except:
            return {
                "status": "ERROR",
                "score": 0,
                "missing_context": "Failed to parse Verifier JSON.",
                "correction": text
            }
