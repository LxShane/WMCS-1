# WMCS World-Model Cognitive System: Workflow Documentation

This document explains the core architecture and execution workflow of the World-Model Cognitive System (WMCS).

## 1. Two-Brain Architecture

The system is divided into two distinct components to ensure both creativity and factual accuracy.

| Component | Role | Nature | Key Elements |
| :--- | :--- | :--- | :--- |
| **System A (Left Brain)** | Logic, Memory, Fact-Checking | Deterministic, slow, verifiable | Concept Store, Vector Memory, Navigator, Logic Engine, Epistemic Gate |
| **System B (Right Brain)** | Language, Creativity, Synthesis | Probabilistic, fast, creative | LLM (Gemini/GPT), Response Generator |

> [!IMPORTANT]
> **System B is FORBIDDEN from guessing facts.** It must only reason over the structured data provided by System A.

---

## 2. The Cognitive Loop (7 Steps)

When a query is received, it follows this rigorous process:

1.  **PERCEPTION**: Parse the query for intent (Definition, Explanation, Capability, etc.) and identify core entities.
2.  **RECALL**: Retrieve primary concepts from the Long-Term Memory and search ChromaDB for semantic context.
3.  **NAVIGATION**: Walk the Knowledge Graph to find related concepts, causal chains, and potential analogies.
4.  **REASONING**: Apply logic (Inheritance, Transitivity, Constraint Checking) to derive a verified answer.
5.  **SYNTHESIS**: Assemble a "Verified Context Packet" containing all facts, confidence scores, and derivations.
6.  **GENERATION**: The LLM (System B) translates the context packet into natural language, citing all Concept IDs.
7.  **GATING**: The Epistemic Gate verifies the response against the original facts. If confidence is low or facts are missing, it triggers the **Deep Researcher**.

---

## 3. Workflow Example: Logic Inference

### Scenario: "Can a Persian cat jump as high as a regular cat?"

**Execution Path:**
- **Recall**: Retrieves the `Persian Cat` (Variant) and `Cat` (Prototype) concepts.
- **Inheritance**: `Persian` inherits the jumping capability from `Cat` ("up to 6x body length").
- **Override Detection**: Found `Persian.overrides.activity_level = low`.
- **Constraint Check**: Found `Persian.overrides.head_shape = brachycephalic` (affects breathing/stamina).
- **Inference**: While the physical capacity is inherited, the specific breed characteristics modify the expected performance.

**Final Answer derivation:**
> "Persian cats inherit a high jumping capacity from the feline prototype, but breed-specific overrides (low activity level and respiratory constraints) mean they typically perform at a reduced level compared to generic cats."

---

## 4. Grounding Principles

- **Constructive Understanding**: Understanding is knowing how to *construct* an object from primitives (e.g., Cat -> Skeletal System -> Bone -> Calcium).
- **Zero Hallucination**: If System A cannot find or verify a fact, System B must reply: *"I do not have enough information."*
- **Persistent Learning**: Failures or gaps in the Knowledge Graph trigger autonomous research to "patch" the mind.
