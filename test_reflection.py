from system_a_cognitive.meta.reflection import ReflectionEngine
from system_a_cognitive.meta.store import MetaReasoningStore
from system_a_cognitive.logic.models import ReasoningTrace, Outcome

def test_reflection_flow():
    print("Testing Reflection Engine...")
    
    # 1. Setup
    reflector = ReflectionEngine()
    store = MetaReasoningStore(data_dir="data")
    
    # 2. Create a Mock Trace (Simulating a failed query)
    trace = ReasoningTrace(query="What is the speed of light?")
    trace.steps = ["Retrieved block: Physics", "Used Newton's laws"]
    trace.outcome = Outcome.FAILURE
    
    feedback = "Newton's laws don't apply to light speed, you need relativity."
    
    # 3. Analyze
    print("Analyzing trace...")
    lesson = reflector.analyze_trace(trace, feedback)
    
    if lesson:
        print(f"SUCCESS: Extracted Lesson: {lesson.content}")
        print(f"Type: {lesson.lesson_type}")
        print(f"Trigger: {lesson.trigger}")
        
        # 4. Save
        store.add_lesson(lesson)
        print("Lesson saved.")
        
        # 5. Verify Load
        store_reload = MetaReasoningStore(data_dir="data")
        assert len(store_reload.lessons) > 0
        print("Lesson reloaded successfully.")
    else:
        print("FAILURE: No lesson extracted.")

if __name__ == "__main__":
    test_reflection_flow()
