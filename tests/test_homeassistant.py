"""Regressions using real Home Assistant classes and mocked device I/O.

The lightweight offline job skips this module; the dedicated HA job installs
requirements-test-ha.txt and executes it against the pinned stable release.
These tests verify software behaviour, not physical controller acceptance.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
import logging
from types import SimpleNamespace
from types import MappingProxyType
from unittest.mock import AsyncMock, Mock, patch

import broadlink.exceptions
import pytest

pytest.importorskip("homeassistant", reason="Requires requirements-test-ha.txt")
import pytest_asyncio

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.helpers.entity_platform import EntityPlatform
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo

from .helpers import load
from .test_model12 import STATE_FRAME

flow_mod = load("config_flow")
sensor_mod = load("sensor")
number_mod = load("number")
button_mod = load("button")
services_mod = load("services")
diagnostics_mod = load("diagnostics")
codec = load("runxin.f79d")

TEST_HOST = "192.0.2.12"
TEST_MAC = "02:00:00:00:00:12"


@pytest_asyncio.fixture
async def hass(tmp_path):
    """Provide the real flow/state APIs without starting integrations or networking."""
    instance = HomeAssistant(str(tmp_path))
    instance.config_entries = config_entries.ConfigEntries(instance, {})
    device_registry.async_setup(instance)
    await device_registry.async_load(instance)
    await entity_registry.async_load(instance)
    instance.data["ypsilon_test_components"] = []
    yield instance
    for platform in instance.data["ypsilon_test_components"]:
        await platform.async_reset()
    await instance.async_stop()


def _flow(hass, *, source=config_entries.SOURCE_USER):
    flow = flow_mod.YpsilonLocalConfigFlow()
    flow.hass = hass
    flow.handler = "ypsilon_local"
    flow.flow_id = "test-model-flow"
    flow.context = {"source": source}
    return flow


def _entity_context(hass, data, *, title="Euro-Clear Midnight"):
    entry = SimpleNamespace(unique_id=TEST_MAC, entry_id="test-entry", title=title)
    coordinator = SimpleNamespace(
        hass=hass,
        data=data,
        config_entry=None,
        last_update_success=True,
        client=SimpleNamespace(firmware=62016),
        async_add_listener=Mock(return_value=lambda: None),
    )
    return coordinator, entry


async def _add_sensor(hass, sensor, entity_id):
    """Register the entity on a real HA platform before writing its state."""
    sensor.entity_id = entity_id
    entry = config_entries.ConfigEntry(
        domain="ypsilon_local", unique_id=TEST_MAC, title=sensor._entry.title,
        data={"host": TEST_HOST}, options={}, source=config_entries.SOURCE_USER,
        version=2, minor_version=1, discovery_keys=MappingProxyType({}),
        subentries_data=[],
    )
    # Register the real entry while mocking setup, so no actual device is polled.
    with patch.object(hass.config_entries, "async_setup", AsyncMock(return_value=True)):
        await hass.config_entries.async_add(entry)
    platform = EntityPlatform(
        hass=hass, logger=logging.getLogger(__name__), domain="sensor",
        platform_name="ypsilon_local", platform=None,
        scan_interval=timedelta(seconds=60), entity_namespace=None,
    )
    platform.config_entry = entry
    hass.data["ypsilon_test_components"].append(platform)
    await platform.async_add_entities([sensor])
    return hass.states.get(sensor.entity_id)


@pytest.mark.asyncio
@pytest.mark.parametrize("model,title", [(9, "Ypsilon G6"), (12, "Euro-Clear Midnight")])
async def test_manual_flow_creates_supported_model_with_mac_identity(hass, model, title):
    flow = _flow(hass)
    flow._async_probe = AsyncMock(return_value=({"deviceModel": model}, TEST_MAC))
    result = await flow.async_step_user({"host": f" {TEST_HOST} "})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == title
    assert result["data"] == {"host": TEST_HOST}
    assert result["version"] == 2
    assert flow.unique_id == format_mac(TEST_MAC)
    flow._async_probe.assert_awaited_once_with(TEST_HOST)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "identity,mac,error",
    [({"deviceModel": 10}, TEST_MAC, "unsupported_device"),
     ({"deviceModel": 12}, None, "cannot_connect")],
)
async def test_manual_flow_rejects_unsupported_model_or_missing_identity(hass, identity, mac, error):
    flow = _flow(hass)
    flow._async_probe = AsyncMock(return_value=(identity, mac))
    result = await flow.async_step_user({"host": TEST_HOST})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}


@pytest.mark.asyncio
@pytest.mark.parametrize("model,title", [(9, "Ypsilon G6"), (12, "Euro-Clear Midnight")])
async def test_dhcp_flow_reprobes_before_creating_entry(hass, model, title):
    flow = _flow(hass, source=config_entries.SOURCE_DHCP)
    flow._async_probe = AsyncMock(return_value=({"deviceModel": model}, TEST_MAC))
    discovery = DhcpServiceInfo(ip=TEST_HOST, hostname="test-softener", macaddress=TEST_MAC)
    result = await flow.async_step_dhcp(discovery)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"
    assert flow.context["confirm_only"] is True
    assert flow.unique_id == format_mac(TEST_MAC)
    result = await flow.async_step_discovery_confirm({})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == title
    assert result["data"] == {"host": TEST_HOST}
    assert flow._async_probe.await_count == 2


@pytest.mark.asyncio
async def test_discovery_rejects_model_that_changes_before_confirmation(hass):
    flow = _flow(hass, source=config_entries.SOURCE_DHCP)
    flow._async_probe = AsyncMock(side_effect=[({"deviceModel": 12}, TEST_MAC), ({"deviceModel": 10}, TEST_MAC)])
    await flow.async_step_dhcp(DhcpServiceInfo(ip=TEST_HOST, hostname="test", macaddress=TEST_MAC))
    result = await flow.async_step_discovery_confirm({})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unsupported_device"


@pytest.mark.asyncio
@pytest.mark.parametrize("fails", [False, True])
async def test_probe_always_closes_temporary_client(hass, monkeypatch, fails):
    client = Mock(mac=TEST_MAC)
    client.connection_diagnostics = {}
    if fails:
        client.read_identity.side_effect = flow_mod.YpsilonConnectionError("test failure")
    else:
        client.read_identity.return_value = {"deviceModel": 12}
    monkeypatch.setattr(flow_mod, "YpsilonLocalClient", Mock(return_value=client))
    if fails:
        with pytest.raises(flow_mod.YpsilonConnectionError):
            await _flow(hass)._async_probe(TEST_HOST)
    else:
        identity, mac = await _flow(hass)._async_probe(TEST_HOST)
        assert identity["deviceModel"] == 12
        assert mac == TEST_MAC
    client.close.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("model,raw,expected", [(9, 24, 24), (12, 250, 25.0)])
async def test_resin_sensor_preserves_scaling_unit_and_unique_id(hass, model, raw, expected):
    data = codec.decode_tlvs({1: (model, 0), 26: (raw, 0)})
    coordinator, entry = _entity_context(hass, data)
    description = next(desc for desc in sensor_mod.SENSORS if desc.key == "resin_volume")
    sensor = sensor_mod.YpsilonSensor(coordinator, entry, description)
    assert sensor.native_value == expected
    assert sensor.native_unit_of_measurement == "L"
    assert sensor.unique_id == f"{TEST_MAC}_resin_volume"
    assert sensor.extra_state_attributes["raw_bytes"] == [raw, 0]
    state = await _add_sensor(hass, sensor, "sensor.test_resin_volume")
    assert float(state.state) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("key,field,raw", [("output_relay_mode", "outRelayMode", 2), ("work_pattern", "workPattern", 255)])
async def test_unknown_enum_writes_unknown_state_and_preserves_raw_code(hass, key, field, raw):
    coordinator, entry = _entity_context(hass, {field: raw})
    description = next(desc for desc in sensor_mod.SENSORS if desc.key == key)
    # Enable the diagnostic in this test as a user can, preserving its normal
    # disabled-by-default setting in the integration.
    description = replace(description, entity_registry_enabled_default=True)
    sensor = sensor_mod.YpsilonSensor(coordinator, entry, description)
    assert sensor.native_value is None
    assert sensor.extra_state_attributes["raw_code"] == raw
    state = await _add_sensor(hass, sensor, f"sensor.test_{key}")
    assert state.state == "unknown"
    assert state.attributes["raw_code"] == raw


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "model,manufacturer,model_name,title",
    [(9, "ATH / BWT / Runxin", "F79D / Ypsilon G6", "Ypsilon G6"),
     (12, "Euro-Clear / Runxin", "Model 12 / Euro-Clear Midnight", "Euro-Clear Midnight")],
)
async def test_device_identity_uses_model_metadata_and_keeps_mac_identifier(hass, model, manufacturer, model_name, title):
    coordinator, entry = _entity_context(hass, {"deviceModel": model}, title=title)
    sensor = sensor_mod.YpsilonSensor(coordinator, entry, sensor_mod.SENSORS[0])
    info = sensor.device_info
    assert info["manufacturer"] == manufacturer
    assert info["model"] == model_name
    assert info["name"] == title
    assert info["identifiers"] == {("ypsilon_local", TEST_MAC)}
    assert sensor.unique_id == f"{TEST_MAC}_flow_rate"


@pytest.mark.asyncio
async def test_alpha_model_controls_remain_available_with_same_commands(hass):
    coordinator, entry = _entity_context(hass, codec.decode_frame(STATE_FRAME))
    coordinator.async_write_and_verify = AsyncMock()
    for desc in number_mod.NUMBERS:
        entity = number_mod.YpsilonNumber(coordinator, entry, desc)
        assert entity.available
        entity._async_write = AsyncMock()
        value = 2.0 if desc.key == "flow_rate_off" else (160 if desc.key == "raw_water_hardness" else 24)
        await entity.async_set_native_value(value)
        raw = 200 if desc.key == "flow_rate_off" else value
        entity._async_write.assert_awaited_once_with({desc.field_id: raw}, value)
    button = button_mod.YpsilonRegenerationButton(coordinator, entry)
    await button.async_press()
    coordinator.async_write_and_verify.assert_awaited_once_with({34: 1}, accept_station_active=True)
    # The advanced service still validates unit-2 field 7 with the same raw range.
    services_mod._validate_raw_fields(coordinator, {7: 200, 47: 160})


@pytest.mark.asyncio
async def test_diagnostics_include_model_evidence_and_raw_resin_bytes(hass):
    coordinator, entry = _entity_context(hass, codec.decode_frame(STATE_FRAME))
    coordinator.scan_interval = 60
    coordinator.client.transient_retries = 0
    coordinator.client.reauth_count = 0
    coordinator.client.connection_diagnostics = {
        "stage": "ready", "devtype": 0x520F, "advertised_lock": False, "last_error": None,
    }
    coordinator.data.update({"host": TEST_HOST, "mac": TEST_MAC})
    entry.version = 2
    entry.options = {}
    entry.data = {"host": TEST_HOST}
    entry.runtime_data = coordinator
    diagnostics = await diagnostics_mod.async_get_config_entry_diagnostics(hass, entry)
    support = diagnostics["protocol"]["model_support"]
    assert support["support_level"] == "alpha"
    assert support["hardware_verified_write_fields"] == [4, 6, 10, 43]
    assert support["pending_write_fields"] == [7, 34, 47]
    assert diagnostics["state"]["_raw_resinVolumeBytes"] == (250, 0)
    assert TEST_HOST not in str(diagnostics)
    assert TEST_MAC not in str(diagnostics)
    assert diagnostics["connection"]["transport"]["stage"] == "ready"
    assert diagnostics_mod._semantic_protocol_summary(None) is None


@pytest.mark.asyncio
@pytest.mark.parametrize("step", ["user", "dhcp", "discovery_confirm", "reconfigure"])
@pytest.mark.parametrize("kind,expected", [
    ("locked", "device_locked"), ("rejected", "invalid_auth"), ("timeout", "cannot_connect"),
])
async def test_setup_paths_distinguish_rejected_auth_from_timeout(hass, step, kind, expected):
    flow = _flow(hass)
    error = (
        flow_mod.YpsilonConnectionError("timeout") if kind == "timeout"
        else flow_mod.YpsilonAuthenticationError(-1, kind == "locked")
    )
    flow._async_probe = AsyncMock(side_effect=error)
    if step == "dhcp":
        result = await flow.async_step_dhcp(DhcpServiceInfo(ip=TEST_HOST, hostname="test", macaddress=TEST_MAC))
        assert result["reason"] == expected
    else:
        if step == "discovery_confirm":
            flow.discovered_host = TEST_HOST
        elif step == "reconfigure":
            flow._get_reconfigure_entry = Mock(return_value=SimpleNamespace(data={"host": TEST_HOST}))
        result = await getattr(flow, f"async_step_{step}")({"host": TEST_HOST})
        assert result["errors"] == {"base": expected}


@pytest.mark.asyncio
async def test_real_probe_logs_safe_authentication_context_before_entry_exists(hass, monkeypatch, caplog):
    transport_mod = load("transport.broadlink_bl3372")
    device = Mock(devtype=0x520F, is_locked=True)
    device.auth.side_effect = broadlink.exceptions.AuthenticationError(-1, f"{TEST_HOST} {TEST_MAC} secret-key")
    monkeypatch.setattr(transport_mod.broadlink, "hello", Mock(return_value=device))
    with caplog.at_level(logging.DEBUG):
        result = await _flow(hass).async_step_user({"host": TEST_HOST})
    assert result["errors"] == {"base": "device_locked"}
    assert "Local setup probe failed" in caplog.text
    assert "transport_stage=authentication" in caplog.text
    assert "error_code=-1" in caplog.text
    assert "advertised_lock=True" in caplog.text
    for private in (TEST_HOST, TEST_MAC, "secret-key"):
        assert private not in caplog.text
    device.auth.assert_called_once_with()
    device.send_packet.assert_not_called()
    device.set_lock.assert_not_called()


@pytest.mark.asyncio
async def test_real_short_auth_response_is_connection_error_even_with_advertised_lock(hass, monkeypatch, caplog):
    transport_mod = load("transport.broadlink_bl3372")
    device = transport_mod.broadlink.Device((TEST_HOST, 80), bytes(6), 0x520F, is_locked=True)
    device.send_packet = Mock(return_value=bytes(0x38) + bytes(16))
    device.decrypt = Mock(return_value=bytes(16))
    monkeypatch.setattr(transport_mod.broadlink, "hello", Mock(return_value=device))
    with caplog.at_level(logging.WARNING):
        result = await _flow(hass).async_step_user({"host": TEST_HOST})
    assert result["errors"] == {"base": "cannot_connect"}
    assert "transport_stage=authentication" in caplog.text
    assert "error_type=ValueError" in caplog.text
    assert "result=cannot_connect" in caplog.text
    assert TEST_HOST not in caplog.text
    assert [call.args[0] for call in device.send_packet.call_args_list] == [0x65]
