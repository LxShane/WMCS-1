# WMCS (World-Model Cognitive System)

**A Level 4 Cognitive Architecture** that learns, grows, and repairs itself.

## 🧠 What is this?
WMCS is a **Neuro-Symbolic Hybrid AI**. It combines the creativity of Large Language Models (LLMs) with the strict logic and persistence of a Knowledge Graph.

Unlike a standard chatbot, this system:
*   **Remembers Forever:** Uses a Vector Database interactions.
*   **Learns Strategies:** The "Meta-Learner" reflects on failures and stores abstract rules ("Wisdom").
*   **Understands Physics:** Infers functionality from material properties (First Principles Reasoning).
*   **Self-Repairs:** An autonomous "Gardener" process audits the extensive knowledge base for decay and gaps, creating patches while you sleep.

## 📂 Architecture
*   **`system_a_cognitive/`**: The "Left Brain" (Logic, Memory, Retrieval).
    *   `ingestion/`: Converts text into strict JSON Concept Blocks.
    *   `memory/`: ChromaDB wrappers for Concepts and Strategies.
    *   `meta/`: The Reflection Engine and Autonomous Gardener.
*   **`system_b_llm/`**: The "Right Brain" (Gemini/LLM Interfaces).
*   `data/concepts/`: The Long-Term Memory (1,900+ JSON files).

## 🧬 The Data Schema (Concept Block)
Every object in the system is stored as a structured JSON file.
```json
{
  "name": "Brick",
  "type": "INANIMATE_OBJECT",
  "id": { "group": 20, "item": 1234 },
  "facets": {
    "STRUCTURAL": {
      "material_properties": {
        "rigidity": "HIGH",
        "state": "SOLID"
      }
    },
    "SPATIAL": {
      "location": "Construction Site",
      "connected_to": ["Mortar", "Wall"]
    }
  }
}
```

## 🚀 Usage

### 1. Setup
```bash
pip install -r requirements.txt
# Create .env file with LLM_API_KEY
```

### 2. Run the Kernel
```bash
python main.py
# Interact with the CLI. Ask questions like:
# "Can I use a Brick as a Hammer?" (Tests Physics Logic)
# "What is a Zorkmid?" (Tests Autonomous Research)
```

### 3. Run the Gardener (Self-Repair)
```bash
python start_gardener.py
# Runs in the background to fix missing data and update old concepts.
```

## 🛠 Features
*   **Deep Research:** Recursively searches the web for unknown terms.
*   **Strategy Injection:** Recalls past lessons to guide future answers.
*   **MacGyver Logic:** Uses material physics to determine functional substitutions.

## ⚠️ Known Issues
*   Legacy data (ingested prior to v2.0) may lack `material_properties`. The `ActiveGardener` is currently patching this.
*   Type classification for ambiguous bio-mechanical entities needs manual review.
