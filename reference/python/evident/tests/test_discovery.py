from evident_rules.approval_precedes_deployment import ApprovalPrecedesDeploymentRule
from evident_rules.dataset_manifest_complete import DatasetManifestCompleteRule

from evident.discovery import discover_rules


def test_discover_rules_finds_both_reference_rules():
    rules = discover_rules()
    rule_types = {type(r) for r in rules}
    assert ApprovalPrecedesDeploymentRule in rule_types
    assert DatasetManifestCompleteRule in rule_types


def test_discovered_rules_are_instantiated():
    rules = discover_rules()
    for rule in rules:
        assert hasattr(rule, "id")
        assert hasattr(rule, "reasoning_class")
        assert callable(rule.evaluate)
