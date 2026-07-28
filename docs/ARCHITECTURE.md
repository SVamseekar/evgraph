# Evident — Architecture

**Status:** Living document. This is the constitution of the project — the thing every specification, package, and design decision must be justifiable against. It changes rarely and only through a recorded decision (§6).

For current project status, sequencing, and what's implemented so far, see `README.md` — that document is expected to change often. This one is not.

---

## 1. Mission

Evident is an open-source Python ecosystem for executable governance engineering. Its purpose is to transform governance artifacts into a common evidence representation that can be evaluated, traced, and reported through deterministic, explainable software components.

Evident evaluates evidence. It does not issue legal or regulatory judgment. Every other statement in this document is a consequence of that sentence.

---

## 2. Philosophy

### Evidence over Verdicts

The project never claims legal or regulatory compliance. It reports what evidence exists, what's missing, and what's inconsistent — leveled by how much interpretation was required to produce it (`STRUCTURAL → CONSISTENCY → HEURISTIC → INTERPRETIVE`, defined in EGS). A finding may never report higher certainty than the evidence it's built from.

### Specifications Before Frameworks

Foundational abstractions — ones later design has a hard dependency on — are specified before they're implemented. Abstractions that only benefit from consistency once patterns exist are extracted from a working reference implementation, not designed in advance. See ADR-0002.

### Grounding Discipline

Nothing enters a specification because it "might be useful." Every concept in a spec must be justified by a concrete, demonstrated need in the reference implementation. An unjustified concept is deferred and recorded as a non-goal, not speculatively designed.

### Developer First

Value within minutes, not after configuration. No YAML required to get a first result. The Python API is the primary surface; the CLI is a thin wrapper over it, never the other way around.

### Explainability

Every finding must be traceable back through the graph to the evidence it depends on. A finding with no traceable evidence chain is not a valid finding.

### Determinism

Given the same Evidence Graph and the same rule version, a rule produces the same finding every time. Non-deterministic evaluation (e.g., an LLM-based rule) must declare itself as such and is bounded to `HEURISTIC` evidence level at most — never `STRUCTURAL` or `CONSISTENCY`.

### Bounded Certainty

A finding's evidence level is bounded by the weakest evidence level among the nodes it cites. Combining a `STRUCTURAL` fact with an `INTERPRETIVE` one produces at best an `INTERPRETIVE` finding. This is not the same as "certainty only decreases" — a `CONSISTENCY`-level finding can be more severe or more actionable than either source fact alone; it just can't be more certain than its weakest input.

---

## 3. Layered Architecture

Dependencies flow one direction only, top to bottom. A layer may depend on layers below it; it may never be depended on by a layer below it, and it may never reach sideways into a layer it doesn't own.

```
──────────────────────────────────────────
 Community Plugins (adapters, rule packs,
 reporters, context providers — external)
──────────────────────────────────────────
 CLI · Python API (`evident`) · Rule Packs
 · Reporters
──────────────────────────────────────────
 APS — Adapter Protocol
──────────────────────────────────────────
 RES — Rule Evaluation
──────────────────────────────────────────
 EGS — Evidence Graph
──────────────────────────────────────────
 evident-core (graph, node, edge, evidence
 level — foundational types only)
──────────────────────────────────────────
```

`evident-core` depends on nothing else in this stack. Every other layer depends, directly or transitively, on `evident-core`. A change that would require a lower layer to know about a higher layer (e.g., `evident-core` importing something from `evident-rules`) is a violation of this architecture, not a pragmatic exception — see the Decision Log (§13) if such a change ever seems necessary.

### A note on specification vs. execution strategy

RES's `Rule.evaluate(graph)` interface (RES §3.1) gives every rule the complete graph, with no built-in subscription, node-type filtering, or indexing mechanism. This is deliberate, not an oversight: **RES specifies evaluation semantics, not execution strategy.** An engine built on top of RES is free to optimize how rules actually run — indexing, graph slicing, incremental evaluation, cached traversals, parallel execution — without any of that touching the `Rule` interface itself. If performance at scale ever demands it, the optimization belongs in an engine/APS layer above RES, not in a change to what a rule receives.

---

## 4. Design Principles

Numbered because they are meant to be cited by number in code review and ADRs, not because there's a strict ordering.

1. Adapters interpret reality; they are the only layer permitted to make a judgment call about what a raw artifact means. Every adapter declares its `evidence_level` and assumptions for what it produces (APS-Core).
2. The Evidence Graph represents *interpreted* evidence, not raw data. It is not a claim of ground truth — it is a claim about what an adapter observed.
3. Rules never mutate the Evidence Graph. A rule reads a graph and produces findings; it does not write back to the graph it read.
4. Rules are deterministic given a fixed graph and rule version (see Determinism, §2).
5. Findings are evidence-centric: every finding cites the specific nodes/edges it depends on (§2, Explainability).
6. Reports never invent evidence. A reporter formats findings; it does not add claims that don't trace back to a finding.
7. A finding's evidence level is bounded by its weakest cited source (§2, Bounded Certainty).
8. Specifications for emergent (Type B) concerns evolve from a working reference implementation, not from speculation (§2, Specifications Before Frameworks; ADR-0002).
9. Every abstraction added to a specification must be grounded in a demonstrated implementation need (§2, Grounding Discipline).
10. The ecosystem grows through extensions (new adapters, rule packs, reporters as independent packages), not through added complexity in `evident-core`. If a feature request would grow core, the default answer is "make it a plugin," not "add it to core."

---

## 5. What Evident Is Not

Explicit non-goals, to prevent scope creep from ever being adjudicated ad hoc:

- Not a legal expert system or compliance certification authority.
- Not a hosted SaaS product or compliance dashboard.
- Not a workflow orchestrator or Kubernetes admission controller.
- Not a document management system.
- Not a replacement for MLflow, OpenTelemetry, or similar observability/experiment-tracking tools — Evident integrates with these via adapters, it does not compete with them.
- Not an LLM wrapper. Where LLM-based evaluation exists (e.g., a heuristic rule using an LLM judge), it is explicitly bounded to `HEURISTIC` evidence level and clearly opt-in, never the default evaluation path.

If a proposed feature falls into one of these categories, it belongs in a separate, clearly-labeled integration or downstream project — not in `evident-core`, EGS, or RES.

---

## 6. Decision Log (ADRs)

Architectural decisions are recorded here as they're made, so debates aren't re-litigated and the *why* survives past the conversation that produced it. Format: number, decision, reasoning, alternatives considered, status.

### ADR-0001 — Evidence Graph as the canonical intermediate representation

**Decision:** All external artifacts are converted to a graph of typed, evidence-leveled nodes and edges (EGS) before any rule evaluates them. No rule evaluates raw source data directly.

**Reasoning:** A single IR decouples adapters from rules — N adapters and M rule packs need N+M integrations instead of N×M. Mirrors Arrow/OpenTelemetry's approach to the same N×M problem in their respective domains.

**Alternatives considered:** Rules operating directly on source-specific formats (rejected — doesn't scale past a handful of adapters); a relational/tabular model instead of a graph (rejected — governance evidence is fundamentally relational/lineage-shaped: approvals reference models, models reference datasets; a graph represents that natively).

**Status:** Accepted.

### ADR-0002 — Specifications precede implementation only for foundational (Type A) concerns

**Decision:** EGS and RES (and APS-Core) are specified before the reference implementation is built. APS-Extensions, RPS, and PES are extracted from the reference implementation after it exists, not designed in advance.

**Reasoning:** Foundational concerns have downstream design that hard-depends on them being fixed first (e.g., RES's confidence model requires EGS's evidence-level scheme to already exist). Emergent concerns (plugin hooks, reporter contracts) only benefit from consistency once real usage patterns exist to generalize from; designing them first risks specifying the wrong abstraction and having to break it later.

**Alternatives considered:** Spec all six documents (EGS, RES, APS, RPS, PES, CVS) before any code (original plan) — rejected as premature generalization at the project-planning level, the same failure mode EGS's own non-goals discipline (§2) guards against at the schema level.

**Status:** Accepted.

### ADR-0003 — Findings use a leveled evidence hierarchy, never bare PASS/FAIL

**Decision:** `Finding` (RES) carries an `evidence_level` (`STRUCTURAL`/`CONSISTENCY`/`HEURISTIC`/`INTERPRETIVE`) and status vocabulary describing evidence state (e.g., complete/missing/inconsistent/unverifiable), not a boolean compliance verdict.

**Reasoning:** A rule engine can verify that evidence exists or is internally consistent; it cannot verify that a legal or regulatory judgment was correct. Conflating the two (via PASS/FAIL language) misrepresents what the tool actually did and is a credibility risk the moment a "PASS" is challenged by a domain expert. This directly implements the Mission (§1) and Evidence over Verdicts principle (§2).

**Alternatives considered:** PASS/FAIL/WARN status with a separate confidence score (original architecture.md draft) — rejected because the level of interpretation involved is orthogonal to confidence, and a high-confidence interpretive judgment is still not something the tool is authorized to assert as fact.

**Status:** Accepted.

### ADR-0005 — Separate evidence certainty from rule reasoning certainty

**Status:** Accepted.

**Context:** Early RES designs assumed a finding's epistemic level could be derived solely from the `EvidenceLevel` (EGS §3.4) of the evidence nodes it cited. During specification work, it became clear this was insufficient: a rule may perform reasoning whose certainty is lower than the certainty of its input evidence — for example, a temporal-consistency check, a heuristic pattern match, or an interpretive analysis, all of which can operate over purely `STRUCTURAL` nodes while introducing their own epistemic weakness. Deriving `Finding.level` from evidence nodes alone would misclassify such findings as more objective than the reasoning process actually permits.

**Decision:** Rules declare a `reasoning_class` (RES §3.1) — an `EvidenceLevel` representing the epistemic ceiling of the rule's *reasoning method*, independent of what it cites. `Finding.level` (RES §4.3) is always computed, never declared directly by a rule author, as the least-certain value among the rule's `reasoning_class` and the evidence levels of every node it cites. A finding may never be represented as more certain than either its supporting evidence or the reasoning process used to derive it.

**Consequences:** Separates evidence certainty from reasoning certainty as two independent inputs to a finding's level. Prevents heuristic or interpretive rules from emitting findings that read as structural. Preserves the evidence-centric philosophy (§2) without conflating observation and inference. Extends Bounded Certainty (§2) and ADR-0003 into a concrete, computed type invariant rather than a convention.

**Alternatives considered:** Deriving `Finding.level` from cited evidence nodes only (rejected — see Context above, this is the flaw the decision corrects).

### ADR-0004 — Evidence Graph snapshots are immutable; no in-place mutation or versioning in v0.1

**Decision:** A constructed `EvidenceGraph` is never modified after construction. Combining evidence from multiple adapters happens by merging node/edge lists at construction time into one new graph, not by mutating an existing one.

**Reasoning:** Immutability keeps traceability simple — a `Finding` can always cite "the graph as of `graph_id`" without ambiguity about whether the graph changed underneath it. Versioning/diffing across snapshots is deferred (EGS §1.2) until a concrete use case (e.g., comparing two scans over time) demonstrates what it actually needs to support.

**Alternatives considered:** Mutable graph with an in-place update API — rejected for v0.1 as unjustified by any current reference use case; revisit only per the Grounding Discipline (§2) if one emerges.

**Status:** Accepted.

---

## Related documents

- `README.md` — mission summary, current status, roadmap (changes frequently; not authoritative on principles — this document is).
- `docs/specs/EGS-v0.1.md` — Evidence Graph Specification.
- `docs/specs/RES-v0.1.md` — Rule Evaluation Specification (not yet written).
- `architecture.md` (repo root) — the original pre-critique blueprint. Superseded by this document; kept for project history, not as a source of current principles.
