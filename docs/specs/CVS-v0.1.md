# Compliance Vocabulary Specification (CVS)

**Version:** 0.1 (Proposed)
**Status:** Draft — assembled, not designed. Per `docs/ROADMAP.md` Stage 4, CVS is compiled from terminology that has already stabilized (used consistently and unambiguously) across EGS, RES, APS-Core, RPS, and PES, once those five documents existed to draw from. It defines no new concepts — every entry below cites the spec that already defines it.

---

## 1. Scope and Non-Goals

### 1.1 Scope

CVS is a single cross-reference of terminology already defined across EGS/RES/APS-Core/RPS/PES, so a reader doesn't have to search five documents to find where a term comes from and what it means. It exists to answer: **when a term appears in this project, which specification is authoritative for it, and what does it actually mean?**

CVS does not introduce new vocabulary, new invariants, or new structures. Every definition below is a restatement (not a reinterpretation) of the source specification's own definition, with a citation back to it.

### 1.2 Non-Goals (v0.1)

| Deferred concept | Why deferred |
|---|---|
| **A closed vocabulary for node/edge `type` strings** | EGS §1.2/Appendix explicitly keeps node and edge `type` as open strings, pending a demonstrated recurring taxonomy across multiple rule packs and adapters. No such taxonomy has stabilized yet — CVS does not manufacture one. |
| **A closed vocabulary for `extraction_method`** | APS-Core §1.3/Appendix A keeps `extraction_method` an open string for the same reason — one data point (soon two: Model Card and dataset-manifest adapters) is not enough to know the real recurring categories. |
| **Regulatory/jurisdictional terminology (EU AI Act, GDPR, ISO 42001, etc.)** | No rule pack for any specific regulatory regime exists yet (that's Stage 5's Research Track, contingent on Stage 3's rule-pack packaging model). CVS v0.1 only compiles Evgraph's own architectural vocabulary, not any external regulatory vocabulary Evgraph might later help express. |
| **`Requirement` / `Assessment` / `Control` / `Obligation`** | RES §1.3 defers this whole cluster of terms; per `docs/ARCHITECTURE.md` ADR-0006, no evidence yet justifies picking one name over another, since no abstraction has been shown to be needed at all. CVS cannot standardize a term for a concept that doesn't exist. |

If a future version of CVS adds any of the above, it must cite the specification (or, for regulatory terms, the rule pack) whose stabilized usage justifies it.

---

## 2. Vocabulary

Organized by originating specification, in the dependency order they were written (`docs/ROADMAP.md` Stage 0–4).

### 2.1 From EGS (Evidence Graph Specification)

| Term | Definition | Source |
|---|---|---|
| **Evidence Graph** | An immutable, directed acyclic graph produced by one or more adapters from one or more source artifacts. | EGS §2 |
| **EvidenceNode** | A single observed fact or artifact reference within the graph. | EGS §2, §3.2 |
| **EvidenceEdge** | A directed, typed relationship between two nodes. | EGS §2, §3.3 |
| **Evidence Level** | The epistemic status a node was produced under: `STRUCTURAL → CONSISTENCY → HEURISTIC → INTERPRETIVE`, ordered most to least certain. Set by the adapter that produced the node. | EGS §3.4 |
| **Source Reference** | A pointer from a node back to the raw artifact/location it was derived from, for traceability. Adapter-defined shape in v0.1 — not standardized. | EGS §2, Appendix |
| **Snapshot** | One complete, immutable Evidence Graph as returned by a single `scan()` (or equivalent) call. | EGS §2 |
| **Adapter** (structural sense) | A component that converts an external artifact into nodes and edges. EGS defines only what an adapter produces; APS-Core defines the adapter contract itself. | EGS §2 |
| **Trace** (operation) | `trace(node_id)`: the edge path connecting a node back to its root ancestor(s). One of four guaranteed traversal operations, alongside `neighbors`, `ancestors`, `descendants`. | EGS §6 |

### 2.2 From RES (Rule Evaluation Specification)

| Term | Definition | Source |
|---|---|---|
| **Rule** | A pure function that evaluates an `EvidenceGraph` and produces zero or more `Finding`s. | RES §2, §3.1 |
| **Reasoning Class** | An `EvidenceLevel` declared by a rule, representing the strongest epistemic claim its reasoning *process* can support — independent of the evidence level of the nodes it cites. | RES §2, §3.1 |
| **Finding** | A rule's output: a traceable, evidence-cited statement of what was observed, together with whether it matches the rule's own declared expectation. Never a verdict. | RES §2, §4.1 |
| **Outcome** | One of `EXPECTATION_MET`, `EXPECTATION_NOT_MET`, `INCONCLUSIVE`. Expresses agreement with the rule's own expectation, never compliance with an external standard. | RES §2, §4.2 |
| **Confidence-Inheritance Invariant** | `Finding.level` is always computed — never declared by a rule author — as the least-certain value among the rule's `reasoning_class` and the evidence levels of every node it cites. A finding can never be presented as more certain than either its evidence or its reasoning method. | RES §4.3 |

### 2.3 From APS-Core (Adapter Protocol Specification)

| Term | Definition | Source |
|---|---|---|
| **Adapter** (protocol sense) | A component with declared `name`, `version`, `evidence_level`, `extraction_method`, `assumptions`, and `supported_source_kinds`, that either returns a valid `EvidenceGraph` or raises `AdapterError`. | APS-Core §2, §3.1 |
| **Assumption** | A structured, stably-identified statement (`id`, `statement`) of an interpretive judgment an adapter makes about its source. | APS-Core §2, §3.2 |
| **Extraction Method** | An open, human-readable description of how an adapter derives graph structure from its source (e.g., `"direct field mapping"`, `"csv column mapping"`). Not a closed vocabulary in v0.1. | APS-Core §2, §3.1 |
| **AdapterError** | The single, chained exception type an adapter raises when it cannot *interpret* its source — never raised for a source that is well-formed but reports an absent or incomplete governance fact (that is evidence, handled by `Outcome.INCONCLUSIVE`, not an adapter failure). | APS-Core §2, §4 |

### 2.4 From RPS (Reporting Protocol Specification)

| Term | Definition | Source |
|---|---|---|
| **Reporter** | A pure function (or small module of functions) taking `(EvidenceGraph, list[Finding])` and producing output in some target format. RPS does not standardize the function's name or return type. | RPS §2, §3.1 |
| **Translation, not invention** | A reporter may map `Finding` fields into its target format's own vocabulary (e.g., SARIF's `level`), but only as a deterministic function of fields RES already defines — never introducing governance semantics (severity, risk, compliance judgment) RES doesn't expose. | RPS §3.2.3 |

### 2.5 From PES (Plugin & Extension Specification)

| Term | Definition | Source |
|---|---|---|
| **Entry point group** | A named group (`"evgraph.rules"`) under which installed packages register importable `Rule` implementations, via Python's standard `importlib.metadata` entry_points mechanism. | PES §2, §3.1 |
| **Discovery** | Enumerating every entry point registered under `"evgraph.rules"` across all installed packages and instantiating each — the mechanism that lets a third-party rule pack affect `scan()` output purely by being installed. | PES §2, §3.2 |

---

## 3. What Has Not Stabilized (and is deliberately absent from this vocabulary)

Per §1.2, several terms appear in this project's history but are explicitly **not** part of CVS v0.1 because no specification has stabilized a definition for them:

- **Verdict** — appears in the superseded `architecture.md`/`docs/ARCHITECTURE-2.md`, replaced by the leveled `Finding`/`Outcome` model (`docs/ARCHITECTURE.md` ADR-0003). Not part of current vocabulary.
- **Requirement, Assessment, Control, Obligation** — RES §1.3, deferred; see §1.2 above.
- **Severity, Risk, Confidence (as a scalar)** — explicitly rejected in favor of the `EvidenceLevel` hierarchy (`docs/ARCHITECTURE.md` §2, "Bounded Certainty"; RES ADR-0005). Not part of current vocabulary, and not expected to become part of it — this is a permanent boundary (`docs/ARCHITECTURE.md` §5), not a pending term.

---

## 4. Compatibility and Versioning Rules

- CVS versions independently of EGS, RES, APS, RPS, and PES (same independence rule established in APS-Core §5, RPS §4, PES §4).
- CVS is definitionally downstream of the other five specs: a term cannot be added to CVS before it has stabilized in whichever specification actually owns it. A CVS change never originates a new term — it only reflects one that already exists elsewhere.

---

## 5. Conformance Requirements

A document or implementation conforms to CVS v0.1 if, wherever it uses a term listed in §2, it uses that term consistently with the definition and source cited there — and does not use any term listed in §3 as though it denoted a stabilized concept.

---

## Related documents

- `docs/ARCHITECTURE.md` — the constitution and decision log (ADR-0003, ADR-0005, ADR-0006) several §3 entries cite.
- `docs/ROADMAP.md` — Stage 4 defines when CVS is assembled and from what.
- `docs/specs/EGS-v0.1.md`, `RES-v0.1.md`, `APS-v0.1.md`, `RPS-v0.1.md`, `PES-v0.1.md` — the five specifications this vocabulary is compiled from; each remains authoritative for its own terms.
