# Model 1 / F150: reported evidence

Dated controller observations, reference values and their limits. For current setup and controls, see the [model guide](../models/model-1.md). These records are evidence, not a new request for tests.

[English](model-1.md) | [Català](model-1.ca.md) | [Español](model-1.es.md) · [Documentation](../index.md)

## Field-specific calibration backlog

| Field | Reported reference | Compare with the app |
|---|---|---|
| 26, resin | Raw `F0 00`, first byte 240 | Resin volume/capacity and unit. HA shows 240 **without L**, with no guessed multiplier. |
| 41–42, per-cycle quantity | Reference 15 | The contributor changed 24 → 15 under Runxin Advanced → Water treatment capacity. The manufacturer distinguishes this from resin volume; confirm its unit and local-field correspondence. HA keeps 15 **without an assumed unit**. |
| 35–36, remaining quantity | Reference 1304 L | Remaining capacity and unit, close to the HA snapshot time. |
| 37–40, daily/weekly quantities | Reference 215 / 192 L | Daily consumption now agrees with controller history (issue #17); weekly average remains distinct from an app history total. |
| 47, hardness | Reference 280 mg/L | Exact label, value and hardness scale. |
| 43, added salt | Reference 25 kg | Bookkeeping amount, not a measured tank level. |
| 4/5/10, clocks/schedule | 20:38 / 00:00 / 00:00 | Clock and visible regeneration schedule; values naturally change over time. |
| 6/7/15/17/19/21/23 | Raw values and programme times | Protection settings, programme durations and maximum interval, wherever visible. |

Resin and per-cycle capacity are uncalibrated. Daily consumption has been compared with the physical controller; other fields retain the shared F79D interpretation with the evidence recorded below. The second resin byte is preserved without assuming a U16 codec. Field 52 remains cached separately; its raw bytes may be older than the rest of the snapshot.


## Confirmed comparisons in 2.9.3

The [2026-10-10 reply](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6096161743) records a clock baseline of 11:23, writes to 11:24 and 11:26, and restoration using manual clock sync. Both the physical controller and Water Device app agreed after each action. Only field 4 was exercised; the experimental option was disabled afterwards. This validates manual clock controls on that unit, not automatic correction or other writes.

The same reply confirms a Dutch controller display with field-2 code 7. HA now labels that model/code pair `dutch`; no language write or app-locale change is made.

The reported unit has nominal 24 L resin. Field 26 remains `F0 00` (reference 240), while fields 41–42 remain reference 15. In the examined manufacturer frontend, `resinVolume` is labelled Resin volume and `periodicWaterProduction` is Water treatment capacity; the older Runxin app's exact setting-to-local-field path is not independently confirmed. `240 / 10 = 24 L` is plausible but not yet a configured-value comparison. Keep both sensors without assumed units and do not copy model 14's U16 override.

Do not reduce a resin-volume setting to match household size: it should describe the actual resin charge. Treatment capacity is a different parameter based on resin, hardness and regeneration settings; a lower programmed capacity with unchanged cycles can cause more frequent regeneration rather than savings. Confirm the label/unit and follow the unit's instructions before suggesting an adjustment. No re-pairing, old-app access, repeated diagnostics or setting changes are needed just to clarify these readings.


## Operation reported after regeneration on 2.9.3

The [later 2026-10-10 report](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6101162421) confirms normal polling and recovery of readings after HA restarts following updates on the reported model-1 unit, with BL3372 firmware 62016 and integration 2.9.3.

At 19:41:45 local time, HA reported brine draw and slow rinse while the controller displayed **“pekel-spoel traag up-flow”**. This independently supports that specific phase label. HA had reported brine refill at 19:35:34, approximately six minutes earlier. With 60-second polling, this observation does not independently validate the configured refill duration or establish a timing error against the earlier seven-minute reading. Earlier aborted attempts are excluded from sequence and duration validation. The HA regeneration option remained off, so these observations do not validate the field-34 start command.

After the cycle, HA showed remaining capacity **3429 L**, compared with **1267 L** reported on 8 October. This records a capacity recovery after regeneration; it is not an independent calibration of its units. Reported hardness remained 280 mg/L, resin `F0 00` / reference 240 and per-cycle reference 15. Assuming hardness expressed as CaCO₃, `3.429 m³ × 28 °f ≈ 96 °f·m³`, or about `4 °f·m³/L` for nominal 24 L resin. This is a consistency check, not a configured-resin comparison or proof of the 0.1 conversion. The contributor recalls an L label beside the old setting but is unsure; its unit and exact local-field correspondence remain pending.

These observations add operational and phase-reading evidence without changing codecs or permissions. The later 2.10.2 Beta promotion enables normal reading statistics while preserving unresolved units. The remaining comparisons above are a calibration backlog; no further tests, screenshots or diagnostic reports are requested from this contributor. The original connection/setup issue can be closed independently of those pending validations.


## Evidence and next steps

[Issue #17](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6044822202) supplied BL3372 devtype `0x520F`, firmware 62016, standard authentication with the app closed, stable code 1 and all 52 requested fields in two successful queries. The fixture in `tests/fixtures/model1_fields.json` preserves published field pairs; reconstructed test frames are **synthetic**, not network captures. Software tests cannot confirm physical units or mechanical actions.

A later model-1 calibration should change only its model policy/presentation or proven codec overrides. It must not change G6/Midnight interpretation to accommodate this device. Reads beyond 52 remain disabled. Model-1 writes other than the validated manual clock remain experimental and require the explicit opt-ins above; software tests do not validate physical acceptance.
