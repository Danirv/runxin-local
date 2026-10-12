#!/usr/bin/env python3
"""Read-only validation of the async BL3372 path; no Home Assistant required.

Use Python 3.13+ and python-broadlink==1.0.6 in an isolated environment.
Discovery/authentication, firmware and fields 1..52 only; never writes settings,
corrects the clock, regenerates, unlocks, provisions or resets the controller.
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
from pathlib import Path
import sys
import types


def _collector():
    name = "_runxin_validation"
    package = types.ModuleType(name)
    package.__path__ = [str(Path(__file__).resolve().parents[1] / "custom_components" / "ypsilon_local")]
    sys.modules[name] = package
    return importlib.import_module(f"{name}.compatibility").probe


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="local device IP/hostname (excluded from report)")
    parser.add_argument("--output", type=Path, default=Path("runxin_async_report.json"))
    args = parser.parse_args()
    report = asyncio.run(_collector()(args.host))
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Report saved: {args.output}")
    return 0 if report["summary"]["status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
