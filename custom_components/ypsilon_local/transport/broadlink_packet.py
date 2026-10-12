"""BL3372 packet checks and single-send adapter for python-broadlink 1.0.6.

Only the write path uses the library's tested framing/endpoint internals. The
public send_packet method retries on silence and expired sessions, which is
inappropriate for commands whose physical delivery may already have occurred.
No global library methods are patched. Reads/authentication keep the library API.
"""
from __future__ import annotations

import asyncio
from typing import Any

from broadlink import exceptions as e

MAGIC = bytes.fromhex("5aa5aa555aa5aa55")


class PacketValidationError(ValueError):
    """A fixed, non-identifying packet validation reason."""


def validate_reply(response: bytes, device: Any, counter: int) -> bytes:
    """Validate the outer reply against the actual request, including auth."""
    if len(response) < 0x38 or response[:8] != MAGIC:
        raise PacketValidationError("invalid_broadlink_header")
    nominal = int.from_bytes(response[0x20:0x22], "little")
    actual = (sum(response, 0xBEAF) - sum(response[0x20:0x22])) & 0xFFFF
    if nominal != actual:
        raise PacketValidationError("invalid_broadlink_packet_checksum")
    if int.from_bytes(response[0x28:0x2A], "little") != counter:
        raise PacketValidationError("broadlink_counter_mismatch")
    if int.from_bytes(response[0x24:0x26], "little") != device.devtype:
        raise PacketValidationError("broadlink_device_type_mismatch")
    if response[0x2A:0x30] != bytes(device.mac)[::-1]:
        raise PacketValidationError("broadlink_mac_mismatch")
    return response


def require_packet_interface(device: Any) -> None:
    """Fail before I/O if a Core library update changes the required interface."""
    for name in ("_exchange", "_frame", "_endpoint", "_drop_endpoint"):
        if not callable(getattr(device, name, None)):
            raise PacketValidationError("unsupported_broadlink_packet_interface")
    if not hasattr(getattr(device, "_lock", None), "__aenter__") or not callable(
        getattr(getattr(device, "_recent", None), "append", None)
    ):
        raise PacketValidationError("unsupported_broadlink_packet_interface")


def guard_exchange(device: Any) -> None:
    """Validate auth/firmware/read replies on this device, before key changes.

    In 1.0.6 auth calls _exchange directly, bypassing send_packet. Capture the
    counter from its framed request rather than assuming a counter delta across
    the library's internal reauthentication. Preserve the original async API.
    """
    if getattr(device, "__dict__", {}).get("_runxin_reply_guard"):
        return
    require_packet_interface(device)
    original = device._exchange

    async def checked(packet: bytes) -> bytes:
        response = bytes(await original(packet))
        return validate_reply(response, device, int.from_bytes(packet[0x28:0x2A], "little"))

    try:
        device._exchange = checked
        device._runxin_reply_guard = True
    except (AttributeError, TypeError) as err:
        raise PacketValidationError("unsupported_broadlink_packet_interface") from err


async def send_packet_once(device: Any, packet_type: int, payload: bytes) -> bytes:
    """Send exactly one datagram; do not reauthenticate/replay this command.

    Calls the tested library's framing and endpoint primitives under its lock.
    Delayed/unrelated responses are discarded within one deadline. Cancellation
    closes the endpoint: the caller must reconcile delivery using a fresh read.
    """
    require_packet_interface(device)
    async with device._lock:
        packet = device._frame(packet_type, bytes(payload))
        transport, protocol = await device._endpoint()
        protocol.drain()
        counter = int.from_bytes(packet[0x28:0x2A], "little")
        device._recent.append(counter)
        try:
            async with asyncio.timeout(device.timeout):
                transport.sendto(packet)
                while True:
                    response, _ = await protocol.queue.get()
                    if response is None:
                        raise e.EndpointClosedError(-4013, "Endpoint closed")
                    if isinstance(response, Exception):
                        raise response
                    # Check a full header before using its counter. A late
                    # response is not an acknowledgement for this write.
                    if len(response) >= 0x38 and int.from_bytes(response[0x28:0x2A], "little") != counter:
                        continue
                    return validate_reply(bytes(response), device, counter)
        except TimeoutError as err:
            device._drop_endpoint()
            raise e.NetworkTimeoutError(-4000, "Network timeout") from err
        except BaseException:
            device._drop_endpoint()
            raise
