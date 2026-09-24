# evgraph

[![PyPI](https://img.shields.io/pypi/v/evgraph.svg)](https://pypi.org/project/evgraph/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/SVamseekar/evgraph/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**The main Python library for [Evgraph](https://github.com/SVamseekar/evgraph) — adapters, reporters, and the public `scan()` API.**

## What is it

`evgraph` is the package most users install directly: it is where the
governance artifacts you already have (a Model Card, an approval record, a
deployment record, a dataset manifest, an MLflow registry) get turned into an
`EvidenceGraph`, evaluated against every rule installed on the system, and
formatted for a human, a CI pipeline, or a standards tool to consume. It sits
on top of `evgraph-core` (the graph and evidence-level vocabulary) and
`evgraph-rules` (the built-in checks), and is what most of the rest of the
Evgraph documentation means when it talks about "running a scan." This package does not install the `evgraph` command. EU AI Assurance OS pins `evgraph-cli==0.1.2`. A missing approval timestamp stays inconclusive. The scan does not invent the field.

A scan is always three steps, regardless of which adapter or reporter is
used: an **adapter** builds a graph, every discovered **rule** evaluates that
graph and returns findings, and a **reporter** formats the graph plus
findings for whoever is reading the output.

## Main features

- **`scan(model_card_path, approval_path, deployment_path)`** — runs the
  Model Card / JSON adapter across the three linked documents that make up a
  model's story (what it is, who approved it, where it was deployed),
  producing one `Report`.
- **`scan_dataset_manifest(manifest_path)`** — runs the dataset-manifest /
  CSV adapter, converting one row per dataset into an `EvidenceGraph`.
- **`scan_promotion(...)`** — runs a promotion-oriented scan from the same JSON
  trio as `scan()`, or from that trio composed with MLflow model/version
  evidence.
- **`evaluate_gate(report, fail_on_inconclusive=False)`** — computes whether a
  report should trip an automation gate. It fails on unmet expectations by
  default and can also fail on inconclusive findings for strict gates.
- **Adapters** — `Model Card` (JSON: model card + approval + deployment,
  linked into one graph), `dataset manifest` (CSV: one `Dataset` node per
  row), and `MLflow model registry` (maps `RegisteredModel`, `ModelVersion`,
  and `Run` from a real MLflow tracking server; deliberately narrow scope —
  experiments, metrics, params, artifacts, and stage/alias transitions are
  not yet mapped). Every adapter interprets reality; none of them invent a
  relationship the source artifact doesn't state.
- **`discover_rules()`** — finds every `Rule` registered under the
  `evgraph.rules` entry-point group across *all* installed packages via
  `importlib.metadata`, not just the built-in `evgraph-rules` pack. This is
  what lets a third-party rule pack affect `scan()` output purely by being
  `pip install`-ed, with no code change to `evgraph` itself.
- **Reporters** — `Report` (the object every scan returns) can render itself
  as **JSON**, **Markdown**, **SARIF** (so findings show up as CI
  annotations in tools that already speak SARIF), and **OSCAL Assessment
  Results** (for interoperability with NIST's compliance-automation
  standard). One graph, one set of findings, four representations — pick the
  one your downstream tool understands.

## Where to get it

The source is hosted on GitHub at: https://github.com/SVamseekar/evgraph

Binary installers for the latest released version are available at the
[Python Package Index (PyPI)](https://pypi.org/project/evgraph/):

```bash
pip install evgraph
pip install "evgraph[mlflow]"   # optional, for the MLflow adapter
```

From source, for contributing:

```bash
git clone https://github.com/SVamseekar/evgraph.git
cd evgraph
pip install -e reference/python/evgraph-core
pip install -e reference/python/evgraph-rules
pip install -e reference/python/evgraph
pip install -e "reference/python/evgraph[mlflow]"
```

## Dependencies

- [`evgraph-core`](https://pypi.org/project/evgraph-core/) — installed
  automatically as a dependency.
- [`evgraph-rules`](https://pypi.org/project/evgraph-rules/) — installed
  automatically as a dependency, so a fresh `pip install evgraph` gets useful
  findings immediately, not an empty rule set.
- `mlflow>=2.0` — optional, only needed for the MLflow adapter
  (`pip install "evgraph[mlflow]"`).

`pytest>=7` is required for the test suite (`pip install "evgraph[test]"`).

## Quickstart

```python
from evgraph import scan, scan_dataset_manifest

report = scan(
    model_card_path="model_card.json",
    approval_path="approval.json",
    deployment_path="deployment.json",
)

print(report.to_json())
for finding in report.findings:
    print(finding.rule_id, finding.outcome, finding.level)

# Trace exactly which nodes and edges a finding rests on:
report.trace(report.findings[0].cited_node_ids[0])

# Same graph, different audiences:
report.to_markdown()                      # human-readable review
report.to_sarif()                         # CI annotations
report.to_oscal_assessment_results()      # compliance tooling
```

```python
manifest_report = scan_dataset_manifest("dataset_manifest.csv")
```

```python
from evgraph import evaluate_gate, scan_promotion

promotion_report = scan_promotion(
    model_card_path="model_card.json",
    approval_path="approval.json",
    deployment_path="deployment.json",
)

gate = evaluate_gate(promotion_report)
if gate.should_fail:
    for reason in gate.reasons:
        print(reason)
```

Runnable, end-to-end versions of these examples live under
[`examples/`](https://github.com/SVamseekar/evgraph/tree/main/examples) in
the main repository.

## Documentation

| For | Start here |
| --- | --- |
| Design principles and decisions | [`docs/ARCHITECTURE.md`](https://github.com/SVamseekar/evgraph/blob/main/docs/ARCHITECTURE.md) |
| Normative specs (adapters, reporting, plugins) | [`docs/specs/`](https://github.com/SVamseekar/evgraph/tree/main/docs/specs) |
| Built-in rule pack | [`evgraph-rules`](https://pypi.org/project/evgraph-rules/) package README |
| Command-line usage | [`evgraph-cli`](https://pypi.org/project/evgraph-cli/) package README |
| Runnable examples | [`examples/`](https://github.com/SVamseekar/evgraph/tree/main/examples) |
| The full library stack | [Main project README](https://github.com/SVamseekar/evgraph) |

## Getting help

Ask questions and report bugs via
[GitHub Issues](https://github.com/SVamseekar/evgraph/issues) on the main
repository.

## Contributing

All contributions, bug reports, and feature requests are welcome on the main
repository. See
[CONTRIBUTING.md](https://github.com/SVamseekar/evgraph/blob/main/CONTRIBUTING.md)
and the
[Code of Conduct](https://github.com/SVamseekar/evgraph/blob/main/CODE_OF_CONDUCT.md).
Security reports:
[SECURITY.md](https://github.com/SVamseekar/evgraph/blob/main/SECURITY.md).

## License

[BSD 3-Clause](https://github.com/SVamseekar/evgraph/blob/main/LICENSE).
