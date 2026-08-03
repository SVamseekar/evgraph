# evgraph-cli

Command-line interface for [Evgraph](https://github.com/SVamseekar/evgraph).

Thin wrapper over the `evgraph` Python library—same behavior as the API,
usable from shells and CI.

```bash
evgraph scan model_card.json approval.json deployment.json --format markdown
evgraph scan-dataset-manifest dataset_manifest.csv --format json
```

## Install

```bash
pip install -e .
```

## License

BSD 3-Clause — see the monorepo `LICENSE`.
