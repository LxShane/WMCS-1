# PART 15: INGESTION RULES & CONTENT NORMALIZATION

## 15.1 The Problem

```
When AI reads: "Cats have soft, furry paws with retractable claws"

BAD OUTPUT (dumped in one place):
┌─────────────────────────────────────────────────────────────────┐
│ CAT_001:                                                        │
│   body_parts: "paws that are soft and furry with retractable    │
│               claws"                                            │
└─────────────────────────────────────────────────────────────────┘

Problems:
├── Natural language stored (not structured)
├── Properties of PAW stored in CAT block
├── No cross-linking to general PAW concept
├── "Retractable claws" is about CLAW, not PAW
└── Cannot reason across domains (paw ≈ hand)
```

## 15.2 The Three-Layer Content Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THREE-LAYER ARCHITECTURE                            │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 1: LEXICON                                                    │   │
│   │ Purpose: Map words → Concept IDs                                    │   │
│   │                                                                     │   │
│   │ • "cat" → CAT_001                                                   │   │
│   │ • "paw" → [PAW_GENERAL, CAT_PAW, DOG_PAW...] (needs disambiguation) │   │
│   │ • "bank" → [BANK_FINANCIAL, BANK_RIVER] (ambiguous)                 │   │
│   │ • "hand" → HUMAN_HAND_001                                           │   │
│   │ • "gato" (Spanish) → CAT_001                                        │   │
│   │                                                                     │   │
│   │ Words are POINTERS, not meaning.                                    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 2: CONCEPTS (Blocks)                                          │   │
│   │ Purpose: Store structured knowledge about each concept              │   │
│   │                                                                     │   │
│   │ • Unique ID (Group, Item)                                           │   │
│   │ • Multi-lens facets (STRUCTURE, FUNCTION, MECHANISM, etc.)          │   │
│   │ • Relations to other concepts (HAS_PART, IS_A, FILLS_ROLE)          │   │
│   │ • Properties specific to THIS concept only                          │   │
│   │                                                                     │   │
│   │ Concepts are MEANING, independent of words.                         │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ LAYER 3: EVIDENCE                                                   │   │
│   │ Purpose: Track where each fact came from                            │   │
│   │                                                                     │   │
│   │ • Source document/URL                                               │   │
│   │ • Extraction timestamp                                              │   │
│   │ • Confidence score                                                  │   │
│   │ • Original text (for audit)                                         │   │
│   │                                                                     │   │
│   │ Evidence GROUNDS concepts in reality.                               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 15.3 The Golden Rule of Content Placement

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║   EACH PROPERTY BELONGS TO THE MOST SPECIFIC CONCEPT IT DESCRIBES           ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝

Example: "Cats have soft, furry paws with retractable claws"

CORRECT PLACEMENT:
──────────────────

CAT_001:
├── HAS_PART: → PAW_CAT_001 (just the link, no properties here)

PAW_CAT_001:
├── TEXTURE: soft, furry          ← Property of cat's paw specifically
├── HAS_PART: → CLAW_CAT_001      ← Link to sub-part
├── INSTANCE_OF: → PAW_GENERAL    ← Link to general concept

CLAW_CAT_001:
├── RETRACTABLE: true             ← Property of cat's claw specifically
├── INSTANCE_OF: → CLAW_GENERAL

PAW_GENERAL:
├── FUNCTION: locomotion, manipulation
├── FOUND_IN: [mammals]           ← True of ALL paws
├── ANALOGOUS_TO: → HAND_GENERAL  ← Cross-domain link

CLAW_GENERAL:
├── COMPOSITION: keratin
├── FUNCTION: grip, defense       ← True of ALL claws
```

---

## 15.4 Content Normalization Rules

### Rule 1: No Pronouns — Always Resolve References

```
INPUT:  "The cat has paws. They are soft."
                          ^^^^
                          What is "they"?

BAD:    Store "they are soft" (unresolved)

GOOD:   Resolve "they" → PAW_CAT_001
        Store in PAW_CAT_001: TEXTURE: soft
```

**Resolution Process:**

```
1. Identify pronoun: "they", "it", "this", "that", "these", "those"
2. Find antecedent in context
3. Map antecedent to Concept ID via Lexicon
4. Replace pronoun with Concept ID in storage

NEVER STORE:
├── it, they, this, that, these, those
├── the former, the latter
├── said [noun], such [noun]
└── any reference that requires context to understand
```

### Rule 2: No Filler Words — Extract Core Terms Only

```
INPUT:  "It is important to note that mitochondria are generally 
         considered to be the powerhouse of the cell, which means 
         they produce energy."

FILLER TO REMOVE:
├── "It is important to note that"
├── "are generally considered to be"
├── "which means"
└── Hedging belongs in CONFIDENCE field, not content

EXTRACTED CORE:
├── MITOCHONDRIA → FUNCTION: ATP_production
├── MITOCHONDRIA → RELATION: powerhouse_of → EUKARYOTIC_CELL
└── Confidence: 0.95 (stored separately)
```

**Filler Word Categories:**

```
REMOVE THESE FROM CONTENT:

Hedging (move to confidence field):
├── generally, usually, often, sometimes, typically
├── considered to be, thought to be, believed to be
├── may, might, could, possibly, probably
└── in most cases, for the most part

Meta-commentary:
├── it is important to note that
├── it should be mentioned that
├── interestingly, notably, significantly
└── as we can see, as mentioned above

Empty connectors:
├── in order to → just "to"
├── due to the fact that → "because"
├── in the event that → "if"
└── at this point in time → "now"

Redundant modifiers:
├── very, really, extremely, quite
├── basic, fundamental (unless technically meaningful)
└── actual, real, true (unless contrasting with false)
```

### Rule 3: No Sentences — Store Structured Relations

```
INPUT:  "The heart pumps blood through the body."

BAD (sentence stored):
┌────────────────────────────────────────────────────┐
│ HEART_001:                                         │
│   description: "The heart pumps blood through      │
│                 the body"                          │
└────────────────────────────────────────────────────┘

GOOD (structured relation):
┌────────────────────────────────────────────────────┐
│ HEART_001:                                         │
│   FUNCTION:                                        │
│     action: PUMP                                   │
│     target: → BLOOD_001                            │
│     destination: → BODY_001                        │
│     mechanism: → CARDIAC_CYCLE_001                 │
└────────────────────────────────────────────────────┘
```

### Rule 4: Explicit Relation Types — No Buried Relations

```
RELATION VOCABULARY:

Hierarchical:
├── IS_A: category membership (cat IS_A mammal)
├── INSTANCE_OF: specific to general (Garfield INSTANCE_OF cat)
├── HAS_TYPE: general to specific (mammal HAS_TYPE cat)
└── SUBCLASS_OF: class hierarchy

Compositional:
├── HAS_PART: whole contains part (cat HAS_PART paw)
├── PART_OF: part belongs to whole (paw PART_OF cat)
├── CONTAINS: spatial containment
└── COMPOSED_OF: material composition

Functional:
├── PRODUCES: output generation (mitochondria PRODUCES ATP)
├── CONSUMES: input requirement
├── ENABLES: capability provision
├── PREVENTS: blocking relationship
└── FILLS_ROLE: functional equivalence (paw FILLS_ROLE manipulator)

Causal:
├── CAUSES: direct causation
├── CAUSED_BY: inverse causation
├── LEADS_TO: indirect consequence
└── REQUIRES: prerequisite

Equivalence:
├── EQUIVALENT_TO: same function, different domain
├── ANALOGOUS_TO: similar but not identical
├── HOMOLOGOUS_TO: shared evolutionary origin
└── CONTRASTS_WITH: meaningful difference

Temporal:
├── PRECEDES: temporal ordering
├── FOLLOWS: inverse temporal
├── DURING: temporal containment
└── TRANSFORMS_INTO: state change
```

### Rule 5: Ambiguous Words — Flag or Resolve

```
INPUT:  "The bank was steep."

STEP 1: Lexicon lookup
        "bank" → [BANK_FINANCIAL_001, BANK_RIVER_001]
        
STEP 2: Context analysis
        "steep" → physical property → likely BANK_RIVER_001
        
STEP 3: Either resolve OR flag

OPTION A - Resolve with confidence:
┌────────────────────────────────────────────────────┐
│ BANK_RIVER_001:                                    │
│   PROPERTY: steep                                  │
│   _resolution_confidence: 0.85                     │
│   _resolution_context: "physical property 'steep'" │
└────────────────────────────────────────────────────┘

OPTION B - Flag as ambiguous (early stage system):
┌────────────────────────────────────────────────────┐
│ PENDING_RESOLUTION:                                │
│   word: "bank"                                     │
│   candidates: [BANK_FINANCIAL_001, BANK_RIVER_001] │
│   context: "steep"                                 │
│   suggested: BANK_RIVER_001                        │
│   status: NEEDS_CONFIRMATION                       │
└────────────────────────────────────────────────────┘
```

---

## 15.5 Placement Decision Tree

```
When AI extracts a property from text, follow this tree:

                    ┌─────────────────────────┐
                    │ What is this property   │
                    │ ABOUT?                  │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │ Identify the SUBJECT    │
                    │ (resolve any pronouns)  │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Property of the │ │ Property of a   │ │ Property shared │
    │ WHOLE entity?   │ │ PART of entity? │ │ across ALL of   │
    │                 │ │                 │ │ this type?      │
    └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
             │                   │                   │
             ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Store in the    │ │ Store in the    │ │ Store in the    │
    │ entity's Block  │ │ PART's Block    │ │ GENERAL Block   │
    │                 │ │                 │ │                 │
    │ CAT_001:        │ │ PAW_CAT_001:    │ │ PAW_GENERAL:    │
    │   weight: 4kg   │ │   texture: soft │ │   digits: 4-5   │
    └─────────────────┘ └─────────────────┘ └─────────────────┘


ADDITIONAL CHECKS:

┌─────────────────────────────────────────────────────────────────┐
│ Is this property ALWAYS true of this type?                      │
│                                                                 │
│ YES → Store in GENERAL block                                    │
│       Example: "Cats have four legs" → CAT_GENERAL              │
│                                                                 │
│ NO  → Store in SPECIFIC block                                   │
│       Example: "My cat has three legs" → CAT_INSTANCE_001       │
│                                                                 │
│ USUALLY → Store in GENERAL with confidence < 1.0                │
│       Example: "Cats usually have four legs"                    │
│       → CAT_GENERAL, confidence: 0.95                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Does this property describe a RELATION to another concept?      │
│                                                                 │
│ YES → Create explicit link, not text                            │
│       "Cats eat mice" → CAT_001 CONSUMES → MOUSE_001            │
│                                                                 │
│ NO  → Store as property value                                   │
│       "Cats weigh 4kg" → CAT_001: weight: 4kg                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15.6 Handling Hierarchy: General vs Specific vs Instance

```
THREE LEVELS OF SPECIFICITY:

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   LEVEL 1: GENERAL (Universal truths about the category)                    │
│   ═══════════════════════════════════════════════════                       │
│                                                                             │
│   PAW_GENERAL (23, 1):                                                      │
│   ├── FUNCTION: locomotion, manipulation, sensing                           │
│   ├── FOUND_IN: mammals                                                     │
│   ├── TYPICAL_STRUCTURE: digits, pads, claws/nails                          │
│   └── ANALOGOUS_TO: → HAND_GENERAL                                          │
│                                                                             │
│   Store here: Properties true of ALL paws everywhere                        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   LEVEL 2: SPECIFIC (True of this type/species)                             │
│   ═════════════════════════════════════════════                             │
│                                                                             │
│   PAW_CAT (23, 51):                                                         │
│   ├── INSTANCE_OF: → PAW_GENERAL                                            │
│   ├── TEXTURE: soft, furry (specific to cat paws)                           │
│   ├── CLAW_TYPE: retractable (specific to cats)                             │
│   ├── DIGIT_COUNT: front=5, back=4                                          │
│   └── SILENT_WALKING: true (cat-specific adaptation)                        │
│                                                                             │
│   PAW_DOG (23, 52):                                                         │
│   ├── INSTANCE_OF: → PAW_GENERAL                                            │
│   ├── TEXTURE: rough, padded                                                │
│   ├── CLAW_TYPE: fixed (non-retractable)                                    │
│   └── DIGIT_COUNT: 4-5                                                      │
│                                                                             │
│   Store here: Properties true of this TYPE but not all paws                 │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   LEVEL 3: INSTANCE (True of this individual only)                          │
│   ════════════════════════════════════════════════                          │
│                                                                             │
│   PAW_GARFIELD_FRONT_LEFT (23, 51, instance="garfield_fl"):                 │
│   ├── INSTANCE_OF: → PAW_CAT                                                │
│   ├── CONDITION: healthy                                                    │
│   ├── INJURY: none                                                          │
│   └── OWNER: → GARFIELD_001                                                 │
│                                                                             │
│   PAW_STRAY_CAT_FRONT_LEFT (23, 51, instance="stray_fl"):                   │
│   ├── INSTANCE_OF: → PAW_CAT                                                │
│   ├── CONDITION: injured                                                    │
│   ├── MISSING_TOES: 1                                                       │
│   └── OWNER: → STRAY_CAT_001                                                │
│                                                                             │
│   Store here: Properties true of THIS INDIVIDUAL only                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


DECISION RULE:

"Cats have retractable claws"
├── Is this true of ALL cats? → YES
├── Is this true of ALL paws? → NO (dogs don't have retractable claws)
└── Store in: PAW_CAT (Level 2: Specific)

"Garfield's paw is injured"
├── Is this true of ALL cats? → NO
├── Is this true of THIS cat always? → NO (temporary state)
└── Store in: PAW_GARFIELD (Level 3: Instance)

"Paws are used for locomotion"
├── Is this true of ALL paws? → YES
└── Store in: PAW_GENERAL (Level 1: General)
```

---

## 15.7 Cross-Domain Linking (Equivalence)

```
THE POWER OF PROPER SEPARATION:

Because properties are stored at the right level, we can now reason:

QUERY: "What is the equivalent of a hand for a cat?"

REASONING:
1. HAND_HUMAN fills roles: [MANIPULATOR, SENSOR, TOOL_USER]
2. Search: What in CAT fills role MANIPULATOR?
3. Found: PAW_CAT fills roles: [MANIPULATOR, LOCOMOTOR, WEAPON]
4. Match: PAW_CAT ≈ HAND_HUMAN (for MANIPULATOR function)

ANSWER: "A cat's paw is functionally equivalent to a human hand 
         for manipulation, though with limitations (no opposable 
         digit, less fine motor control)."

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   HAND_HUMAN ─────────── FILLS_ROLE ─────────▶ MANIPULATOR      │
│        │                                            ▲           │
│        │                                            │           │
│   ANALOGOUS_TO                                 FILLS_ROLE       │
│        │                                            │           │
│        ▼                                            │           │
│   PAW_CAT ───────────── FILLS_ROLE ─────────────────┘           │
│                                                                 │
│   This link is POSSIBLE because:                                │
│   • HAND properties are in HAND block (not HUMAN block)         │
│   • PAW properties are in PAW block (not CAT block)             │
│   • Both link to abstract MANIPULATOR role                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15.8 The Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION PIPELINE                                │
│                                                                             │
│   INPUT TEXT                                                                │
│   "Cats have soft, furry paws with retractable claws that help             │
│    them climb trees silently."                                              │
│                                                                             │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 1: ENTITY EXTRACTION                                           │   │
│   │                                                                     │   │
│   │ LLM extracts: [cats, paws, claws, trees]                            │   │
│   │ Properties: [soft, furry, retractable, climb, silently]             │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 2: LEXICON LOOKUP & DISAMBIGUATION                             │   │
│   │                                                                     │   │
│   │ "cats" → CAT_001 (unambiguous)                                      │   │
│   │ "paws" → PAW_CAT_001 (context: cats)                                │   │
│   │ "claws" → CLAW_CAT_001 (context: cats + paws)                       │   │
│   │ "trees" → TREE_001 (unambiguous)                                    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 3: PROPERTY ASSIGNMENT (Placement Decision)                    │   │
│   │                                                                     │   │
│   │ "soft, furry" describes → paws → PAW_CAT_001: TEXTURE               │   │
│   │ "retractable" describes → claws → CLAW_CAT_001: RETRACTABLE         │   │
│   │ "climb" describes → cats (ability) → CAT_001: CAPABILITY            │   │
│   │ "silently" describes → climbing action → mechanism link             │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 4: RELATION EXTRACTION                                         │   │
│   │                                                                     │   │
│   │ CAT_001 ──HAS_PART──▶ PAW_CAT_001                                   │   │
│   │ PAW_CAT_001 ──HAS_PART──▶ CLAW_CAT_001                              │   │
│   │ CAT_001 ──CAPABILITY──▶ CLIMB                                       │   │
│   │ CLAW_CAT_001 ──ENABLES──▶ CLIMB (mechanism)                         │   │
│   │ PAW_CAT_001 ──ENABLES──▶ SILENT_MOVEMENT (mechanism)                │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 5: GENERALIZATION CHECK                                        │   │
│   │                                                                     │   │
│   │ "retractable claws" - Is this true of ALL cats?                     │   │
│   │   → YES → Store in CAT_CLAW (specific type)                         │   │
│   │   → Not all CLAWS are retractable → Don't store in CLAW_GENERAL     │   │
│   │                                                                     │   │
│   │ "paws have claws" - Is this true of ALL paws?                       │   │
│   │   → MOSTLY → Store in PAW_GENERAL with confidence 0.9               │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 6: EVIDENCE ATTACHMENT                                         │   │
│   │                                                                     │   │
│   │ Each extracted fact gets:                                           │   │
│   │ ├── source: "input_document_001"                                    │   │
│   │ ├── original_text: "Cats have soft, furry paws..."                  │   │
│   │ ├── extraction_timestamp: 2026-01-31T10:00:00Z                      │   │
│   │ └── confidence: 0.85 (based on source trust)                        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STEP 7: EPISTEMIC GATE VALIDATION                                   │   │
│   │                                                                     │   │
│   │ CHECK: Are all references resolved? (no pronouns)          ✓        │   │
│   │ CHECK: Are properties in correct blocks?                   ✓        │   │
│   │ CHECK: Are relations explicit (not buried in text)?        ✓        │   │
│   │ CHECK: Is evidence attached?                               ✓        │   │
│   │ CHECK: Any ambiguous terms flagged?                        ✓        │   │
│   │                                                                     │   │
│   │ → PASS: Commit to Block storage                                     │   │
│   │ → FAIL: Return to earlier step with specific error                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                              BLOCKS STORED                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 15.9 LLM Prompt Template for Ingestion

```
SYSTEM PROMPT FOR INGESTION:

You are extracting structured knowledge from text into WMCS Blocks.

RULES:
1. NEVER store pronouns (it, they, this, that) - resolve to concept IDs
2. NEVER store filler words (importantly, generally, it should be noted)
3. NEVER store sentences - extract structured relations
4. ALWAYS place properties in the MOST SPECIFIC concept they describe
5. ALWAYS use explicit relation types (HAS_PART, PRODUCES, CAUSES, etc.)
6. ALWAYS flag ambiguous terms for resolution

OUTPUT FORMAT:

For each fact extracted, output:

{
  "target_block": "<CONCEPT_ID>",
  "facet": "<STRUCTURE|FUNCTION|MECHANISM|etc>",
  "property": "<property_name>",
  "value": "<extracted_value>" OR "→ <LINKED_CONCEPT_ID>",
  "relation_type": "<HAS_PART|PRODUCES|IS_A|etc>" (if linking),
  "confidence": <0.0-1.0>,
  "placement_reasoning": "<why this property belongs in this block>"
}

EXAMPLE:

Input: "Cats have soft, furry paws"

Output:
[
  {
    "target_block": "CAT_001",
    "facet": "STRUCTURE",
    "property": "has_part",
    "value": "→ PAW_CAT_001",
    "relation_type": "HAS_PART",
    "confidence": 1.0,
    "placement_reasoning": "Ownership relation: cat has paw"
  },
  {
    "target_block": "PAW_CAT_001",
    "facet": "STRUCTURE",
    "property": "texture",
    "value": "soft, furry",
    "relation_type": null,
    "confidence": 0.95,
    "placement_reasoning": "Texture is property of the paw itself, not the cat"
  }
]

WRONG OUTPUT (do not do this):
{
  "target_block": "CAT_001",
  "property": "paws",
  "value": "soft and furry paws with claws"  ← WRONG: sentence, properties of paw in cat block
}
```

---

## 15.10 Validation Checklist

```
BEFORE ANY BLOCK IS STORED, VERIFY:

□ NO PRONOUNS
  Scan for: it, they, this, that, these, those, he, she, its, their
  If found → REJECT, resolve first

□ NO FILLER
  Scan for: importantly, generally, basically, actually, essentially
  If found → STRIP and re-evaluate

□ NO SENTENCES
  If value contains subject + verb + object structure → DECOMPOSE
  
□ CORRECT PLACEMENT
  Ask: "Is this property true of THIS concept specifically?"
  If true of parent → move up
  If true of sub-part → move down
  If true of all instances → move to GENERAL

□ EXPLICIT RELATIONS
  All links use defined relation types
  No relations buried in text strings

□ AMBIGUITY HANDLED
  Multi-meaning words either:
  - Resolved with confidence score, OR
  - Flagged in PENDING_RESOLUTION queue

□ EVIDENCE ATTACHED
  Source document identified
  Confidence calculated
  Original text preserved for audit

□ GENERALIZATION LEVEL CORRECT
  Universal truths → GENERAL block
  Type-specific → SPECIFIC block  
  Individual facts → INSTANCE block
```

---

## 15.11 Summary

```
THE INGESTION RULES IN ONE PAGE:

1. WORDS ARE POINTERS
   └── Lexicon maps words → Concept IDs
   └── Same concept, different words = same ID

2. PROPERTIES GO TO MOST SPECIFIC CONCEPT
   └── "Cat has soft paws" → texture in PAW block, not CAT block
   └── Ask: "What is this REALLY about?"

3. NO NATURAL LANGUAGE IN BLOCKS
   └── No pronouns (resolve them)
   └── No filler words (strip them)
   └── No sentences (decompose them)
   └── Structured relations only

4. THREE LEVELS OF STORAGE
   └── GENERAL: True of all instances
   └── SPECIFIC: True of this type
   └── INSTANCE: True of this individual

5. EXPLICIT RELATIONS
   └── Use defined vocabulary: HAS_PART, PRODUCES, CAUSES, IS_A, etc.
   └── Never bury relations in text

6. HANDLE AMBIGUITY
   └── Flag or resolve multi-meaning words
   └── Never assume - ask or defer

7. EVIDENCE EVERYTHING
   └── Source, timestamp, confidence
   └── Original text for audit

8. GATE VALIDATES
   └── Epistemic Gate checks all rules
   └── Reject malformed content
   └── Return specific errors for fixing
```
