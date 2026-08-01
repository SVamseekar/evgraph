"""Stage 1 reference-implementation demo: from evident import scan.

Run from reference/python/evident's environment:
    python examples/model_card_deployment/run.py
"""

from pathlib import Path

from evident import scan

HERE = Path(__file__).parent

report = scan(
    model_card_path=HERE / "model_card.json",
    approval_path=HERE / "approval.json",
    deployment_path=HERE / "deployment.json",
)

print(report.to_json())
