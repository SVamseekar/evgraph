# Urielle Clause 04 x Evgraph mapping experiment

This is an experiment, not a product integration. It doesn't change EGS, RES, or touch Urielle's scoring authority in any way.

Urielle: https://github.com/wholidi/Urielle-ISO42001-AIMS-Toolkit
Evgraph demo: `examples/urielle_clause04/`

## Why this exists

William asked whether a Urielle evidence request/control could map into an Evgraph node/rule, so the ISO 42001 assessment layer could consume machine-verifiable evidence instead of only documented evidence.

Clause 8 / Annex A (bias, provenance, operational controls) isn't built on his side yet — only Clause 4 is. So this experiment sticks to Clause 4.

## Who does what

Urielle's Clause 04 engine requests evidence, assesses it, scores readiness, and flags things for human review. It doesn't consume Evgraph graphs.

The Evgraph adapter + rule normalize Urielle's evidence records into a graph and report whether structured references exist. It doesn't touch the ISO 42001 decision, the readiness score, or human disposition.

## Mapping

| Urielle field | Evgraph |
| --- | --- |
| One evidence record / `question_id` (`C4-Q01`...`C4-Q04`) | `EvidenceNode` type `UrielleAuditQuestion` |
| `actual_evidence_references[]` | `EvidenceNode` type `UrielleEvidenceReference` |
| reference -> question | `EvidenceEdge` type `SUPPORTS` |
| empty `actual_evidence_references` | `reference_count: 0` (that's a fact, not a failure) |
| `confidence_score`, `auditor_flag` | copied over as attributes, not read as a verdict |
| Urielle `EvidenceAssessor.decision` | not produced |
| Urielle readiness score | not produced |

The rule (`clause04-question-has-structured-evidence`) reasons at the STRUCTURAL level: `EXPECTATION_MET` if there's at least one structured reference, `EXPECTATION_NOT_MET` if there isn't. Never framed as pass/fail compliance.

The sidecar reporter emits Urielle-shaped `deterministic_checks` with `check_type: EVIDENCE_TYPE_VALID` only — no `decision` field anywhere in it.

## Running it against a realistic scenario (Harborline)

Not meant to be a clean demo pack — mid-size lender, live credit-decision model, a thin AIMS.

Input: `examples/urielle_clause04/artifacts/harborline_responses.json`
Ran it through the actual cloned `Urielle-ISO42001-AIMS-Toolkit` MVP_1 (`run_clause04_assessment` + `EvidenceAssessor` + `FindingGenerator`), then fed Urielle's own generated evidence records into Evgraph — not a hand-written snapshot.

Live result (2026-09-04): Urielle readiness score **76.25**. 2 draft findings, both `PENDING`.

| Question | What the company actually has | Urielle says (live) | Evgraph says (live) |
| --- | --- | --- | --- |
| C4-Q01 context | Register cited, last reviewed mid-2024, doesn't mention the EU AI Act high-risk classification | `EVIDENCED` (confidence 1.0) — his keyword scorer treats the long response as complete | structured ref present |
| C4-Q02 stakeholders | Register cited, applicants marked TBD, competent authority unnamed | `REQUIRES_HUMAN_JUDGEMENT` (confidence 0.4) — TBD hits his negation list | structured ref present |
| C4-Q03 scope | Scope cited, doesn't name the live credit model | `EVIDENCED` (confidence 1.0) — scorer has no way to know the model is out of scope | structured ref present |
| C4-Q04 AIMS processes | Confluence narrative, nothing attached | `REQUIRES_HUMAN_JUDGEMENT` (confidence 0.65, no evidence ids) — auditor_flag gets checked before the empty-refs check, so it lands here instead of NOT_EVIDENCED | structured ref absent |

Urielle's gaps: `weak_evidence` on Q02 and Q04, `missing_structured_evidence_reference` on Q04.

The interesting part: both tools agree Q04 has no file pointer. They disagree on whether Q01/Q03 are "good enough" — his scorer judges content quality, ours only checks presence. That disagreement is the actual point of running this, not something to smooth over.

What Evgraph doesn't decide, and shouldn't: whether a stale register counts as sufficient, whether a TBD applicant field fails 4.2, whether the model being out of scope matters. That stays with Urielle and a human reviewer.

## A second run, using only public information

Same run, but instead of the fictional Harborline pack, the input was built from public AWS/Microsoft pages and PDFs — the kind of thing that's actually publicly available, since no real company publishes a filled-out AIMS register.

Live result: Urielle readiness **85.0**. Q01/Q03 came back `EVIDENCED` off the public PDF/markdown pages, Q02 came back `NOT_EVIDENCED`, Q04 needed human review. Evgraph agreed with Urielle on where the pointers were present or missing.

Honest caveat on both runs: this is questionnaire JSON going through two engines, not an auditor actually opening a real spreadsheet. The sidecar checks don't set Urielle's decision or score — they just sit next to it.

## What's not in this

- No ISO 42001 rule pack added to `evgraph-rules`
- No changes to EGS or RES
- No demographic parity, no cryptographic provenance
- No EU AI Act control plane in this experiment
- No claim that Harborline is real or that any of this counts as certification evidence
