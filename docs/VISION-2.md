If we **forget the long-term vision** (Rust, Go, independent implementations, research, etc.) and look only at what you're actually building over the next few stages, the ecosystem is surprisingly small.

I'd separate it into **Core**, **Extensions**, and **Research**.

---

# Core Libraries (These are the actual project)

These are the libraries that define Evgraph today.

## 1. `evgraph-core` ⭐⭐⭐⭐⭐

This is the heart of the ecosystem.

Contains:

* `EvidenceGraph`
* `EvidenceNode`
* `EvidenceEdge`
* `EvidenceLevel`
* `Rule`
* `Finding`
* Graph traversal
* Serialization
* EGS implementation
* RES implementation

Everything depends on this.

Nothing inside depends on higher layers.

---

## 2. `evgraph` ⭐⭐⭐⭐⭐

This is what users install.

```bash
pip install evgraph
```

Contains:

* Python API
* `scan()`
* `load_graph()`
* High-level API
* Default adapters
* Default reporter
* Thin wrapper around `evgraph-core`

Example

```python
from evgraph import scan

report = scan("logs.parquet")
```

Most users never need to know `evgraph-core` exists.

---

# Extension Libraries

These extend the ecosystem without changing the core.

---

## 3. `evgraph-adapters`

Contains adapters.

For example

```
JSON

CSV

Parquet

Pandas

Polars

DuckDB
```

Eventually

```
Spark

Snowflake

BigQuery

MLflow
```

Their job is

```
Reality

↓

Evidence Graph
```

---

## 4. `evgraph-rules`

Contains rule packs.

Examples

```
EU AI Act

ISO 42001

GDPR

NIST AI RMF
```

These consume the graph.

```
Evidence Graph

↓

Findings
```

---

## 5. `evgraph-reporters`

Consumes findings.

Produces

```
JSON

Markdown

HTML

SARIF
```

Nothing else.

---

## 6. `evgraph-cli`

Just a wrapper.

```
evgraph scan

evgraph report

evgraph trace
```

It should contain almost zero business logic.

Everything should already exist in

```
evgraph
```

---

# Research Libraries (NOT core)

These stay completely separate.

---

## 7. `evgraph-context`

Context Virtualization.

```
Real Context

↓

Virtual Objects

↓

LLM

↓

Rehydration
```

Very experimental.

Security sensitive.

---

## 8. `evgraph-provenance`

Cryptographic integrity.

```
Evidence Graph

↓

Hashes

↓

Merkle Trees

↓

Verification
```

No governance logic.

Only provenance.

---

# So today...

Ignoring future language implementations,

ignoring SaaS,

ignoring products,

your ecosystem is basically

```
evgraph-core
        ↑
        │
    evgraph
   ↙   ↓    ↘
adapters rules reporters
        │
       CLI
```

with

```
context

provenance
```

off to the side as research packages.

---

# Personally...

I would **not** create all eight repositories immediately.

I'd keep **one monorepo** with multiple packages.

Like

```
evgraph/

packages/

    evgraph-core/

    evgraph/

    evgraph-adapters/

    evgraph-rules/

    evgraph-reporters/

    evgraph-cli/

    evgraph-context/

    evgraph-provenance/
```

Publish them independently later if it makes sense.

---

# If I were prioritizing them

## Phase 1

```
evgraph-core
```

---

## Phase 2

```
evgraph
```

---

## Phase 3

```
evgraph-adapters
```

---

## Phase 4

```
evgraph-rules
```

---

## Phase 5

```
evgraph-reporters
```

---

## Phase 6

```
evgraph-cli
```

---

## Much later

```
evgraph-context

evgraph-provenance
```

---

# My recommendation

For the **current project**, I would think of it as **six production packages plus two research packages**:

| Package              | Purpose                                          | Priority |
| -------------------- | ------------------------------------------------ | -------- |
| `evgraph-core`       | Specifications implemented in Python (EGS + RES) | ⭐⭐⭐⭐⭐    |
| `evgraph`            | Public Python API                                | ⭐⭐⭐⭐⭐    |
| `evgraph-adapters`   | Convert artifacts into an Evidence Graph         | ⭐⭐⭐⭐     |
| `evgraph-rules`      | Rule packs that evaluate evidence                | ⭐⭐⭐⭐     |
| `evgraph-reporters`  | Export findings in different formats             | ⭐⭐⭐      |
| `evgraph-cli`        | Thin command-line interface                      | ⭐⭐⭐      |
| `evgraph-context`    | Context Virtualization (research)                | 🔬        |
| `evgraph-provenance` | Cryptographic provenance (research)              | 🔬        |

**One refinement to your earlier thinking:** I would keep `evgraph-adapters`, `evgraph-rules`, and `evgraph-reporters` as **framework packages** that define extension interfaces and include a handful of built-in implementations. Individual adapters (for example, `evgraph-adapter-pandas`) or rule packs (for example, `evgraph-rule-eu-ai-act`) can become separate packages later, once the extension interfaces have stabilized through real-world use. That follows the same grounding discipline you've applied everywhere else: don't split until experience shows the boundaries are correct.
