#!/usr/bin/env python3
"""Probe BroadLink discovery/authentication without changing device settings.

Run this in a Python environment with broadlink==0.19.0 installed. The report
deliberately omits the host, device name, MAC, control ID, session key, packets
and exception messages. It does not require Home Assistant or query F79D state.
"""

from __future__ import annotations

import argparse
from importlib.metadata import version
import json
import platform
from typing import Any

import broadlink


def _error_details(err: Exception) -> dict[str, Any]:
    code = getattr(err, "errno", None)
    return {
        "ok": False,
        "error_type": type(err).__name__,
        "error_code": code if isinstance(code, int) else None,
    }


def probe_connection(host: str, *, timeout: float = 5) -> dict[str, Any]:
    """Attempt one handshake and an optional firmware read, returning safe JSON."""
    report: dict[str, Any] = {
        "broadlink_version": version("broadlink"),
        "python_version": platform.python_version(),
        "timeout_seconds": timeout,
        "discovery": {"ok": False},
        "authentication": {"attempted": False},
        "firmware": {"attempted": False},
    }
    try:
        device = broadlink.hello(host, timeout=timeout)
    except Exception as err:  # noqa: BLE001 - diagnostic boundary; omit raw error text
        report["discovery"] = _error_details(err)
        return report
    if device is None:
        report["discovery"] = {"ok": False, "error_type": "NoDevice"}
        return report

    advertised_lock = getattr(device, "is_locked", None)
    report["discovery"] = {
        "ok": True,
        "devtype": f"0x{int(device.devtype):04x}",
        "advertised_lock": advertised_lock if isinstance(advertised_lock, bool) else None,
    }
    device.timeout = timeout
    try:
        try:
            authenticated = device.auth()
        except Exception as err:  # noqa: BLE001 - report library/crypto errors safely too
            report["authentication"] = {"attempted": True, **_error_details(err)}
            return report
        if authenticated is False:
            report["authentication"] = {
                "attempted": True, "ok": False, "error_type": "AuthenticationRejected",
            }
            return report
        report["authentication"] = {"attempted": True, "ok": True}
        try:
            firmware = int(device.get_fwversion())
        except Exception as err:  # noqa: BLE001 - optional metadata, never needed for auth
            report["firmware"] = {"attempted": True, **_error_details(err)}
        else:
            report["firmware"] = {"attempted": True, "ok": True, "version": firmware}
        return report
    finally:
        # 0.19.0 closes each packet socket itself; support objects with a socket
        # too, without retaining an authenticated handle after the probe.
        sock = getattr(device, "sock", None)
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass


def _timeout(value: str) -> float:
    seconds = float(value)
    if not 0 < seconds <= 60:
        raise argparse.ArgumentTypeError("timeout must be greater than 0 and at most 60 seconds")
    return seconds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="local device IP/hostname (omitted from the report)")
    parser.add_argument("--timeout", type=_timeout, default=5, help="per-packet timeout in seconds (default: 5)")
    args = parser.parse_args()
    report = probe_connection(args.host, timeout=args.timeout)
    print(json.dumps(report, indent=2))
    return 0 if report["authentication"].get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
