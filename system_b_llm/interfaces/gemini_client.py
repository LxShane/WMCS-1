from typing import Dict, Any
import json
import os
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from .llm_provider import LLMProvider

class GeminiClient(LLMProvider):
    def __init__(self, api_key: str, model: str):
        if genai is None:
            raise ImportError("The 'google-genai' library is required. Run `pip install google-genai`.")
        
        # New SDK Client Initialization
        self.client = genai.Client(api_key=api_key)
        self.model_name = model

    def completion(self, system_prompt: str, user_prompt: str) -> str:
        try:
            full_prompt = f"{system_prompt}\n\nUser Query: {user_prompt}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"Error connecting to Gemini: {str(e)}"

    def completion_with_search(self, system_prompt: str, user_prompt: str) -> str:
        """
        Uses Google Search Grounding to verify facts using the new SDK.
        """
        try:
            full_prompt = f"{system_prompt}\n\nUser Query: {user_prompt}"
            
            # Use the correct tool config for the new SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(
                        google_search=types.GoogleSearch()
                    )]
                )
            )
            
            # The response object in the new SDK might have different structure for grounding metadata
            # For now, we just return the text which should incorporate the search results
            return response.text
            
        except Exception as e:
            print(f"DEBUG: Web Search Failed ({e}). Falling back to standard generation.")
            return self.completion(system_prompt, user_prompt)

    def json_completion(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Forces JSON output using prompt engineering.
        """
        system_prompt += "\nIMPORTANT: Return valid JSON only. Do not wrap in markdown code blocks."
        
        text = self.completion(system_prompt, user_prompt)
        
        # Clean up possible markdown
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"DEBUG: JSON Parse Failed on Gemini output. Raw: {text}")
            return {"error": "Failed to parse JSON", "raw": text}

    def embed_content(self, text: str) -> list[float]:
        """
        Generates vector embeddings for the given text using 'text-embedding-004'.
        """
        try:
            response = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Embedding Failed: {e}")
            return []

    def analyze_image(self, prompt: str, image_path: str) -> str:
        """
        Multimodal analysis using Gemini 1.5 Flash/Pro.
        """
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, img]
            )
            return response.text
        except ImportError:
            return "Error: PIL (Pillow) library not installed."
        except Exception as e:
            return f"Image Analysis Failed: {str(e)}"
