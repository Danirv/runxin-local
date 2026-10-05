# Ypsilon 2.7.1

Local Home Assistant integration for compatible Runxin F79D / BroadLink BL3372 water softeners, tested with ATH/BWT Ypsilon G6 and Euro-Clear Midnight.

## 2.7.1

Distinguishes rejected local authentication from other setup failures and reports an advertised local-control lock without assuming it caused the rejection. Adds sanitized connection logs, transport diagnostics, a standalone report script and troubleshooting guides in English, Catalan and Spanish.

This patch helps investigate authentication failures such as issue #17; it does not introduce a new authentication method or claim to fix an untested firmware restriction. The handshake, retries, valve commands and model-12 Alpha compatibility remain unchanged.

## 2.7.0

Adds **experimental / Alpha compatibility** for the **Euro-Clear Midnight** (Runxin controller model 12, BroadLink BL3372 `0x520F`), tested on a Midnight 25. It retains the original sensors and controls. Writes to the clock, continuous-flow limit, regeneration time and salt added were hardware-verified; fields 7 and 47 and mechanical field-34 actions remain pending on this model. Every write still uses strict fresh read-back. Alpha applies to model 12, not to existing G6 support.

Diagnostics now expose per-model hardware evidence and both original resin-volume bytes. Midnight 25's `FA 00` still displays as 25 L; the second byte and larger resin volumes require more evidence, with no guessed codec change.

## 2.6.3

This maintenance release fixes the F79D field-7 (`flowRateOff`) wire codec using physical Ypsilon G6 evidence and restores its hardware-write verification status.

Highlights:

- restores field 7 to **16-bit big-endian** for both reads and writes;
- documents the decisive hardware vector: wire bytes `03 E8` are raw `1000` in BE and correspond to the vendor application's `10.00 m³/h`; the regressed LE interpretation produced raw `59395` / `593.95 m³/h` in Home Assistant;
- writes `2.00 m³/h` as raw `200` / bytes `00 C8` instead of the incorrect LE bytes `C8 00`;
- restores `HARDWARE_WRITE_VERIFIED` for field 7 based on the earlier physically verified BE implementation plus the current independent read-back evidence;
- keeps the safe Home Assistant range at `0.00–10.00 m³/h` for the physically calibrated cubic-metre unit mode;
- preserves strict post-write reconciliation: an ACK alone is still never accepted as proof that the controller adopted a setting;
- adds protocol and audit regressions for the exact real-device byte vectors and the historical `59395` misdecode;
- keeps field 52 on its intentional slow-refresh cache rather than moving it into the normal 1..51 polling block;
- reviews English, Catalan and Spanish translations; no translation key or label change is required for this wire-codec fix.

### Upgrade note

No entity registry migration is required. The existing flow-rate cutoff number retains the same unique ID, range, unit and translations; only its raw wire encoding/decoding is corrected.

The transport-neutral `runxin/` layer remains independent from Home Assistant and BroadLink. The Home Assistant integration supports BroadLink BL3372 (`0x520F`) with Runxin controller model 9 (Ypsilon G6) and, since 2.7.0, model 12 (Euro-Clear Midnight).
