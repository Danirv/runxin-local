"""The candidate's standalone read-only launcher does not import HA."""
import inspect
import json
import sys
from unittest.mock import AsyncMock

from scripts import validate_async_connection


def test_collector_loads_the_actual_async_readonly_module():
    collector = validate_async_connection._collector()
    assert inspect.iscoroutinefunction(collector)
    assert collector.__module__ == "_runxin_validation.compatibility"


def test_cli_saves_sanitized_partial_report_without_printing_host(monkeypatch, tmp_path, capsys):
    report = {"summary": {"status": "partial"}, "authentication": {"ok": True}}
    collector = AsyncMock(return_value=report)
    monkeypatch.setattr(validate_async_connection, "_collector", lambda: collector)
    output = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", ["validate_async_connection.py", "192.0.2.17", "--output", str(output)])
    assert validate_async_connection.main() == 2
    assert json.loads(output.read_text()) == report
    assert "192.0.2.17" not in capsys.readouterr().out
    collector.assert_awaited_once_with("192.0.2.17")
