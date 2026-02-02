import uuid
from datetime import datetime
from system_b_llm.interfaces.gemini_client import GeminiClient
from config import Config
from ..logic.models import ReasoningTrace, MetaLesson, Outcome

REFLECTION_PROMPT = """
You are the Meta-Reasoning Engine. 
Review the following thinking process and user feedback.
Analyze WHY it succeeded or failed.

Context:
Query: {query}
Steps: {steps}
User Feedback: {feedback}
Outcome: {outcome}

Task:
Extract a generalized LESSON about how to reason better.
Format as JSON:
{{
  "type": "STRATEGY" | "CAUTION",
  "trigger": "when to apply this lesson (keyword or topic)",
  "content": "The lesson text",
  "confidence": 0.0 to 1.0
}}
"""

class ReflectionEngine:
    def __init__(self):
        self.client = GeminiClient(Config.LLM_API_KEY, Config.LLM_MODEL)

    def analyze_trace(self, trace: ReasoningTrace, feedback: str) -> MetaLesson:
        """
        Uses LLM to critique the trace and extract a lesson.
        """
        prompt = REFLECTION_PROMPT.format(
            query=trace.query,
            steps=trace.steps,
            feedback=feedback,
            outcome=trace.outcome.value
        )
        
        print("DEBUG: reflecting...")
        result = self.client.json_completion(
            "You are a critical reasoning analyst.", 
            prompt
        )
        
        if "error" in result:
            return None
            
        return MetaLesson(
            id=str(uuid.uuid4())[:8],
            lesson_type=result.get("type", "STRATEGY"),
            content=result.get("content", "No lesson extracted"),
            trigger=result.get("trigger", "*"),
            confidence=result.get("confidence", 0.5),
            created_at=datetime.now().isoformat()
        )
