# Validation Plan — Stage 4.5

**Status:** Living document, gating Stage 5. Not a specification — this records why Stage 4.5 exists, exactly what remains unproven after Stages 0–4, and what evidence would confirm or falsify each open hypothesis. See `docs/ROADMAP.md` Stage 4.5 for the scoped work items this document grounds.

---

## Why this stage exists

Stages 0 through 4 validated one thing thoroughly: **that the architecture is internally coherent and can be built as described.** Every spec (EGS, RES, APS-Core, RPS, PES, CVS) was either grounded in a concrete implementation need before being written, or extracted from working code after the fact. Every claimed capability — two structurally different adapters conforming to one protocol, rule packs distributing independently, third-party plugin discovery — was demonstrated with a real test, not asserted.

What was never tested is whether any of that matters to anyone outside this project. `docs/research/standards-comparison.md` and `docs/research/practitioner-and-market-check.md` (commissioned specifically to stress-test the founding premise rather than defend it) surfaced two concrete, unresolved gaps, recorded in `docs/ARCHITECTURE.md` ADR-0007:

1. Evgraph has not demonstrated interoperability with an established external standard (OSCAL was analyzed on paper, not integrated).
2. Evgraph has not demonstrated that its core abstraction solves a problem for anyone who wasn't already inside this conversation. The N×M interoperability pressure that justified the Arrow/OpenTelemetry comparison in ADR-0001 remains, in the research's own words, "not yet demonstrated."

Both gaps are pre-conditions for Stage 5, not just nice-to-haves: Stage 5's research packages (`evgraph-provenance`, `evgraph-context`, community rule packs) are additional investment in an ecosystem whose value beyond this repository is still unconfirmed. Building them before closing these gaps would be compounding uncertainty on top of uncertainty — the same failure mode the Grounding Discipline (`docs/ARCHITECTURE.md` §2) already guards against at the schema level, applied here at the strategic level.

## The specific hypotheses under test

| # | Hypothesis | Status before Stage 4.5 | What would confirm it | What would falsify it |
|---|---|---|---|---|
| H1 | EGS/RES's internal model (in particular `EvidenceLevel` and the confidence-inheritance invariant) is not redundant with an existing standard and can interoperate with one. | Partially supported (paper analysis only — `standards-comparison.md`) | A working OSCAL reporter produces a valid Assessment Results document without requiring any change to EGS or RES. | The translation turns out to be lossy in a way that matters (not just an extension property, but a genuine structural mismatch), or requires changing EGS/RES to accommodate OSCAL. |
| H2 | APS-Core's adapter contract, validated so far only against two synthetic reference adapters, generalizes to a real external system's actual artifact shapes. | Untested against anything real | One production-quality adapter (MLflow, LangSmith, OpenLineage, GitHub Actions, or OpenMetadata) is built against a real API without requiring a change to EGS or APS-Core. | Building it reveals APS-Core needs adapter-specific carve-outs, the same failure signal Stage 2's exit condition already watches for. |
| H3 | There is a real, nameable interoperability or workflow problem that Evgraph's abstraction solves for practitioners who actually own AI governance evidence day to day. | Actively contradicted in the fragmented-ownership case, and superseded by mature tooling (ValidMind, Modelscape) in the single-owner (banking MRM) case — per `practitioner-and-market-check.md` | Independent practitioners, asked "what problem would this solve for you?", converge on a recurring, specific answer connected to what Evgraph actually does. | Conversations surface no recurring pattern, or surface a different problem (e.g., "we don't write documentation at all," "governance ownership is the issue, not format") that Evgraph's current design doesn't address. |

H1 and H2 are answerable by building (Stage 4.5 Goals 1–2). H3 is answerable only by direct practitioner contact (Goal 3) — no amount of further research or code changes this in place of actually asking.

## What depends on the outcome

- **If H1 and H2 hold, H3 does not:** Evgraph is a technically sound reference architecture without demonstrated external demand. Per ADR-0007, this is an acceptable outcome, not a failure — but it means Stage 5 should not proceed on the theory that an ecosystem will emerge around it. The honest move at that point is to say so in the README and treat the project as complete as a reference implementation, updating further only if new evidence arrives.
- **If H3 holds:** whatever recurring problem practitioners name becomes the actual scoping input for what Stage 5 (or a revised roadmap) should build — not `evgraph-provenance`/`evgraph-context` by default, but whatever the conversations actually surfaced.
- **If H1 or H2 fails:** that is itself valuable information about EGS/RES/APS-Core's actual limits, to be recorded as a new ADR the same way ADR-0005/ADR-0006 recorded prior design corrections — not something to quietly work around.

## Non-goals for this document

This is not a marketing plan, a fundraising pitch, or a user-research methodology guide. It records exactly three things: why Stage 4.5 exists, what's being tested, and what result changes what decision. Anything beyond that belongs in the roadmap (scoped work) or the research documents themselves (findings), not here.

---

## Related documents

- `docs/ROADMAP.md` Stage 4.5 — the scoped work items this plan grounds.
- `docs/ARCHITECTURE.md` ADR-0007 — the decision this validation stage exists to test.
- `docs/research/standards-comparison.md` — source of H1/H2.
- `docs/research/practitioner-and-market-check.md` — source of H3.
