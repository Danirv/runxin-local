"""Tests for transport/client contracts and bounded delivery behavior."""

from __future__ import annotations

import json
import logging
from unittest.mock import AsyncMock, Mock

import broadlink.exceptions
import pytest

from .helpers import broadlink_reply, io_mock, load

client_mod = load("runxin.client")
framing = load("runxin.framing")
transport_mod = load("transport.broadlink_bl3372")


def _empty_write_response() -> bytes:
    header = [0x5A, 0x5C, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0x12, 0, 0]
    inner = [0xDF, 0xFD, 0, framing.WRITE_RESPONSE_CODE, 0, 0xDE]
    header[15] = len(inner)
    inner[2] = len(inner)
    inner[-2] = sum(inner[:-2]) & 0xFF
    frame = header + inner + [0, 0xA5]
    frame[2] = len(frame)
    frame[-2] = sum(frame[:-2]) & 0xFF
    return bytes(frame)


@pytest.mark.asyncio
async def test_client_prefers_write_specific_hook() -> None:
    class Fake:
        def __init__(self) -> None:
            self.reads = 0
            self.writes = 0

        async def transact(self, frame: bytes) -> bytes:
            self.reads += 1
            return _empty_write_response()

        async def transact_write(self, frame: bytes) -> bytes:
            self.writes += 1
            return _empty_write_response()

    fake = Fake()
    client = client_mod.F79DClient(fake)
    await client.write_fields({43: 50})
    assert fake.writes == 1
    assert fake.reads == 0


@pytest.mark.asyncio
async def test_write_path_never_retries_ambiguous_error(monkeypatch) -> None:
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.1")
    calls = 0

    async def fail_once(frame: bytes, **kwargs) -> bytes:
        nonlocal calls
        calls += 1
        raise transport_mod.BroadlinkOuterError(-5)

    monkeypatch.setattr(transport, "_transact_once", fail_once)
    with pytest.raises(transport_mod.BroadlinkOuterError):
        await transport.transact_write(b"frame")
    assert calls == 1


@pytest.mark.asyncio
async def test_read_transient_retries_are_bounded(monkeypatch) -> None:
    transport = transport_mod.BroadlinkBL3372Transport(
        "192.0.2.1", transient_delays=(0.0, 0.0)
    )
    calls = 0

    async def eventually_ok(frame: bytes) -> bytes:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise transport_mod.BroadlinkOuterError(-5)
        return b"ok"

    monkeypatch.setattr(transport, "_transact_once", eventually_ok)
    monkeypatch.setattr(transport_mod.asyncio, "sleep", AsyncMock())
    monkeypatch.setattr(transport_mod.random, "uniform", lambda _a, _b: 0.0)
    assert await transport.transact(b"frame") == b"ok"
    assert calls == 3
    assert transport.transient_retries == 2


@pytest.mark.asyncio
async def test_reauth_budget_does_not_consume_transient_budget(monkeypatch) -> None:
    transport = transport_mod.BroadlinkBL3372Transport(
        "192.0.2.1", transient_delays=(0.0, 0.0)
    )
    sequence = [-1, -5, -5, 0]

    async def sequence_reply(frame: bytes) -> bytes:
        code = sequence.pop(0)
        if code:
            raise transport_mod.BroadlinkOuterError(code)
        return b"ok"

    monkeypatch.setattr(transport, "_transact_once", sequence_reply)
    monkeypatch.setattr(transport, "_drop_session", AsyncMock())
    monkeypatch.setattr(transport_mod.asyncio, "sleep", AsyncMock())
    monkeypatch.setattr(transport_mod.random, "uniform", lambda _a, _b: 0.0)
    assert await transport.transact(b"frame") == b"ok"
    assert transport.reauth_count == 1
    assert transport.transient_retries == 2


@pytest.mark.parametrize("locked", [True, False, None])
@pytest.mark.parametrize("method", ["transact", "transact_write"])
@pytest.mark.asyncio
async def test_rejected_handshake_retains_evidence_without_sending_runxin(
    monkeypatch, caplog, locked, method
) -> None:
    secret = "192.0.2.17 02:00:00:00:00:17 private-session-key"
    device = io_mock(devtype=0x520F, is_locked=locked)
    device.auth = AsyncMock()
    device.auth.side_effect = broadlink.exceptions.AuthenticationError(-1, secret)
    hello = AsyncMock(return_value=device)
    monkeypatch.setattr(transport_mod.broadlink, "hello", hello)
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.17")
    with caplog.at_level(logging.DEBUG, logger=transport_mod.__name__):
        with pytest.raises(transport_mod.BroadlinkAuthenticationError) as caught:
            await getattr(transport, method)(b"private-frame")
    assert caught.value.code == -1
    assert caught.value.is_locked is locked
    assert isinstance(caught.value.__cause__, broadlink.exceptions.AuthenticationError)
    hello.assert_called_once_with("192.0.2.17", timeout=5)
    device.auth.assert_called_once_with()
    device.send_packet.assert_not_called()
    device.set_lock.assert_not_called()
    device.get_fwversion.assert_not_called()
    assert transport._device is None
    assert transport.reauth_count == 0
    details = transport.diagnostics
    assert details["stage"] == "authentication"
    assert details["devtype"] == 0x520F
    assert details["advertised_lock"] is locked
    assert details["last_error"] == {
        "stage": "authentication", "error_type": "AuthenticationError", "error_code": -1,
    }
    safe_output = json.dumps(details) + caplog.text + str(caught.value)
    for value in secret.split() + ["private-frame"]:
        assert value not in safe_output
    details["last_error"]["error_code"] = 123
    assert transport.diagnostics["last_error"]["error_code"] == -1


@pytest.mark.asyncio
async def test_false_auth_result_is_rejected_without_runxin(monkeypatch) -> None:
    device = io_mock(devtype=0x520F, is_locked=False)
    device.auth = AsyncMock()
    device.auth.return_value = False
    monkeypatch.setattr(transport_mod.broadlink, "hello", AsyncMock(return_value=device))
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.17")
    with pytest.raises(transport_mod.BroadlinkAuthenticationError):
        await transport.transact(b"frame")
    device.send_packet.assert_not_called()
    assert transport.diagnostics["last_error"]["error_code"] is None


@pytest.mark.asyncio
async def test_advertised_lock_does_not_prevent_successful_auth_or_change_packet(monkeypatch) -> None:
    device = io_mock(devtype=0x520F, is_locked=True)
    device.auth = AsyncMock()
    device.auth.return_value = True
    device.get_fwversion = AsyncMock()
    device.get_fwversion.return_value = 62016
    device.send_packet = AsyncMock()
    device.send_packet.return_value = bytes(0x38) + bytes(16)
    device.decrypt.return_value = transport_mod.pack_tfb(b"reply") + bytes(9)
    monkeypatch.setattr(transport_mod.broadlink, "hello", AsyncMock(return_value=device))
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.17")
    assert await transport.transact(b"frame") == b"reply"
    assert transport.identifier is not None
    device.send_packet.assert_called_once_with(0x6A, transport_mod.pack_tfb(b"frame"))
    device.set_lock.assert_not_called()
    assert transport.firmware == 62016
    assert transport.diagnostics["stage"] == "ready"
    assert transport.diagnostics["advertised_lock"] is True
    assert transport.diagnostics["last_error"] is None


@pytest.mark.parametrize("stage", ["discovery", "authentication"])
@pytest.mark.asyncio
async def test_timeout_is_not_classified_as_authentication_rejection(monkeypatch, stage) -> None:
    error = broadlink.exceptions.NetworkTimeoutError(-4000, "private-host")
    device = io_mock(devtype=0x520F, is_locked=True)
    if stage == "discovery":
        hello = AsyncMock(side_effect=error)
    else:
        hello = AsyncMock(return_value=device)
        device.auth = AsyncMock()
        device.auth.side_effect = error
    monkeypatch.setattr(transport_mod.broadlink, "hello", hello)
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.17")
    with pytest.raises(transport_mod.RunxinTransportError) as caught:
        await transport.transact(b"frame")
    assert not isinstance(caught.value, transport_mod.BroadlinkAuthenticationError)
    assert transport.diagnostics["last_error"] == {
        "stage": stage, "error_type": "NetworkTimeoutError", "error_code": -4000,
    }
    assert "private-host" not in json.dumps(transport.diagnostics)
    device.send_packet.assert_not_called()


@pytest.mark.asyncio
async def test_later_success_preserves_historical_error_but_reports_ready_stage(monkeypatch) -> None:
    device = io_mock(devtype=0x520F, is_locked=False)
    device.auth = AsyncMock()
    device.auth.side_effect = [broadlink.exceptions.AuthenticationError(-1, "rejected"), True]
    device.get_fwversion.return_value = 62016
    device.send_packet.return_value = bytes(0x38) + bytes(16)
    device.decrypt.return_value = transport_mod.pack_tfb(b"reply") + bytes(9)
    monkeypatch.setattr(transport_mod.broadlink, "hello", AsyncMock(return_value=device))
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.17")
    with pytest.raises(transport_mod.BroadlinkAuthenticationError):
        await transport.transact(b"frame")
    assert await transport.transact(b"frame") == b"reply"
    assert transport.diagnostics["stage"] == "ready"
    assert transport.diagnostics["last_error"]["stage"] == "authentication"
    assert transport.diagnostics["last_error"]["error_code"] == -1
    assert device.auth.call_count == 2
    device.send_packet.assert_called_once_with(0x6A, transport_mod.pack_tfb(b"frame"))


@pytest.mark.asyncio
async def test_short_real_broadlink_auth_response_is_transport_failure_not_rejection(monkeypatch) -> None:
    # The real 1.0.6 auth implementation passes a 12-byte session key to AES
    # when given only 16 decrypted bytes; cryptography raises ValueError.
    device = transport_mod.broadlink.Device(("192.0.2.17", 80), bytes(6), 0x520F)
    auth_exchange = AsyncMock(side_effect=lambda packet: broadlink_reply(device))
    device._exchange = auth_exchange
    device.decrypt = Mock(return_value=bytes(16))
    monkeypatch.setattr(transport_mod.broadlink, "hello", AsyncMock(return_value=device))
    transport = transport_mod.BroadlinkBL3372Transport("192.0.2.17")
    with pytest.raises(transport_mod.RunxinTransportError) as caught:
        await transport.transact(b"frame")
    assert not isinstance(caught.value, transport_mod.BroadlinkAuthenticationError)
    assert isinstance(caught.value.__cause__, ValueError)
    assert transport.diagnostics["last_error"] == {
        "stage": "authentication", "error_type": "ValueError", "error_code": None,
    }
    assert transport._device is None
    assert [int.from_bytes(call.args[0][0x26:0x28], "little") for call in auth_exchange.call_args_list] == [0x65]
    assert transport.reauth_count == 0


@pytest.mark.asyncio
async def test_rejected_authentication_releases_discovered_socket(monkeypatch):
    device = io_mock(devtype=0x520F, is_locked=True)
    device.auth = AsyncMock()
    device.auth.side_effect = broadlink.exceptions.AuthenticationError(-1)
    monkeypatch.setattr(transport_mod.broadlink, 'hello', AsyncMock(return_value=device))
    transport = transport_mod.BroadlinkBL3372Transport('192.0.2.1')
    with pytest.raises(transport_mod.BroadlinkAuthenticationError):
        await transport._connect()
    device.aclose.assert_awaited_once()
    assert transport._device is None
