"""Exercise read-only model-1 setup, entities and blocked mutation routes in HA."""
from datetime import datetime, time
from types import MappingProxyType, SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
pytest.importorskip('homeassistant', reason='Requires requirements-test-ha.txt')
from homeassistant import config_entries
from homeassistant.const import Platform
from homeassistant.exceptions import ServiceValidationError
from .helpers import load
from .test_homeassistant import hass, _flow, _entity_context, _add_sensor
from .test_control_guards import _coordinator
from .test_model1 import reported_state

flow_mod = load('config_flow')
sensor_mod = load('sensor')
coordinator_mod = load('coordinator')
init_mod = load('__init__')
services_mod = load('services')
diagnostics_mod = load('diagnostics')


@pytest.mark.asyncio
async def test_model1_flow_explains_alpha_and_persists_read_only_policy(hass):
    flow = _flow(hass)
    flow._async_probe = AsyncMock(return_value=({'deviceModel': 1}, '02:00:00:00:00:01'))
    result = await flow.async_step_user({'host': '192.0.2.1'})
    assert result['step_id'] == 'readonly_alpha'
    result = await flow.async_step_readonly_alpha({})
    assert result['data'] == {'host': '192.0.2.1', 'controller_model': 1}
    assert result['options'] == {'auto_sync_clock': False, 'adaptive_polling': False}
    assert 'Alpha' in result['title']


@pytest.mark.asyncio
@pytest.mark.parametrize('field,value', [(4, (12, 0)), (6, 50), (7, 100), (10, (0, 0)), (34, 1), (43, 25), (47, 280)])
async def test_model1_rejects_all_existing_control_fields_before_any_io(hass, field, value):
    coordinator, client, _ = _coordinator(hass, 1)
    coordinator._async_strict_read = AsyncMock()
    with pytest.raises(ServiceValidationError) as err:
        await coordinator.async_write_and_verify({field: value})
    assert err.value.translation_key == 'model_write_not_allowed'
    client.write_fields.assert_not_called()
    coordinator._async_strict_read.assert_not_awaited()
    with pytest.raises(ServiceValidationError):
        await coordinator.async_start_regeneration()
    assert not coordinator._regeneration_requested
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
async def test_auto_clock_and_reload_cannot_override_configured_model1_policy(hass, monkeypatch):
    coordinator, client, entry = _coordinator(hass, 9, data={'controller_model': 1})
    coordinator.data = {'deviceModel': 9, 'currentTime': '00:00:00'}
    coordinator.auto_sync_clock = True  # Stored options or direct mutation cannot grant permission.
    coordinator._async_strict_read = AsyncMock()
    monkeypatch.setattr(coordinator_mod.dt_util, 'now', Mock(return_value=datetime(2026, 10, 7, 20, 0)))
    await coordinator._async_sync_clock_if_needed(coordinator.data)
    assert coordinator.read_only
    assert coordinator.data['_clockSyncs'] == 0
    client.write_fields.assert_not_called()
    coordinator._async_strict_read.assert_not_awaited()
    with pytest.raises(ServiceValidationError):
        await coordinator.async_write_and_verify({43: 25})


@pytest.mark.asyncio
async def test_model1_poll_retains_complete_state_and_sends_no_clock_write(hass, monkeypatch):
    coordinator, client, _ = _coordinator(hass, 1)
    coordinator.auto_sync_clock = True
    client.read_state.return_value = reported_state()
    monkeypatch.setattr(coordinator_mod.dt_util, 'now', Mock(return_value=datetime(2026, 10, 7, 12, 0)))
    for _ in range(2):
        data = await coordinator._async_update_data()
        assert data['resinVolume'] == 240
        assert data['_rawFieldBytes'][26] == [240, 0]
        assert data['_clockSyncs'] == 0
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('code', [9, 12])
async def test_existing_models_keep_first_refresh_clock_sync(hass, monkeypatch, code):
    coordinator, client, _ = _coordinator(hass, code)
    coordinator.data = None  # HA has not published the first successful poll yet.
    coordinator.auto_sync_clock = True
    monkeypatch.setattr(coordinator_mod.dt_util, 'now', Mock(return_value=datetime(2026, 10, 7, 12, 0)))
    baseline = {'deviceModel': code, 'currentTime': '00:00:00'}
    coordinator._async_strict_read = AsyncMock(side_effect=[baseline, {**baseline, 'currentTime': '12:00:00'}])
    data = baseline.copy()
    await coordinator._async_sync_clock_if_needed(data)
    client.write_fields.assert_called_once_with({4: (12, 0)})
    assert data['_clockSyncs'] == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('automatic', [False, True])
async def test_fresh_model1_identity_blocks_pending_clock_write(hass, monkeypatch, automatic):
    coordinator, client, _ = _coordinator(hass, 9)
    coordinator._async_strict_read = AsyncMock(return_value={'deviceModel': 1, 'currentTime': '00:00:00'})
    monkeypatch.setattr(coordinator_mod.dt_util, 'now', Mock(return_value=datetime(2026, 10, 7, 12, 0)))
    if automatic:
        coordinator.auto_sync_clock = True
        await coordinator._async_sync_clock_if_needed({'deviceModel': 9, 'currentTime': '00:00:00'})
    else:
        with pytest.raises(ServiceValidationError):
            await coordinator.async_write_and_verify({4: (12, 0)})
    assert coordinator.read_only
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
async def test_model1_startup_and_unload_forward_only_read_platforms(hass, monkeypatch):
    coordinator, client, entry = _coordinator(hass, 1)
    client.read_state.return_value = reported_state()
    forward = AsyncMock()
    unload = AsyncMock(return_value=True)
    monkeypatch.setattr(init_mod, '_get_store', Mock(return_value=SimpleNamespace(client=client, field52_cache={})))
    monkeypatch.setattr(hass.config_entries, 'async_forward_entry_setups', forward)
    monkeypatch.setattr(hass.config_entries, 'async_unload_platforms', unload)
    for _ in range(2):
        entry._async_set_state(hass, config_entries.ConfigEntryState.SETUP_IN_PROGRESS, None)
        assert await init_mod.async_setup_entry(hass, entry)
        assert entry.runtime_data.read_only
        assert await init_mod.async_unload_entry(hass, entry)
        await entry.runtime_data.async_shutdown()
    assert forward.call_args.args[1] == [Platform.BINARY_SENSOR, Platform.SENSOR]
    assert unload.call_args.args[1] == [Platform.BINARY_SENSOR, Platform.SENSOR]
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
async def test_manual_platform_setup_does_not_create_controls(hass):
    coordinator, client, entry = _coordinator(hass, 1)
    entry.runtime_data = coordinator
    add = Mock()
    for platform in ('number', 'time', 'button'):
        await load(platform).async_setup_entry(hass, entry, add)
    add.assert_not_called()
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
async def test_advanced_services_reject_loaded_model1_entries(hass, monkeypatch):
    from homeassistant.config_entries import ConfigEntryState
    coordinator, client, entry = _coordinator(hass, 1)
    mocked_entry = SimpleNamespace(domain='ypsilon_local', state=ConfigEntryState.LOADED,
                                  data={}, runtime_data=coordinator)
    monkeypatch.setattr(hass.config_entries, 'async_get_entry', Mock(return_value=mocked_entry))
    services_mod.async_setup_services(hass)
    for name, extra in [('write_fields', {'fields': {43: 25}}), ('advance_phase', {'phase': 1})]:
        with pytest.raises(ServiceValidationError) as err:
            await hass.services.async_call('ypsilon_local', name, {'config_entry_id': 'test', **extra}, blocking=True)
        assert err.value.translation_key == 'model_write_not_allowed'
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('key,expected,unit', [('resin_volume', 240, None), ('periodic_water', 15, None),
    ('daily_water', 215, 'L'), ('residual_water', 1304, 'L'), ('reference_hardness', 280, 'mg/L')])
async def test_model1_sensor_states_keep_uncertainty_and_disable_statistics(hass, key, expected, unit):
    coordinator, entry = _entity_context(hass, reported_state())
    desc = next(desc for desc in (*sensor_mod.SENSORS, *sensor_mod.READ_ONLY_SETTINGS) if desc.key == key)
    sensor = sensor_mod.YpsilonSensor(coordinator, entry, desc)
    assert sensor.native_value == expected
    assert sensor.native_unit_of_measurement == unit
    assert sensor.state_class is None
    assert sensor.extra_state_attributes['interpretation'] == 'reference_f79d_pending_app_validation'
    state = await _add_sensor(hass, sensor, f'sensor.model1_{key}')
    assert state.state == str(expected)
    assert state.attributes.get('unit_of_measurement') == unit
    assert 'state_class' not in state.attributes
    assert state.attributes['raw_field_bytes']


@pytest.mark.asyncio
async def test_reference_settings_exist_only_for_read_only_models(hass):
    for code in (1, 9, 12):
        coordinator, entry = _entity_context(hass, {**reported_state(), 'deviceModel': code})
        entry.runtime_data = coordinator
        entities = []
        await sensor_mod.async_setup_entry(hass, entry, lambda group: entities.extend(group))
        keys = {entity.entity_description.key for entity in entities}
        assert ('reference_clock' in keys) is (code == 1)
        assert len({entity.unique_id for entity in entities}) == len(entities)


@pytest.mark.asyncio
async def test_model1_diagnostics_include_raw_pairs_and_permissions_without_identifiers(hass):
    coordinator, client, entry = _coordinator(hass, 1)
    coordinator.data = {**reported_state(), 'mac': '02:00:00:00:00:01', 'host': '192.0.2.1'}
    client.firmware = 62016
    client.connection_diagnostics = {'stage': 'ready'}
    client.reauth_count = client.transient_retries = 0
    entry.runtime_data = coordinator
    diagnostics = await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics['state']['_rawFieldBytes'][26] == [240, 0]
    assert diagnostics['protocol']['model_support']['read_only']
    assert diagnostics['protocol']['model_support']['resin_volume_scale'] is None
    assert '192.0.2.1' not in str(diagnostics)
    assert '02:00:00:00:00:01' not in str(diagnostics)


@pytest.mark.asyncio
async def test_read_only_options_hide_clock_and_ignore_attempt_to_enable_it(hass):
    coordinator, client, entry = _coordinator(hass, 1, data={'controller_model': 1})
    options = flow_mod.YpsilonLocalOptionsFlow()
    options.hass = hass
    options.handler = entry.entry_id
    options.flow_id = 'model1-options'
    options.context = {'entry_id': entry.entry_id}
    # Use HA's real options-flow entry lookup.
    hass.config_entries._entries[entry.entry_id] = entry
    result = await options.async_step_init()
    keys = {key.schema for key in result['data_schema'].schema}
    assert 'auto_sync_clock' not in keys
    assert 'clock_tolerance_minutes' not in keys
    assert 'scan_interval' in keys
    result = await options.async_step_init({'scan_interval': 120, 'auto_sync_clock': True})
    assert result['data']['auto_sync_clock'] is False


@pytest.mark.asyncio
async def test_future_partial_permissions_filter_control_entities_without_copying_codec(hass, monkeypatch):
    from dataclasses import replace
    models = load('models')
    monkeypatch.setitem(models.CONTROLLER_MODELS, 9, replace(models.controller_model(9), allowed_write_fields=frozenset({4})))
    coordinator, client, entry = _coordinator(hass, 9)
    entry.runtime_data = coordinator
    entities = []
    for platform in ('number', 'time', 'button'):
        await load(platform).async_setup_entry(hass, entry, lambda group: entities.extend(group))
    assert len(entities) == 2
    assert isinstance(entities[0], load('time').YpsilonTime)
    assert entities[0].entity_description.field_id == 4
    assert isinstance(entities[1], load('button').YpsilonSyncClockButton)
    with pytest.raises(ServiceValidationError):
        await coordinator.async_write_and_verify({43: 25})
    client.write_fields.assert_not_called()


@pytest.mark.asyncio
async def test_diagnostics_do_not_export_arbitrary_connection_error_text(hass):
    coordinator, client, entry = _coordinator(hass, 1)
    coordinator.data = {**reported_state(), '_lastPollError': 'Device at 192.0.2.1 private-token'}
    client.firmware = 62016
    client.connection_diagnostics = {'stage': 'response', 'last_error': {'error_type': 'TimeoutError'}}
    client.reauth_count = client.transient_retries = 0
    entry.runtime_data = coordinator
    diagnostic = await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
    assert 'private-token' not in str(diagnostic)
    assert '192.0.2.1' not in str(diagnostic)
    assert coordinator.data['_lastPollError'] == 'Device at 192.0.2.1 private-token'
    assert diagnostic['connection']['transport']['last_error']['error_type'] == 'TimeoutError'


@pytest.mark.asyncio
async def test_dhcp_model1_uses_the_same_read_only_confirmation(hass):
    flow = _flow(hass, source=config_entries.SOURCE_DHCP)
    flow._async_probe = AsyncMock(return_value=({'deviceModel': 1}, '02:00:00:00:00:01'))
    from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
    result = await flow.async_step_dhcp(DhcpServiceInfo(ip='192.0.2.1', hostname='test', macaddress='020000000001'))
    assert result['step_id'] == 'discovery_confirm'
    result = await flow.async_step_discovery_confirm({})
    assert result['step_id'] == 'readonly_alpha'
    result = await flow.async_step_readonly_alpha({})
    assert result['data']['controller_model'] == 1


@pytest.mark.asyncio
async def test_missing_or_changed_identity_does_not_promote_provisional_sensor_statistics(hass):
    coordinator, entry = _entity_context(hass, reported_state())
    entry.data = {'controller_model': 1}
    desc = next(desc for desc in sensor_mod.SENSORS if desc.key == 'daily_water')
    sensor = sensor_mod.YpsilonSensor(coordinator, entry, desc)
    for code in (1, None, 9):
        coordinator.data['deviceModel'] = code
        assert sensor.state_class is None
        assert sensor.extra_state_attributes['interpretation'] == 'reference_f79d_pending_app_validation'
