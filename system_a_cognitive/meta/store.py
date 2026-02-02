import json
import os
import uuid
from typing import List
from ..logic.models import MetaLesson

class MetaReasoningStore:
    def __init__(self, data_dir="data"):
        self.filepath = os.path.join(data_dir, "meta_lessons.json")
        self.lessons: List[MetaLesson] = []
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.lessons = [MetaLesson.from_dict(d) for d in data]
        except Exception as e:
            print(f"Error loading meta-lessons: {e}")

    def save(self):
        data = [l.to_dict() for l in self.lessons]
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def add_lesson(self, lesson: MetaLesson):
        self.lessons.append(lesson)
        self.save()

    def get_relevant_lessons(self, query: str) -> List[MetaLesson]:
        # Simple keyword matching for now
        # In future, use embeddings/SysB to match "trigger"
        relevant = []
        q_lower = query.lower()
        for lesson in self.lessons:
            # Very basic trigger match
            if lesson.trigger.lower() in q_lower or lesson.trigger == "*":
                relevant.append(lesson)
        return relevant
