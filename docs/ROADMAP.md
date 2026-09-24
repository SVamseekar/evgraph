# Evgraph — Roadmap

**Status:** Living document, expected to change as the project learns. Structured as capability stages, not dates — per `docs/ARCHITECTURE.md` §2 (Specifications Before Frameworks) and ADR-0002, later stages are deliberately underspecified until earlier stages produce the evidence needed to design them.

Each stage lists an **exit condition** — what must be true before moving to the next stage. A stage is not "done when the code is written," it's done when its exit condition holds.

For the principles governing *why* this order was chosen, see `docs/ARCHITECTURE.md` (constitution). For what's true *right now*, see `README.md`. This document is the path connecting the two, from basic to advanced.

---

## Stage 0 — Foundational Specifications *(complete)*

**What exists:**
- `docs/ARCHITECTURE.md` — constitution: mission, principles, layered architecture, non-goals, decision log
- `docs/specs/EGS-v0.1.md` — Evidence Graph Specification
- `docs/specs/RES-v0.1.md` — Rule Evaluation Specification

**Exit condition:** EGS and RES are stable enough that a reference implementation can be built against them without expecting to rewrite their core structural model mid-implementation. ("Stable enough" does not mean "frozen" — open questions listed in each spec's appendix are expected to remain open until Stage 1 answers them with real evidence.) **Met** — see Stage 1.

---

## Stage 1 — Reference Implementation *(complete — current stage)*

**Goal:** Prove the two hypotheses stated in `README.md`:
1. The Evidence Graph is a useful canonical representation across heterogeneous AI-system artifacts.
2. Rules can consume that graph and produce explainable, traceable findings without claiming interpretive/legal authority they don't have.

**Scope — deliberately minimal, one of each:**
- `evgraph-core` — the foundational types from EGS/RES (`EvidenceGraph`, `EvidenceNode`, `EvidenceEdge`, `EvidenceLevel`, `Rule`, `Finding`) as actual Python code, nothing else. Implemented at `reference/python/evgraph-core/`.
- **One adapter** — a Model Card / JSON adapter (`reference/python/evgraph/src/evgraph/adapters/model_card.py`), converting three JSON artifacts (Model Card, human approval, deployment record) into the EGS §10 three-node graph shape.
- **One rule pack, one rule** — `approval-precedes-deployment` (`reference/python/evgraph/src/evgraph/rules/approval_precedes_deployment.py`), matching RES §10 exactly: `reasoning_class = CONSISTENCY`, computed `Finding.level`, `EXPECTATION_MET`/`EXPECTATION_NOT_MET`/`INCONCLUSIVE` outcomes.
- **One reporter** — plain JSON (`reference/python/evgraph/src/evgraph/reporters/json_reporter.py`) matching EGS §5 / RES §6 serialization, including `egs_version`/`res_version` fields.
- `evgraph` — the thin public package wrapping the above (`from evgraph import scan`), at `reference/python/evgraph/`.
- Example artifacts and a runnable demo at `examples/model_card_deployment/`.

**Explicitly not in scope for this stage:** APS as a written spec (it's extracted *from* this work, per ADR-0002), a CLI, any second adapter or rule, performance optimization of any kind. None of these were added.

**Exit condition:** `scan()` on a real artifact produces a `Finding` whose `level` is computed correctly per RES §4.3, is traceable back through EGS `trace()`, and required no change to EGS/RES's structural model to build. **Met** — running `examples/model_card_deployment/run.py` produces a `CONSISTENCY`-level `EXPECTATION_NOT_MET` finding with a correct two-edge `trace`, matching RES §10's worked example exactly. No EGS/RES structural change was required; no new ADR was needed. 30 tests pass across `evgraph-core` and `evgraph` (`pytest -q` in each package directory).

---

## Stage 2 — Adapter Protocol, Grounded *(complete)*

**Goal:** Write APS-Core from what Stage 1's adapter actually needed — not from imagination.

**Scope:**
- `docs/specs/APS-v0.1.md` (Core only): the `Adapter` interface, required declarations (`evidence_level`, `assumptions`, `extraction_method`), lifecycle, error handling (`AdapterError`, interpretation-vs-governance-deficiency distinction).
- A **second adapter**, structurally different from the first — `evgraph-adapter-dataset-manifest` (`reference/python/evgraph/src/evgraph/adapters/dataset_manifest.py`), reading a CSV of dataset records into standalone `Dataset` nodes, versus the first adapter's linked JSON documents.
- A **second rule** — `dataset-manifest-complete` (`reference/python/evgraph/src/evgraph/rules/dataset_manifest_complete.py`), `reasoning_class = STRUCTURAL` and single-node reasoning, versus the first rule's `CONSISTENCY` cross-node reasoning.
- Retrofitted the Model Card adapter to conform to APS-Core (it predated the spec): now exposes `name`/`version`/`evidence_level`/`extraction_method`/`assumptions`/`supported_source_kinds` and raises `AdapterError` (chained) for interpretation failures, while treating missing `approved_at`/`deployed_at` as evidence, not adapter failure.
- `Adapter`, `AdapterError`, `Assumption` added to `evgraph-core` (`reference/python/evgraph-core/src/evgraph_core/adapter.py`).

**Exit condition:** Two structurally different adapters both conform to APS-Core without APS-Core needing adapter-specific carve-outs. **Met** — both adapters share the identical `Adapter` interface, `AdapterError` model, and four-step lifecycle with no special-casing, despite one reading linked JSON and the other reading flat CSV into a standalone graph (EGS §3.5's disconnected-graph allowance, no invented cross-adapter edge). 33 tests pass across both packages (`pytest -q` in each package directory); both example demos (`examples/model_card_deployment/`, `examples/dataset_manifest/`) run end-to-end.

---

## Stage 3 — Reporting and Multiple Rule Packs *(complete)*

**Goal:** Extract RPS (Reporting Protocol Specification) from real reporter implementations, and prove rule packs can be published and consumed independently.

**Scope:**
- Two concrete reporters built directly against `Finding`/RES, with no shared spec at build time: Markdown (`reference/python/evgraph/src/evgraph/reporters/markdown_reporter.py`, human-facing prose) and SARIF (`.../sarif_reporter.py`, CI/tooling-facing, mapping `Outcome` into SARIF's `level` vocabulary as a documented structural translation, never a severity judgment).
- `docs/specs/RPS-v0.1.md`, extracted from comparing all three reporters (JSON, Markdown, SARIF) — a deliberately thin contract (two inputs, order-independence, no invented governance semantics), since a richer one wasn't demonstrated as shared.
- `evgraph-rules` (`reference/python/evgraph-rules/`) — a real, independently-versioned package containing both existing rules (`approval-precedes-deployment`, `dataset-manifest-complete`), moved out of `evgraph`, which now depends on it rather than containing rule code.
- First resolution attempt at RES's open Requirement/Assessment aggregation question (RES §1.3): recorded as a negative result — the two rules share nothing beyond both implementing `Rule`, so "rule-pack membership" is not a meaningful aggregation boundary. See `docs/ARCHITECTURE.md` ADR-0006 ("multiplicity alone does not justify an abstraction; shared semantics do").

**Exit condition:** A rule pack can be installed and used without modifying `evgraph-core`, and a reporter can be swapped without modifying rule packs. **Met** — `evgraph-rules` is a separate installable package depending only on `evgraph-core`; `evgraph` depends on it and both example pipelines (`examples/model_card_deployment/`, `examples/dataset_manifest/`) still run correctly post-extraction. Three reporters (JSON, Markdown, SARIF) coexist on the same `Finding` list with no rule-pack changes required. 42 tests pass across `evgraph-core`, `evgraph-rules`, and `evgraph`.

---

## Stage 4 — Plugin Model and CLI *(complete)*

**Goal:** Extract PES (Plugin & Extension Specification) from real extension points now demonstrated in Stages 2–3, and add the thin CLI wrapper.

**Scope:**
- A concrete discovery mechanism built first (per ADR-0002, since Stages 2–3 had no existing wiring to generalize from): `evgraph-rules` registers both rules under a `"evgraph.rules"` Python entry_point group (`pyproject.toml`); `evgraph/src/evgraph/discovery.py`'s `discover_rules()` enumerates and instantiates them via `importlib.metadata`; `scan.py`'s hardcoded rule lists were replaced with calls to `discover_rules()`.
- `docs/specs/PES-v0.1.md` — extracted from that mechanism. Scoped to rules only — reporters (selected explicitly via `report.to_markdown()`/`to_sarif()`) and adapters (still directly constructed) showed no evidence of needing discovery yet (`docs/ARCHITECTURE.md` ADR-0006).
- `evgraph-cli` (`reference/python/evgraph-cli/`) — thin wrapper exposing exactly the existing Python API (`scan`, `scan_dataset_manifest`, each `Report` output method) as `evgraph scan ...`/`evgraph scan-dataset-manifest ...` with a `--format` flag; contains no logic beyond argument parsing and format-name dispatch.
- `docs/specs/CVS-v0.1.md` — assembled (not designed) from terminology that stabilized across EGS/RES/APS-Core/RPS/PES, with an explicit section listing terms that have *not* stabilized (Requirement, Verdict, Severity) and are deliberately excluded.

**Exit condition:** A third-party developer can write a new rule pack as an independent package and have it discovered by the CLI/API without modifying any `evgraph-*` package. **Met** — a scratch package (`third-party-rule`, registering `AlwaysInconclusiveRule` under `"evgraph.rules"`, depending only on `evgraph-core`, never imported by `evgraph`) was pip-installed and its finding appeared in `scan()`'s output immediately; uninstalling it reverted discovery to the original two rules, with zero code changes to any `evgraph-*` package. (Discovery for adapters/reporters remains out of scope per PES §1.3 — no evidence yet justifies it.) 49 tests pass across all four packages (`evgraph-core`, `evgraph-rules`, `evgraph`, `evgraph-cli`).

---

## Stage 4.5 — Validation & Interoperability *(current stage)*

**Goal:** Validate the reference implementation against an established external standard and a real-world engineering workflow, and gather direct practitioner feedback, before investing in Stage 5's research track. This stage exists because `docs/ARCHITECTURE.md` ADR-0007 (grounded in `docs/research/standards-comparison.md` and `docs/research/practitioner-and-market-check.md`) left two questions explicitly unresolved: can Evgraph interoperate cleanly with an established governance standard, and does the architecture solve a real problem for practitioners rather than a primarily architectural one? Neither question casts doubt on EGS/RES/APS/PES's internal correctness — both are pre-conditions for deciding whether Stage 5's research packages (which assume the foundation is worth building further on) are worth starting yet.

Reasoning for inserting this as a new stage rather than revising Stages 0–4: those stages are a historical record of what was actually built and validated at the time; the assumptions this stage tests were only surfaced by later research, not known during Stages 0–4, so backdating them into that history would misrepresent when the project actually learned what it learned.

**Goal 1 — Standards integration (OSCAL reporter).** *(complete)*
- Scope: an OSCAL reporter (`reference/python/evgraph/src/evgraph/reporters/oscal_reporter.py`), following RPS's existing translation-not-invention precedent (RPS §3.2.3) — the same pattern as the existing SARIF reporter. Translates `Finding` into OSCAL's `assessment-results` `finding`/`observation` model; carries `EvidenceLevel`/`reasoning_class`/`Outcome` as documented, non-standard OSCAL `prop` extensions since OSCAL has no native analog to them (`docs/research/standards-comparison.md`). Scoped to `assessment-results` only — no SSP, Component Definition, Catalog, Profile, or Assessment Plan support, per the same grounding discipline used everywhere else in this project.
- Exit condition: a valid OSCAL Assessment Results document is generated from the existing reference implementation, every lossy or extended field translation is documented, and no change to EGS or RES is required. **Met** — verified against the real RES §10 example via `evgraph scan ... --format oscal`; every `Finding`/`EvidenceNode` field Evgraph considers load-bearing is represented, either natively or via a documented `prop` extension; zero new concepts introduced into EGS/RES. Full findings recorded in `docs/research/oscal-roundtrip.md`. 56 tests pass across all four packages (up from 49).

**Goal 2 — One real external integration.** *(complete)*
- Scope: `evgraph-adapter-mlflow` (`reference/python/evgraph/src/evgraph/adapters/mlflow_adapter.py`) — an MLflow model-registry adapter, built and tested against a real, locally running MLflow 3.14 tracking server (not documentation or memory). Deliberately narrow: only `RegisteredModel`, `ModelVersion`, and `Run` are mapped, matching the same grounding discipline used for adapter scope everywhere else in this project. `mlflow` is a development/validation dependency only — not a runtime dependency of the `evgraph` package.
- Exit condition: a real artifact from the external system is normalized into an `EvidenceGraph` without modifying EGS or APS-Core. **Met.** Strengthened per the design discussion into: *a rule never anticipated during adapter design can evaluate the resulting graph without modifying the adapter, EGS, or APS-Core.* Verified with a new rule, `model-version-has-training-provenance` (`reference/python/evgraph-rules/`), written independently of the adapter's implementation, registered via the existing `"evgraph.rules"` entry_point mechanism, and confirmed against real seeded data — including a deliberately messy case (a model version with no linked run, no description, no tags, a real and valid MLflow state) that the adapter represents as evidence (`has_linked_run: false`), not as an `AdapterError`, per APS-Core §4.2. Full findings recorded in `docs/research/mlflow-adapter-validation.md`. 65 tests pass across all four packages (up from 56).

**Goal 3 — Practitioner validation.** *(preparation complete; interviews open)* Explicitly not a coding task — it requires direct outreach and interviews with practitioners. A related interoperability experiment (not a Goal 3 substitute, not an ISO 42001 pack) maps Urielle Clause 04 evidence records into Evgraph without touching Urielle's score: `examples/urielle_clause04/` and `docs/research/urielle-clause04-mapping.md`.
- Preparation (done): `docs/research/practitioner-outreach-kit.md` (one-page explanation, 5–10 min demo script on shipped CLI paths, primary question + capped follow-ups, targeting), `docs/research/practitioner-interview-log.md`, `docs/research/practitioner-decision-memo.md`.
- Primary interview question: *"What problem, if any, would this solve for you?"*
- Target: practitioners who actually own this problem space day to day (ML platform engineers, MLOps engineers, model risk managers, AI governance leads) — not general AI-interested audiences.
- Success metric is explicitly not positive feedback, stars, or praise — it's whether a recurring, specific problem pattern emerges across independent conversations (default bar: 5–8 interviews; see decision memo for Path A/B/C).

**Exit condition (whole stage):** Proceed to Stage 5 only if at least one of the following holds:
1. Practitioners identify a recurring real problem the current architecture addresses, or
2. The OSCAL integration demonstrates clear interoperability value independent of market adoption.

If neither holds, the next step is not Stage 5 — it's revising Evgraph's positioning, narrowing scope, or explicitly concluding (as ADR-0007 already allows) that Evgraph's value is primarily architectural/reference rather than as a production ecosystem, and adjusting the roadmap from there rather than proceeding into research packages built on an unvalidated foundation.

See `docs/research/validation-plan.md` for the full reasoning, the specific unproven hypotheses this stage tests, and what evidence would confirm or falsify each one.

---

## Stage 5 — Research Track (parallel, not sequential) *(blocked on Stage 4.5's exit condition)*

**Explicitly separated from the numbered stages above** because these are research efforts, not scoped deliverables — they don't have exit conditions in the same sense, and per `docs/ARCHITECTURE.md` §5 (What Evgraph Is Not) they must not be allowed to influence `evgraph-core`'s design until independently validated.

- **`evgraph-provenance`** — hash chains, Merkle trees, cryptographic anchoring, tamper detection. No governance logic, no adapters — provenance only.
- **`evgraph-context`** — context virtualization (real context → virtual objects → LLM → rehydration). Security-sensitive; requires its own trust/threat-model review before it touches anything else in the ecosystem, independent of this roadmap.
- Community rule packs for specific regimes (EU AI Act, ISO 42001, NIST AI RMF, GDPR, HIPAA, SOC2, etc.) — these can start as soon as Stage 3's rule-pack packaging model is proven, and are expected to be built by contributors, not centrally, once Stage 4's plugin model exists.

These may start once their prerequisite stage's exit condition is met (provenance and community rule packs need Stage 3; context virtualization needs Stage 4's plugin boundary at minimum, plus its own security review). None of them are prerequisites for Stages 1–4.

---

## What "advanced" means here

There is no stage where Evgraph starts issuing compliance verdicts, replacing legal review, or becoming a dashboard product — that's not a later stage of this roadmap, it's excluded permanently (`docs/ARCHITECTURE.md` §5). "Advanced" in this roadmap means: more artifact types understood (adapters), more consistency and structural checks available (rules), more output formats (reporters), and a larger set of people who can extend the system without touching its core — not a system that becomes more willing to assert certainty it doesn't have.

## Related documents

- `docs/ARCHITECTURE.md` — the principles this roadmap's stage ordering is derived from (see especially ADR-0002).
- `README.md` — current status; should always agree with "Stage 0" / wherever this roadmap says "you are here."
- `docs/specs/` — EGS and RES exist; APS, RPS, PES, CVS are written at the stage indicated above, not before.
