# Urielle Clause 04 mapping experiment

Small experiment against [William Holidi Hartono's Urielle ISO/IEC 42001 AIMS Toolkit](https://github.com/wholidi/Urielle-ISO42001-AIMS-Toolkit).

Evgraph reads Urielle's existing Clause 04 evidence-record JSON, builds an Evidence Graph out of it, and runs one rule against it: does this audit question have a structured evidence reference or not.

Urielle still owns everything else:

- readiness score
- evidence decision (`EVIDENCED` / `PARTIALLY_EVIDENCED` / etc.)
- human review
- the actual ISO 42001 call

Evgraph doesn't certify anything here.

## Scenario

Made-up lender, Harborline Consumer Finance. They run a scoring tool on loan applications. Their AI management system is new and run by two people who don't own the model itself.

The four Urielle questions (`C4-Q01`–`C4-Q04`) are filled out the way this stuff usually actually looks in practice — files exist, but they're stale, incomplete, scoped wrong, or just described in a Confluence page with nothing attached.

Clause 4 only. No bias metrics, no provenance, no Clause 8.

## Running it

From the Evgraph repo root, with the venv active. You'll need William's MVP installed so his scorer actually runs:

```bash
source .venv/bin/activate
pip install -e /path/to/Urielle-ISO42001-AIMS-Toolkit/MVP_1
python examples/urielle_clause04/run.py
```

That prints Urielle's readiness score, decisions, and draft findings first, then Evgraph's findings on the same evidence records. Output files land in `handoff/`.

Tests:

```bash
cd examples/urielle_clause04 && pytest -q
```

## What William can take from this

`handoff/urielle_sidecar_checks.json` (written when you run it) is a list of checks in Urielle's own shape (`EVIDENCE_TYPE_VALID`). They sit next to his assessor's output, don't replace it.

See `docs/research/urielle-clause04-mapping.md` for the mapping details and how this got sent over.
