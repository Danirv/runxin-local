# Controller model 1 / F150: Alpha, read-only by default

[English](model-1-alpha.md) | [Català](model-1-alpha.ca.md) | [Español](model-1-alpha.es.md)

Version **2.9.0** admits controller code **1** with continuous read-only entities. The public manufacturer's enumeration calls this code **F150**; the commercial product and valve identity in issue #17 are unconfirmed. This does not claim support for every F150-branded product or firmware.

The integration release is stable; Alpha describes support for this particular model.

## Install and compare

1. Install version 2.9.0 or later through HACS, or download the release ZIP and copy only `custom_components/ypsilon_local` to `/config/custom_components/ypsilon_local`. Keep a backup of the previous integration folder and restart Home Assistant. Do not install `runxin_local`; the domain-migration pilot is separate.
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

By default there are **no number, time or button controls**, clock corrections or configuration/mechanical commands. Advanced admin services reject this default mode. The coordinator and composition adapter enforce the policy independently of the UI. From 2.9.1, optional manual test permissions can be enabled as described below; no model-1 write is yet hardware-verified.

All model-1 readings are provisional: numeric entities have **no long-term statistics state class**. Ordinary recorder history can still be retained. Known enum labels are reference labels; unmapped values retain their numeric codes.

## Optional manual write tests (2.9.1)

Open **Settings → Devices & services → Runxin Local → Configure** for the operational model-1 entry. Enable **experimental model-1 settings** and save. The integration reloads automatically and adds controls for:

| Field | Manual test | Reference baseline in issue #17 |
|---|---|---|
| 4 | Device clock or manual sync button | Read the current clock; it naturally advances |
| 6 | Continuous-flow timeout | 50 (reference minutes) |
| 10 | Regeneration schedule | 00:00 |
| 43 | Added-salt bookkeeping | 25 (reference kg) |
| 47 | Hardness | 280 (reference mg/L) |

These are reference interpretations and **all model-1 writes remain pending hardware verification**. Use the actual fresh baseline, not these historical numbers. Change one setting by a small valid amount, wait for fresh read-back, compare with the app/controller where visible, restore the original value and confirm restoration. Record field, baseline, requested value, read-back, display/units and restored value. Partial results are useful; do not repeat writes if their delivery is ambiguous. The integration reconciles once without blindly resending.

**Regeneration start** has a second, separate option and also requires the settings mode enabled. Use it only for a normally planned physical cycle. The button checks a fresh in-service/vacation-off state, sends the existing field-34 value-1 command once and confirms the phase transition. Direct phase advancement remains blocked, including through administrator services; the option does not grant arbitrary field-34 commands.

**Automatic clock correction stays off**, even if an old option says otherwise. **Field 7 / flow cutoff stays blocked**, even if the unit changes: this unit reported code 1, while the established writable cutoff is calibrated for code 2. Vacation writes and resin/capacity writes are not enabled.

Turn the settings option off to return to read-only mode; this also disables regeneration tests, revokes the old write session and removes operational controls on reload. The existing reference sensors, unique IDs, raw bytes, unconfirmed units and absence of provisional long-term statistics are preserved. Read-only defaults also survive upgrades/restarts.

Diagnostics report model-default evidence separately from the effective `write_policy` (enabled test options, permitted fields, adapter restrictions and automatic-clock permission). Download them after each completed test sequence; exporting diagnostics does not query or write the device. G6/model-12/model-14 policy and conversions are unaffected.

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

A later model-1 calibration should change only its model policy/presentation or proven codec overrides. It must not change G6/Midnight interpretation to accommodate this device. Reads beyond 52 remain disabled. Model-1 manual writes are experimental and only available after the explicit opt-ins below; software tests do not validate physical acceptance.
