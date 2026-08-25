# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What this project is

Evgraph is a reference implementation and architecture exploring **executable governance evidence** for AI systems. It defines the Evidence Graph — a canonical IR that governance artifacts (Model Cards, approval records, deployment logs, dataset manifests, MLflow registry data, etc.) are converted into — plus a rule-evaluation model that produces explainable, traceable, *leveled* findings from that graph. It explicitly stops at the evidence boundary: it reports what evidence exists, is missing, or is inconsistent, and never issues a legal/regulatory compliance verdict. See `docs/ARCHITECTURE.md` §1–2 and ADR-0003.

Read `README.md` first for current status; `docs/ARCHITECTURE.md` for the constitution (principles + ADRs, changes rarely); `docs/ROADMAP.md` for capability-staged sequencing. `README.md` and `ROADMAP.md` change often and are the sources of truth for "what stage are we in now" — `ARCHITECTURE.md` is not, and should not be read for current status.

## Repository layout

```
evgraph/
  docs/
    specs/          # EGS, RES, APS, RPS, PES, CVS — normative specifications
    research/        # standards-comparison, practitioner/market check, validation docs
    ARCHITECTURE.md  # constitution: mission, principles, layered architecture, ADRs
    ROADMAP.md       # capability-staged plan with exit conditions per stage
  reference/
    python/
      evgraph-core/   # foundational types only (EvidenceGraph, EvidenceNode, EvidenceEdge,
                       # EvidenceLevel, Rule, Finding, Adapter, AdapterError, Assumption)
      evgraph-rules/  # reference rule pack, independently versioned, registers rules via
                       # the "evgraph.rules" entry_point group
      evgraph/        # adapters, reporters, discover_rules(), public scan() API (pip install evgraph)
      evgraph-cli/     # thin `evgraph scan ...` wrapper, no logic beyond arg parsing/dispatch
  examples/           # runnable end-to-end demos, one per adapter/scenario
```

Each `reference/python/*` directory is an independently versioned, installable Python package with its own `pyproject.toml`, `src/`, and `tests/`.

## Commands

A `.venv` at the repo root has all four packages installed editable, plus `mlflow`, `pytest`, etc. Activate it before running anything:

```bash
source .venv/bin/activate
```

**Run all tests for one package** (each package's tests only import that package + its declared deps — always `cd` into the package dir first, or imports fail with `ModuleNotFoundError`):

```bash
cd reference/python/evgraph-core && pytest -q
cd reference/python/evgraph-rules && pytest -q
cd reference/python/evgraph && pytest -q
cd reference/python/evgraph-cli && pytest -q
```

**Run a single test:**

```bash
cd reference/python/evgraph && pytest tests/test_scan.py::test_name -q
```

**Run the CLI** (installed as `evgraph` inside the venv):

```bash
evgraph scan --model-card ... --format markdown
evgraph scan-dataset-manifest ...
```

**Run an example demo directly:**

```bash
python examples/model_card_deployment/run.py
python examples/dataset_manifest/run.py
python examples/full_demo/run.py
```

There is no root-level build/lint config — each package is a plain `setuptools` project (`pyproject.toml`, `src/` layout); there is no shared tox/nox/Makefile driving all four at once, so iterate per-package as shown above.

## Architecture: the layered dependency rule

Dependencies flow one direction only (`docs/ARCHITECTURE.md` §3):

```
Community Plugins (external adapters, rule packs, reporters, context providers)
CLI · Python API (`evgraph`) · Rule Packs · Reporters
APS — Adapter Protocol
RES — Rule Evaluation
EGS — Evidence Graph
evgraph-core (graph, node, edge, evidence level — foundational types only)
```

`evgraph-core` depends on nothing else in the stack. A lower layer must never know about a higher layer (e.g. `evgraph-core` importing anything from `evgraph-rules` is a constitution violation, not a pragmatic shortcut). When extending the system, the default is "make it a plugin" (new adapter/rule pack/reporter package), not "add it to `evgraph-core`" (Design Principle 10).

### The core model, concretely

- **EvidenceGraph** — immutable DAG built once by adapters merging node/edge lists at construction time; never mutated in place (ADR-0004). Combining multiple adapters' output means building one new graph, not patching an existing one.
- **Adapters** interpret raw artifacts into typed `EvidenceNode`/`EvidenceEdge` facts. They are the *only* layer allowed to make an interpretive judgment call about what a raw artifact means, and must declare `evidence_level`, `assumptions`, and `extraction_method` for whatever they produce (APS-Core). See `evgraph/src/evgraph/adapters/{model_card,dataset_manifest,mlflow_adapter}.py` for the shared shape despite reading structurally different sources (linked JSON vs. flat CSV vs. a live MLflow registry).
- **Evidence Level** is an ordered hierarchy, `STRUCTURAL → CONSISTENCY → HEURISTIC → INTERPRETIVE` (most to least certain), set per-node by the adapter and only ever *lowered*, never raised, downstream.
- **Rules** read a full graph and return `Finding`s; they never write back to the graph (`Rule.evaluate(graph)` per RES §3.1). Rules are deterministic given a fixed graph and rule version — a non-deterministic rule (e.g. LLM-based) must declare itself as such and is capped at `HEURISTIC`, never `STRUCTURAL`/`CONSISTENCY` (Determinism principle; `docs/ARCHITECTURE.md` §5 non-goals also bar this being the default eval path).
- **Finding.level is computed, never declared** (ADR-0005): a rule declares a `reasoning_class` (the epistemic ceiling of *how* it reasons, independent of what it cites); `Finding.level` is always the least-certain value among `reasoning_class` and the evidence levels of every node the finding cites. This is why a `CONSISTENCY`-reasoning rule over purely `STRUCTURAL` nodes still can't produce a `STRUCTURAL` finding.
- **Findings never use bare PASS/FAIL** (ADR-0003) — outcome vocabulary describes evidence state (e.g. `EXPECTATION_MET`/`EXPECTATION_NOT_MET`/`INCONCLUSIVE`), and every finding must cite the specific nodes/edges it depends on, traceable via the graph's `trace()`.
- **Reporters never invent evidence** — they format `Finding`s into an output shape (JSON, Markdown, SARIF, OSCAL) without adding claims that don't trace back to a finding. SARIF/OSCAL mappings of `Outcome` are documented as structural translation, never a severity judgment (RPS §3.2.3 "translation, not invention").
- **Rule discovery** is plugin-based via Python entry_points: `evgraph-rules` registers its rules under the `"evgraph.rules"` group in its `pyproject.toml`; `evgraph/src/evgraph/discovery.py`'s `discover_rules()` enumerates them via `importlib.metadata`. A third-party package can add rules with zero changes to any `evgraph-*` package by registering under the same entry_point group. Adapters and reporters are *not* discovered this way (still directly constructed/selected) — no evidence yet justifies discovery for them (ADR-0006, PES §1.3).

### Why specs precede some code but not other code

Foundational (Type A) abstractions — EGS, RES, APS-Core — are specified *before* implementation, because downstream design hard-depends on them being fixed (e.g. you can't design a confidence model without first fixing how evidence enters the graph with what epistemic status). Emergent (Type B) abstractions — RPS (reporting), PES (plugins) — are *extracted from working code* after real patterns exist, not designed speculatively in advance (ADR-0002). When adding a new reporter or plugin-style extension point, look at how the existing ones actually behave before generalizing; don't design the abstraction first.

Every concept added to a spec must be justified by a concrete, demonstrated need in the reference implementation (Grounding Discipline) — an idea that "might be useful later" belongs in a spec's Non-Goals section, not in the spec itself. Multiplicity alone (having two of something) does not justify introducing a shared abstraction — shared *semantics* do (ADR-0006). If you're tempted to generalize across two rules/adapters/reporters, check whether they share more than just "both implement the same interface."

## What Evgraph deliberately is not

(`docs/ARCHITECTURE.md` §5 — treat these as hard boundaries, not aspirational)

- Not a legal expert system or compliance certification authority — never emit a compliance verdict.
- Not a hosted SaaS product, compliance dashboard, workflow orchestrator, admission controller, or document management system.
- Not a replacement for MLflow/OpenTelemetry-style tools — integrate via adapters, don't compete.
- Not an LLM wrapper — any LLM-based evaluation is explicitly opt-in, bounded to `HEURISTIC` evidence level, and never the default path.

## Current stage and unresolved question

Per `docs/ROADMAP.md`, Stages 0–4 are complete (specs, reference implementation, APS, reporting/rule-pack separation, plugin discovery + CLI). The project is in **Stage 4.5 (Validation & Interoperability)** — validating against OSCAL (done, `docs/research/oscal-roundtrip.md`) and a real external system via the MLflow adapter (done, `docs/research/mlflow-adapter-validation.md`), with practitioner validation still open. Per ADR-0007, the *technical* architecture (EGS/RES, especially `EvidenceLevel` and the confidence-inheritance invariant) is validated as non-redundant with existing standards, but the market-adoption thesis is explicitly an unproven hypothesis, not a stated goal — don't write or imply ecosystem-adoption claims without an independent third-party adopter to cite. Stage 5 (provenance, context virtualization, community regulatory rule packs) is blocked on Stage 4.5's exit condition and is not a prerequisite for anything already built.

`architecture.md` at the repo root is superseded by `docs/ARCHITECTURE.md` and kept only for project history — do not treat it as a source of current principles.
