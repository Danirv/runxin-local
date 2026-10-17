"""Regress the namespace collision with the real legacy package installed."""
import importlib.metadata
import inspect
from unittest.mock import Mock

import broadlink_async
import pytest

from .test_async_broadlink import api, probe, wire


@pytest.fixture
def legacy(monkeypatch):
    try:
        legacy_version = importlib.metadata.version("broadlink")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("Run in the dedicated legacy-coexistence environment")
    assert legacy_version == "0.19.0"
    import broadlink
    assert not inspect.iscoroutinefunction(broadlink.hello)
    assert inspect.iscoroutinefunction(broadlink_async.hello)
    assert broadlink.__file__ != broadlink_async.__file__
    assert broadlink.exceptions.AuthenticationError is not broadlink_async.exceptions.AuthenticationError
    forbidden = Mock(side_effect=AssertionError("Legacy device I/O must not be used"))
    monkeypatch.setattr(broadlink, "hello", forbidden)
    yield forbidden
    forbidden.assert_not_called()


@pytest.mark.asyncio
async def test_real_async_auth_read_and_single_write_with_legacy_installed(legacy, wire, monkeypatch):
    device, peer = wire
    from unittest.mock import AsyncMock
    monkeypatch.setattr(broadlink_async, "hello", AsyncMock(return_value=device))
    client = api.YpsilonLocalClient("127.0.0.1")
    try:
        assert (await client.read_identity())["deviceModel"] == 9
        assert (await client.read_state({}))["resinVolume"] == 24
        previous = len(peer.frames)
        await client.write_fields({43: 25})
        assert len(peer.frames) == previous + 1
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_readonly_collector_uses_new_distribution_with_legacy_installed(legacy, wire, monkeypatch):
    device, peer = wire
    from unittest.mock import AsyncMock
    monkeypatch.setattr(broadlink_async, "hello", AsyncMock(return_value=device))
    report = await probe.probe("127.0.0.1", timeout=0.08)
    assert report["summary"]["status"] == "complete"
    assert report["summary"]["fields_observed_count"] == 52
    assert report["broadlink_distribution"] == "broadlink-async"
    assert report["broadlink_version"] == "1.1.0"
    assert len(peer.frames) == 4
