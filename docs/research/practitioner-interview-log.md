# Practitioner Interview Log — Stage 4.5 Goal 3

**Status:** Template. Copy this file (or duplicate the blank block below) once per conversation. Do not aggregate praise here — aggregate **problem statements in their words**.

**Related:** `practitioner-outreach-kit.md` (script), `practitioner-decision-memo.md` (exit), `validation-plan.md` H3.

---

## How to use

1. Fill one **Interview** block per person (independent conversations only — two people from the same team on the same call count as **one** conversation unless they own different problems).
2. Quote or paraphrase the problem **in their vocabulary**; do not rewrite into Evgraph jargon.
3. After each interview, update the **Running pattern board** at the bottom (or keep a single shared board in this file).
4. Stop early only if patterns clearly saturate (see decision memo). Default bar: **5–8** independent conversations.

---

## Interview — blank (copy from here)

```
Date:
Interviewer:
Channel: (call / conf / async)

Role / title:
Org context: (industry; approximate size; regulated? Y/N/unknown)
Owns day-to-day: (CI / registry / MRM review / governance policy / other — their words)

Primary answer — “What problem, if any, would this solve for you?”
(verbatim or close paraphrase):

Maps to Evgraph as shipped today?
[ ] Yes — which part (graph / rules / CI gate / reviewer pack / OSCAL export / adapter)
[ ] Partially — what would still be missing
[ ] No — different problem
[ ] No — already solved by (name tool/process if given)
[ ] Unclear — need follow-up

Objections / constraints (time, org politics, “we don’t produce those artifacts,” security, etc.):

Follow-ups used (if any) and answers:

Anything that contradicts desk research (practitioner-and-market-check.md)?

Notes (facts only; no adoption claims):
```

---

## Running pattern board

Update after each interview. A “pattern” needs **≥2 independent** conversations naming the same problem class before it counts toward H3 confirmation.

| Pattern (short label) | Problem in practitioners’ words | Interview IDs / dates | Maps to Evgraph? | Count |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |
| | | | | |

### Anti-patterns (also record — these falsify or redirect H3)

| Anti-pattern | Examples | Count |
| --- | --- | --- |
| No problem / curiosity only | “Interesting but we wouldn’t use it” | |
| Upstream of evidence format | “We don’t write model cards / approvals at all” | |
| Already served | “ValidMind / Modelscape / internal MRM suite does this” | |
| Ownership / process, not tooling | “Nobody owns governance; format won’t help” | |
| Different problem | (severity) | |

---

## Interview — 2026-09 (async) William Holidi Hartono

```
Date: 2026-09 (async LinkedIn)
Interviewer: Soura
Channel: async

Role / title: Builder of Urielle ISO/IEC 42001 AIMS Toolkit
Org context: OSS ISO 42001 toolkit; Clause 4 executable assessment MVP
Owns day-to-day: ISO 42001 Clause 4 evidence request, assessment, deterministic scoring under an agentic layer that does not own the score

Primary answer — “What problem, if any, would this solve for you?”
Whether a Urielle evidence request/control can map to an Evgraph node/rule so ISO 42001 assessment can consume machine-verifiable evidence rather than only documented evidence.

Maps to Evgraph as shipped today?
[x] Partially — graph/rules can check structured evidence presence; Urielle still owns score/decision; Clause 8 evidence types (bias/provenance) are not in either repo yet

Objections / constraints:
Loan-scoring evidence types (provenance, bias/parity) belong to ISO 42001 Clause 8 / Annex A; Urielle only covers Clause 4 so far — no landing spot for those types.

Follow-ups used (if any) and answers:
Soura proposed one small Clause 4 mapping instead of a full integration.

Anything that contradicts desk research (practitioner-and-market-check.md)?
This is an adjacent-tool builder, not an in-house MLOps/MRM owner. One conversation. Does not confirm H3.

Notes (facts only; no adoption claims):
He read Evgraph (EvidenceLevel ladder; no compliance certification). He asked whether demographic parity / cryptographic provenance exist (they do not). Experiment recorded in docs/research/urielle-clause04-mapping.md.
```

---

## Completed interviews (index)

| # | Date | Role | Pattern label(s) | Map? |
| --- | --- | --- | --- | --- |
| 1 | 2026-09 | Urielle / ISO 42001 toolkit author | evidence-request ↔ node/rule mapping; Clause 4 vs 8 landing spot | Partially |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| 6 | | | | |
| 7 | | | | |
| 8 | | | | |
