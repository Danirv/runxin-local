# Using Runxin Local

[English](usage.md) | [Català](usage.ca.md) | [Español](usage.es.md) · [Documentation](index.md)

## Entities and controls

Operational entities show flow, daily consumption, remaining treatment capacity, operating status, regeneration mode, work pattern, vacation status and active alerts. Diagnostic entities provide programme durations/countdowns, maintenance flags, resin settings, controller identity and connection health. Some diagnostics are disabled by default; enable them from the device's entity list when needed.

Controls depend on the [controller model](model-support.md). Models 9/12/14 retain their clock, regeneration schedule, hardness, salt-added and protection settings, regeneration button and administrator services. Pending hardware validations are listed separately from permissions. Model 1 exposes only validated manual clock controls by default, with explicit options for other tests; see [its guide](models/model-1.md).

A missing reading stays unavailable/unknown; it is not fabricated as zero. Unknown enum values appear as decimal codes with `raw_code`, rather than hiding the received value. Known labels follow the reference mapping and confirmed per-model exceptions.

## Water consumption and statistics

| Entity | Meaning | Home Assistant statistics |
|---|---|---|
| Daily consumption | Controller's cumulative counter for the current day; resets at the day boundary | `total_increasing`; use as the Energy dashboard's water source |
| Flow rate | Latest instantaneous sample | `measurement`; short draws between polls may not appear |
| Remaining treatment capacity | Controller's current remaining treatment quantity, not water stored in a tank | `measurement` |
| Controller weekly average consumption | Average reported by the controller, not the app's historical weekly total | No state class |
| Treatment capacity per cycle | Configured/reported treatment-cycle quantity, not consumed water | No state class |

After setup or updating model 1, wait for HA to collect statistics, then choose **Daily consumption** in the Energy dashboard's water sources. Existing entities can be retained. Enabling statistics does not backfill long-term statistics that were never recorded.

For a current-week total, derive it from the daily counter/history rather than treating the controller's weekly average as a weekly meter. Older releases generated statistics for weekly average and per-cycle quantity; HA may offer to remove those obsolete statistics. That cleanup does not delete the entities or their normal recorder history.

Volume/flow units follow the controller's unit selector. Model-1 resin and per-cycle values remain **unitless**, without assumed scaling or statistics. Model-12 and model-14 resin use different byte decoders; see the [model policy](model-support.md).

## Salt, resin and maintenance

**Added salt amount** is the controller's field-43 setting (0–100 kg), not a measured salt-tank level. The integration writes the requested value; pressing the same 25 kg value twice does not implement a 50 kg accumulator in HA. It does not estimate or decrement remaining salt after regeneration. Low-brine concentration and the salt reminder are separate controller signals.

Resin volume is a configured parameter, not a physical measurement of tank contents. A nominal product capacity does not always equal the configured value. The resin-maintenance regeneration threshold is a threshold, not the number of cycles already completed.

## Polling and clock options

Open the integration entry's **Configure** options. Normal polling defaults to **60 seconds**; adaptive polling uses **10 seconds** while flowing or in an observed mechanical transition. On models 9/12/14, adaptive polling and automatic clock correction are enabled by default. Clock tolerance defaults to **2 minutes**. A seasonal time change can therefore cause a clock correction.

Model 1 defaults to fixed 60-second polling with adaptive polling off. Its automatic clock correction is blocked independently of a saved option; manual clock and Sync clock remain available. Optional model-1 settings and regeneration start are separate, default-off test options.

Field 52 is a slow-changing service interval, refreshed separately every **3600 seconds** and cached. Exported raw pairs can have different ages; a diagnostic snapshot is not proof that every field was freshly queried together.

## Vacation status and regeneration

Vacation is read-only: `off` means the flag is clear; `preparing` means the flag is set before stable station 8; `active` means the flag is set and station is 8. Raw operating status remains available. Stable vacation is idle for adaptive polling.

The regeneration button requires a fresh in-service reading with vacation off, rejects overlapping requests, sends one start command and checks the resulting phase. It moves the physical valve and uses water/salt. A protocol ACK alone does not prove a change; ambiguous delivery is reconciled by fresh reads without blindly replaying the command. [Hardware verification](hardware-verification.md) records which actions were actually tested per model.

## Advanced services

Administrator-only **`ypsilon_local.write_fields`** accepts reversible, permitted settings with raw-value/range/unit validation. **`ypsilon_local.advance_phase`** handles the explicit phase-control operation separately. Both use the configured entry and enforce effective model permissions; diagnostic-only entries cannot write. Model 1 does not permit phase advancement, and field 49 has no HA writer.

Use ordinary entity controls for routine settings. Protocol encoding capability is broader than the integration's permission set; consult the [field catalogue](f79d.md) before interpreting raw values.

## Diagnostics and help

For an existing operational entry, **Download diagnostics** exports cached state without starting another device query. For unknown models or failed setup, the separate [compatibility collector](compatibility-report.md) makes an explicit, bounded set of read requests. Saved diagnostic-only entries have no entities, polling or controls. For connection errors, start with [troubleshooting](troubleshooting.md).
