# Contributing to Evident

Thank you for considering a contribution. This document describes how to set
up a development environment, run tests, and propose changes.

## Code of conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Development setup

Requirements:

- Python 3.10 or newer
- A virtual environment (recommended)

```bash
git clone https://github.com/souravamseekarmarti/evident.git
cd evident
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e reference/python/evident-core
pip install -e reference/python/evident-rules
pip install -e reference/python/evident
pip install -e reference/python/evident-cli
pip install pytest
```

Optional dependencies used by specific adapters or validation:

```bash
pip install mlflow   # only needed for MLflow adapter tests / local demos
```

## Running tests

Each package is independently installable. Run tests from the package directory
so imports resolve correctly:

```bash
cd reference/python/evident-core && pytest -q
cd reference/python/evident-rules && pytest -q
cd reference/python/evident && pytest -q
cd reference/python/evident-cli && pytest -q
```

Or from the repository root after editable installs:

```bash
pytest reference/python/evident-core reference/python/evident-rules \
       reference/python/evident reference/python/evident-cli -q
```

## Project layout and dependency rule

Dependencies flow in one direction only (see `docs/ARCHITECTURE.md`):

```
CLI · Python API · Rule packs · Reporters
        ↓
   Adapter Protocol / Rule Evaluation
        ↓
   Evidence Graph (evident-core)
```

`evident-core` must not import higher-layer packages. Prefer new adapters,
rule packs, and reporters as separate packages or plugins rather than
expanding the core.

## What to contribute

Useful contributions include:

- Adapters for additional artifact formats
- Rules and rule packs (via the `evident.rules` entry-point group)
- Reporters for additional output formats
- Bug fixes and test coverage
- Clarifications to specifications grounded in implementation experience

Out of scope (see architecture non-goals):

- Compliance verdicts or legal determination engines
- Hosted SaaS dashboards or workflow products
- Changes that raise evidence levels beyond what adapters declare

## Pull request checklist

1. Tests pass for every package you touch.
2. New public behavior is covered by tests.
3. Spec or architecture changes are justified by a concrete need in the
   reference implementation (grounding discipline).
4. Commit messages describe *why* the change exists, in complete sentences.
5. No secrets, credentials, or local-only paths are committed.

## Versioning and releases

Packages share a monorepo version tag (`vX.Y.Z`). Version numbers follow
[Semantic Versioning](https://semver.org/). Notable changes are recorded in
`CHANGELOG.md`.

## Reporting security issues

See [SECURITY.md](SECURITY.md). Do not open public issues for vulnerabilities.
