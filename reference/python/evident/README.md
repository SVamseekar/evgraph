# evident

Python API for [Evident](https://github.com/SVamseekar/evident):
adapters, reporters, rule discovery, and the public `scan()` /
`scan_dataset_manifest()` entry points.

```python
from evident import scan

report = scan(model_card_path="model_card.json", ...)
```

## Install

```bash
pip install -e .
# optional MLflow adapter dependency:
pip install -e ".[mlflow]"
```

## License

BSD 3-Clause. See the monorepo `LICENSE` file.
