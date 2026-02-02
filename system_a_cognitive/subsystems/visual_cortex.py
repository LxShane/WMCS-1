import json
from termcolor import colored
import os

class VisualCortex:
    """
    Subsystem for processing visual inputs (Diagrams, Charts, Schematics).
    """
    def __init__(self, client):
        self.client = client

    def analyze_diagram(self, image_path: str):
        """
        Extracts structural concepts from a diagram.
        """
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}

        print(colored(f"  [Visual Cortex] Scanning '{image_path}'...", "magenta"))

        prompt = """
        Analyze this technical diagram/image.
        Goal: Extract the distinct components and their relationships.
        
        Output strictly in JSON format:
        {
            "concepts": [
                {
                    "name": "Component Name",
                    "type": "Category (e.g., Valve, Organ, Node)",
                    "description": "Visual appearance and function if inferable",
                    "connections": ["Connected Component Name"]
                }
            ]
        }
        """
        
        response_text = self.client.analyze_image(prompt, image_path)
        
        # Parse JSON
        try:
            # Clean up markdown
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            print(colored(f"  [Visual Cortex] Identified {len(data.get('concepts', []))} visual entities.", "green"))
            return data
        except Exception as e:
            print(colored(f"  [Visual Cortex] Parse Error: {e}", "red"))
            return {"error": "Failed to parse visual data", "raw": response_text}
