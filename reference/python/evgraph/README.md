# evgraph

Main Python library for [Evgraph](https://github.com/SVamseekar/evgraph).

Use this package for day-to-day work: adapters, reporters, rule discovery, and
the public scan API.

```python
from evgraph import scan, scan_dataset_manifest

report = scan(
    model_card_path="model_card.json",
    approval_path="approval.json",
    deployment_path="deployment.json",
)
print(report.to_json())
```

## Features

- **Adapters:** Model Card (JSON), dataset manifest (CSV), MLflow registry
- **Reporters:** JSON, Markdown, SARIF, OSCAL
- **API:** `scan()`, `scan_dataset_manifest()`, `discover_rules()`

## Install

```bash
pip install -e .
pip install -e ".[mlflow]"   # optional, for the MLflow adapter
```

## License

BSD 3-Clause — see the monorepo `LICENSE`.
