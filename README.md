# Evident

[![CI](https://github.com/souravamseekarmarti/evident/actions/workflows/ci.yml/badge.svg)](https://github.com/souravamseekarmarti/evident/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)

A reference implementation and architecture for **executable governance evidence**,
with an open Python library stack.

Evident is not a SaaS platform or compliance dashboard. It defines the
**Evidence Graph** — a canonical intermediate representation that governance
artifacts (Model Cards, approval records, deployment logs, evaluation datasets,
registry metadata, and similar sources) can be converted into — and a rule
evaluation model that produces explainable, traceable findings from that graph.

Governance evidence collection, normalization, and consistency-checking are
computable. Legal and regulatory *interpretation* is not: Evident stops at the
evidence boundary and never issues compliance verdicts. See
`docs/specs/RES-v0.1.md` for how findings are leveled so that boundary is
enforced in the type system, not only in documentation.

**What this project is** (`docs/ARCHITECTURE.md`, ADR-0007): a reference runtime
model for representing and evaluating governance evidence — not a proposed
industry standard, and not a claim that broad adoption is likely. Existing
standards (for example OSCAL) are interoperability targets where a concrete case
justifies integration. Ecosystem-wide interoperability claims remain open
hypotheses tracked under `docs/research/`.

---

## Status

**Stages 0–4 complete.** Stage 4.5 (validation and interoperability) is in
progress: OSCAL and MLflow validation are done; practitioner validation remains
open. See `docs/ROADMAP.md`.

| Package | Version | Role |
| --- | --- | --- |
| `evident-core` | 0.1.0 | Foundational graph, node, edge, level, rule, and finding types |
| `evident-rules` | 0.1.0 | Reference rule pack (entry-point discovery) |
| `evident` | 0.1.0 | Adapters, reporters, `scan()` API, rule discovery |
| `evident-cli` | 0.1.0 | `evident` command-line interface |

Specifications (all v0.1): EGS, RES, APS, RPS, PES, CVS under `docs/specs/`.

---

## Installation

From a clone of this repository (packages are not yet published to PyPI):

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e reference/python/evident-core
pip install -e reference/python/evident-rules
pip install -e reference/python/evident
pip install -e reference/python/evident-cli
```

Optional MLflow adapter support:

```bash
pip install -e "reference/python/evident[mlflow]"
```

Requires **Python 3.10+**.

---

## Quickstart

```bash
# Model Card / approval / deployment scan (JSON artifacts)
evident scan \
  examples/model_card_deployment/model_card.json \
  examples/model_card_deployment/approval.json \
  examples/model_card_deployment/deployment.json \
  --format markdown

# Dataset manifest scan
evident scan-dataset-manifest \
  examples/dataset_manifest/dataset_manifest.csv \
  --format json
```

Python API:

```python
from evident import scan

report = scan(
    model_card_path="examples/model_card_deployment/model_card.json",
    approval_path="examples/model_card_deployment/approval.json",
    deployment_path="examples/model_card_deployment/deployment.json",
)
print(report.to_json())
```

Runnable demos:

```bash
python examples/model_card_deployment/run.py
python examples/dataset_manifest/run.py
python examples/full_demo/run.py
```

---

## Repository layout

```
evident/
  docs/
    specs/           # EGS, RES, APS, RPS, PES, CVS
    research/        # standards comparison, validation notes
    ARCHITECTURE.md  # constitution and ADRs
    ROADMAP.md       # capability-staged plan
  reference/python/
    evident-core/    # foundational types
    evident-rules/   # reference rule pack
    evident/         # adapters, reporters, public API
    evident-cli/     # CLI wrapper
  examples/          # end-to-end demos
```

---

## Core concepts

| Term | Meaning |
| --- | --- |
| **Evidence Graph** | Immutable DAG produced by adapters from source artifacts |
| **EvidenceNode / EvidenceEdge** | Typed, evidence-leveled facts and relationships |
| **Evidence Level** | `STRUCTURAL → CONSISTENCY → HEURISTIC → INTERPRETIVE` (most to least certain); only ever lowered downstream |
| **Finding** | A rule's output over the graph; leveled, never a bare PASS/FAIL |

See `docs/specs/CVS-v0.1.md` for the full cross-vocabulary.

---

## Documentation

| Document | Purpose |
| --- | --- |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Mission, principles, layered design, ADRs |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Capability stages and exit conditions |
| [`docs/VISION.md`](docs/VISION.md) | Strategic hypotheses (non-normative) |
| [`docs/specs/`](docs/specs/) | Normative specifications |
| [`docs/research/`](docs/research/) | Standards and validation research |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Development and contribution guide |

---

## Development

```bash
source .venv/bin/activate
pip install pytest

cd reference/python/evident-core && pytest -q
cd ../evident-rules && pytest -q
cd ../evident && pytest -q
cd ../evident-cli && pytest -q
```

Continuous integration runs the same suite on Python 3.10–3.12
(`.github/workflows/ci.yml`).

---

## Versioning and tags

This monorepo uses [Semantic Versioning](https://semver.org/). Shared release
tags are annotated git tags of the form `vX.Y.Z` (for example `v0.1.0`). All
four packages share the same version for this release train. See
`CHANGELOG.md` for release notes.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
the [Code of Conduct](CODE_OF_CONDUCT.md). For security reports, see
[SECURITY.md](SECURITY.md).

---

## Citation

If you use Evident in academic or industry work, please cite it. A machine-readable
citation is available in [`CITATION.cff`](CITATION.cff).

---

## License

BSD 3-Clause License. See [LICENSE](LICENSE).
