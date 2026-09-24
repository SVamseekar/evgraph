# evgraph-cli

[![PyPI](https://img.shields.io/pypi/v/evgraph-cli.svg)](https://pypi.org/project/evgraph-cli/)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://github.com/SVamseekar/evgraph/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

**The `evgraph` command-line tool for [Evgraph](https://github.com/SVamseekar/evgraph).**

## What is it

`evgraph-cli` gives shell scripts, CI pipelines, and pre-commit hooks the
same governance scan the `evgraph` Python API exposes, without writing any
Python. It is intentionally a *thin* wrapper: this package contains no
logic of its own beyond argument parsing and output-format selection —
scanning and reporting are entirely delegated to
`evgraph.scan()` / `evgraph.scan_dataset_manifest()` / `Report`, so the CLI
and the library can never drift in behavior. EU AI Assurance OS pins this package at `evgraph-cli==0.1.2`. A missing approval timestamp stays inconclusive. The scan does not invent the field.

## Main features

- **`evgraph scan MODEL_CARD APPROVAL DEPLOYMENT`** — runs the Model Card
  adapter across the three linked artifacts and prints a `Report`.
- **`evgraph scan-dataset-manifest MANIFEST`** — runs the dataset-manifest
  adapter over a CSV file and prints a `Report`.
- **`--format {json,markdown,sarif,oscal}`** — selects how the report is
  rendered (default `json`); `sarif` for CI annotations, `markdown` for a
  human-readable review, `oscal` for compliance tooling.
- **`--gate`** — after printing the report, return exit code `1` when gate
  evaluation finds evidence expectations not met.
- **`--gate --strict`** — also return exit code `1` when gate evaluation finds
  inconclusive evidence.

## Exit codes

By default, completed scans are report-only: findings are printed and the CLI
returns `0`, even when the report contains unmet evidence expectations. Use
`--gate` when a shell script or CI pipeline should trip on those findings, and
`--gate --strict` when inconclusive findings should also trip the gate.

- `0` — the command completed and no requested gate tripped.
- `1` — `--gate` was requested and gate evaluation tripped.
- `2` — usage, tool, adapter, or input error.

Gate exit codes are automation signals over evidence findings, not legal or
regulatory compliance verdicts.

## Where to get it

The source is hosted on GitHub at: https://github.com/SVamseekar/evgraph

Binary installers for the latest released version are available at the
[Python Package Index (PyPI)](https://pypi.org/project/evgraph-cli/):

```bash
pip install evgraph-cli
```

From source, for contributing:

```bash
git clone https://github.com/SVamseekar/evgraph.git
cd evgraph
pip install -e reference/python/evgraph-core
pip install -e reference/python/evgraph-rules
pip install -e reference/python/evgraph
pip install -e reference/python/evgraph-cli
```

## Dependencies

- [`evgraph`](https://pypi.org/project/evgraph/) — installed automatically
  as a dependency, which in turn pulls in `evgraph-core` and
  `evgraph-rules`.

`pytest>=7` is required for the test suite
(`pip install "evgraph-cli[test]"`).

## Quickstart

```bash
evgraph scan model_card.json approval.json deployment.json --format markdown
evgraph scan-dataset-manifest dataset_manifest.csv --format json
```

In a CI pipeline, emitting SARIF lets findings show up as inline annotations
in tools that already consume that format:

```bash
evgraph scan model_card.json approval.json deployment.json --format sarif > evgraph.sarif
```

## Documentation

| For | Start here |
| --- | --- |
| The Python API this CLI wraps | [`evgraph`](https://pypi.org/project/evgraph/) package README |
| Output format details (SARIF, OSCAL) | [`docs/specs/`](https://github.com/SVamseekar/evgraph/tree/main/docs/specs) |
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
