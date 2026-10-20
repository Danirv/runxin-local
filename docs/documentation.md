# Maintaining the documentation

[Documentation index](index.md) · [Contributing](../CONTRIBUTING.md)

## Where information belongs

| Information | Maintained location | Update rule |
|---|---|---|
| Project purpose and quick start | `README.md`, `docs/README.ca.md`, `docs/README.es.md` | Describe current behavior; link to detail instead of adding version-by-version sections |
| HACS card | `info.md` | Current version, setup and short release summary; link to the changelog for history |
| Installation and updates | `docs/installation*.md` | One process per language, including manual installation and retained entries |
| Everyday entities, water statistics, options, services | `docs/usage*.md` | Explain user-visible behavior; defer wire details to reference pages |
| Supported controllers and permissions | `models.py`, summarized in `docs/model-support.md` | Distinguish permission, evidence and uncertain conversions; do not infer support from API names |
| Model-specific setup and limits | `docs/models/model-*.md` | Current support first; no release-history stream or duplicated shared setup |
| Dated observations and source comparisons | `docs/evidence/`, hardware verification and WaterDevice research | Preserve date, hardware, bytes, scope and negative results; do not rewrite observations as universal facts |
| Wire format and field interpretation | Protocol, F79D, settings and BL3372 reference pages | Keep layers separate; link to the evidence behind exceptional codecs |
| Development and publication | `CONTRIBUTING*.md`, `PUBLISHING*.md` | Match requirement files, checks and workflows rather than an old test environment |
| Release chronology | `CHANGELOG.md` | Keep historical statements in their release context; a past Alpha label does not describe current support |

Current behavior is defined by the implementation. `models.py` is the support/permission registry, `hacs.json` declares minimum HA, `manifest.json` declares version/dependencies, entity/platform modules define presentation and `.github/workflows/` defines CI/release behavior. Cite the relevant code or evidence when they disagree with prose; do not change runtime policy merely to make a stale document true.

## Languages

User installation/usage and per-model guides are maintained in English, Catalan and Spanish. Some older technical translations are condensed; the English catalogue contains the full table. Translations must still agree on minimum HA, dependency namespace, controller support, units, write permissions and pending evidence.

For a behavior change, update the affected language variants in the same PR. If a detailed page is available only in English, label that fallback in the index rather than linking to a missing translation. Do not copy an entire release history into each language's landing page.

## Stable links and navigation

Use `docs/models/model-*.md` for new model links. The old `model-*-alpha*.md` files are compatibility entry points for URLs already shared in issues. They contain links and preserved section anchors, not a second maintained copy of the guide.

Every maintained page should be reachable from the documentation index or a linked guide. Use relative repository links. Keep explicit anchors when a heading already linked from an issue must change; update internal links to their canonical destination.

Run `python scripts/docs_check.py` to check local Markdown paths, fragments, navigation and language counterparts. It does not contact external sites or certify the accuracy of external manuals. External evidence links must be checked when changing their associated claim; historical sources are dated observations, not automatically current API documentation.

## Before merging documentation changes

- Compare current model tables, ranges, defaults and minimum versions with code and requirement files.
- Keep read evidence, write acceptance and optional permissions separate.
- Run documentation, publication and existing project audits. Documentation-only changes do not need a manifest version bump or another release.
- Keep HACS installation in sync with the default catalog; the accepted submission is [hacs/default#10717](https://github.com/hacs/default/pull/10717).
- Preserve identifiers, source links and dated evidence when moving content.

## Brand assets

The integration ships square `icon.png` / `icon@2x.png`, landscape `logo.png` / `logo@2x.png` and dark variants in `custom_components/ypsilon_local/brand/`. Each asset serves its own crop/layout; do not substitute a square icon for the wordmark. Existing branding checks cover geometry and distinct artwork. HACS/HA presentation can also depend on frontend caching.
