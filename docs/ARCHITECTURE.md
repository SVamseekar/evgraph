# Evgraph — Architecture

**Status:** Living document. This is the constitution of the project — the thing every specification, package, and design decision must be justifiable against. It changes rarely and only through a recorded decision (§6).

For current project status, sequencing, and what's implemented so far, see `README.md` — that document is expected to change often. This one is not.

---

## 1. Mission

Evgraph is an open-source Python **library ecosystem** for executable governance engineering. Its purpose is to transform governance artifacts into a common evidence representation that can be evaluated, traced, and reported through deterministic, explainable software components that people install and run in their own environments.

The product is libraries (`evgraph-core`, `evgraph-rules`, `evgraph`, `evgraph-cli`)—not a hosted service, dashboard, or certification authority.

Evgraph evaluates evidence. It does not issue legal or regulatory judgment. A missing approval timestamp stays inconclusive. The scan does not invent the field. EU AI Assurance OS pins `evgraph-cli==0.1.2` so the evidence pack and a live scan report the same current gap. Every other statement in this document is a consequence of that boundary.

---

## 2. Philosophy

### Evidence over Verdicts

The project never claims legal or regulatory compliance. It reports what evidence exists, what's missing, and what's inconsistent — leveled by how much interpretation was required to produce it (`STRUCTURAL → CONSISTENCY → HEURISTIC → INTERPRETIVE`, defined in EGS). A finding may never report higher certainty than the evidence it's built from.

### Specifications Before Frameworks

Foundational abstractions — ones later design has a hard dependency on — are specified before they're implemented. Abstractions that only benefit from consistency once patterns exist are extracted from working library code, not designed in advance. See ADR-0002.

### Grounding Discipline

Nothing enters a specification because it "might be useful." Every concept in a spec must be justified by a concrete, demonstrated need in the shipped libraries. An unjustified concept is deferred and recorded as a non-goal, not speculatively designed.

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
 CLI · Python API (`evgraph`) · Rule Packs
 · Reporters
──────────────────────────────────────────
 APS — Adapter Protocol
──────────────────────────────────────────
 RES — Rule Evaluation
──────────────────────────────────────────
 EGS — Evidence Graph
──────────────────────────────────────────
 evgraph-core (graph, node, edge, evidence
 level — foundational types only)
──────────────────────────────────────────
```

`evgraph-core` depends on nothing else in this stack. Every other layer depends, directly or transitively, on `evgraph-core`. A change that would require a lower layer to know about a higher layer (e.g., `evgraph-core` importing something from `evgraph-rules`) is a violation of this architecture, not a pragmatic exception — see the Decision Log (§13) if such a change ever seems necessary.

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
10. The ecosystem grows through extensions (new adapters, rule packs, reporters as independent packages), not through added complexity in `evgraph-core`. If a feature request would grow core, the default answer is "make it a plugin," not "add it to core."

---

## 5. What Evgraph Is Not

Explicit non-goals, to prevent scope creep from ever being adjudicated ad hoc:

- Not a legal expert system or compliance certification authority.
- Not a hosted SaaS product or compliance dashboard.
- Not a workflow orchestrator or Kubernetes admission controller.
- Not a document management system.
- Not a replacement for MLflow, OpenTelemetry, or similar observability/experiment-tracking tools — Evgraph integrates with these via adapters, it does not compete with them.
- Not an LLM wrapper. Where LLM-based evaluation exists (e.g., a heuristic rule using an LLM judge), it is explicitly bounded to `HEURISTIC` evidence level and clearly opt-in, never the default evaluation path.

If a proposed feature falls into one of these categories, it belongs in a separate, clearly-labeled integration or downstream project — not in `evgraph-core`, EGS, or RES.

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

### ADR-0006 — Multiplicity alone does not justify an abstraction; shared semantics do

**Decision:** The existence of multiple instances of something (multiple adapters, multiple rules, multiple rule packs) is not, by itself, grounds for introducing a new abstraction to group or standardize them. An abstraction is justified only once multiple instances demonstrate a **shared semantic**, not merely shared multiplicity.

**Context:** Stage 3 made a first resolution attempt at RES's deferred Requirement/Assessment aggregation question (RES §1.3, RES Appendix), now that `evgraph-rules` exists as a real, independently-versioned package containing two rules (`approval-precedes-deployment`, `dataset-manifest-complete`). The two rules evaluate entirely unrelated governance artifacts — deployment/approval workflow versus dataset metadata — and share nothing beyond both implementing `Rule` (RES §3.1). No natural "Requirement" grouping emerged between them. This is a useful negative result, not an absence of one: it shows that "belongs to the same rule pack" is not, by itself, a meaningful aggregation boundary.

**Reasoning:** Contrast with the two cases where an abstraction *was* justified: two structurally different adapters (Model Card/JSON, dataset-manifest/CSV) shared a genuine contract — every adapter converts a source into an `EvidenceGraph` and must declare `evidence_level`/`assumptions`/etc. — which is why APS-Core (ADR-0002) was justified after only two instances. Two rules sharing only "both are rules" is a weaker relationship than that, and doesn't warrant a `Requirement` type. The distinguishing question is not "how many are there?" but "what do they actually share beyond their common interface?"

**Consequences:** RES's Requirement/Assessment aggregation remains deferred (RES Appendix). The concrete trigger for revisiting it is sharper than "multiple rule packs exist": it is multiple rules demonstrably evaluating one externally identifiable obligation (e.g., several rules that together check one named regulatory article). This principle generalizes beyond RES — it is the same reasoning that should be applied before introducing any future grouping abstraction in this project (e.g., before Stage 4's PES asks whether adapters, rules, and reporters need a common plugin metadata shape).

**Alternatives considered:** Introducing a minimal `Requirement` type now, grouping the two existing rules under invented labels — rejected as manufacturing a grouping neither rule's design implies, purely to have an artifact to show; exactly the speculative-design failure mode the Grounding Discipline (§2) exists to prevent.

**Status:** Accepted.

### ADR-0007 — Evgraph is a reference runtime model, not a proposed replacement for existing governance standards

**Decision:** Evgraph positions itself as a reference implementation and architecture exploring executable governance evidence — not as a proposed industry-wide interoperability standard. Existing standards (e.g., OSCAL) are treated as interoperability *targets* where a concrete integration is demonstrated (e.g., an OSCAL reporter, analogous to the existing SARIF reporter), not as competitors EGS/RES need to replace or as prior art that invalidates EGS/RES's internal model. Any claim that Evgraph solves a genuine N×M interoperability problem, or that ecosystem-wide adoption is likely, remains an explicit **hypothesis** — not a stated goal — until demonstrated by an independent third-party adopter.

**Context:** Two research documents (`docs/research/standards-comparison.md`, `docs/research/practitioner-and-market-check.md`) were produced to stress-test the project's founding premise against real prior art and real market/practitioner evidence, rather than assuming it. Findings:

1. **Technical comparison** (OSCAL, PROV-O, OpenLineage, read from primary sources — actual metaschemas/specs, not secondary summaries): none of the three duplicates EGS/RES's core contribution. OSCAL's `observation`/`finding`/`risk` model and PROV-O have no analog to `EvidenceLevel` or RES's computed confidence-inheritance invariant (RES §4.3) — that part of the design is not redundant with existing standards. OSCAL's assessment-results layer is however a credible *export target*: `EvidenceGraph → Findings → OSCAL assessment-results`, built the same way as the existing JSON/Markdown/SARIF reporters (translation, not invention, per RPS §3.2.3).
2. **Practitioner/market check**: where a single-owner, regulated discipline solving essentially this problem already exists (banking's Model Risk Management under SR 11-7 since 2011), mature commercial tooling (ValidMind, MathWorks Modelscape) already does close to what Evgraph proposes, with far more deployed history. Where AI governance ownership is fragmented (no single owner across legal/compliance/ML-eng), the practitioner-reported failure mode is documentation never being produced at all (60%+ of Hugging Face models ship with no model card) and real enforcement actions tracing to substantive harms, not to missing structured evidence format.
3. **The N×M interoperability claim underlying ADR-0001's Arrow/OpenTelemetry framing is not yet demonstrated.** With two adapters and two rules, no independent third party has hit a redundant-integration problem Evgraph solves. This is recorded plainly as an open, unresolved question — not glossed over as if it were already true.

**Reasoning:** The architecture (EGS/RES/APS-Core/RPS/PES/CVS and the reference implementation) is validated on its own terms: internally consistent, non-redundant with existing standards, and functionally demonstrated end-to-end (49 tests, working CLI, working third-party plugin discovery). What is *not* validated is the market/adoption thesis in the original `architecture.md`/README framing ("become the foundational Python ecosystem for Computational Governance," modeled explicitly on Arrow/OpenTelemetry's adoption trajectory). Conflating "the architecture is sound" with "this will become adopted infrastructure" would overstate what's actually been shown. Per the Grounding Discipline (§2) already applied to every technical decision in this project, the same discipline should apply to the project's own strategic claims about itself: don't assert market necessity that hasn't been demonstrated, any more than a spec should assert structure that hasn't been demonstrated.

**Consequences:** `README.md`'s framing changes from ecosystem-aspiration language to reference-implementation language (see the README diff accompanying this ADR). This does not change EGS/RES/APS-Core/RPS/PES/CVS or any code — it changes how the project describes its own validation status. Future claims of ecosystem necessity or industry adoption should cite an independent adopter, the same way a structural spec change must cite a concrete reference-implementation case (§1.1 pattern, applied to strategy instead of schema).

**Alternatives considered:** Leaving the original ecosystem-adoption framing unchanged on the theory that "infrastructure sometimes precedes its buyer" (true of Arrow/OpenTelemetry/LLVM historically) — not rejected as false, but rejected as a claim that cannot currently be distinguished from wishful thinking without evidence either way; the honest position is "hypothesis, not demonstrated," not "probably true because other projects did it."

**Status:** Accepted.

---

## Related documents

- `README.md` — mission summary, current status (changes frequently; not authoritative on principles — this document is).
- `docs/ROADMAP.md` — capability-staged plan from the current state to the full ecosystem, gated by exit conditions rather than dates.
- `docs/specs/EGS-v0.1.md` — Evidence Graph Specification.
- `docs/specs/RES-v0.1.md` — Rule Evaluation Specification.
- `docs/research/standards-comparison.md` — technical comparison against OSCAL, PROV-O, OpenLineage; grounds ADR-0007.
- `docs/research/practitioner-and-market-check.md` — practitioner/market validation check; grounds ADR-0007.
- `architecture.md` (repo root) — the original pre-critique blueprint. Superseded by this document; kept for project history, not as a source of current principles.
