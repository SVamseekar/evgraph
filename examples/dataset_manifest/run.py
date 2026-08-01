"""Stage 2 demo: the second adapter (CSV) and second rule, pressure-testing APS-Core.

Run from reference/python/evident's environment:
    python examples/dataset_manifest/run.py
"""

from pathlib import Path

from evident import scan_dataset_manifest

HERE = Path(__file__).parent

report = scan_dataset_manifest(HERE / "dataset_manifest.csv")

print(report.to_json())
