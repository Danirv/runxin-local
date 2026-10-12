"""Real async library/AES/UDP regressions; a loopback peer replaces hardware."""
from __future__ import annotations

import asyncio
import importlib.metadata
import inspect
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import broadlink
from broadlink import exceptions
import pytest
import pytest_asyncio

from .helpers import broadlink_reply, load

packet = load("transport.broadlink_packet")
transport_mod = load("transport.broadlink_bl3372")
framing = load("runxin.framing")
api = load("api")
WRITE_PAYLOAD = transport_mod.pack_tfb(load("runxin.f79d").build_write_fields({43: 25}))
probe = load("compatibility")


class Peer(asyncio.DatagramProtocol):
    """A BroadLink/Runxin peer using the real library's AES implementation."""

    def __init__(self):
        self.crypto = broadlink.Device(("127.0.0.1", 80), bytes.fromhex("020000000009"), 0x520F)
        self.key = bytes.fromhex("11112222333344445555666677778888")
        self.frames = []
        self.drop = False
        self.error = 0
        self.delayed_counter = False
        self.values = {f: (0, 0) for f in range(1, 53)}
        self.values.update({1: (9, 0), 8: (2, 0), 26: (24, 0)})

    def connection_made(self, transport):
        self.endpoint = transport

    def datagram_received(self, data, addr):
        self.frames.append(bytes(data))
        command = int.from_bytes(data[0x26:0x28], "little")
        if command == 0x65:
            self.crypto.update_aes(bytes.fromhex("097628343fe99e23765c1513accf8b02"))
        payload = self.crypto.decrypt(data[0x38:])
        if self.drop:
            return
        if self.error:
            plaintext = bytes(16)
        elif command == 0x65:
            plaintext = (1234).to_bytes(4, "little") + self.key
        elif payload[:1] == b"\x68":
            plaintext = bytes(4) + (62016).to_bytes(2, "little")
        else:
            inner = framing.inner_frame(payload[2:2 + int.from_bytes(payload[:2], "little")])
            if inner[3] == 0x09:
                triples = [v for f in inner[4:-2] for v in (f, *self.values[f])]
                product = framing.build_frame(framing.QUERY_RESPONSE_CODE, triples)
            else:
                product = framing.build_frame(framing.WRITE_RESPONSE_CODE, [])
            plaintext = len(product).to_bytes(2, "little") + product
        body = b"" if self.error else self.crypto.encrypt(plaintext + bytes((-len(plaintext)) % 16))
        self.crypto.count = int.from_bytes(data[0x28:0x2A], "little")
        reply = broadlink_reply(self.crypto, body, self.error)
        if self.delayed_counter:
            old = bytearray(reply)
            old[0x28:0x2A] = ((self.crypto.count - 1) & 0xFFFF).to_bytes(2, "little")
            old[0x20:0x22] = bytes(2)
            old[0x20:0x22] = (sum(old, 0xBEAF) & 0xFFFF).to_bytes(2, "little")
            self.endpoint.sendto(old, addr)
        self.endpoint.sendto(reply, addr)
        if command == 0x65:
            self.crypto.update_aes(self.key)


@pytest_asyncio.fixture
async def wire():
    loop = asyncio.get_running_loop()
    endpoint, peer = await loop.create_datagram_endpoint(Peer, local_addr=("127.0.0.1", 0))
    device = broadlink.Device(endpoint.get_extra_info("sockname"), bytes.fromhex("020000000009"), 0x520F)
    device.timeout = 0.08
    yield device, peer
    await device.aclose()
    endpoint.close()
    await asyncio.sleep(0)


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [None, -5, -7])
async def test_write_sends_one_real_datagram_without_replay_or_reauth(wire, error, monkeypatch):
    device, peer = wire
    # Make the library retry interval shorter than our timeout: a call to its
    # public send_packet would retransmit, and -7 would also reauthenticate.
    monkeypatch.setattr(broadlink.device, "DEFAULT_RETRY_INTVL", 0.01)
    peer.drop = error is None
    peer.error = error or 0
    if error is None:
        with pytest.raises(exceptions.NetworkTimeoutError):
            await packet.send_packet_once(device, 0x6A, WRITE_PAYLOAD)
    else:
        reply = await packet.send_packet_once(device, 0x6A, WRITE_PAYLOAD)
        assert int.from_bytes(reply[0x22:0x24], "little", signed=True) == error
    await asyncio.sleep(0.025)
    assert len(peer.frames) == 1
    assert int.from_bytes(peer.frames[0][0x26:0x28], "little") == 0x6A


@pytest.mark.asyncio
async def test_write_discards_delayed_reply_and_waits_without_resending(wire):
    device, peer = wire
    peer.delayed_counter = True
    await packet.send_packet_once(device, 0x6A, WRITE_PAYLOAD)
    assert len(peer.frames) == 1


@pytest.mark.asyncio
async def test_write_cancellation_closes_endpoint_and_does_not_resend(wire):
    device, peer = wire
    peer.drop = True
    task = asyncio.create_task(packet.send_packet_once(device, 0x6A, WRITE_PAYLOAD))
    for _ in range(30):
        if peer.frames:
            break
        await asyncio.sleep(0.001)
    assert len(peer.frames) == 1
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert device._transport is None
    assert len(peer.frames) == 1


@pytest.mark.asyncio
async def test_real_auth_aes_reads_and_adapter_identity_with_loopback_peer(wire, monkeypatch):
    device, peer = wire
    monkeypatch.setattr(broadlink, "hello", AsyncMock(return_value=device))
    client = api.YpsilonLocalClient("127.0.0.1")
    try:
        identity = await client.read_identity()
        state = await client.read_state({})
        assert identity["deviceModel"] == 9
        assert identity["mac"] == "020000000009"
        assert state["resinVolume"] == 24
        assert state["_rawFieldBytes"][26] == [24, 0]
        assert client.firmware == 62016
        assert client.write_policy["allowed_write_fields"] == [4, 6, 7, 10, 34, 43, 47]
    finally:
        await client.close()
    assert device._transport is None
    assert {int.from_bytes(f[0x26:0x28], "little") for f in peer.frames} == {0x65, 0x6A}


@pytest.mark.asyncio
async def test_real_async_readonly_scan_auth_guard_and_raw_fields(wire, monkeypatch):
    device, peer = wire
    peer.values[1] = (15, 0)
    monkeypatch.setattr(broadlink, "hello", AsyncMock(return_value=device))
    report = await probe.probe("127.0.0.1", timeout=0.08)
    assert report["authentication"]["ok"]
    assert report["summary"]["fields_observed_count"] == 52
    assert report["controller"]["code"] == 15
    assert not report["controller"]["supported_for_normal_use"]
    assert device._transport is None
    assert len(peer.frames) == 4  # auth, firmware, identity, full read
    assert "020000000009" not in json.dumps(report)


@pytest.mark.asyncio
async def test_cancelled_readonly_authentication_closes_real_endpoint(wire, monkeypatch):
    device, peer = wire
    peer.drop = True
    monkeypatch.setattr(broadlink, "hello", AsyncMock(return_value=device))
    task = asyncio.create_task(probe.probe("127.0.0.1", timeout=1))
    for _ in range(30):
        if peer.frames:
            break
        await asyncio.sleep(0.001)
    assert peer.frames
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert device._transport is None


@pytest.mark.asyncio
async def test_ambiguous_adapter_write_is_not_replayed_during_fresh_read(wire, monkeypatch):
    device, peer = wire
    monkeypatch.setattr(broadlink, "hello", AsyncMock(return_value=device))
    client = api.YpsilonLocalClient("127.0.0.1")
    client._transport.timeout = 0.05
    try:
        await client.read_identity()
        baseline_calls = len(peer.frames)
        peer.drop = True
        with pytest.raises(api.YpsilonConnectionError):
            await client.write_fields({43: 25})
        assert len(peer.frames) == baseline_calls + 1
        peer.drop = False
        state = await client.read_state({})
        assert state["saltAddition"] == 0
        assert client._transport.diagnostics["stage"] == "ready"
        # Recovery adds auth/firmware-free queries; it cannot replay the SET.
        writes = 0
        for frame in peer.frames:
            if int.from_bytes(frame[0x26:0x28], "little") != 0x6A:
                continue
            plaintext = peer.crypto.decrypt(frame[0x38:])
            if plaintext[:1] == b"\x68":
                continue
            inner = framing.inner_frame(plaintext[2:2 + int.from_bytes(plaintext[:2], "little")])
            writes += inner[3] == 0x19
        assert writes == 1
    finally:
        await client.close()


def test_core_and_runxin_share_the_async_distribution_without_old_package():
    pytest.importorskip("homeassistant")
    from homeassistant.components.broadlink.device import BroadlinkDevice
    from homeassistant.components.broadlink import device as core_broadlink
    assert importlib.metadata.version("python-broadlink") == "1.0.6"
    with pytest.raises(importlib.metadata.PackageNotFoundError):
        importlib.metadata.version("broadlink")
    assert core_broadlink.blk is broadlink
    assert inspect.iscoroutinefunction(broadlink.hello)
    assert inspect.iscoroutinefunction(BroadlinkDevice.async_auth)
    manifest = json.loads((Path(__file__).parents[1] / "custom_components/ypsilon_local/manifest.json").read_text())
    assert manifest["requirements"] == ["python-broadlink==1.0.6"]


@pytest.mark.asyncio
async def test_read_closed_endpoint_recovery_has_one_session_budget(monkeypatch):
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.1")
    transact = AsyncMock(side_effect=[exceptions.EndpointClosedError(-4013), b"ok"])
    monkeypatch.setattr(transport, "_transact_once", transact)
    monkeypatch.setattr(transport, "_drop_session", AsyncMock())
    assert await transport.transact(b"frame") == b"ok"
    assert transact.await_count == 2
    assert transport.reauth_count == 1


@pytest.mark.asyncio
async def test_old_overwritten_runtime_fails_before_device_io(monkeypatch):
    hello = Mock()
    monkeypatch.setattr(broadlink, "hello", hello)
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.1")
    with pytest.raises(transport_mod.RunxinTransportError, match="Incompatible BroadLink runtime"):
        await transport.transact(b"frame")
    hello.assert_not_called()
