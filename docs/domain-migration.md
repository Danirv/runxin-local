# Domain migration pilot: ypsilon_local → runxin_local

This is an **experimental 3.0.0-alpha.1 branch**, not a normal HACS update.
The stable 2.8.x integration continues to use `ypsilon_local`. Do not merge or
publish this pilot as stable before real-installation testing. [Català](domain-migration.ca.md).

## Why an offline pilot

Home Assistant treats an integration domain as permanent. Its normal config-entry
update API does not accept a new domain. HACS also expects one integration folder
per repository. The pilot therefore does not modify HA internals in a running
instance or ship two active integrations. The standard-library migration tool
changes explicitly scoped stored records **while HA Core is stopped** and installs
the new folder in the same transaction. This is an experimental maintenance
operation, not an official HA domain-renaming API.

The tool preserves config-entry IDs, entity registry IDs and entity IDs, device
IDs, unique IDs, entry data/options and user preferences. It changes config-entry
`domain`, entity `platform` and device identifier namespaces, including deleted
records, and moves saved compatibility-report stores under their new keys. It
refuses conflicting destinations, foreign device ownership, v1 config entries,
unknown major storage versions and unsafe paths. Minor storage revisions are
preserved rather than converted. HA 2026.9.4's actual storage schemas are tested;
other versions still need validation.

It never contacts the controller, writes to the recorder database, rewrites
history/statistics, or edits automations/dashboards. Entity IDs, units and protocol
conversions remain unchanged. On restarting, the integration resumes its existing
normal behavior, including polling and any configured clock synchronization.
A cloned HA must not access the same controller concurrently with the production
instance; stop the production integration/Core or block the clone's device access.

Both `runxin_local.write_fields` / `advance_phase` and their `ypsilon_local` aliases
use the same admin-only guarded handlers and original config-entry IDs. Diagnostic
entries remain read-only through both namespaces. Templates filtering explicitly
by integration domain and logger configuration referencing the old Python package
need individual adjustment. This tool cannot preserve every arbitrary literal in
external configuration; device-automation references containing an explicit old
domain also need review. Standard entity-ID-based automations keep their references.

## Prepare (no changes yet)

1. Record HA Core, HACS and integration versions. The pilot requires the existing
   MAC-based v2 config entries. Upgrade through the old domain first if needed.
2. Create and download a **full Home Assistant backup**, including recorder data.
   For HA OS in Proxmox, a stopped-VM backup/snapshot provides an additional route
   back; a clone must not run alongside production against the same device.
3. Save the original entity IDs, custom names, disabled entities, device ID, entry
   ID, areas, labels and key dashboards. Note latest state/history/statistics.
4. Suspend automatic HACS updates for this integration during the pilot. HACS's
   cached repository domain is not rewritten by this tool. Do not use HACS to
   download/reinstall/remove this integration mid-pilot. Its metadata/update path
   must be checked separately before a stable release; do not edit its storage.
5. Use a terminal outside HA Core (for HA OS, an SSH/Terminal add-on that stays
   running when Core stops). It must have **Python 3.10+ and git**, with read/write
   access to the real HA config directory. No Python dependencies are required.
   Do not install Python packages into HA Core. If those tools or paths are absent,
   identify the add-on/environment before proceeding.

Example for an HA OS terminal with `/config` as its real config directory and
`/share` as persistent working storage:

```sh
python3 --version
git --version
ha core info
git clone --depth 1 --branch feat/runxin-domain-migration https://github.com/Danirv/runxin-local.git /share/runxin-domain-pilot
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py preview --config-dir /config
```

Some add-ons expose HA's configuration as `/homeassistant` instead. Use that path
consistently if it contains `.storage/core.config_entries`. The script does not
print hosts, MACs, credentials or full stored records. Preview reads the config,
validates the source and reports counts only; it changes nothing. It refuses a
migration if new-domain entries already exist. **Do not remove/re-add entries to
work around a refusal.** Investigate the specific condition first.

## Apply with Core stopped

Check that the downloaded code is the draft PR's intended revision. The default
source is the checkout containing the script, so no separate install is needed.

```sh
ha core stop
ha core info
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py apply --config-dir /config --core-stopped
```

`--core-stopped` is your explicit acknowledgement: the script cannot independently
verify Core's status across containers and does not stop it. Confirm it is stopped
first. If preview/apply refuses, **keep Core stopped** until the folder/registries
are consistent or the backup is restored; do not improvise storage edits.

Before changing registries, apply saves exact original bytes and a transaction
journal under `/config/runxin-domain-backup-<timestamp>-<suffix>` with private
permissions. The original integration folder is retained there. The new code is
staged, checksums guard against concurrent changes, and individual files are
replaced atomically. Changes across files are not a single filesystem transaction;
handled errors trigger restoration, while the journal supports recovery after an
interruption. The snapshot is limited to affected records/code and **does not
replace a full HA backup**. It includes all config entries in the saved registry,
which can contain other integrations' credentials: **never attach it to an issue**.

If apply completes, run verify once before restarting, using the exact printed
backup path:

```sh
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py verify --backup-dir /config/runxin-domain-backup-<timestamp>-<suffix>
ha core start
```

Replace the example path; do not type the angle brackets literally. Core starts
under `runxin_local` with the existing entry/device/entity IDs. The old folder is
not left active. New-domain setup/discovery refuses while old-domain entries
remain, preventing a duplicate flow from masking an incomplete migration.

## Validate and provide results

After startup, check all of the following:

- One integration/device for each previous entry, no duplicate entities or `_2`
  IDs, same entity/config-entry/device IDs, names, areas, labels and disabled flags.
- Normal G6 readings and units match the pre-migration baseline; existing history,
  long-term statistics and dashboards continue under the original entity IDs.
- Options, including polling and clock synchronization, remain as before.
- Existing entity-based automations still resolve their targets. Review explicit
  `ypsilon_local` domain filters, Python logger names and device-automation domains.
- Both advanced service namespaces are listed; an old alias points to the original
  config entry. Do not start a regeneration just to test a namespace. Any actual
  write test should be a previously validated, appropriate setting; the migration
  itself requires no writes. The protocol/read-back guards are unchanged.
- Any pre-existing diagnostic entry still downloads the same saved report without
  polling or controls.
- Restart Core again and repeat the identity/duplicate check. Confirm no missing
  integration, duplicate-device, or entry-migration errors in logs.

Once Core has persisted the post-restart registries, run the read-only verification:

```sh
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py verify --backup-dir /config/runxin-domain-backup-<timestamp>-<suffix>
```

Verification compares identity/settings and saved reports with the private
snapshot, detects missing/additional owned registry IDs, and prints counts. It
cannot prove recorder continuity, physical device behavior, all YAML references,
or HACS upgrades; the visual/live checks above are still needed. Active Core can
save asynchronously, so repeat after a clean stop if the result is ambiguous.
Share versions, anonymized screenshots, verification counts and sanitized errors,
not the backup or complete storage files. Real G6 success does not validate model
12 or other HA versions.

## Return to the old version

For an immediate pre-start rollback, or recovery from an interrupted apply:

```sh
ha core stop
python3 /share/runxin-domain-pilot/scripts/migrate_domain.py rollback --backup-dir /config/runxin-domain-backup-<timestamp>-<suffix> --core-stopped
ha core start
```

Rollback verifies snapshot checksums and refuses to overwrite registry/code
changes made since migration. It restores the original bytes and old folder.
**After running the pilot in real HA, restore the full pre-test HA backup/snapshot
if rollback refuses.** Do not force registry changes or simply replace the folder;
that would leave config entries pointing to the wrong domain. Do not delete the
private snapshot until the outcome and the return path are settled.

## Stable-release gate

Keep this PR in draft until the real G6 pilot, two restarts, original history/
statistics, options and automations are confirmed. Separately test HACS refreshing
from the old installation and the future prerelease/release without recreating
entries, removing the wrong folder or retaining two active domains. The offline
migration is a one-time user operation; do not present it as an automatic HACS
update. Publishing an alpha must use GitHub's prerelease flag and must not replace
the stable latest release. Decide the public migration path before merging into
main or publishing 3.0.0 stable.
