# Evgraph

[![CI](https://github.com/SVamseekar/evgraph/actions/workflows/ci.yml/badge.svg)](https://github.com/SVamseekar/evgraph/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)

**Python libraries for executable governance evidence.**

Evgraph turns the artifacts you already produce—Model Cards, approvals,
deployment records, dataset manifests, model-registry metadata—into a single
**Evidence Graph**, then runs clear, deterministic rules over that graph and
returns findings you can explain, export, and audit.

It is a library stack, not a hosted product:

- installable Python packages
- a small CLI for local and CI use
- adapters that read real systems (including MLflow)
- reporters for JSON, Markdown, SARIF, and OSCAL

Evgraph reports what the evidence shows. It does **not** certify legal or
regulatory compliance.

---

## Why Evgraph exists

AI governance work is full of files and systems that do not talk to each other:
a Model Card here, an approval ticket there, a registry entry somewhere else.
Reviewers still stitch those pieces together by hand.

Evgraph makes that work programmatic:

1. **Adapters** read your artifacts and build an Evidence Graph.
2. **Rules** evaluate the graph and emit leveled findings.
3. **Reporters** format those findings for people, pipelines, or standards tools.

You keep ownership of policy and judgment. Evgraph owns the graph, the checks,
and the trail of what was checked.

---

## Packages

| Package | What it is |
| --- | --- |
| [`evgraph-core`](reference/python/evgraph-core/) | Core types: graph, nodes, edges, evidence levels, rules, findings |
| [`evgraph-rules`](reference/python/evgraph-rules/) | Built-in rule pack (discoverable via entry points) |
| [`evgraph`](reference/python/evgraph/) | Adapters, reporters, and the `scan()` / `scan_dataset_manifest()` API |
| [`evgraph-cli`](reference/python/evgraph-cli/) | `evgraph` command-line tool |

All packages are versioned together at **0.1.0** (see [CHANGELOG](CHANGELOG.md)).

---

## Install

Python **3.10+**. From a clone of this repository:

```bash
git clone https://github.com/SVamseekar/evgraph.git
cd evgraph
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e reference/python/evgraph-core
pip install -e reference/python/evgraph-rules
pip install -e reference/python/evgraph
pip install -e reference/python/evgraph-cli
```

Optional MLflow adapter dependency:

```bash
pip install -e "reference/python/evgraph[mlflow]"
```

> Packages are published from this monorepo. PyPI distribution is planned;
> until then, install from source as above.

---

## Quickstart

### CLI

```bash
# Check model card + approval + deployment consistency
evgraph scan \
  examples/model_card_deployment/model_card.json \
  examples/model_card_deployment/approval.json \
  examples/model_card_deployment/deployment.json \
  --format markdown

# Check a dataset manifest
evgraph scan-dataset-manifest \
  examples/dataset_manifest/dataset_manifest.csv \
  --format json
```

Output formats: `json`, `markdown`, `sarif`, `oscal`.

### Python

```python
from evgraph import scan

report = scan(
    model_card_path="examples/model_card_deployment/model_card.json",
    approval_path="examples/model_card_deployment/approval.json",
    deployment_path="examples/model_card_deployment/deployment.json",
)

print(report.to_json())
for finding in report.findings:
    print(finding.rule_id, finding.outcome, finding.level)
```

### Examples

```bash
python examples/model_card_deployment/run.py
python examples/dataset_manifest/run.py
python examples/full_demo/run.py
```

---

## What you get

### Evidence Graph

Adapters produce an immutable directed graph of typed facts
(`EvidenceNode` / `EvidenceEdge`). That graph is the shared intermediate form
every rule and reporter understands.

### Evidence levels

Every node and finding carries a level of certainty:

`STRUCTURAL` → `CONSISTENCY` → `HEURISTIC` → `INTERPRETIVE`

Findings never claim more certainty than the evidence they cite. Levels are
only lowered as reasoning gets less certain—never raised.

### Findings, not pass/fail stamps

Rules return explainable outcomes with citations back into the graph (for
example expectation met / not met / inconclusive). You always see *why*, not
only a green or red badge.

### Built-in adapters and reporters

| Adapters | Reporters |
| --- | --- |
| Model Card + approval + deployment (JSON) | JSON |
| Dataset manifest (CSV) | Markdown |
| MLflow model registry | SARIF |
| | OSCAL Assessment Results |

### Extensible rules

Third-party rule packs register under the `evgraph.rules` entry-point group.
Install a pack; `scan()` picks it up—no changes to core packages required.

---

## Who it is for

- **ML / platform engineers** who want governance checks in CI and local tooling
- **Model risk and governance teams** who need machine-readable evidence trails
- **Tool authors** who want to plug new artifact types (adapters) or policies (rules)

---

## What Evgraph is not

- Not a compliance certification authority or legal expert system
- Not a SaaS dashboard, workflow engine, or document management product
- Not a replacement for MLflow, OpenTelemetry, or your source of truth systems—
  it integrates with them through adapters
- Not an LLM wrapper: evaluation is deterministic by default

For the full boundary list, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Documentation

| For | Start here |
| --- | --- |
| Using the libraries | This README and `examples/` |
| Design principles and decisions | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Product roadmap | [`docs/ROADMAP.md`](docs/ROADMAP.md) |
| Normative specs (graph, rules, adapters, reporting, plugins) | [`docs/specs/`](docs/specs/) |
| Standards notes (OSCAL, MLflow, prior art) | [`docs/research/`](docs/research/) |
| Contributing | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Releases | [`CHANGELOG.md`](CHANGELOG.md) |

---

## Project layout

```
evgraph/
  docs/                 Architecture, roadmap, specs, research
  reference/python/     Installable packages (evgraph-core, evgraph-rules, evgraph, evgraph-cli)
  examples/             Runnable end-to-end demos
```

---

## Development

```bash
source .venv/bin/activate
pip install pytest

pytest reference/python/evgraph-core -q
pytest reference/python/evgraph-rules -q
pytest reference/python/evgraph -q
pytest reference/python/evgraph-cli -q
```

CI runs the same suite on Python 3.10–3.12.

---

## Versioning

Semantic Versioning. Monorepo releases use annotated tags (`v0.1.0`, …).
All four packages share a version for each release train.

---

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md)
and the [Code of Conduct](CODE_OF_CONDUCT.md). Security reports:
[SECURITY.md](SECURITY.md).

---

## Citation

Use [`CITATION.cff`](CITATION.cff) if you cite Evgraph in academic or industry work.

---

## License

[BSD 3-Clause](LICENSE).
