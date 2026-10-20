# Model 1 / F150

[English](model-1.md) | [Català](model-1.ca.md) | [Español](model-1.es.md) · [Support matrix](../model-support.md) · [Documentation](../index.md)

**Beta readings; validated manual clock controls.** F150 is the manufacturer API name for controller code 1, not a confirmed commercial identity. Evidence comes from the unbranded softener in issue #17, BL3372 `0x520F`, firmware 62016. It does not establish support for every F150-labelled valve.

## Installation

Follow [installation and updates](../installation.md). Existing operational entries update in place. Delete a saved diagnostic-only entry before adding the same device normally. Setup explains the uncertain units; default polling is 60 seconds with adaptive polling off.

## What is enabled

- Normal status, water and diagnostic readings, including daily consumption with `total_increasing` for the Energy dashboard. Weekly average is not a cumulative meter.
- **Manual Device clock and Sync clock (field 4)**, validated against the app/controller and available without experimental options.
- Reference sensors for settings, raw received field pairs and model/effective-permission metadata. Some diagnostics are disabled by default.
- **Resin and per-cycle capacity stay unitless and excluded from statistics.** Reported resin bytes `F0 00` / reference 240 do not establish litres or a multiplier; per-cycle reference 15 is a separate value. Other readings are not blocked by those two unresolved units.

Automatic clock correction, field-7 flow-cutoff writes, vacation writes and direct phase advancement remain blocked. Code 7 for controller language is confirmed as Dutch on this model; other enum labels remain reference interpretations unless separately confirmed.

## Optional experimental settings

Open **Settings → Devices & services → Runxin Local → Configure**. The default-off experimental-settings option enables manual controls for fields **6/10/43/47** (continuous-flow time, regeneration schedule, added salt and hardness). These writes remain pending physical verification on model 1.

A second default-off option permits only **regeneration start (34)** and also requires experimental settings enabled. It does not permit arbitrary phase changes. Use a normally planned cycle for any future physical validation; it is not needed to collect a report.

For a voluntary reversible-setting test, use the actual fresh baseline, change one permitted value, compare fresh HA read-back and the app/controller, restore and confirm restoration. A lost response is not a reason to repeat the command blindly. Turning test options off revokes/replaces the write session and removes extra controls while retaining manual clock, readings, identities and cached data.

## Evidence and unresolved details

The [dated evidence record](../evidence/model-1.md) preserves raw/reference values, manual clock restoration, language, phase observations and the distinction between resin and treatment capacity. [Hardware verification](../hardware-verification.md#model-1--f150-daily-consumption-and-beta-readings-in-2102) records the later controller comparison supporting daily statistics.

No repeated tests or reports are requested from the issue #17 contributor. The pending calibration backlog is separate from resolving that connection/setup issue. Fresh diagnostics from a normal entry export cached state without a new scan.
