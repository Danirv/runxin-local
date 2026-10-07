# Multi-model audit — 2026-10-07

[English](multi-model-audit.md) | [Català](multi-model-audit.ca.md)

This is the initial Alpha audit; see [current follow-up](audit-followup.md).
Scope: main `7a1dbc6` (2.8.0), the model-1 report in issue #17 and the changes prepared for **2.9.0-alpha.1**. The domain-migration PR #24 was checked as a separate pending dependency, not merged into this Alpha. PR #21 was not reviewed. No device/cloud command, real HA migration, issue reply, merge, tag or release was performed during this audit.

## Assessment

The split into transport, pure Runxin protocol, composition adapter, model registry and HA presentation is a sound base for the observed compatible models. A wholesale folder rewrite or a protocol copy per model is unnecessary. The missing piece was effective per-model capability policy: support/evidence metadata alone did not restrict writes. The Alpha adds that policy while preserving legacy model-9/12 behavior.

An arbitrary multi-profile runtime is **not implemented yet**. The registry now records `protocol_profile`, but setup/client composition still uses F79D-compatible identity/map on BL3372. A future independently captured RO/F104/different framing family needs a real selector and its own catalogue/fixtures. API/cloud property names cannot supply local field IDs or byte encodings.

## Findings addressed

| Finding | Change | Evidence/limits |
|---|---|---|
| Alpha metadata did not enforce permissions; adding a model would expose legacy controls and automatic clock writes | Explicit default-empty `allowed_write_fields`; model-1 no controls, no clock writes, service/coordinator/adapter guards; configured read-only policy retained across reloads | Mocked HA startup/reload, every existing control field, service bypasses, forced legacy clock option and fresh identity changes tested; G6/Midnight first-refresh clock sync preserved |
| Unknown model-specific units could be presented as calibrated measurements/statistics | Resin and per-cycle quantity unitless, all model-1 readings marked provisional and without statistics; add read-only setting sensors | Real HA state attributes tested; physical comparisons remain pending |
| Only resin/flow raw bytes were retained in normal diagnostics | Opt-in protocol field-pair capture used by adapter, raw bytes exposed in diagnostics/reference entities | Original report pairs tested; reconstructed frames are synthetic, not packet captures |
| Future partial model permissions could still show unrelated controls | Number/time/button creation filters explicit field permission; coordinator remains authoritative | Synthetic partial policy test; G6/Midnight policy unchanged |
| Inner frame length below six could escape as `IndexError` | Reject as `RunxinProtocolError` before indexing | Lengths 0..5 covered; valid existing frames retained |
| Protocol client accepted either read/write response opcode for either request | Require C9 for queries and D9 for writes; invalidate on mismatch | Wrong-opcode tests; no request encoding change |
| Discovery socket could remain open on authentication/type rejection | Close temporary socket on failed connect, preserving the original exception | Rejected-auth regression; no alternate authentication/unlock behavior |
| Runtime third-party exception text could leak identifiers in exported normal diagnostics | Replace exported poll-error text with a fixed message and retain structured transport metadata | Identifier/token test; HA's local runtime error text is unchanged |
| Release workflow would publish hyphenated versions as normal latest | Both release paths use `--prerelease --latest=false` for prerelease versions | Shell syntax/metadata reviewed; no release actually published |
| Documentation focused on G6/model 12 and blurred support/profile/evidence | Add support matrix, model-1 EN/CA/ES guides; rewrite architecture; update extension/report guides and issue template; document app workaround as one case | Links/translation/publication audits; manufacturer enum is descriptive only |

## Areas reviewed and retained

- Identity and lifecycle: MAC unique IDs, config-entry v2, platform cleanup, diagnostic-only storage/remove/unload, reconfigure/options and pending domain migration.
- Protocol: field catalogue, endian/duration/volume/enum behavior, provenance, unknown/missing values, frame validation, write encodings and pure-module boundaries.
- Transport: ordinary discovery/auth, devtype, TFB/decryption, bounded read retries, reauthentication, single-send writes, socket lifecycle and safe structured metadata.
- HA coordination/presentation: stale-state tolerance, busy cadence, vacation semantics, clock rollover, write reconciliation, regeneration prechecks, ranges, admin restrictions and unit/state-class contracts.
- Diagnostics: bounded collector, outbound opcode guard, cancellation, cache-versus-poll separation, redaction and same-response volume dependencies.
- Project/distribution: manifest/HACS metadata, version alignment, translations/branding, issue/contribution/security documentation, tests, offline/native-HA workflows and prerelease publication behavior.

Existing model-9/12 read sets, wire encoding, flow calibration/ranges, resin conversion, entity IDs, domain and documented pending write actions are preserved. Raw metadata and stricter invalid-response handling are additive; valid device request bytes are unchanged. No additional cloud dependencies or scans beyond 52 are introduced.

## Deferred work and limits

1. **Physical model-1 calibration:** compare resin/cycle quantity first, then capacity/consumption/flow, hardness scale, programme times/enums and field applicability. Software tests prove restrictions/decoding, not physical semantics. Zero/false receipt is not proof of implemented features.
2. **Profile variations:** introduce proven per-model codec/enum/applicability overrides if comparisons expose differences. Add a general selector only with a second independently demonstrated local profile; do not generalize the 52-field map to all Runxin devices.
3. **Release confidence:** native tests use HA 2026.9.4/Python 3.14.7/BroadLink 0.19.0. Hardware endurance and actual contributor HA restart/app comparison are not validated here. Neither the manifest nor HACS metadata declares a minimum HA version; compatibility with older versions needs a defined target and a dedicated job before claiming it.
4. **Migration:** PR #24 remains draft and needs the maintainer's backed-up pilot, HACS update-path decision and reconciliation with this newer main-line work before merging. Internal Ypsilon facade names/domain stay for compatibility.
5. **Packaging/CI:** a separate protocol package is premature without another real consumer. Pin floating validation actions to immutable revisions and add a minimum-HA compatibility job in later focused work; this Alpha does not claim those distribution changes.
6. **Raw snapshot timing:** field 52 remains cached independently; raw pairs represent received fields and can differ in age. Missing requested fields retain missing semantics. Unknown fields spontaneously returned can be preserved as bytes, but their meaning is unverified.

## Validation

Run `python scripts/publication_check.py`, `python scripts/audit.py`, `python scripts/field_surface_audit.py`, `python -m pytest -q` and `python -m compileall -q custom_components/ypsilon_local scripts tests`. The dedicated native-HA job includes the model-1 mutation/setup/entity tests. Local results and final GitHub checks are recorded in the PR; they must not be described as hardware validation.

Local results: **253 passed** with HA 2026.9.4/Python 3.14.7; **118 passed, 3 HA modules skipped** in the independent Python 3.13.15 environment. Publication, architecture/translation/protocol and field-surface audits passed. HA emits one upstream `aiohttp` deprecation warning.

Follow-up: the [second report](https://github.com/Danirv/runxin-local/issues/17#issuecomment-6045265175), generated inside HA 2026.9.4 with integration 2.8.0, again returns all 52 fields in two calls, without query failures or retries. Model 1, firmware 62016 and the unconfirmed resin/cycle values remain unchanged. Reference remaining capacity drops from 1304 to 1284 while daily use rises from 215 to 235: both differ by 20. This supports consistency of the shared map across snapshots, but does not validate units or physical applicability against the app. A second sanitized field-pair fixture covers this evidence.
