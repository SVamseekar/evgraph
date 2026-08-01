# evident-cli

Command-line interface for [Evident](https://github.com/SVamseekar/evident).

Thin wrapper over the `evident` Python library—same behavior as the API,
usable from shells and CI.

```bash
evident scan model_card.json approval.json deployment.json --format markdown
evident scan-dataset-manifest dataset_manifest.csv --format json
```

## Install

```bash
pip install -e .
```

## License

BSD 3-Clause — see the monorepo `LICENSE`.
