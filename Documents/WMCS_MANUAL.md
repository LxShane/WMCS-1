# World-Model Cognitive System (WMCS) - System Manual

> **Version**: 2026.02 (Post-Refactor)  
> **Status**: Operational  
> **Type**: Neuro-Symbolic Hybrid Architecture

---

## 1. What is WMCS?

WMCS is a **"Left Brain / Right Brain" Artificial Intelligence**. It solves the two biggest problems of modern LLMs: **Hallucination** (making things up) and **Amnesia** (forgetting things).

### The "Two-Brain" Architecture
*   **System A (Left Brain)**: The Cognitive Engine.
    *   **Role**: Logic, Memory, Fact-Checking, Navigation.
    *   **Nature**: Deterministic, slow, verifiable.
    *   **Components**: ChromaDB, Navigator, Logic Engine, Epistemic Gate.
*   **System B (Right Brain)**: The LLM (Gemini 2.0).
    *   **Role**: Language, Creativity, Synthesis, Extraction.
    *   **Nature**: Probabilistic, fast, creative.
    *   **Constraint**: It is FORBIDDEN from guessing facts. It must use System A's data.

---

## 2. Core Components

### 🧠 Memory Systems
1.  **Concept Store (The "Cortex")**
    *   **Format**: 12,669+ JSON files (`data/concepts/*.json`).
    *   **Role**: The "Source of Truth". Human-readable structured data.
    *   **Structure**: Every concept has Layers (`Surface`, `Deep`), Facets (`Spatial`, `Physics`), and Claims (`Subject -> Predicate -> Object`).
2.  **Vector Memory (The "Index")**
    *   **Technology**: ChromaDB (12,600+ vectors).
    *   **Role**: Allows semantic search ("find me things *like* a cat").
    *   **Recent Upgrade**: Rebuilt with strict filename-based IDs to prevent corruption.

### ⚙️ Cognitive Engines
1.  **Identity Manager**: Governance system that mints unique `(Group, Item)` IDs for every concept (e.g., Cat is `20, 1004`).
2.  **Navigator**: A graph traversal engine. It "walks" from concept to concept using Claims.
    *   *New:* Uses `RelationBuilder` to automatically link concepts via IDs.
3.  **Epistemic Gate**: A firewall for truth. It grades every answer from 0.0 to 1.0. If confidence < 0.9, it refuses to answer.
4.  **Deep Researcher**: An autonomous agent that browses the web to learn new things when the system says "I don't know".

### 🤖 Maintenance Agents
1.  **The Active Gardener**: A background process that runs when you sleep.
    *   **Audits**: Checks concepts for missing data (Physics, Spatial info).
    *   **Patches**: Triggers research to fill gaps.
    *   **Connects**: Scans for missing links and builds ID-relations between concepts.

---

## 3. How It Operates (The Cognitive Loop)

When you ask a question like *"How do cargo receptors work?"*:

1.  **Perception**: `QueryParser` analyzes intent.
2.  **Recall**: `ChromaStore` searches for "cargo receptor" and finds the JSON block.
3.  **Navigation**: `Navigator` looks at the block's exits. It loads related concepts (e.g., "Vesicle", "Golgi Body").
4.  **Synthesis**: The **Logic Engine** feeds these Verified Facts to the LLM.
5.  **Reasoning**: The LLM writes a response, *citing* the specific IDs it used.
6.  **Gating**: The `EpistemicGate` checks the citations.
    *   *If Valid*: Answer delivered.
    *   *If Invalid*: Trigger `DeepResearcher` to learn more.

---

## 4. Command Reference

### 🚀 Running the System
| Command | Description |
|:---|:---|
| `python main.py` | Starts the WMCS Kernel (Interactive Mode). |
| `python server/api.py` | Starts the REST API server. |

### 🤖 Agents & Background Processes
| Command | Description |
|:---|:---|
| `python run_gardener.py` | **Start the Gardener.** Audits concepts, fills gaps, and builds relations. |
| `python stress_test_crispr.py` | **Trigger Deep Research.** Demonstrates the researcher learning a specific topic. |

### 🛠️ Maintenance & Tools
| Script | Use Case |
|:---|:---|
| `python batch_enrich.py` | **Run this often.** Scans all 12k concepts and adds ID links to make them navigable. |
| `python rebuild_chromadb.py` | **Emergency Repair.** Deletes and rebuilds the Vector Index if search breaks. |
| `python add_relations.py` | Manually adds specific relations to key concepts (Cat, Dog, etc). |

### 🧪 Testing & Diagnostics
| Script | Use Case |
|:---|:---|
| `python reality_check.py` | Fast diagnostic. Checks if DB, API, and Config are working. |
| `python final_exam.py` | **Full Stress Test.** Runs complex scenarios (Ambiguity, Lateral Thinking, Research). |
| `python test_nav.py` | Verifies that the Navigator can find paths between concepts. |
| `python test_relations.py` | Tests the `RelationBuilder` utility. |

Other cmd
python main.py             # Start the main Kernel (Interactive Chat)
python server/api.py       # Start the API Server
python batch_enrich.py     # Scan all concepts and add ID links
python run_gardener.py     # Start the background maintenance agent
python stress_test_crispr.py # Test the Deep Researcher
python reality_check.py    # Quick system health check
python final_exam.py       # Full stress test suite
python test_nav.py         # Test graph navigation
python test_relations.py   # Test relation building
python rebuild_chromadb.py # Emergency: Rebuild vector index
python add_relations.py    # Manually add relations to concepts

---

## 5. Directory Structure
```
WMCS_1/
├── system_a_cognitive/    # The Left Brain (Logic)
│   ├── memory/            # ChromaDB & JSON Stores
│   ├── logic/             # Navigator, Relations, Identity
│   ├── meta/              # Gardener & Researcher agents
│   └── ingestion/         # Ingestor (Learning Engine)
├── system_b_llm/          # The Right Brain (LLM)
├── data/
│   ├── concepts/          # 12,000+ Concept Files (JSON)
│   └── chroma_db/         # Vector Database
├── main.py                # Kernel Entry Point
└── requirements.txt       # Python Dependencies
```
