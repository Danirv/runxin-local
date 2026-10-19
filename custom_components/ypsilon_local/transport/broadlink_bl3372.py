"""BroadLink BL3372 transport for raw Runxin transactions.

This module owns every BroadLink-specific concern: discovery/authentication,
0x6A packet transport, encryption, the two-byte TFB length envelope, outer
response errors, session refresh and the observed transient -5 retry policy.
The Runxin codec never imports this module or the `broadlink_async` package.

Read transactions may be retried within bounded budgets. Write transactions are
sent at most once: after a timeout/outer error the command may already have been
accepted by the physical controller, so retrying blindly could duplicate a
mechanical action. The Home Assistant layer reconciles ambiguous writes through
an independent read-back instead.
"""

from __future__ import annotations

import logging
import inspect
import random
import asyncio
from typing import Any

import broadlink_async as broadlink

from .broadlink_packet import guard_exchange, send_packet_once, PacketValidationError

from ..runxin.errors import RunxinTransportError
from .base import RunxinTransport

DEFAULT_DEVTYPE = 0x520F
DEFAULT_SOCKET_TIMEOUT = 5
DEFAULT_TRANSIENT_ERROR_CODE = -5
DEFAULT_AUTH_ERROR_CODES = frozenset({-1, -7})
DEFAULT_TRANSIENT_DELAYS = (0.4, 0.8)

_LOGGER = logging.getLogger(__name__)

BROADLINK_EXCEPTIONS = (
    broadlink.exceptions.BroadlinkException,
    OSError,
    TimeoutError,
    PacketValidationError,
)


class BroadlinkOuterError(RunxinTransportError):
    """BroadLink outer response error read from packet offset 0x22."""

    def __init__(self, code: int) -> None:
        self.code = code
        super().__init__(f"BroadLink outer error {code}")


class BroadlinkUnsupportedDeviceError(RunxinTransportError):
    """Discovery found a different BroadLink type, before authentication."""

    def __init__(self, devtype: int) -> None:
        self.devtype = devtype
        super().__init__(f"Unexpected devtype 0x{devtype:04x}")


class BroadlinkAuthenticationError(RunxinTransportError):
    """Local authentication was rejected, before any Runxin request was sent.

    The advertised lock is evidence from discovery, not proof of the cause.
    Preserve this distinction even when authentication succeeds on a device
    that advertises a lock. Never include a device repr, keys or packet bytes.
    """

    def __init__(self, code: int | None, is_locked: bool | None) -> None:
        self.code = code
        self.is_locked = is_locked
        super().__init__(
            "BroadLink local authentication rejected "
            f"(code={code}, advertised_lock={is_locked})"
        )


def pack_tfb(frame: bytes) -> bytes:
    """Wrap a raw Runxin frame in the BL3372 two-byte little-endian length."""
    return len(frame).to_bytes(2, "little") + frame


def unpack_tfb(plaintext: bytes) -> bytes:
    """Remove the BL3372 length prefix and ignore decrypted block padding."""
    if len(plaintext) < 2:
        raise RunxinTransportError("missing BL3372 TFB length prefix")
    declared = int.from_bytes(plaintext[:2], "little")
    if declared > len(plaintext) - 2:
        raise RunxinTransportError("BL3372 declared length exceeds plaintext")
    return plaintext[2:2 + declared]


class BroadlinkBL3372Transport(RunxinTransport):
    """Authenticated BroadLink transport carrying Runxin frames over 0x6A."""

    def __init__(
        self,
        host: str,
        *,
        expected_devtype: int | None = DEFAULT_DEVTYPE,
        timeout: float = DEFAULT_SOCKET_TIMEOUT,
        transient_error_code: int = DEFAULT_TRANSIENT_ERROR_CODE,
        auth_error_codes: frozenset[int] = DEFAULT_AUTH_ERROR_CODES,
        transient_delays: tuple[float, ...] = DEFAULT_TRANSIENT_DELAYS,
    ) -> None:
        self.host = host
        self.expected_devtype = expected_devtype
        self.timeout = timeout
        self.transient_error_code = transient_error_code
        self.auth_error_codes = auth_error_codes
        self.transient_delays = transient_delays

        self._device: Any = None
        self._firmware: int | None = None
        self._lock = asyncio.Lock()
        self.transient_retries = 0
        self.reauth_count = 0
        self._stage = "not_started"
        self._devtype: int | None = None
        self._is_locked: bool | None = None
        self._last_error: dict[str, Any] | None = None

    @property
    def identifier(self) -> str | None:
        """Return the BroadLink MAC as a plain 12-character hex string."""
        raw = getattr(self._device, "mac", None) if self._device else None
        if raw is None:
            return None
        if isinstance(raw, (bytes, bytearray)):
            return raw.hex()
        return str(raw).replace(":", "").replace("-", "").lower()

    @property
    def mac(self) -> str | None:
        """Compatibility alias for `identifier`."""
        return self.identifier

    @property
    def firmware(self) -> int | None:
        return self._firmware

    @property
    def diagnostics(self) -> dict[str, Any]:
        """Return allowlisted metadata, available even if authentication fails."""
        return {
            "transient_retries": self.transient_retries,
            "reauth_count": self.reauth_count,
            "stage": self._stage,
            "devtype": self._devtype,
            "advertised_lock": self._is_locked,
            "last_error": dict(self._last_error) if self._last_error else None,
        }

    def _record_failure(self, err: Exception) -> None:
        """Retain useful error metadata without untrusted exception text."""
        source = err.__cause__ or err
        code = getattr(err, "code", getattr(source, "errno", None))
        self._last_error = {
            "stage": self._stage,
            "error_type": type(source).__name__,
            "error_code": code if isinstance(code, int) else None,
        }
        _LOGGER.debug(
            "BroadLink transaction failed (stage=%s, error_type=%s, "
            "error_code=%s, devtype=%s, advertised_lock=%s)",
            self._stage, self._last_error["error_type"],
            self._last_error["error_code"], self._devtype, self._is_locked,
        )

    async def _drop_session(self) -> None:
        device = self._device
        self._device = None
        if device is not None:
            try:
                await device.aclose()
            except BROADLINK_EXCEPTIONS:
                pass

    async def invalidate(self) -> None:
        """Drop the current authenticated BroadLink session."""
        await self._drop_session()

    async def close(self) -> None:
        """Close the BroadLink socket and discard the session."""
        async with self._lock:
            await self._drop_session()

    async def _connect(self) -> Any:
        self._stage = "discovery"
        self._devtype = None
        self._is_locked = None
        _LOGGER.debug("Starting BroadLink discovery (timeout=%ss)", self.timeout)
        if not inspect.iscoroutinefunction(broadlink.hello):
            raise RunxinTransportError("Incompatible broadlink-async runtime; check the installed dependency")
        device = await broadlink.hello(self.host, timeout=self.timeout)
        if device is None:
            raise RunxinTransportError("No BroadLink device found")
        self._stage = "device_type"
        self._devtype = int(device.devtype)
        advertised_lock = getattr(device, "is_locked", None)
        self._is_locked = advertised_lock if isinstance(advertised_lock, bool) else None
        _LOGGER.debug(
            "BroadLink discovery succeeded (devtype=0x%04x, advertised_lock=%s)",
            self._devtype, self._is_locked,
        )
        try:
            if (
                self.expected_devtype is not None
                and int(device.devtype) != self.expected_devtype
            ):
                raise BroadlinkUnsupportedDeviceError(self._devtype)
            guard_exchange(device)
            device.timeout = self.timeout
            self._stage = "authentication"
            try:
                authenticated = await device.auth()
            except broadlink.exceptions.AuthenticationError as err:
                raise BroadlinkAuthenticationError(err.errno, self._is_locked) from err
            except ValueError as err:
                # A short decrypted auth payload can supply an invalid AES
                # session-key length even with broadlink-async 1.1.0. This is a malformed
                # response, not a proven rejection or a reason to unlock/retry.
                raise RunxinTransportError("Invalid BroadLink authentication response") from err
            if authenticated is False:
                raise BroadlinkAuthenticationError(None, self._is_locked)
        except BaseException:
            # Discovery created a socket but authentication did not establish
            # a reusable session. Release it before propagating the same error.
            try:
                await device.aclose()
            except BROADLINK_EXCEPTIONS:
                pass
            raise
        self._device = device
        _LOGGER.debug("BroadLink local authentication succeeded")

        if self._firmware is None:
            try:
                self._firmware = int(await device.get_fwversion())
            except Exception as err:  # noqa: BLE001 - cosmetic metadata only
                self._firmware = None
                _LOGGER.debug(
                    "BroadLink firmware metadata unavailable (%s)", type(err).__name__
                )
        return device

    async def _transact_once(self, frame: bytes, *, write: bool = False) -> bytes:
        device = self._device or await self._connect()
        self._stage = "request"
        if write:
            response = await send_packet_once(device, 0x6A, pack_tfb(frame))
        else:
            response = await device.send_packet(0x6A, pack_tfb(frame))
        response = bytes(response)
        self._stage = "response"
        if len(response) < 0x38:
            raise RunxinTransportError("Short BroadLink response")

        error = int.from_bytes(response[0x22:0x24], "little", signed=True)
        if error:
            raise BroadlinkOuterError(error)

        encrypted = response[0x38:]
        if not encrypted or len(encrypted) % 16:
            raise RunxinTransportError("Invalid BroadLink encrypted length")
        try:
            plaintext = device.decrypt(encrypted)
        except BROADLINK_EXCEPTIONS as err:
            raise RunxinTransportError(f"BroadLink decrypt failed: {err}") from err
        result = unpack_tfb(plaintext)
        self._stage = "ready"
        return result

    async def _transact_read_resilient(self, frame: bytes) -> bytes:
        """Retry bounded, idempotent read transactions.

        Outer -5 is empirically transient on the tested BL3372/F79D. The exact
        internal cause is not known. Authentication-like outer errors get one
        fresh session. These budgets are independent so an auth refresh cannot
        accidentally consume the last transient retry slot.
        """
        transient_attempt = 0
        reauth_remaining = 1
        while True:
            try:
                return await self._transact_once(frame)
            except broadlink.exceptions.ConnectionClosedError:
                if not reauth_remaining:
                    raise
                reauth_remaining -= 1
                self.reauth_count += 1
                await self._drop_session()
                continue
            except BroadlinkOuterError as err:
                if err.code in self.auth_error_codes and reauth_remaining:
                    reauth_remaining -= 1
                    self.reauth_count += 1
                    await self._drop_session()
                    continue
                if (
                    err.code == self.transient_error_code
                    and transient_attempt < len(self.transient_delays)
                ):
                    base = self.transient_delays[transient_attempt]
                    transient_attempt += 1
                    self.transient_retries += 1
                    await asyncio.sleep(base + random.uniform(0, base / 2))
                    continue
                raise

    async def transact(self, frame: bytes) -> bytes:
        """Carry one read/idempotent raw Runxin request through BroadLink."""
        async with self._lock:
            try:
                return await self._transact_read_resilient(frame)
            except asyncio.CancelledError:
                await self._drop_session()
                raise
            except RunxinTransportError as err:
                self._record_failure(err)
                await self._drop_session()
                raise
            except BROADLINK_EXCEPTIONS as err:
                self._record_failure(err)
                await self._drop_session()
                raise RunxinTransportError(str(err)) from err

    async def transact_write(self, frame: bytes) -> bytes:
        """Send one Runxin write exactly once and never retry it blindly.

        Any transport failure after packet submission is ambiguous: the F79D
        may have executed the command even if the acknowledgement was lost.
        Callers must reconcile by reading physical state before deciding whether
        a retry is safe.
        """
        async with self._lock:
            try:
                return await self._transact_once(frame, write=True)
            except asyncio.CancelledError:
                await self._drop_session()
                raise
            except RunxinTransportError as err:
                self._record_failure(err)
                await self._drop_session()
                raise
            except BROADLINK_EXCEPTIONS as err:
                self._record_failure(err)
                await self._drop_session()
                raise RunxinTransportError(str(err)) from err
