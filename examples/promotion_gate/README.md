# Promotion Gate Example

This example shows how to use Evgraph promotion scans in review and CI. The gate
is an automation signal over evidence findings: it reports evidence that exists,
is missing, or is inconsistent. It is not a legal or regulatory compliance
verdict.

The commands below reuse the sample JSON artifacts from
`examples/model_card_deployment/`.

## Report-Only Scan

By default, scans are report-only. The command exits `0` when the scan completes,
even if findings include unmet evidence expectations.

```bash
evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format markdown
```

Use report-only mode when reviewers need the evidence trail but the pipeline
should not block promotion automatically.

## Optional Gate

Add `--gate` when CI should return exit code `1` for findings whose outcome is
`EXPECTATION_NOT_MET`.

```bash
evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format sarif \
  --gate > evgraph-promotion.sarif
```

Add `--strict` with `--gate` when inconclusive findings should also trip the
gate.

```bash
evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format json \
  --gate \
  --strict
```

`--strict` is only valid with `--gate`; using it alone is a usage error.

## Reviewer Pack

A reviewer pack can be produced by running the same scan through the existing
reporters. Markdown is useful for human review, SARIF for code-hosting or CI
annotations, and OSCAL Assessment Results for standards-tool interoperability.

```bash
mkdir -p promotion-review

evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format markdown > promotion-review/evgraph-promotion.md

evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format sarif > promotion-review/evgraph-promotion.sarif

evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format oscal > promotion-review/evgraph-promotion-oscal.json
```

These files are different renderings of the same evidence graph and findings.
They do not add a compliance claim beyond the cited evidence.
