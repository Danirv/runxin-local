# Controller model 1 / F150: read-only Alpha

[English](model-1-alpha.md) | [Català](model-1-alpha.ca.md) | [Español](model-1-alpha.es.md)

Version **2.9.0-alpha.1** admits controller code **1** with continuous read-only entities. The public manufacturer's enumeration calls this code **F150**; the commercial product and valve identity in issue #17 are unconfirmed. This does not claim support for every F150-branded product or firmware.

## Install and compare

1. Install this prerelease when published, or download the PR branch's source ZIP and copy only `custom_components/ypsilon_local` to `/config/custom_components/ypsilon_local`. Keep a backup of the previous integration folder and restart Home Assistant. Do not install `runxin_local`; the domain-migration pilot is separate.
2. If you saved a diagnostic-only entry for this device, download its report first, then delete that entry before adding the device normally. Diagnostic entries have no operational entities and are not silently converted.
3. Add **Runxin Local**, enter the local IP, and accept the **Read-only Alpha** explanation. Default polling is once per minute, with adaptive polling off. Clock correction remains blocked even if an old option is enabled.
4. Open the device and compare its sensors with the working vendor app. Some reference/diagnostic entities are disabled by default; enable them in the entity list if useful. No settings need to be changed to make a comparison.
5. From the integration entry menu, **Download diagnostics** and attach the JSON to the existing issue. This exports the last cached state and does not trigger another scan. Include a few app readings with their units and approximate comparison time; redact account/device identifiers in screenshots.

The domain, config-entry version and G6/Midnight entity identities stay unchanged. A normal integration setup authenticates and polls, so it is a small amount of active LAN traffic. If the app and HA interfere, pause HA polling or disable the entry temporarily while collecting app screenshots; it does not need to be unpaired.

## What is enabled

- Existing status, water, programme-duration and diagnostic sensors, using the **reference F79D interpretation**.
- Sensor equivalents for clock, regeneration schedule, hardness, added salt, continuous-flow timeout, flow-cutoff raw value and closure-reason raw code.
- The original two bytes of received fields in diagnostics (`state._rawFieldBytes`), plus raw bytes/reference markers on entities. No raw network packets, encryption keys or session IDs are included.
- Model/evidence/write-permission metadata. Zero/false readings are retained, but receipt alone does not prove a field is applicable.

There are **no number, time or button controls**, no clock corrections and no configuration/mechanical commands. Advanced admin services also reject this model. The coordinator and composition adapter enforce the policy independently of the UI. The integration has no model-1 write opt-in.

All model-1 readings are provisional: numeric entities have **no long-term statistics state class**. Ordinary recorder history can still be retained. Known enum labels are reference labels; unmapped values retain their numeric codes.

## Priority comparisons from issue #17

| Field | Reported reference | Compare with the app |
|---|---|---|
| 26, resin | Raw `F0 00`, first byte 240 | Resin volume/capacity and unit. HA shows 240 **without L**, with no guessed multiplier. |
| 41–42, per-cycle quantity | Reference 15 | Its actual label and unit. HA shows 15 **without L**; do not assume this is treatment-water capacity. |
| 35–36, remaining quantity | Reference 1304 L | Remaining capacity and unit, close to the HA snapshot time. |
| 37–40, daily/weekly quantities | Reference 215 / 192 L | Daily consumption and the controller's weekly average, not necessarily an app history total. |
| 47, hardness | Reference 280 mg/L | Exact label, value and hardness scale. |
| 43, added salt | Reference 25 kg | Bookkeeping amount, not a measured tank level. |
| 4/5/10, clocks/schedule | 20:38 / 00:00 / 00:00 | Clock and visible regeneration schedule; values naturally change over time. |
| 6/7/15/17/19/21/23 | Raw values and programme times | Protection settings, programme durations and maximum interval, wherever visible. |

Resin and per-cycle capacity are uncalibrated. Other displayed units/scales are reference candidates, not independently validated measurements. The second resin byte is preserved without assuming a U16 codec. Field 52 remains cached separately; its raw bytes may be older than the rest of the snapshot.

## Evidence and next steps

[Issue #17](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6044822202) supplied BL3372 devtype `0x520F`, firmware 62016, standard authentication with the app closed, stable code 1 and all 52 requested fields in two successful queries. The fixture in `tests/fixtures/model1_fields.json` preserves published field pairs; reconstructed test frames are **synthetic**, not network captures. Software tests cannot confirm physical units or mechanical actions.

A later model-1 calibration should change only its model policy/presentation or proven codec overrides. It must not change G6/Midnight interpretation to accommodate this device. Reads beyond 52 and model-1 writes are not tested or enabled by this Alpha.
