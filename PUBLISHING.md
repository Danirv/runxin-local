# Publishing Runxin Local

[English](PUBLISHING.md) | [Català](PUBLISHING.ca.md) | [Español](PUBLISHING.es.md)

Runxin Local is included in the HACS default catalog following [hacs/default#10717](https://github.com/hacs/default/pull/10717), merged on 20 October 2026. Normal releases continue in this repository; no new catalog submission is needed for each release. Model support labels and integration release channels are independent.

<a id="1-repository-metadata"></a>
<a id="2-repository-requirements"></a>
<a id="3-publish-a-github-release-from-the-web"></a>
<a id="4-test-through-hacs"></a>
<a id="5-hacs-default-inclusion"></a>
<a id="prereleases-and-maintenance-changes"></a>
<a id="publishing-runxin-local-on-github-and-hacs"></a>
<a id="release-discipline"></a>
<a id="repository-rename"></a>

## Prepare a release

1. Choose a new, unused semantic version. Never reuse or move a published tag to distribute later code.
2. Update `manifest.json`, `CHANGELOG.md` and the title/current-release summary in `info.md` together. Keep older history in the changelog.
3. Run the checks below in the offline environment and run the full native HA suites in separate environments from `requirements-test-ha.txt` and `requirements-test-ha-baseline.txt`.
4. Merge the release changes to `main` after HACS, hassfest and audit/HA regressions pass.

Documentation-only maintenance can merge without changing the manifest or publishing a release.

## Publish from GitHub

1. Open **Actions → Publish GitHub release → Run workflow**.
2. Select **main** and run the workflow.
3. Check the resulting release, `v<manifest version>` tag, manual-install ZIP and validation runs.

The workflow reads the manifest version, runs offline publication/audit/field-surface/tests/compile checks, rejects an existing GitHub Release, creates or recovers its annotated tag, checks out and validates that exact tagged source, builds the ZIP and publishes the release. It does not replace the native HA checks performed before merge.

A version containing `-` is published as `--prerelease --latest=false`. A model's Alpha/Beta status alone does not make the integration release a prerelease or alter write permissions.

## Git CLI alternative

```bash
VERSION="$(python -c 'import json; print(json.load(open("custom_components/ypsilon_local/manifest.json"))["version"])')"
git tag -a "v${VERSION}" -m "Runxin Local ${VERSION}"
git push origin "v${VERSION}"
```

## Checks and repository maintenance

```bash
python scripts/docs_check.py
python scripts/publication_check.py
python scripts/audit.py
python scripts/field_surface_audit.py
python -m pytest -q
python -m compileall -q custom_components/ypsilon_local scripts tests
```

Do not manually create a duplicate release for the same tag. A manually pushed tag triggers the tag-release job; a tag created by the web job does not require a second run.

Maintain Issues, repository topics, brand assets, action pins and HACS/hassfest checks. The completed repository rename is documented in [installation](docs/installation.md); keep the old GitHub name unused for redirects and keep the integration domain `ypsilon_local`.

`scripts/configure_repository.py` is for adapting a fresh template/fork, not a routine release step. Never commit vendor APKs, firmware, proprietary dumps, credentials, keys or unredacted captures. See [contributing](CONTRIBUTING.md) and [documentation maintenance](docs/documentation.md).
