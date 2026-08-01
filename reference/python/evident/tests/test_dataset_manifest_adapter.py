from pathlib import Path

import pytest
from evident_core import AdapterError, EvidenceLevel

from evident.adapters.dataset_manifest import DatasetManifestAdapter, DatasetManifestArtifact

SCRATCH = Path(__file__).parent / "_scratch"


def write_csv(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "manifest.csv"
    p.write_text(content)
    return p


def test_scan_produces_one_dataset_node_per_row(tmp_path):
    csv_path = write_csv(
        tmp_path,
        "dataset_id,source,license,contains_pii\n"
        "training-v3,internal-warehouse,CC-BY-4.0,false\n"
        "eval-set-2,internal-warehouse,,true\n",
    )
    graph = DatasetManifestAdapter().scan(DatasetManifestArtifact(manifest_path=csv_path))

    assert len(graph.nodes) == 2
    assert all(n.type == "Dataset" for n in graph.nodes)
    assert all(n.evidence_level == EvidenceLevel.STRUCTURAL for n in graph.nodes)
    assert graph.edges == ()

    by_id = {n.attributes["dataset_id"]: n for n in graph.nodes}
    assert by_id["training-v3"].attributes["license"] == "CC-BY-4.0"
    assert by_id["training-v3"].attributes["contains_pii"] is False
    assert by_id["eval-set-2"].attributes["license"] == ""
    assert by_id["eval-set-2"].attributes["contains_pii"] is True


def test_missing_required_column_raises_adapter_error(tmp_path):
    csv_path = write_csv(tmp_path, "dataset_id,source\ntraining-v3,internal-warehouse\n")
    with pytest.raises(AdapterError):
        DatasetManifestAdapter().scan(DatasetManifestArtifact(manifest_path=csv_path))


def test_empty_dataset_id_raises_adapter_error(tmp_path):
    csv_path = write_csv(
        tmp_path,
        "dataset_id,source,license,contains_pii\n,internal-warehouse,CC-BY-4.0,false\n",
    )
    with pytest.raises(AdapterError):
        DatasetManifestAdapter().scan(DatasetManifestArtifact(manifest_path=csv_path))


def test_missing_file_raises_adapter_error(tmp_path):
    with pytest.raises(AdapterError):
        DatasetManifestAdapter().scan(DatasetManifestArtifact(manifest_path=tmp_path / "nope.csv"))


def test_adapter_declares_aps_core_fields():
    adapter = DatasetManifestAdapter()
    assert adapter.name == "evident-adapter-dataset-manifest"
    assert adapter.evidence_level == EvidenceLevel.STRUCTURAL
    assert adapter.supported_source_kinds == ["csv"]
    assert len(adapter.assumptions) >= 1
