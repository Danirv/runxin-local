"""Reported model-1 bytes and effective write policy, without HA or hardware."""
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from .helpers import load

models = load('models')
codec = load('runxin.f79d')
framing = load('runxin.framing')
api = load('api')
client_mod = load('runxin.client')


def reported_pairs():
    records = json.loads(Path(__file__).with_name('fixtures').joinpath('model1_fields.json').read_text())
    return {int(field): tuple(pair) for field, pair in records['fields'].items()}


def reported_state():
    state = codec.decode_tlvs(reported_pairs())
    state['_rawFieldBytes'] = {field: list(pair) for field, pair in reported_pairs().items()}
    return state


def synthetic_response():
    # Reconstructed with our framing builder; never label this a wire capture.
    payload = [byte for field, pair in reported_pairs().items() for byte in (field, *pair)]
    return framing.build_frame(framing.QUERY_RESPONSE_CODE, payload)


def test_reported_pairs_decode_without_claiming_physical_conversions():
    state = reported_state()
    assert len(reported_pairs()) == 52
    assert state['deviceModel'] == 1
    assert state['station'] == 0
    assert state['waterVolumeUnit'] == 1
    assert state['resinVolume'] == 240
    assert state['periodicWaterProduction'] == 15
    assert state['residualWaterProduction'] == 1304
    assert state['dailyWaterConsumption'] == 215
    assert state['averageWeeklyWaterConsumption'] == 192
    assert state['rawWaterHardness'] == 280
    assert state['saltAddition'] == 25
    assert models.resin_volume_litres(240, 1) is None
    assert codec.decode_frame(synthetic_response()) == codec.decode_tlvs(reported_pairs())


def test_models_default_to_read_only_and_evidence_does_not_enable_writes():
    new_model = models.ControllerModel(code=99, title='Test', model_name='Test', manufacturer='Test',
                                      hardware_verified_write_fields=(4,))
    assert new_model.read_only
    assert new_model.allowed_write_fields == frozenset()
    assert models.model_support_details(1)['read_only']
    assert models.model_support_details(1)['allowed_write_fields'] == []
    for code in (9, 12):
        assert models.controller_model(code).allowed_write_fields == frozenset({4, 6, 7, 10, 34, 43, 47})
        assert not models.controller_model(code).read_only
    assert models.controller_model(True) is None
    assert models.controller_protocol_name(1) == 'F150'


def test_raw_capture_is_opt_in_and_does_not_change_query_bytes():
    transport = Mock()
    transport.transact.return_value = synthetic_response()
    client = client_mod.F79DClient(transport, capture_raw=True)
    data = client.read_state()
    assert data['_rawFieldBytes'][26] == [240, 0]
    assert data['_rawFieldBytes'][42] == [0, 15]
    transport.transact.assert_called_once_with(codec.build_query(list(range(1, 52))))
    plain = client_mod.F79DClient(transport).read_state()
    assert '_rawFieldBytes' not in plain


@pytest.mark.parametrize('code', [None, 1, 14, True])
def test_composition_adapter_blocks_non_writable_or_unknown_models_before_transport(code):
    client = api.YpsilonLocalClient('192.0.2.1')
    client._f79d = Mock()
    client._observe_model({'deviceModel': code})
    with pytest.raises(api.YpsilonConnectionError):
        client.write_fields({43: 25})
    client._f79d.write_fields.assert_not_called()
    client.close()


def test_model1_write_block_is_latched_across_missing_or_changed_identity():
    client = api.YpsilonLocalClient('192.0.2.1')
    client._f79d = Mock()
    for state in ({'deviceModel': 1}, {}, {'deviceModel': 9}):
        client._observe_model(state)
        with pytest.raises(api.YpsilonConnectionError):
            client.write_fields({4: (20, 38)})
    client._f79d.write_fields.assert_not_called()
    client.close()


@pytest.mark.parametrize('code', [9, 12])
def test_existing_controller_write_payload_and_settle_policy_are_unchanged(code, monkeypatch):
    client = api.YpsilonLocalClient('192.0.2.1')
    client._f79d = Mock()
    client._observe_model({'deviceModel': code})
    sleep = Mock()
    monkeypatch.setattr(api.time, 'sleep', sleep)
    client.write_fields({7: 200, 43: 25})
    client._f79d.write_fields.assert_called_once_with({7: 200, 43: 25})
    sleep.assert_called_once_with(api.WRITE_SETTLE_DELAY)
    with pytest.raises(api.YpsilonConnectionError):
        client.write_fields({49: 1})
    client.close()


@pytest.mark.parametrize('length', range(6))
def test_short_inner_frames_raise_a_protocol_error_instead_of_index_error(length):
    malformed = bytearray(synthetic_response())
    malformed[19] = length
    malformed[-2] = sum(malformed[:-2]) & 255
    with pytest.raises(load('runxin.errors').RunxinProtocolError, match='too short'):
        codec.decode_frame(bytes(malformed))


@pytest.mark.parametrize('reading', [True, False])
def test_response_opcode_must_match_read_or_write_request(reading):
    transport = Mock()
    opcode = framing.WRITE_RESPONSE_CODE if reading else framing.QUERY_RESPONSE_CODE
    response = framing.build_frame(opcode, [])
    transport.transact.return_value = transport.transact_write.return_value = response
    client = client_mod.F79DClient(transport)
    with pytest.raises(load('runxin.errors').RunxinProtocolError, match='opcode'):
        client.read_identity() if reading else client.write_fields({43: 25})
    transport.invalidate.assert_called_once()
