# Model 12 / F105: Euro-Clear Midnight

[English](model-12.md) | [Català](model-12.ca.md) | [Español](model-12.es.md) · [Support matrix](../model-support.md) · [Documentation](../index.md)

**Beta**, scoped to the tested Euro-Clear Midnight 25 with ECOPRO+ head and BL3372 `0x520F`, reporting controller code 12. F105 is the manufacturer's API enum name; it is not interchangeable with every commercial valve reference.

## Setup and controls

Follow [installation and updates](../installation.md) and retain existing operational entries. Normal readings/statistics, clock controls, regeneration schedule, hardness, added salt, continuous-flow protection and the existing regeneration/services surface remain available. Automatic clock correction follows the normal options. Vacation is read-only.

| Write evidence | Fields |
|---|---|
| Hardware-verified on the reported unit | 4 clock, 6 continuous-flow time, 10 regeneration time, 43 added salt |
| Pending hardware verification, with existing permissions retained | 7 flow cutoff, 47 hardness, 34 regeneration/mechanical operations |

Matching readings do not verify writes. Every exposed operation retains range/unit checks, model policy and fresh-state reconciliation. Beta does not change permissions or claim new physical tests.

## Resin, enums and hardness

Field 26 `FA 00` is decoded with the existing **U8 × 0.1** rule and displays **25 L** on the tested Midnight 25. Both original bytes remain available. This capture does not establish the high byte's meaning; do not copy model 14's U16 decoder. Resin is a configured parameter, not a measurement of the tank's physical contents.

Reported work-pattern code **255** and relay-mode code **2** remain decimal values with `raw_code`; the consulted manuals do not establish names for those protocol codes. Missing data remains unknown.

The Midnight manual uses a model-specific hardness convention (German hardness × 10, with a CaO mg/L reference elsewhere). Preserve the reported setting and compare the exact controller/manual units; do not silently substitute a different scale or generalise it to the G6.

## Evidence

The [hardware record](../hardware-verification.md#euro-clear-midnight--controller-model-12) contains captured readings, baseline/change/restore results, the clock-sync observation, consulted manuals and pending checks. If the manufacturer app is unavailable, a physical controller comparison can provide independent display evidence. Future optional write results must remain separate from read comparisons.
