"""Load the pure protocol packages without importing Home Assistant."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "ypsilon_local"
TEST_PKG = "_ypsilon_testpkg"


def _ensure_namespace() -> None:
    if TEST_PKG not in sys.modules:
        root = types.ModuleType(TEST_PKG)
        root.__path__ = [str(INTEGRATION)]
        sys.modules[TEST_PKG] = root
    for child in ("runxin", "transport"):
        name = f"{TEST_PKG}.{child}"
        if name not in sys.modules:
            pkg = types.ModuleType(name)
            pkg.__path__ = [str(INTEGRATION / child)]
            sys.modules[name] = pkg


def load(relative: str):
    """Load e.g. `runxin.f79d` or `transport.broadlink_bl3372`."""
    _ensure_namespace()
    full = f"{TEST_PKG}.{relative}"
    if full in sys.modules:
        return sys.modules[full]
    path = INTEGRATION.joinpath(*relative.split(".")).with_suffix(".py")
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full] = module
    spec.loader.exec_module(module)
    return module


def io_mock(*args, **kwargs):
    """Synchronous metadata parent with explicit asynchronous I/O children."""
    from unittest.mock import Mock, AsyncMock
    result = Mock(*args, **kwargs)
    for name in ("read_state", "read_fields", "read_identity", "write_fields",
                 "transact", "transact_write", "close", "auth", "get_fwversion",
                 "send_packet", "aclose", "invalidate", "_exchange"):
        setattr(result, name, AsyncMock())
    return result


def broadlink_reply(device, body=bytes(16), error=0):
    """A structurally valid reply; caller chooses real or fake encrypted body."""
    header = bytearray(0x38)
    header[:8] = bytes.fromhex("5aa5aa555aa5aa55")
    header[0x22:0x24] = error.to_bytes(2, "little", signed=True)
    header[0x24:0x26] = device.devtype.to_bytes(2, "little")
    header[0x26:0x28] = (0x03E9).to_bytes(2, "little")
    header[0x28:0x2A] = device.count.to_bytes(2, "little")
    header[0x2A:0x30] = device.mac[::-1]
    response = header + body
    response[0x20:0x22] = (sum(response, 0xBEAF) & 0xFFFF).to_bytes(2, "little")
    return bytes(response)
