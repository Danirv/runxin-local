"""HA coexistence, unload/reload and revocation using the async client."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import broadlink
import pytest

pytest.importorskip("homeassistant")
from homeassistant.components.broadlink.device import BroadlinkDevice

from .helpers import io_mock, load
from .test_homeassistant import hass
from .test_async_broadlink import wire

api = load("api")
init_mod = load("__init__")


@pytest.mark.asyncio
async def test_core_device_and_runxin_use_real_async_auth_without_global_patch(hass, wire, monkeypatch):
    device, peer = wire
    original_send = broadlink.Device.send_packet
    original_exchange = broadlink.Device._exchange
    monkeypatch.setattr(broadlink, "hello", AsyncMock(return_value=device))
    client = api.YpsilonLocalClient("127.0.0.1")
    native = BroadlinkDevice(hass, SimpleNamespace(title="Core device"))
    native.api = broadlink.Device(device.host, device.mac, device.devtype)
    native.api.timeout = 0.08
    try:
        assert (await client.read_identity())["deviceModel"] == 9
        assert await native._async_get_firmware_version() == 62016
        assert (await client.read_state({}))["resinVolume"] == 24
        assert broadlink.Device.send_packet is original_send
        assert broadlink.Device._exchange is original_exchange
    finally:
        await client.close()
        await native.api.aclose()
    assert device._transport is None
    assert native.api._transport is None


@pytest.mark.asyncio
async def test_unload_closes_session_and_reload_replaces_client_preserving_cache(hass, monkeypatch):
    entry = SimpleNamespace(entry_id="async-entry", data={"host": "192.0.2.1"}, options={},
                            runtime_data=SimpleNamespace(platforms=[]))
    clients = []

    def create(host, **kwargs):
        client = io_mock(host=host)
        clients.append(client)
        return client

    monkeypatch.setattr(init_mod, "YpsilonLocalClient", create)
    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", AsyncMock(return_value=True))
    store = await init_mod._get_store(hass, entry)
    store.field52_cache["value"] = 300
    first = store.client
    assert await init_mod.async_unload_entry(hass, entry)
    first.revoke_writes.assert_called_once()
    first.close.assert_awaited_once()
    assert store.inactive
    replacement = await init_mod._get_store(hass, entry)
    assert replacement is store
    assert replacement.field52_cache == {"value": 300}
    assert replacement.client is clients[1]
    assert not replacement.inactive


@pytest.mark.asyncio
async def test_revocation_blocks_write_waiting_for_operation_lock():
    client = api.YpsilonLocalClient("192.0.2.1")
    client._f79d = io_mock()
    client._observe_model({"deviceModel": 9})
    await client._lock.acquire()
    task = asyncio.create_task(client.write_fields({43: 25}))
    await asyncio.sleep(0)
    client.revoke_writes()
    client._lock.release()
    with pytest.raises(api.YpsilonConnectionError):
        await task
    client._f79d.write_fields.assert_not_awaited()
    await client.close()


@pytest.mark.asyncio
async def test_close_blocks_queued_read_from_reopening_removed_client():
    client = api.YpsilonLocalClient("192.0.2.1")
    client._f79d = io_mock()
    await client._lock.acquire()
    read = asyncio.create_task(client.read_identity())
    close = asyncio.create_task(client.close())
    await asyncio.sleep(0)
    client._lock.release()
    with pytest.raises(api.YpsilonConnectionError, match="closed"):
        await read
    await close
    client._f79d.read_identity.assert_not_awaited()
    client._f79d.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_first_refresh_closes_session_and_marks_store_inactive(hass, monkeypatch):
    entry = SimpleNamespace(entry_id="failed-entry", data={"host": "192.0.2.1"})
    store = init_mod.YpsilonStore(client=io_mock())
    coordinator = SimpleNamespace(async_config_entry_first_refresh=AsyncMock(side_effect=RuntimeError("offline")))
    monkeypatch.setattr(init_mod, "_get_store", AsyncMock(return_value=store))
    monkeypatch.setattr(init_mod, "YpsilonDataUpdateCoordinator", lambda *args: coordinator)
    with pytest.raises(RuntimeError, match="offline"):
        await init_mod.async_setup_entry(hass, entry)
    assert store.inactive
    store.client.close.assert_awaited_once()
