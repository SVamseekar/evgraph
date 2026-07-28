# Evident — Roadmap

**Status:** Living document, expected to change as the project learns. Structured as capability stages, not dates — per `docs/ARCHITECTURE.md` §2 (Specifications Before Frameworks) and ADR-0002, later stages are deliberately underspecified until earlier stages produce the evidence needed to design them.

Each stage lists an **exit condition** — what must be true before moving to the next stage. A stage is not "done when the code is written," it's done when its exit condition holds.

For the principles governing *why* this order was chosen, see `docs/ARCHITECTURE.md` (constitution). For what's true *right now*, see `README.md`. This document is the path connecting the two, from basic to advanced.

---

## Stage 0 — Foundational Specifications *(current stage)*

**What exists:**
- `docs/ARCHITECTURE.md` — constitution: mission, principles, layered architecture, non-goals, decision log
- `docs/specs/EGS-v0.1.md` — Evidence Graph Specification
- `docs/specs/RES-v0.1.md` — Rule Evaluation Specification

**What doesn't exist yet:** any code. `reference/python/` is empty.

**Exit condition:** EGS and RES are stable enough that a reference implementation can be built against them without expecting to rewrite their core structural model mid-implementation. ("Stable enough" does not mean "frozen" — open questions listed in each spec's appendix are expected to remain open until Stage 1 answers them with real evidence.)

**You are here.**

---

## Stage 1 — Reference Implementation

**Goal:** Prove the two hypotheses stated in `README.md`:
1. The Evidence Graph is a useful canonical representation across heterogeneous AI-system artifacts.
2. Rules can consume that graph and produce explainable, traceable findings without claiming interpretive/legal authority they don't have.

**Scope — deliberately minimal, one of each:**
- `evident-core` — the foundational types from EGS/RES (`EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`, `EvidenceLevel`, `Rule`, `Finding`) as actual Python code, nothing else.
- **One adapter** (e.g., a Model Card / JSON adapter — simple enough to not need APS-Core speculation, concrete enough to exercise `evidence_level` declaration and `SourceReference`).
- **One rule pack, one rule** — the `approval-precedes-deployment` example already worked out in RES §10 is the natural first candidate, since its `reasoning_class`/`Finding.level` computation is already fully specified there.
- **One reporter** — plain JSON output matching each spec's serialization format (EGS §5, RES §6). No HTML/PDF/SARIF yet — those belong to Stage 3.
- `evident` — the thin public package wrapping the above (`from evident import scan`).

**Explicitly not in scope for this stage:** APS as a written spec (it's extracted *from* this work, per ADR-0002), a CLI, any second adapter or rule, performance optimization of any kind.

**Exit condition:** `scan()` on a real artifact produces a `Finding` whose `level` is computed correctly per RES §4.3, is traceable back through EGS `trace()`, and required no change to EGS/RES's structural model to build — only, at most, resolution of an already-tracked open question (e.g., the Observation-vs-Evidence question in EGS's appendix). If building this *does* force a structural change to EGS or RES, that change is recorded as a new ADR before proceeding, not silently absorbed into the code.

---

## Stage 2 — Adapter Protocol, Grounded

**Goal:** Write APS-Core from what Stage 1's adapter actually needed — not from imagination.

**Scope:**
- `docs/specs/APS-v0.1.md` (Core only): the `Adapter` interface, required declarations (`evidence_level`, `assumptions`, `extraction_method` — as discussed in the original design conversation), lifecycle, error handling.
- A **second adapter**, deliberately of a different shape than the first (e.g., a tabular/CSV or Pandas adapter instead of a document/JSON one), built against the new APS-Core spec to pressure-test that it generalizes beyond the one shape Stage 1 proved.
- A **second rule**, to pressure-test that `Rule`/`Finding` (RES) generalizes beyond the one example already worked out.

**Exit condition:** Two structurally different adapters both conform to APS-Core without APS-Core needing adapter-specific carve-outs. If they do need carve-outs, that's a sign APS-Core was written too early or too narrowly — revise it, recording why, before moving on.

---

## Stage 3 — Reporting and Multiple Rule Packs

**Goal:** Extract RPS (Reporting Protocol Specification) from real reporter implementations, and prove rule packs can be published and consumed independently.

**Scope:**
- Two or three concrete reporters (Markdown, HTML, SARIF are the most likely candidates given CI/tooling integration value) built directly against `Finding`/RES, with no shared spec yet.
- `docs/specs/RPS-v0.1.md`, extracted once those reporters reveal what's actually common between them (per ADR-0002 — this is a Type B / emergent concern, not designed in advance).
- A second, independently-versioned rule pack (`evident-rules` as a real package boundary, not just a folder) — proves rules can be distributed separately from `evident-core` without violating the layered architecture (`docs/ARCHITECTURE.md` §3).
- First resolution attempt at RES's open Requirement/Assessment aggregation question (RES §1.3), now that multiple rule packs exist to demonstrate (or fail to demonstrate) a common aggregation pattern.

**Exit condition:** A rule pack can be installed and used without modifying `evident-core`, and a reporter can be swapped without modifying rule packs. Both directions of the plugin promise in `docs/ARCHITECTURE.md` §4 (Design Principle 10) hold in practice, not just in theory.

---

## Stage 4 — Plugin Model and CLI

**Goal:** Extract PES (Plugin & Extension Specification) from real extension points now demonstrated in Stages 2–3, and add the thin CLI wrapper.

**Scope:**
- `docs/specs/PES-v0.1.md` — plugin discovery/registration mechanism, generalized from however adapters and reporters ended up being wired in during Stages 2–3.
- `evident-cli` — thin wrapper per `docs/ARCHITECTURE.md`'s Developer First principle; the CLI must not contain logic that doesn't already exist in the Python API.
- `docs/specs/CVS-v0.1.md` — Compliance Vocabulary Specification, assembled from the terminology that has by now stabilized across EGS/RES/APS/RPS.

**Exit condition:** A third-party developer can write a new adapter, rule pack, or reporter as an independent package and have it discovered by the CLI/API without modifying any `evident-*` package. This is the first stage where "ecosystem" stops being aspirational language and starts being a testable claim.

---

## Stage 5 — Research Track (parallel, not sequential)

**Explicitly separated from the numbered stages above** because these are research efforts, not scoped deliverables — they don't have exit conditions in the same sense, and per `docs/ARCHITECTURE.md` §5 (What Evident Is Not) they must not be allowed to influence `evident-core`'s design until independently validated.

- **`evident-provenance`** — hash chains, Merkle trees, cryptographic anchoring, tamper detection. No governance logic, no adapters — provenance only.
- **`evident-context`** — context virtualization (real context → virtual objects → LLM → rehydration). Security-sensitive; requires its own trust/threat-model review before it touches anything else in the ecosystem, independent of this roadmap.
- Community rule packs for specific regimes (EU AI Act, ISO 42001, NIST AI RMF, GDPR, HIPAA, SOC2, etc.) — these can start as soon as Stage 3's rule-pack packaging model is proven, and are expected to be built by contributors, not centrally, once Stage 4's plugin model exists.

These may start once their prerequisite stage's exit condition is met (provenance and community rule packs need Stage 3; context virtualization needs Stage 4's plugin boundary at minimum, plus its own security review). None of them are prerequisites for Stages 1–4.

---

## What "advanced" means here

There is no stage where Evident starts issuing compliance verdicts, replacing legal review, or becoming a dashboard product — that's not a later stage of this roadmap, it's excluded permanently (`docs/ARCHITECTURE.md` §5). "Advanced" in this roadmap means: more artifact types understood (adapters), more consistency and structural checks available (rules), more output formats (reporters), and a larger set of people who can extend the system without touching its core — not a system that becomes more willing to assert certainty it doesn't have.

## Related documents

- `docs/ARCHITECTURE.md` — the principles this roadmap's stage ordering is derived from (see especially ADR-0002).
- `README.md` — current status; should always agree with "Stage 0" / wherever this roadmap says "you are here."
- `docs/specs/` — EGS and RES exist; APS, RPS, PES, CVS are written at the stage indicated above, not before.
