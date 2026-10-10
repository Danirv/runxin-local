"""Opted-in model-1 adapter permissions with no sockets or hardware writes."""
from unittest.mock import Mock

import pytest
from .helpers import load

models = load("models")
api = load("api")


@pytest.mark.parametrize("writes,regen,fields", [
    (False, False, set()), (False, True, set()),
    (True, False, {4, 6, 10, 43, 47}), (True, True, {4, 6, 10, 34, 43, 47}),
])
def test_opt_in_permissions_do_not_claim_verification_or_change_other_models(writes, regen, fields):
    assert models.allowed_write_fields(1, model1_test_writes=writes,
                                       model1_test_regeneration=regen) == fields
    assert models.model_support_details(1)["hardware_verified_write_fields"] == [4]
    assert models.model_support_details(1)["pending_write_fields"] == [6, 10, 34, 43, 47]
    assert not models.model_support_details(1)["experimental_writes_verified"]
    assert models.model_support_details(1)["read_only"]
    for code in (9, 12, 14):
        assert models.allowed_write_fields(code, model1_test_writes=writes,
                                           model1_test_regeneration=regen) == models.EXISTING_CONTROL_FIELDS
    assert not models.allowed_write_fields(15, model1_test_writes=True)


def test_adapter_requires_each_opt_in_and_never_grants_flow_cutoff_or_vacation(monkeypatch):
    monkeypatch.setattr(api.time, "sleep", Mock())
    client = api.YpsilonLocalClient("192.0.2.1", model1_test_writes=True)
    client._f79d = Mock()
    client._observe_model({"deviceModel": 1})
    client.write_fields({43: 26})
    client._f79d.write_fields.assert_called_once_with({43: 26})
    for fields in ({7: 100}, {34: 1}, {49: 1}):
        with pytest.raises(api.YpsilonConnectionError):
            client.write_fields(fields)
    client._observe_model({"deviceModel": 9})
    with pytest.raises(api.YpsilonConnectionError):
        client.write_fields({7: 100})
    assert client.write_policy["allowed_write_fields"] == [4, 6, 10, 43, 47]
    client.revoke_writes()
    with pytest.raises(api.YpsilonConnectionError):
        client.write_fields({43: 25})
    client._f79d.write_fields.assert_called_once()
    client.close()


def test_mechanical_opt_in_permits_only_regeneration_start(monkeypatch):
    monkeypatch.setattr(api.time, "sleep", Mock())
    client = api.YpsilonLocalClient("192.0.2.1", model1_test_writes=True,
                                    model1_test_regeneration=True)
    client._f79d = Mock()
    client._observe_model({"deviceModel": 1})
    for value in (0, 2, 3, 4):
        with pytest.raises(api.YpsilonConnectionError):
            client.write_fields({34: value})
    with pytest.raises(api.YpsilonConnectionError):
        client.write_fields({34: 1, 43: 25})
    client.write_fields({34: 1})
    client._f79d.write_fields.assert_called_once_with({34: 1})
    client.close()
