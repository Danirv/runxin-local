# Model 14 / Runxin F136: Midnight Alpha support

[English](model-14-alpha.md) | [Català](model-14-alpha.ca.md) | [Español](model-14-alpha.es.md)

Runxin Local **2.9.0** accepts controller model **14 / F136** through the existing BL3372 (`0x520F`) and F79D-compatible path. The integration release is stable; this controller's support is **Alpha**, initially scoped to the Euro-Clear Midnight 25 / ECOPRO+ unit reported in [issue #22](https://github.com/Danirv/runxin-local/issues/22).

The contributor added model 14 locally and reports working discovery, authentication, identity/state reads and the model-12 field map. They report local writes verified for **4 (clock), 6 (continuous-flow timeout), 10 (regeneration time) and 43 (salt added)**. These reports are accepted as contributor hardware evidence. Fields **7 (flow cutoff), 34 (mechanical actions) and 47 (hardness)** remain pending.

## Installation and controls

Install 2.9.0 or later, restart HA and add Runxin Local normally. No manual registry change is required. A working, locally modified operational entry can be updated in place: the domain and MAC-based unique IDs are retained. Review any unrelated local edits before replacing the integration folder. A diagnostic-only entry remains diagnostic-only; download its report and remove that entry before adding the operational device.

The normal Midnight sensors, number/time controls, automatic clock correction, regeneration button and validated administrator services are available. Commands use the existing encodings, ranges, fresh-state guards and read-back confirmation. Pending controls remain available for validation; their presence is not a completed hardware test. Vacation remains read-only and no extra command or field scan is introduced.

## Conversions and remaining comparisons

The reported shared Midnight map supplies the initial conversions. Resin uses **raw first byte × 0.1 L**, as on model 12; no raw model-14 resin pair/app comparison has yet been supplied. The resin sensor and diagnostics expose `resin_volume_scale_confirmed=false`; both raw bytes remain available. This is an adopted Alpha conversion, not an independently captured model-14 measurement. Known enums retain their labels; unmapped codes stay visible.

Attach cached HA diagnostics and whichever app/controller values and units are readily available. The exact local model entry and raw resin/display comparison are especially useful. Previously completed writes need not be repeated: existing baseline/change/fresh-read/restore results are welcome. Fields 7/34/47 remain separately pending; do not trigger a mechanical action solely to produce a report. See [hardware verification](hardware-verification.md).
