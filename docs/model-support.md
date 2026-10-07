# Controller support and evidence

This is the current model policy for **2.9.0-alpha.1**. A commercial brand, valve reference, BroadLink device type and Runxin `deviceModel` code are different identifiers.

| Controller code | Manufacturer enum name | Integration policy | Field evidence | Writes |
|---|---|---|---|---|
| 9 | F79D | Reference ATH/BWT Ypsilon G6 | Reference hardware and per-field checks | Existing fields 4/6/7/10/34/43/47; field 34 remains pending physical verification |
| 12 | F105 | Alpha Euro-Clear Midnight 25 | Captured state/app comparison; resin scale 0.1 | Existing fields 4/6/7/10/34/43/47; 4/6/10/43 hardware-verified, 7/34/47 pending |
| 1 | F150 | Read-only Alpha, issue #17 | All 52 requested field IDs received; reference semantics/applicability pending | None; clock correction and admin services blocked |
| 14 | F136 | One-time diagnostic report only | Contributor report in issue #22; independent comparisons pending | None through a diagnostic entry |
| Other codes | Descriptive API names, where known | One-time diagnostic report only | No automatic support from the name table | None through a diagnostic entry |

`models.py` is the authoritative policy registry. `allowed_write_fields` is effective permission; `hardware_verified_write_fields`/`pending_write_fields` document evidence. They serve different purposes: legacy pending controls for 9/12 are preserved, while a new model defaults to an empty permission set. An Alpha label alone does not grant or withdraw write permission.

A periodic read-only Alpha is distinct from a saved diagnostic-only entry. The Alpha authenticates/polls and creates reference sensors; a diagnostic-only entry loads a saved one-time report without polling or entities. Neither permits writes.

## Shared maps and model-specific behavior

Models 1/9/12 currently use the F79D-compatible frame and field-map path. That does not mean their full physical semantics are identical. Model 12 keeps its resin scale. Model 1 keeps resin/per-cycle values without confirmed units and all readings marked provisional, with long-term statistics disabled. Original bytes are retained for comparison.

The catalogue's hardware-write evidence is reference G6 evidence, not a blanket claim for every model. Future differences in byte order, enums, units or applicability require model/profile-specific evidence and regression fixtures; do not change the shared G6 definition to fit another controller.

## Beyond field 52

52 is the current **F79D catalogue**, not a proven universal Runxin limit. The public API lists additional pressure, RO-filter, TDS and immersion-detector properties for other families. Cloud object properties are not local numeric field IDs. No automatic scan beyond 52, alternate profile, unknown-model control or cloud dependency is added here.

## Promotion

- Diagnostic evidence → read-only Alpha: coherent identity, readable frame/map, minimal read set and tests that block all mutation routes.
- Read-only Alpha → calibrated readings: app/controller comparisons with units, representative nonzero values and per-model fixtures. Field receipt/zero defaults alone do not prove applicability.
- Controls: per-field write encoding, range and baseline/set/fresh-read/restore evidence. Metadata must distinguish verified and pending actions.
- Beta/release: sustained real HA operation, reload/restart checks, missing-field/unknown-enum handling and documented hardware/firmware scope. Software tests do not replace those hardware checks.

See [model 1 comparison](model-1-alpha.md), [hardware evidence](hardware-verification.md), [adding a profile](adding-a-device-profile.md) and [audit findings](multi-model-audit.md).
