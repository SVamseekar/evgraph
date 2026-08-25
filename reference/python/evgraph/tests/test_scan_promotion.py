from pathlib import Path
from dataclasses import dataclass, field
from importlib import import_module

import pytest

from evgraph import scan, scan_promotion

REPO_ROOT = Path(__file__).resolve().parents[4]
EXAMPLE_DIR = REPO_ROOT / "examples" / "model_card_deployment"


@dataclass
class FakeRegisteredModel:
    name: str
    description: str | None
    creation_timestamp: int


@dataclass
class FakeModelVersion:
    version: str
    status: str
    description: str | None
    source: str
    creation_timestamp: int
    run_id: str


@dataclass
class FakeRunInfo:
    run_id: str
    status: str
    user_id: str | None


@dataclass
class FakeRunData:
    tags: dict = field(default_factory=dict)


@dataclass
class FakeRun:
    info: FakeRunInfo
    data: FakeRunData


class FakeMlflowClient:
    def __init__(self, registered_model, versions, runs_by_id):
        self._registered_model = registered_model
        self._versions = versions
        self._runs_by_id = runs_by_id

    def get_registered_model(self, name):
        if name != self._registered_model.name:
            raise KeyError(name)
        return self._registered_model

    def search_model_versions(self, filter_string):
        return self._versions

    def get_run(self, run_id):
        return self._runs_by_id[run_id]


def make_promotion_client():
    registered_model = FakeRegisteredModel(
        name="risk-scorer-v3",
        description="Credit risk scoring model",
        creation_timestamp=1785255931998,
    )
    version = FakeModelVersion(
        version="1",
        status="READY",
        description="v3, trained on internal warehouse data",
        source="runs:/abc123/model",
        creation_timestamp=1785255932011,
        run_id="abc123",
    )
    run = FakeRun(
        info=FakeRunInfo(run_id="abc123", status="FINISHED", user_id="alice"),
        data=FakeRunData(tags={"team": "risk-eng"}),
    )
    return FakeMlflowClient(registered_model, [version], {"abc123": run})


def test_scan_promotion_json_matches_scan():
    kwargs = dict(
        model_card_path=EXAMPLE_DIR / "model_card.json",
        approval_path=EXAMPLE_DIR / "approval.json",
        deployment_path=EXAMPLE_DIR / "deployment.json",
    )
    a = scan(**kwargs)
    b = scan_promotion(**kwargs)
    assert [f.outcome for f in a.findings] == [f.outcome for f in b.findings]
    assert [f.rule_id for f in a.findings] == [f.rule_id for f in b.findings]


def test_scan_promotion_rejects_partial_args():
    with pytest.raises(ValueError):
        scan_promotion(model_card_path=EXAMPLE_DIR / "model_card.json")


def test_scan_promotion_mlflow_composes(monkeypatch):
    scan_module = import_module("evgraph.scan")
    monkeypatch.setattr(scan_module, "_mlflow_client", lambda tracking_uri: make_promotion_client())

    report = scan_promotion(
        model_card_path=EXAMPLE_DIR / "model_card.json",
        approval_path=EXAMPLE_DIR / "approval.json",
        deployment_path=EXAMPLE_DIR / "deployment.json",
        mlflow_tracking_uri="http://test",
        mlflow_model_name="risk-scorer-v3",
        mlflow_model_version="1",
    )

    types = {n.type for n in report.graph.nodes}
    assert "ModelCard" in types
    assert "MLflowModelVersion" in types
    assert any(e.type == "REFERS_TO_REGISTRY_VERSION" for e in report.graph.edges)


def test_mlflow_client_import_error_mentions_extra(monkeypatch):
    scan_module = import_module("evgraph.scan")
    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "mlflow.tracking":
            raise ImportError("missing mlflow")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ImportError, match=r'pip install "evgraph\[mlflow\]"'):
        scan_module._mlflow_client("http://test")
