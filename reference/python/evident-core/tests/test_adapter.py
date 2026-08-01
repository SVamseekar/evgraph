from evident_core import AdapterError, Assumption


def test_assumption_holds_id_and_statement():
    a = Assumption(id="X-001", statement="something is assumed")
    assert a.id == "X-001"
    assert a.statement == "something is assumed"


def test_adapter_error_chains_cause_and_carries_identity():
    original = ValueError("bad input")
    try:
        try:
            raise original
        except ValueError as exc:
            raise AdapterError(adapter_name="test-adapter", adapter_version="0.1.0", message="failed") from exc
    except AdapterError as err:
        assert err.adapter_name == "test-adapter"
        assert err.adapter_version == "0.1.0"
        assert err.message == "failed"
        assert err.__cause__ is original
