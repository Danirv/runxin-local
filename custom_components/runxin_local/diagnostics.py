"""Diagnostics for Ypsilon Local."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .models import model_support_details
from .const import CONF_DIAGNOSTIC_ONLY
from .runxin.semantics import (
    REGENERATION_PATTERN_KEYS,
    STATION_KEYS,
    SYSTEM_CLOSE_REASON_KEYS,
    VOLUME_UNIT_KEYS,
    WORK_PATTERN_KEYS,
)

TO_REDACT = {"mac", "host", "unique_id"}


def _semantic_protocol_summary(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return compact interpreted protocol metadata alongside the raw state."""
    if not data:
        return None

    regeneration_code = data.get("regenerationPattern")
    work_code = data.get("workPattern")
    volume_unit_code = data.get("waterVolumeUnit")
    station_code = data.get("station")
    close_code = data.get("systemCloseReason")

    return {
        "profile": "F79D",
        "device_model": data.get("deviceModel"),
        "model_support": model_support_details(data.get("deviceModel")),
        "volume_unit_code": volume_unit_code,
        "volume_unit": VOLUME_UNIT_KEYS.get(volume_unit_code),
        "regeneration_pattern_code": regeneration_code,
        "regeneration_pattern": REGENERATION_PATTERN_KEYS.get(regeneration_code),
        "work_pattern_code": work_code,
        "work_pattern": WORK_PATTERN_KEYS.get(work_code),
        "station_code": station_code,
        "station": STATION_KEYS.get(station_code),
        "vacation_enabled": data.get("vacationPattern"),
        "vacation_status": data.get("_vacationStatus"),
        "system_close_reason_code": close_code,
        "system_close_reason": SYSTEM_CLOSE_REASON_KEYS.get(close_code),
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return everything needed to debug a report, minus identifying data."""
    if entry.data.get(CONF_DIAGNOSTIC_ONLY):
        return {"diagnostic_only": True, "compatibility_report": entry.runtime_data.report}
    coordinator = entry.runtime_data
    client = coordinator.client

    return {
        "entry": {
            "version": entry.version,
            "options": dict(entry.options),
            "data": async_redact_data(dict(entry.data), TO_REDACT),
        },
        "connection": {
            "available": coordinator.last_update_success,
            "scan_interval": coordinator.scan_interval,
            "firmware": client.firmware,
            "transient_retries": client.transient_retries,
            "reauth_count": client.reauth_count,
            "transport": client.connection_diagnostics,
        },
        "protocol": _semantic_protocol_summary(coordinator.data),
        "state": async_redact_data(coordinator.data, TO_REDACT)
        if coordinator.data
        else None,
    }
