# Evident

An open specification for executable AI governance evidence, with a Python reference implementation.

Evident is not a SaaS platform or compliance dashboard. It defines the **Evidence Graph** — a canonical intermediate representation that any AI-system artifact (Model Cards, approval records, deployment logs, evaluation datasets, traces, etc.) can be converted into — and a rule-evaluation model for producing explainable, traceable findings from that graph.

Governance evidence collection, normalization, and consistency-checking are computable. Legal/regulatory *interpretation* is not — Evident stops at the evidence boundary and never issues compliance verdicts. See `docs/specs/RES-v0.1.md` (once written) for how findings are leveled to make that boundary explicit and enforced in the type system, not just documented.

## Status

**Stage 0 (Foundational Specifications) — complete. Entering Stage 1 (Reference Implementation).**

EGS v0.1 (`docs/specs/EGS-v0.1.md`) and RES v0.1 (`docs/specs/RES-v0.1.md`) are drafted. `docs/ARCHITECTURE.md` records the project's constitution and decision log. Next: one adapter, one rule, one reporter, built against these two specs — see `docs/ROADMAP.md` for the full capability-staged plan (Stage 0 through Stage 5) and each stage's exit condition.

## Why specs before code

Foundational abstractions (Type A: EGS, RES, APS-Core) get specified before implementation because downstream design has a hard dependency on them being fixed — you cannot design a confidence model without first knowing how evidence enters the graph with what epistemic status.

Emergent abstractions (Type B: plugin hooks, reporter contracts, extension points) get *extracted from working code*, not designed in advance — they only benefit from consistency once real patterns exist, and speculative design here is the most likely source of an expensive early rewrite.

Every concept in a spec must be justified by a concrete use case in the reference implementation. Nothing goes in because it might be needed later — see each spec's Non-Goals section.

## Repository layout

```
evident/
  docs/
    specs/          # EGS, RES, APS, RPS, PES, CVS — written in that dependency order
  reference/
    python/
      evident-core/  # foundational abstractions only, once code starts
      evident/       # public API surface (pip install evident)
  examples/
```

No `context/`, `provenance/`, `adapters/`, or CLI packages exist yet. Those are future work, contingent on the two core hypotheses holding up under a reference implementation:

1. The Evidence Graph is a useful canonical representation across heterogeneous AI-system artifacts.
2. Rules can consume that graph and produce explainable, traceable findings without claiming interpretive/legal authority they don't have.

## Core terminology (subject to CVS once written)

- **Evidence Graph** — immutable, directed acyclic graph produced by adapters from source artifacts.
- **EvidenceNode / EvidenceEdge** — typed, evidence-leveled facts and relationships within the graph.
- **Evidence Level** — `STRUCTURAL → CONSISTENCY → HEURISTIC → INTERPRETIVE`, set at the adapter/node level and only ever lowered, never raised, by downstream findings.
- **Finding** — a rule's output over the graph, leveled per the hierarchy above, never a bare PASS/FAIL.

## Next step

Review `docs/specs/EGS-v0.1.md`, then draft RES v0.1 (rule inputs, `Finding` structure with the leveled hierarchy formalized as a type invariant, confidence-inheritance rule from evidence levels).
