# WMCS v2.0 - System Layer Status Report

**Current Operational State**: `WEB_API_MODE` (Dashboard)

## Layer 1: Perception & Ingestion (System B)
| Component | Status | Description |
| :--- | :--- | :--- |
| **Query Parser** | 🟢 **ACTIVE** | Detects intent (Question vs Command). |
| **Content Ingestor** | 🟢 **ACTIVE** | Parses incoming text/files into Concept Blocks. |
| **Identity Manager** | 🟢 **ACTIVE** | Resolves names to Unique Concept IDs (e.g. `cat` -> `(21, 1)`). |

## Layer 2: Memory & Retrieval (System A)
| Component | Status | Description |
| :--- | :--- | :--- |
| **Vector Store (Chroma)** | 🟢 **ACTIVE** | Semantic Search for relevant concepts. |
| **Concept Navigator** | 🟢 **ACTIVE** | "Agentic" traversal (Node-hopping) to find related context. |
| **Functional Search** | 🟡 **STANDBY** | Available for Analogy queries, but not used in standard Q&A. |

## Layer 3: Reasoning & Curiosity (System A)
| Component | Status | Description |
| :--- | :--- | :--- |
| **Logic Engine** | 🟢 **ACTIVE** | Synthesizes facts and detects conflicts/missing links. |
| **Gap Detection** | 🟢 **ACTIVE** | Autonomously detects "Unknown Concepts" in the logic trace. |
| **Deep Researcher** | 🟢 **ACTIVE** | **(New)** Triggers web simulation to learn missing concepts on-the-fly. |

## Layer 4: Epistemics & Output (System B)
| Component | Status | Description |
| :--- | :--- | :--- |
| **Epistemic Gate** | 🟢 **ACTIVE** | Validates confidence. Rejects hallucinations. |
| **Response Generator** | 🟢 **ACTIVE** | Translates internal logic into natural language. |

## Layer 5: Metacognition (The "Self")
| Component | Status | Description |
| :--- | :--- | :--- |
| **External Verifier** | 🔴 **OFFLINE** | (CLI Only) Critiques the AI's own answer *after* generation. |
| **Reflection Engine** | 🔴 **OFFLINE** | (CLI Only) Learns from user feedback ("No, that's wrong"). |
| **Subconscious Loop** | 🔴 **OFFLINE** | Background dreaming/consolidation. Requires manual activation. |

> **Note**: The "Offline" layers are currently designed for the *Interactive Terminal* mode. To enable them in the Web Dashboard, we would need to make the API asynchronous (Streaming) to allow for "After-thought" updates.
