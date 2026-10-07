#!/usr/bin/env python3
"""Experimental offline domain migration. Standard library only; no device I/O.

Never run apply/rollback while Home Assistant Core is running. A full HA backup
is required independently of the private, limited transaction backup made here.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

OLD = "ypsilon_local"
NEW = "runxin_local"
CORE = ("core.config_entries", "core.entity_registry", "core.device_registry")
VERSIONS = {"core.config_entries": {1}, "core.entity_registry": {1}, "core.device_registry": {2, 3}}


class MigrationError(ValueError):
    """Unsafe or unsupported migration; nothing should be guessed."""


@dataclass
class Change:
    relative: str
    before: bytes | None
    after: bytes | None


@dataclass
class Plan:
    config: Path
    changes: list[Change]
    counts: dict[str, int]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(data: dict) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode()


def path_at(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise MigrationError("Unsafe path")
    path = root / rel
    for part in (path, *path.parents):
        if part == root.parent:
            break
        if part.is_symlink():
            raise MigrationError("Symlink paths are not supported")
    return path


def read_optional(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def store(config: Path, key: str) -> tuple[bytes, dict]:
    raw = path_at(config, f".storage/{key}").read_bytes()
    obj = json.loads(raw)
    if obj.get("key") != key or obj.get("version") not in VERSIONS.get(key, {1}):
        raise MigrationError(f"Unsupported storage schema: {key}")
    if not isinstance(obj.get("data"), dict):
        raise MigrationError(f"Invalid storage data: {key}")
    return raw, obj


def rows(obj: dict, key: str, *, required: bool = True) -> list[dict]:
    value = obj["data"].get(key, [] if not required else None)
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise MigrationError(f"Invalid registry collection: {key}")
    return value


def make_plan(config: Path) -> Plan:
    config = config.resolve()
    originals = {key: store(config, key) for key in CORE}
    work = {key: deepcopy(value[1]) for key, value in originals.items()}
    entries = rows(work[CORE[0]], "entries")
    old_entries = [e for e in entries if e.get("domain") == OLD]
    if any(e.get("domain") == NEW for e in entries):
        raise MigrationError("A runxin_local entry already exists; refusing to combine installations")
    if not old_entries:
        raise MigrationError("No ypsilon_local entries found; this is not a fresh-install tool")
    ids = {e.get("entry_id") for e in old_entries}
    if None in ids or len(ids) != len(old_entries):
        raise MigrationError("Missing or duplicate config-entry IDs")
    if len({e.get("entry_id") for e in entries}) != len(entries):
        raise MigrationError("Duplicate config-entry IDs in registry")
    counts = {"entries": len(ids), "entities": 0, "devices": 0, "reports": 0}
    for entry in old_entries:
        if entry.get("version") != 2:
            raise MigrationError("Pilot requires v2 (MAC-based) entries; upgrade the old integration first")
        entry["domain"] = NEW
    ent_obj = work[CORE[1]]
    entities = rows(ent_obj, "entities")
    for ent in entities + rows(ent_obj, "deleted_entities", required=False):
        if ent.get("platform") == OLD:
            if ent.get("config_entry_id") not in ids and ent in entities:
                raise MigrationError("Legacy entity is not linked to a migrated entry")
            ent["platform"] = NEW
            counts["entities"] += ent in entities
            options = ent.get("options", {})
            if OLD in options:
                if NEW in options:
                    raise MigrationError("Conflicting entity options")
                options[NEW] = options.pop(OLD)
    entity_keys = [(e.get("entity_id", "").split(".")[0], e.get("platform"), e.get("unique_id")) for e in entities]
    if len(set(entity_keys)) != len(entity_keys):
        raise MigrationError("Entity identity collision after migration")
    dev_obj = work[CORE[2]]
    device_lists = [rows(dev_obj, "devices"), rows(dev_obj, "child_devices", required=False), rows(dev_obj, "deleted_devices", required=False)]
    device_keys: dict[tuple, str] = {}
    for collection in device_lists:
        for dev in collection:
            identifiers = dev.get("identifiers", [])
            if not isinstance(identifiers, list) or any(not isinstance(i, (list, tuple)) or len(i) != 2 for i in identifiers):
                raise MigrationError("Invalid device identifiers")
            is_old = any(i[0] == OLD for i in identifiers)
            if is_old and collection is device_lists[0]:
                owners = set(dev.get("config_entries", []))
                if dev.get("config_entry_id"):
                    owners.add(dev["config_entry_id"])
                if not owners or not owners <= ids:
                    raise MigrationError("Legacy device has foreign ownership; needs individual review")
            for identifier in identifiers:
                if identifier[0] == OLD:
                    identifier[0] = NEW
            if dev.get("domain") == OLD:
                dev["domain"] = NEW
            counts["devices"] += is_old and collection is device_lists[0]
            # Deleted/orphan records can retain a former identity; compare active
            # devices and children only, using the config entry as in current HA.
            if collection is not device_lists[2]:
                for identifier in identifiers:
                    scope = dev.get("config_entry_id")
                    key = (*identifier, scope)
                    if key in device_keys and device_keys[key] != dev.get("id"):
                        raise MigrationError("Device identity collision after migration")
                    device_keys[key] = dev.get("id")
    changes = []
    for key in CORE:
        before, obj = originals[key]
        if obj != work[key]:
            changes.append(Change(f".storage/{key}", before, encode(work[key])))
    for entry in old_entries:
        if not entry.get("data", {}).get("diagnostic_only"):
            continue
        report_id = entry["data"].get("diagnostic_report_id")
        if not isinstance(report_id, str) or not report_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in report_id):
            raise MigrationError("Invalid diagnostic report ID")
        old_key = f"{OLD}.compatibility.{report_id}"
        new_key = f"{NEW}.compatibility.{report_id}"
        if path_at(config, f".storage/{new_key}").exists():
            raise MigrationError("Destination report already exists")
        if not path_at(config, f".storage/{old_key}").exists():
            continue  # Existing missing report remains missing, not recreated.
        before, obj = store(config, old_key)
        obj["key"] = new_key
        changes.extend([Change(f".storage/{old_key}", before, None), Change(f".storage/{new_key}", None, encode(obj))])
        counts["reports"] += 1
    return Plan(config, changes, counts)


def tree_digest(path: Path) -> str:
    pieces = []
    for item in sorted(path.rglob("*")):
        if item.is_symlink():
            raise MigrationError("Integration tree contains symlinks")
        if "__pycache__" in item.parts or item.suffix == ".pyc":
            continue
        if item.is_file():
            pieces.append(f"{item.relative_to(path).as_posix()}:{digest(item.read_bytes())}")
    return digest("\n".join(pieces).encode())


def check_source(source: Path) -> None:
    manifest = json.loads((source / "manifest.json").read_bytes())
    if manifest.get("domain") != NEW:
        raise MigrationError("Source is not the runxin_local integration")
    tree_digest(source)


def atomic_write(path: Path, content: bytes, mode: int = 0o600) -> None:
    fd, name = tempfile.mkstemp(prefix=".runxin-stage-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            os.chmod(name, mode)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def transaction_lock(config: Path):
    # Linux HA OS/container and Linux/macOS offline copies. An advisory lock
    # prevents another copy of this tool, not Home Assistant; Core must be stopped.
    import fcntl
    path = path_at(config, ".runxin-domain-migration.lock")
    with path.open("a") as handle:
        os.chmod(path, 0o600)
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as err:
            raise MigrationError("Another migration transaction is running") from err
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def apply_plan(plan: Plan, source: Path) -> Path:
    """Install the new code and change registries while Core is stopped."""
    check_source(source)
    config = plan.config
    old_code = path_at(config, f"custom_components/{OLD}")
    new_code = path_at(config, f"custom_components/{NEW}")
    if not old_code.is_dir() or new_code.exists():
        raise MigrationError("Expected only the existing ypsilon_local code folder")
    tree_digest(old_code)
    for change in plan.changes:
        if read_optional(path_at(config, change.relative)) != change.before:
            raise MigrationError("Storage changed since preview; stop Core and retry")
    backup = config / f"runxin-domain-backup-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    backup.mkdir(mode=0o700)
    stage = backup / "staged_component"
    shutil.copytree(source, stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    metadata = {"schema": 1, "config": str(config), "state": "prepared", "counts": plan.counts,
                "new_code_sha256": tree_digest(stage), "changes": []}
    for index, change in enumerate(plan.changes):
        backup_file = f"original-{index}.bin" if change.before is not None else None
        if backup_file:
            atomic_write(backup / backup_file, change.before)
        metadata["changes"].append({"path": change.relative, "backup_file": backup_file,
                                   "before_sha256": digest(change.before) if change.before is not None else None,
                                   "after_sha256": digest(change.after) if change.after is not None else None})
    journal = backup / "transaction.json"
    atomic_write(journal, encode(metadata))
    try:
        # Every original file is durably backed up before any registry is changed.
        for change in plan.changes:
            path = path_at(config, change.relative)
            if read_optional(path) != change.before:
                raise MigrationError("Storage changed during migration")
            if change.after is None:
                path.unlink()
            else:
                atomic_write(path, change.after)
        os.replace(old_code, backup / "legacy_component")
        os.replace(stage, new_code)
        metadata["state"] = "complete"
        atomic_write(journal, encode(metadata))
    except BaseException:
        # Restore only files this transaction changed. Core is still required to
        # be stopped; the private journal supports recovery after process death.
        for change in plan.changes:
            path = path_at(config, change.relative)
            if change.before is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, change.before)
        if (backup / "legacy_component").exists():
            if new_code.exists():
                shutil.rmtree(new_code)
            os.replace(backup / "legacy_component", old_code)
        metadata["state"] = "reverted"
        atomic_write(journal, encode(metadata))
        raise
    return backup


def read_transaction(backup: Path) -> tuple[Path, dict]:
    metadata = json.loads((backup / "transaction.json").read_bytes())
    if metadata.get("schema") != 1 or metadata.get("state") not in {"prepared", "complete"}:
        raise MigrationError("Unsupported or already reverted transaction")
    config = Path(metadata["config"]).resolve()
    if backup.resolve().parent != config:
        raise MigrationError("Backup does not belong to this configuration directory")
    for change in metadata["changes"]:
        if not change["path"].startswith(".storage/"):
            raise MigrationError("Unexpected transaction path")
        path_at(config, change["path"])
        if change["backup_file"]:
            raw = path_at(backup, change["backup_file"]).read_bytes()
            if digest(raw) != change["before_sha256"]:
                raise MigrationError("Backup checksum mismatch")
    return config, metadata


def rollback(backup: Path) -> None:
    config, metadata = read_transaction(backup)
    old_code = path_at(config, f"custom_components/{OLD}")
    new_code = path_at(config, f"custom_components/{NEW}")
    for change in metadata["changes"]:
        raw = read_optional(path_at(config, change["path"]))
        sha = digest(raw) if raw is not None else None
        if sha not in {change["before_sha256"], change["after_sha256"]}:
            raise MigrationError("Storage changed after migration; restore the full HA backup instead")
    if new_code.exists() and tree_digest(new_code) != metadata["new_code_sha256"]:
        raise MigrationError("New integration code changed; restore the full HA backup instead")
    legacy = backup / "legacy_component"
    if legacy.exists() and old_code.exists():
        raise MigrationError("Legacy code folder already exists")
    if not legacy.exists() and not old_code.exists():
        raise MigrationError("Legacy code backup is missing")
    for change in metadata["changes"]:
        path = path_at(config, change["path"])
        if change["backup_file"]:
            atomic_write(path, (backup / change["backup_file"]).read_bytes())
        else:
            path.unlink(missing_ok=True)
    if legacy.exists():
        if new_code.exists():
            shutil.rmtree(new_code)
        os.replace(legacy, old_code)
    metadata["state"] = "reverted"
    atomic_write(backup / "transaction.json", encode(metadata))


def verify(backup: Path) -> dict[str, int]:
    """Check preserved user-facing identities/settings after a real HA restart."""
    config, metadata = read_transaction(backup)
    if metadata["state"] != "complete":
        raise MigrationError("Migration did not complete")
    saved = {c["path"]: json.loads((backup / c["backup_file"]).read_bytes())
             for c in metadata["changes"] if c["backup_file"]}
    old_entries = [e for e in rows(saved[f".storage/{CORE[0]}"], "entries") if e.get("domain") == OLD]
    current_entries = {e["entry_id"]: e for e in rows(store(config, CORE[0])[1], "entries")}
    ids = {e["entry_id"] for e in old_entries}
    for old in old_entries:
        new = current_entries.get(old["entry_id"], {})
        for key in ("entry_id", "unique_id", "data", "options", "title", "disabled_by", "pref_disable_polling", "pref_disable_new_entities", "version", "minor_version"):
            if old.get(key) != new.get(key):
                raise MigrationError(f"Config entry setting changed: {key}")
        if new.get("domain") != NEW:
            raise MigrationError("Config entry did not keep its new domain")
    for key, collection, id_key, fields in (
        (CORE[1], "entities", "entity_id", ("id", "entity_id", "unique_id", "config_entry_id", "device_id", "name", "icon", "area_id", "disabled_by", "hidden_by", "labels", "aliases", "aliases_v2")),
        (CORE[2], "devices", "id", ("id", "config_entry_id", "config_entries", "area_id", "name_by_user", "disabled_by", "labels", "connections")),
    ):
        if f".storage/{key}" not in saved:
            continue
        old_rows = rows(saved[f".storage/{key}"], collection)
        current_rows = rows(store(config, key)[1], collection)
        new_rows = {row[id_key]: row for row in current_rows}
        def owned(row):
            return row.get("config_entry_id") in ids or bool(set(row.get("config_entries", [])) & ids)
        if {r[id_key] for r in old_rows if owned(r)} != {r[id_key] for r in current_rows if owned(r)}:
            raise MigrationError("Owned registry IDs changed or duplicated")
        for old in old_rows:
            if not owned(old):
                continue
            new = new_rows.get(old[id_key], {})
            for field in fields:
                if old.get(field) != new.get(field):
                    raise MigrationError(f"Registry identity or preference changed: {field}")
            if collection == "entities" and new.get("platform") != NEW:
                raise MigrationError("Entity platform did not migrate")
            if collection == "entities":
                expected_options = deepcopy(old.get("options", {}))
                if OLD in expected_options:
                    expected_options[NEW] = expected_options.pop(OLD)
                if expected_options != new.get("options", {}):
                    raise MigrationError("Entity options changed")
            else:
                expected_identifiers = [[NEW if namespace == OLD else namespace, value]
                                        for namespace, value in old.get("identifiers", [])]
                if sorted(expected_identifiers) != sorted(new.get("identifiers", [])):
                    raise MigrationError("Device identifiers did not migrate")
    for change in metadata["changes"]:
        if change["path"].startswith(f".storage/{NEW}.compatibility."):
            raw = read_optional(path_at(config, change["path"]))
            if raw is None or digest(raw) != change["after_sha256"]:
                raise MigrationError("Saved diagnostic report changed or is missing")
    return metadata["counts"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("preview", "apply", "verify", "rollback"))
    parser.add_argument("--config-dir", type=Path)
    parser.add_argument("--source-dir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--core-stopped", action="store_true", help="Explicitly confirm Core is stopped; this tool cannot stop it")
    args = parser.parse_args(argv)
    try:
        if args.operation in {"preview", "apply"}:
            if not args.config_dir:
                raise MigrationError("--config-dir is required")
            plan = make_plan(args.config_dir)
            source = args.source_dir.resolve() / "custom_components" / NEW
            check_source(source)
            print(json.dumps({"operation": args.operation, "counts": plan.counts}, indent=2))
            if args.operation == "apply":
                if not args.core_stopped:
                    raise MigrationError("Stop Home Assistant Core, then pass --core-stopped")
                with transaction_lock(plan.config):
                    # Re-read under the transaction lock rather than reuse a preview.
                    backup = apply_plan(make_plan(plan.config), source)
                print(f"Migration complete. Private backup: {backup}")
        else:
            if not args.backup_dir:
                raise MigrationError("--backup-dir is required")
            backup = args.backup_dir.resolve()
            config, _ = read_transaction(backup)
            if args.operation == "verify":
                print(json.dumps({"identities_preserved": True, "counts": verify(backup)}, indent=2))
            else:
                if not args.core_stopped:
                    raise MigrationError("Stop Home Assistant Core, then pass --core-stopped")
                with transaction_lock(config):
                    rollback(backup)
                print("Original registries and integration code restored")
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as err:
        # Registry/credential contents and arbitrary exception messages must not
        # be printed; only our fixed validation messages are user-facing.
        print(f"Migration refused: {err if isinstance(err, MigrationError) else type(err).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
