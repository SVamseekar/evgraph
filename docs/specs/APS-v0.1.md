# Adapter Protocol Specification (APS) — Core

**Version:** 0.1 (Proposed)
**Status:** Draft — not an industry standard. This is a proposed specification for the `evgraph` open-source Python ecosystem. It is expected to change based on findings from the reference implementation.

---

## 1. Scope and Non-Goals

### 1.1 Scope

APS-Core defines the contract between an **Adapter** and the rest of the `evgraph` ecosystem: what an adapter must declare about itself, what it must produce, and how it must report failure. It specifies:

- The `Adapter` interface's required declarations (`evidence_level`, `extraction_method`, `assumptions`, `supported_source_kinds`)
- The output contract: an adapter either produces a valid `EvidenceGraph` (EGS §3.5) or raises a declared error
- The `AdapterError` model, including the interpretation/governance-deficiency distinction (§4.2)
- A minimal lifecycle

APS-Core exists to test one hypothesis: **that the interpretive judgment calls an adapter makes when converting a real artifact into evidence can be captured as structured, inspectable declarations, without requiring APS to standardize how any adapter is actually invoked.** As with EGS and RES, every concept here is included because the reference implementation's one adapter (`evgraph-adapter-modelcard`, Stage 1) concretely needed it — nothing is included on the basis of anticipated future adapters.

### 1.2 Fundamental Principle

> **Adapters interpret reality; they do not evaluate governance.**

This is APS's equivalent of EGS's evidence-over-verdicts stance and RES's confidence-inheritance invariant — each foundational spec has exactly one idea, and every other rule in that spec is a consequence of it. Concretely: an adapter's job ends at producing a faithful, evidence-leveled representation of what it observed in a source artifact. It must never decide whether what it observed is *governance-adequate* — that judgment belongs to a `Rule` (RES), and encoding it in an adapter would let a rule engine's conclusions leak backward into the layer that's supposed to be pre-judgment. §4.2 makes this a normative rule, not just a principle.

### 1.3 Non-Goals (v0.1)

| Deferred concept | Why deferred |
|---|---|
| **Invocation signature standardization** | APS-Core does not mandate what an `Adapter`'s callable (e.g. `scan(...)`) accepts as input. The reference adapter (`ModelCardArtifacts`, three named file paths) has a signature specific to what it consumes; a CSV adapter's natural signature will differ. Standardizing this with one adapter as evidence risks producing a meaningless generic parameter (`source: Any`) that hides complexity rather than resolving it. APS standardizes only declarations and the `EvidenceGraph` output — see §1.2 and §3. |
| **Adapter discovery / plugin loading / registration** | How an adapter is found, installed, or wired into a running system is PES's concern (Stage 4), not APS-Core's. APS-Core defines what a conforming `Adapter` *is*, not how one is loaded. |
| **Orchestration across heterogeneous adapters** | A higher-level API that dispatches to the right adapter for a given source (what `evgraph.scan()` may eventually do) is a concern of the `evgraph` public package, not APS-Core. APS governs the adapter/graph boundary only. |
| **Partial / degraded `EvidenceGraph` output** | v0.1 requires an adapter to either return a complete, valid `EvidenceGraph` or raise `AdapterError` — never a graph missing expected nodes with no failure signaled. No reference case demonstrates what a "partial graph" would mean structurally (Does RES still run? Does it change `EvidenceLevel`? Is a missing node different from a malformed one?). Revisit only if a concrete implementation need arises. |
| **Streaming / incremental extraction** | EGS §4 already commits to graphs being fully constructed, not incrementally built. APS-Core inherits that constraint and does not define a partial/streaming adapter lifecycle. |
| **Closed `extraction_method` taxonomy** | `extraction_method` is an open string in v0.1 (§3.1), not an enum. With exactly one adapter as evidence, any enumerated taxonomy (`DIRECT_MAPPING`, `REGEX`, `LLM_ASSISTED`, ...) would be guessed, not demonstrated. This mirrors EGS's treatment of node/edge `type` as an open string pending CVS. Revisit once a second and third adapter exist to show what categories actually recur (Stage 2 exit condition). |

If a future version of APS-Core adds any of the above, it must cite the specific reference-implementation case that required it, per §1.1.

---

## 2. Core Terminology

| Term | Definition |
|---|---|
| **Adapter** | A component that converts one or more source artifacts into nodes and edges of an `EvidenceGraph` (EGS §2). APS-Core defines what an adapter declares and produces; EGS defines the shape of what it produces. |
| **Assumption** | A structured, stably-identified statement of an interpretive judgment the adapter makes about its source (e.g., "`approved_at` is interpreted as an ISO 8601 timestamp") — see §3.2. |
| **Extraction Method** | An open, human-readable description of how an adapter derives graph structure from its source (e.g., `"direct field mapping"`). Not a closed vocabulary in v0.1 (§1.3). |
| **AdapterError** | The single, chained exception type an adapter raises when it cannot interpret its source (§4). |

Terms defined in EGS (`EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`, `EvidenceLevel`, `SourceReference`) and RES (`Rule`, `Finding`) are used here as defined there and are not redefined.

---

## 3. Adapter Model

```
Source Artifact
      │
      ▼
   Adapter
      │
      ▼
 EvidenceGraph
      │
      ▼
    Rules
```

### 3.1 Adapter Interface

```
Adapter:
    name: str                          # unique identifier, e.g. "evgraph-adapter-modelcard"
    version: str
    evidence_level: EvidenceLevel      # maximum certainty this adapter may assign to evidence it produces
    extraction_method: str             # open string, e.g. "direct field mapping" (§1.3)
    assumptions: list[Assumption]      # see §3.2
    supported_source_kinds: list[str]  # e.g. ["json"]

    <adapter-defined callable>(...) -> EvidenceGraph   # signature not standardized (§1.3)
```

- `evidence_level` is the ceiling: every `EvidenceNode` (EGS §3.4) the adapter produces must carry an `evidence_level` no more certain than this declared value. **All evidence produced by an adapter is bounded by this single, adapter-wide declaration — APS v0.1 does not define a per-node evidence-level assignment policy or permit one adapter invocation to emit nodes at differing evidence levels.** This mirrors RES's `reasoning_class` (RES §3.1) — both are epistemic ceilings declared once by the component, not computed per-invocation.
- `extraction_method` and `assumptions` exist so that a human (or, later, tooling) inspecting a graph can answer "why does this node exist, and what did the adapter assume to produce it?" without reading the adapter's source code.
- `supported_source_kinds` declares what kind(s) of source artifact the adapter is built to interpret (e.g., `["json"]`). It is descriptive metadata, not a validation mechanism APS mandates be enforced at runtime.
- The callable that performs extraction (`scan`, or any adapter-chosen name) is not part of the standardized interface — only its return contract (§3.3) and failure contract (§4) are.

### 3.2 Assumption Structure

```
Assumption:
    id: str          # stable identifier, e.g. "MC-001"
    statement: str   # human-readable statement of the interpretive judgment made
```

- Every non-trivial interpretive choice an adapter makes about its source SHOULD be recorded as an `Assumption`. Example, from the reference Model Card adapter: `Assumption(id="MC-001", statement="approved_at and deployed_at are interpreted as ISO 8601 timestamps")`.
- `id` gives assumptions a stable identity so they can be referenced elsewhere (e.g., in documentation or a future finding explanation: "this finding depends on assumption MC-001 holding"). APS-Core does not define any mechanism that consumes this reference in v0.1 — the field exists so one can be built later without changing the `Assumption` shape.
- `statement` is free-text natural language. APS-Core does not define a structured assumption schema (field/operator/constraint) — this would be designing a DSL for human reasoning, not documenting it, and has no reference case demonstrating a need.

### 3.3 Output Contract

- An adapter invocation MUST either:
  1. Return a complete, valid `EvidenceGraph` (conforming to EGS §9's conformance requirements) — every node's `evidence_level` no more certain than the adapter's declared `evidence_level` (§3.1); or
  2. Raise `AdapterError` (§4) — no `EvidenceGraph` is returned at all.
- There is no third outcome in v0.1. An adapter must not return a graph it considers incomplete or degraded without raising (§1.3).

---

## 4. Error Model

### 4.1 AdapterError

```
AdapterError(Exception):
    adapter_name: str
    adapter_version: str
    message: str
```

- `AdapterError` is the one exception type APS-Core standardizes. An adapter MUST raise `AdapterError` — not an unwrapped underlying exception (`KeyError`, `FileNotFoundError`, `json.JSONDecodeError`, etc.) — when it cannot convert its source into an `EvidenceGraph`.
- The underlying cause MUST be preserved through exception chaining (Python: `raise AdapterError(...) from exc`). This is normative, not a style preference: it keeps `AdapterError` as a stable, inspectable failure type for tooling while still preserving the original diagnostic detail for a human debugging the adapter.

### 4.2 Interpretation Failures vs. Governance Deficiencies

This is the concrete expression of §1.2's Fundamental Principle, and the single most important normative rule in this document:

> **`AdapterError` represents a failure of interpretation, not a governance deficiency in the source artifact.**

This distinction is APS-Core's identity in the same way "reasoning cannot become more certain than its evidence" is RES's — everything else in this section exists to make it concrete and enforceable.

- **Raise `AdapterError`** for: malformed input (invalid JSON), an unreadable/missing file, an unsupported schema version, or a source missing keys the adapter structurally requires to produce any graph at all.
- **Do not raise** — instead, represent as evidence — for: a source that is readable and well-formed but reports an absent or incomplete governance fact (e.g., an approval record that exists but has no `approved_at` field). This is not an adapter failure; it is exactly the kind of gap a `Rule` is positioned to reason about (RES's `INCONCLUSIVE` outcome, RES §4.2, exists for precisely this case). An adapter that raised on every missing governance fact would be making a governance judgment call it is not entitled to make — it would be quietly deciding what counts as disqualifying, which is a `Rule`'s job, not an `Adapter`'s.

### 4.3 Lifecycle

APS-Core v0.1 defines a minimal, four-step lifecycle for a conforming adapter invocation:

1. Validate that the source is well-formed enough to interpret at all.
2. Extract evidence from the source per the adapter's declared `extraction_method` and `assumptions`.
3. Construct the `EvidenceGraph` (EGS §3.5, §4 — immutable once constructed).
4. Return the graph, or raise `AdapterError` (§4.1) if step 1 or 2 could not be completed.

No hooks, callbacks, streaming steps, or plugin lifecycle events are defined. If a future adapter demonstrates a concrete need for one (e.g., incremental extraction over a very large source), that is grounds for a v0.2 change, per §1.1 — not something to design speculatively now.

---

## 5. Compatibility and Versioning Rules

- APS versions follow `MAJOR.MINOR`. v0.1 is pre-1.0: no compatibility guarantees are made between 0.x versions.
- **APS versions independently of EGS and RES.** A change to APS's `MAJOR.MINOR` does not imply, require, or signal any corresponding change to EGS or RES — the three specifications are versioned on their own timelines, since each governs a distinct layer (§1.2, `docs/ARCHITECTURE.md` §3).
- A breaking change to the `Adapter` interface or `AdapterError` model (§3, §4) requires a version bump and must cite the reference-implementation case that required it, per §1.1.
- Adapters SHOULD declare which APS version they were built against, following the same convention as `egs_version`/`res_version` (EGS §5, RES §6).

---

## 6. Conformance Requirements

An implementation conforms to APS-Core v0.1 **only if** it:

1. Exposes the declarations in §3.1 (`name`, `version`, `evidence_level`, `extraction_method`, `assumptions`, `supported_source_kinds`).
2. Never produces an `EvidenceNode` whose `evidence_level` is more certain than the adapter's declared `evidence_level`.
3. Either returns a complete, EGS-conformant `EvidenceGraph` or raises `AdapterError` — never a third outcome (§3.3).
4. Raises `AdapterError`, with the original cause chained, for interpretation failures only — never for governance deficiencies in otherwise-valid source data (§4.2).
5. Does not claim support for any item listed as a non-goal in §1.3 under the name "APS-Core."

---

## 7. Illustrative Example

The reference Model Card adapter (`evgraph-adapter-modelcard`, Stage 1) under APS-Core:

```
Adapter:
    name: "evgraph-adapter-modelcard"
    version: "0.1.0"
    evidence_level: STRUCTURAL
    extraction_method: "direct field mapping"
    assumptions: [
        Assumption(id="MC-001", statement="approved_at and deployed_at are interpreted as ISO 8601 timestamps"),
        Assumption(id="MC-002", statement="a missing intended_use field is treated as has_intended_use: false, not as an extraction failure"),
    ]
    supported_source_kinds: ["json"]
```

Given a syntactically invalid JSON file, this adapter raises:

```
AdapterError(
    adapter_name="evgraph-adapter-modelcard",
    adapter_version="0.1.0",
    message="model_card.json is not valid JSON",
) # chained from the underlying json.JSONDecodeError
```

Given a well-formed `approval.json` that omits `approved_at`, the adapter does **not** raise — it produces a `HumanApproval` node whose `attributes` dict has no `approved_at` key, per §4.2. `ApprovalPrecedesDeploymentRule` (RES §3.1) already handles exactly this case by returning a `Finding` with `outcome: INCONCLUSIVE` (RES §4.2) rather than the adapter deciding the record is unusable.

---

## Appendix A: Design Rationale

Recorded here so a future contributor proposing one of §1.3's deferred concepts finds the reasoning before re-opening the discussion:

- **Why no standardized invocation signature:** A generic `scan(source: Any)` either becomes meaningless (what is `source`? a path? a directory? a live connection?) or forces every future adapter into an unnatural shape chosen before that adapter's real requirements were known. APS-Core's contract is the `EvidenceGraph` an adapter produces, not how it's called to produce it — the same way EGS standardizes the graph, not a storage backend, and RES standardizes `Finding`, not rule scheduling (`docs/ARCHITECTURE.md` §3, "A note on specification vs. execution strategy").
- **Why no discovery/plugin mechanism:** Belongs to PES (Stage 4), once real extension points exist from Stages 2–3 to generalize from (ADR-0002).
- **Why no orchestration layer:** Dispatching to the right adapter for a given input is a composition concern for the `evgraph` public package, a layer above APS-Core (`docs/ARCHITECTURE.md` §3).
- **Why no partial/degraded graphs:** No reference case shows what a partial graph would mean for RES evaluation, `EvidenceLevel`, or graph validity (EGS §3.1's node-id/edge-reference invariants). Adding this speculatively risks the same mistake the EGS review process explicitly rejected: standardizing structure before a concrete need demonstrates its shape.
- **Why no closed `extraction_method` enum:** With one adapter as evidence, any enumeration would be guessed categories, not demonstrated ones. `extraction_method` is descriptive metadata nothing currently computes over or branches on — unlike `EvidenceLevel`, which is semantic (RES's confidence-inheritance invariant, RES §4.3, computes with it). Descriptive metadata earns a closed vocabulary only once multiple real implementations show a stable, recurring taxonomy (mirrors EGS's treatment of node/edge `type`, deferred to CVS).

## Appendix B: Open Questions for v0.2

- Does `extraction_method` converge on a stable, small set of recurring values once a second and third adapter exist (Stage 2's CSV/tabular adapter, and beyond)? If so, is a CVS-level controlled vocabulary the right home for it, or does it stay adapter-defined free text permanently?
- Does a concrete adapter ever need partial/degraded graph output, and if so, what would that mean for EGS's graph-validity invariants and RES's evaluation semantics?
- Should `Assumption.id` ever be referenced from a `Finding` (RES §4.1) to make "this finding depends on assumption X holding" explicit and traceable? No reference case requires this yet.
- Should a single adapter invocation ever be permitted to produce multiple `EvidenceGraph`s (e.g., one adapter over a large heterogeneous source producing several disjoint graphs) rather than exactly one? APS-Core v0.1 assumes one invocation produces one graph and says nothing further; no reference case has required otherwise.

---

## Related documents

- `docs/ARCHITECTURE.md` — constitution; APS-Core's Fundamental Principle (§1.2) extends the same evidence/interpretation boundary established there.
- `docs/ROADMAP.md` — Stage 2 defines what APS-Core is scoped to prove: two structurally different adapters conforming without adapter-specific carve-outs.
- `docs/specs/EGS-v0.1.md` — the `EvidenceGraph` output contract APS-Core adapters must satisfy.
- `docs/specs/RES-v0.1.md` — `reasoning_class`/`Finding.level`, the RES-side analogue of APS-Core's `evidence_level` ceiling.
