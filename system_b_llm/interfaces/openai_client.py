from typing import Dict, Any
import json
import os
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None # Handle missing dependency gracefully

from .llm_provider import LLMProvider

class OpenAIClient(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model: str):
        if OpenAI is None:
            raise ImportError("The 'openai' library is required. Run `pip install openai`.")
        
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def completion(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"

    def json_completion(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Forces JSON output. 
        Note: Local models might struggle with strict JSON mode if not supported.
        We'll use a prompt trick + parsing.
        """
        system_prompt += "\nIMPORTANT: Valid JSON Output ONLY. No markdown, no explanations."
        
        text = self.completion(system_prompt, user_prompt)
        
        # Clean up markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback mock for robustness if LLM fails JSON
            print(f"DEBUG: JSON Parse Failed. Raw: {text}")
            return {"error": "Failed to parse JSON", "raw": text}
