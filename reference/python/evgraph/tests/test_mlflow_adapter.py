"""Tests for the MLflow adapter using a fake client — no live MLflow server
required for the test suite. The adapter's real behavior against a live
server is documented, with real transcripts, in
docs/research/mlflow-adapter-validation.md; these tests pin the same
node/edge shapes down for regression purposes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest
from evgraph_core import AdapterError, EvidenceLevel

from evgraph.adapters.mlflow_adapter import MLflowAdapter, MLflowModelSource


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


def make_client_with_clean_and_messy_versions():
    registered_model = FakeRegisteredModel(
        name="risk-scorer", description="Credit risk scoring model", creation_timestamp=1785255931998
    )
    clean_version = FakeModelVersion(
        version="1",
        status="READY",
        description="v3, trained on internal warehouse data",
        source="runs:/abc123/model",
        creation_timestamp=1785255932011,
        run_id="abc123",
    )
    messy_version = FakeModelVersion(
        version="2",
        status="READY",
        description="",
        source="s3://some-bucket/manually-uploaded-model",
        creation_timestamp=1785255932022,
        run_id="",
    )
    run = FakeRun(
        info=FakeRunInfo(run_id="abc123", status="FINISHED", user_id="alice"),
        data=FakeRunData(tags={"team": "risk-eng"}),
    )
    return FakeMlflowClient(
        registered_model, [clean_version, messy_version], {"abc123": run}
    )


def test_registered_model_and_versions_become_nodes():
    client = make_client_with_clean_and_messy_versions()
    graph = MLflowAdapter().scan(client, MLflowModelSource(registered_model_name="risk-scorer"))

    node_types = {n.type for n in graph.nodes}
    assert node_types == {"MLflowRegisteredModel", "MLflowModelVersion", "MLflowRun"}
    assert all(n.evidence_level == EvidenceLevel.STRUCTURAL for n in graph.nodes)


def test_clean_version_has_trained_by_edge():
    client = make_client_with_clean_and_messy_versions()
    graph = MLflowAdapter().scan(client, MLflowModelSource(registered_model_name="risk-scorer"))

    clean_version_node = next(n for n in graph.nodes if n.attributes.get("version") == "1")
    assert clean_version_node.attributes["has_linked_run"] is True
    trained_by_edges = [
        e for e in graph.edges if e.source_id == clean_version_node.id and e.type == "TRAINED_BY"
    ]
    assert len(trained_by_edges) == 1


def test_messy_version_with_no_run_id_has_no_trained_by_edge_and_no_error():
    """A ModelVersion with an empty run_id is evidence, not an adapter failure (APS-Core §4.2)."""
    client = make_client_with_clean_and_messy_versions()
    graph = MLflowAdapter().scan(client, MLflowModelSource(registered_model_name="risk-scorer"))

    messy_version_node = next(n for n in graph.nodes if n.attributes.get("version") == "2")
    assert messy_version_node.attributes["has_linked_run"] is False
    assert messy_version_node.attributes["description"] == ""
    trained_by_edges = [e for e in graph.edges if e.source_id == messy_version_node.id and e.type == "TRAINED_BY"]
    assert trained_by_edges == []


def test_unknown_registered_model_raises_adapter_error():
    client = make_client_with_clean_and_messy_versions()
    with pytest.raises(AdapterError):
        MLflowAdapter().scan(client, MLflowModelSource(registered_model_name="does-not-exist"))


def test_model_version_of_edges_link_every_version_to_the_model():
    client = make_client_with_clean_and_messy_versions()
    graph = MLflowAdapter().scan(client, MLflowModelSource(registered_model_name="risk-scorer"))

    model_node = next(n for n in graph.nodes if n.type == "MLflowRegisteredModel")
    model_version_of_edges = [e for e in graph.edges if e.type == "MODEL_VERSION_OF"]
    assert len(model_version_of_edges) == 2
    assert all(e.target_id == model_node.id for e in model_version_of_edges)
