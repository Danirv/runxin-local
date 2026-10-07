# Architecture and documentation follow-up — 2026-10-08

[English](audit-followup.md) | [Català](audit-followup.ca.md) | [Español](audit-followup.es.md)

This continues the full-project audit after PR #25 and release **2.9.0-alpha.1**, starting from main `036b808`. The [initial audit](multi-model-audit.md) records the Alpha implementation; this document tracks the remaining shared work. PR #21 is excluded. Domain migration stays in draft PR #24.

## Architecture assessment

The transport / pure wire protocol / adapter / model policy / HA split is appropriate for the observed models. Compatible models should share framing and codecs, with evidenced conversion/permission differences in model policy. No directory copy per model or speculative protocol factory is needed now. A genuinely different wire family will require its own descriptor, catalogue, fixtures and explicit selection path. `protocol_profile` remains descriptive metadata.

| Area | Follow-up result |
|---|---|
| Protocol isolation | The static audit now catches relative imports escaping nested `runxin/` packages, networking dependencies and transport coupling. |
| Transport isolation | Transport code may use neutral Runxin errors/framing, but cannot import field/semantic maps or the HA adapter. The base contract cannot depend on BroadLink. |
| Model evidence versus permissions | Diagnostics retain model evidence and add `write_policy`: configured/observed identity, coordinator restriction, adapter restriction, allowed-field intersection and requested/permitted clock sync. Export uses cached state only. |
| HA compatibility checks | The full test suite runs separately on HA 2026.9.3 and 2026.9.4 with Python 3.14. Test-tool versions are pinned. These are tested releases, not a declared minimum version. |
| Workflow references | Checkout, setup-python, HACS and hassfest action source is pinned to immutable commits, and the audit rejects floating remote `uses` references. Existing Dependabot updates remain weekly. |
| Validator limits | HACS/hassfest upstream action definitions still launch containers with floating tags. Source pinning does not pin those images or every transitive dependency; it is not a fully reproducible toolchain. |
| Documentation | Contribution/publishing instructions cover the full suite and prereleases in EN/CA/ES, reference the shared support policy, retain the domain and distinguish current guidance from historical research. |

The compatibility facades, G6/model-12 conversions, ranges, command bytes, polling sets, domain, config-entry version and existing unique IDs remain unchanged. No new write or mechanical command is enabled. Runtime changes only add cached diagnostic metadata.

## Pending work and completion evidence

| Pending item | Evidence needed | Next action |
|---|---|---|
| Model 1 calibration | App labels/units and near-simultaneous HA readings; resin raw 240 and per-cycle reference 15 first | Contributor comparisons in issue #17, then a model-specific fixture/correction. No inferred multiplier or controls. |
| Model 12 promotion | Remaining field-7/47 and mechanical field-34 checks; sustained HA/app agreement | Owner validation described in the hardware guide; retain existing Alpha policy meanwhile. |
| G6 mechanical/vacation actions | Physical behavior/read-back for field 34; a demonstrated local vacation action | Separate targeted hardware work. Field 49 stays excluded; no guessed commands. |
| Model 14 / other families | Coherent read-only reports plus app/controller comparisons; independently observed local IDs/codecs for extra fields | Keep diagnostic-only policy. Cloud pressure/RO/TDS names do not supply local IDs above 52. |
| Domain migration | Backed-up G6 HA pilot, registry/automation checks, HACS update path and reconciliation with newer main | Continue PR #24 separately when the maintainer can run the pilot. |
| Older HA support | A chosen earlier compatibility target and native setup/entity/service tests against it | Current tests cover 2026.9.3/2026.9.4 only; do not add an untested HACS minimum or claim older support. |
| Validator image reproducibility | Verified compatible container digests and an intentional update process | Consider separately from source pinning; continue upstream validation meanwhile. |
| Package extraction | A second real protocol consumer and a supported version/distribution contract | Keep the pure package inside this repository until justified. |

The import audit is a static architecture check, not a runtime sandbox. Field 52 remains cached separately, so its bytes may be older than the other readings. Returned zero/false fields do not establish physical applicability.

## Validation and publishing

Use separate environments for `requirements-test-offline.txt`, `requirements-test-ha.txt` and `requirements-test-ha-baseline.txt`; run `python -m pytest -q` in each. Run the publication, architecture, field-surface and compile checks as documented in [CONTRIBUTING](../CONTRIBUTING.md).

This maintenance work is **Unreleased**. It does not move or replace the published Alpha tag. Choose a new manifest/changelog/info version before distributing it; the release workflow refuses an existing release. The maintainer controls merging/publication. Native tests use simulated I/O and are not hardware validation.

Local results: **275 passed on each HA version**, **136 passed / 3 HA modules skipped** offline, plus publication, architecture, field-surface, workflow YAML/shell, relative-link, diff and compile checks. Native HA emits one upstream aiohttp deprecation warning. Final GitHub checks are recorded in the PR.
