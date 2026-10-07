"""Offline migration invariants, refusal paths, transaction recovery and rollback."""
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import migrate_domain as migration


@pytest.fixture
def installation(tmp_path):
    config = tmp_path / 'config'
    storage = config / '.storage'
    storage.mkdir(parents=True)
    entries = [
        {'entry_id':'g6','domain':'ypsilon_local','version':2,'minor_version':1,'unique_id':'02:00:00:00:00:09',
         'title':'My G6','data':{'host':'192.0.2.9'},'options':{'auto_sync_clock':False},'disabled_by':None},
        {'entry_id':'diag','domain':'ypsilon_local','version':2,'unique_id':'02:00:00:00:00:14',
         'data':{'diagnostic_only':True,'diagnostic_report_id':'opaque_report'},'options':{},'disabled_by':'user'},
        {'entry_id':'other','domain':'other','version':1,'data':{'secret':'do not log'},'options':{}},
    ]
    entities = [
        {'id':'registry-id','entity_id':'sensor.my_original_flow','platform':'ypsilon_local',
         'unique_id':'02:00:00:00:00:09_flow_rate','config_entry_id':'g6','device_id':'device-id',
         'name':'User custom name','area_id':'kitchen','disabled_by':'user','hidden_by':'user',
         'labels':['label'],'options':{'sensor':{'display_precision':3},'ypsilon_local':{'example':1}}},
        {'entity_id':'sensor.other','platform':'other','unique_id':'other','config_entry_id':'other'},
    ]
    devices = [{'id':'device-id','config_entry_id':'g6','identifiers':[['ypsilon_local','02:00:00:00:00:09']],
                'connections':[['mac','02:00:00:00:00:09']],'area_id':'kitchen','name_by_user':'My softener'}]
    objects = {
        'core.config_entries':(1,{'entries':entries}),
        'core.entity_registry':(1,{'entities':entities,'deleted_entities':[{'entity_id':'sensor.deleted', 'platform':'ypsilon_local','unique_id':'deleted'}]}),
        'core.device_registry':(3,{'devices':devices,'child_devices':[], 'deleted_devices':[{'id':'deleted','domain':'ypsilon_local','identifiers':[['ypsilon_local','deleted']]}]}),
        'ypsilon_local.compatibility.opaque_report':(1,{'fields':[{'field_id':1,'raw_byte_pair':[14,0]}]}),
    }
    for key,(version,data) in objects.items():
        (storage/key).write_bytes(migration.encode({'key':key,'version':version,'minor_version':0,'data':data}))
    old = config/'custom_components/ypsilon_local'
    old.mkdir(parents=True)
    (old/'manifest.json').write_text('{"domain":"ypsilon_local","version":"2.8.0"}')
    (old/'custom.txt').write_text('original local code')
    # Neither recorder nor automations should be touched by this migration.
    (config/'home-assistant_v2.db').write_bytes(b'recorder untouched')
    (config/'automations.yaml').write_text('action: ypsilon_local.write_fields\n')
    source = tmp_path/'source'
    source.mkdir()
    (source/'manifest.json').write_text('{"domain":"runxin_local","version":"3.0.0-alpha.1"}')
    (source/'const.py').write_text('DOMAIN = "runxin_local"\n')
    return config, source


def snapshot(config):
    return {str(p.relative_to(config)):p.read_bytes() for p in config.rglob('*') if p.is_file()}


def edit(config, key, fn):
    path=config/'.storage'/key
    obj=json.loads(path.read_bytes());fn(obj['data']);path.write_bytes(migration.encode(obj))


def test_preview_has_no_side_effects_or_secret_output(installation, capsys):
    config,source=installation
    before=snapshot(config)
    assert migration.make_plan(config).counts == {'entries':2,'entities':1,'devices':1,'reports':1}
    assert snapshot(config)==before
    assert 'secret' not in capsys.readouterr().out


def test_apply_retains_all_ids_settings_reports_and_unrelated_data(installation):
    config,source=installation
    before=snapshot(config)
    backup=migration.apply_plan(migration.make_plan(config),source)
    assert migration.verify(backup)=={'entries':2,'entities':1,'devices':1,'reports':1}
    after=snapshot(config)
    for key in ('automations.yaml','home-assistant_v2.db'):
        assert after[key]==before[key]
    ents=json.loads(after['.storage/core.entity_registry'])['data']
    assert ents['entities'][0]['options']=={'sensor':{'display_precision':3},'runxin_local':{'example':1}}
    assert ents['deleted_entities'][0]['platform']=='runxin_local'
    assert ents['entities'][1]==json.loads(before['.storage/core.entity_registry'])['data']['entities'][1]
    report=json.loads(after['.storage/runxin_local.compatibility.opaque_report'])
    assert report['key']=='runxin_local.compatibility.opaque_report'
    assert report['data']==json.loads(before['.storage/ypsilon_local.compatibility.opaque_report'])['data']
    assert not (config/'custom_components/ypsilon_local').exists()
    assert (backup/'legacy_component/custom.txt').read_text()=='original local code'
    assert backup.stat().st_mode & 0o777 == 0o700
    for p in backup.glob('original-*.bin'):
        assert p.stat().st_mode & 0o777 == 0o600


def test_rollback_restores_original_bytes_and_code(installation):
    config,source=installation
    before=snapshot(config)
    backup=migration.apply_plan(migration.make_plan(config),source)
    migration.rollback(backup)
    after=snapshot(config)
    for key,value in before.items():
        assert after[key]==value
    assert not (config/'custom_components/runxin_local').exists()
    assert not (config/'.storage/runxin_local.compatibility.opaque_report').exists()
    with pytest.raises(migration.MigrationError):
        migration.rollback(backup)


@pytest.mark.parametrize('mutate',[
    lambda c:edit(c,'core.config_entries',lambda d:d['entries'].append({'entry_id':'new','domain':'runxin_local'})),
    lambda c:edit(c,'core.config_entries',lambda d:d['entries'][0].update(version=1)),
    lambda c:edit(c,'core.entity_registry',lambda d:d['entities'][0].update(config_entry_id='foreign')),
    lambda c:edit(c,'core.entity_registry',lambda d:d['entities'].append({**d['entities'][0],'entity_id':'sensor.collision','platform':'runxin_local'})),
    lambda c:edit(c,'core.device_registry',lambda d:d['devices'][0].update(config_entry_id='foreign')),
    lambda c:edit(c,'core.config_entries',lambda d:d['entries'][1]['data'].update(diagnostic_report_id='../unsafe')),
])
def test_unsafe_or_conflicting_installations_refused_without_writes(installation,mutate):
    config,source=installation;mutate(config);before=snapshot(config)
    with pytest.raises(migration.MigrationError):migration.make_plan(config)
    assert snapshot(config)==before


def test_unknown_schema_and_symlink_refused(installation):
    config,source=installation
    path=config/'.storage/core.device_registry';obj=json.loads(path.read_bytes());obj['version']=999;path.write_bytes(migration.encode(obj))
    with pytest.raises(migration.MigrationError):migration.make_plan(config)
    path.unlink();path.symlink_to(source/'manifest.json')
    with pytest.raises(migration.MigrationError):migration.make_plan(config)


def test_detects_concurrent_storage_change_before_any_mutation(installation):
    config,source=installation;plan=migration.make_plan(config)
    edit(config,'core.config_entries',lambda d:d['entries'][0]['options'].update(new_option=True))
    before=snapshot(config)
    with pytest.raises(migration.MigrationError):migration.apply_plan(plan,source)
    assert snapshot(config)==before


def test_failed_transaction_automatically_restores_registries_and_code(installation):
    config,source=installation;before=snapshot(config)
    real=migration.atomic_write
    def fail(path,*args,**kwargs):
        if path==config/'.storage/core.entity_registry' and not fail.failed:
            fail.failed=True
            raise OSError('injected failure')
        return real(path,*args,**kwargs)
    fail.failed=False
    with patch.object(migration,'atomic_write',side_effect=fail):
        with pytest.raises(OSError):migration.apply_plan(migration.make_plan(config),source)
    after=snapshot(config)
    for key,value in before.items():assert after[key]==value
    assert not (config/'custom_components/runxin_local').exists()


def test_rollback_refuses_changes_after_ha_restart(installation):
    config,source=installation;backup=migration.apply_plan(migration.make_plan(config),source)
    edit(config,'core.config_entries',lambda d:d['entries'][0]['options'].update(new_setting=True))
    before=snapshot(config)
    with pytest.raises(migration.MigrationError,match='full HA backup'):migration.rollback(backup)
    assert snapshot(config)==before


def test_verify_detects_lost_entity_preferences(installation):
    config,source=installation;backup=migration.apply_plan(migration.make_plan(config),source)
    edit(config,'core.entity_registry',lambda d:d['entities'][0].update(name='Lost name'))
    with pytest.raises(migration.MigrationError,match='preference'):migration.verify(backup)


def test_cli_requires_explicit_stop_acknowledgement(installation,capsys):
    config,source=installation
    checkout=source.parent/'checkout';(checkout/'custom_components').mkdir(parents=True)
    import shutil
    shutil.copytree(source,checkout/'custom_components/runxin_local')
    before=snapshot(config)
    assert migration.main(['apply','--config-dir',str(config),'--source-dir',str(checkout)])==1
    assert snapshot(config)==before
    assert '--core-stopped' in capsys.readouterr().out


def test_failed_code_install_restores_moved_old_code(installation):
    config,source=installation;before=snapshot(config)
    real=migration.os.replace
    def fail(src,dest):
        if Path(dest)==config/'custom_components/runxin_local' and not fail.failed:
            fail.failed=True
            raise OSError('injected code move failure')
        return real(src,dest)
    fail.failed=False
    with patch.object(migration.os,'replace',side_effect=fail):
        with pytest.raises(OSError):migration.apply_plan(migration.make_plan(config),source)
    after=snapshot(config)
    for key,value in before.items():assert after[key]==value


def test_prepared_journal_can_recover_after_interruption(installation):
    config,source=installation;before=snapshot(config)
    backup=migration.apply_plan(migration.make_plan(config),source)
    journal=backup/'transaction.json'
    data=json.loads(journal.read_bytes());data['state']='prepared';journal.write_bytes(migration.encode(data))
    migration.rollback(backup)
    after=snapshot(config)
    for key,value in before.items():assert after[key]==value


def test_corrupted_backup_refuses_rollback(installation):
    config,source=installation
    backup=migration.apply_plan(migration.make_plan(config),source)
    (backup/'original-0.bin').write_bytes(b'corrupt')
    before=snapshot(config)
    with pytest.raises(migration.MigrationError,match='checksum'):migration.rollback(backup)
    assert snapshot(config)==before


def test_verify_detects_new_duplicate_entity(installation):
    config,source=installation;backup=migration.apply_plan(migration.make_plan(config),source)
    edit(config,'core.entity_registry',lambda d:d['entities'].append({**d['entities'][0],'entity_id':'sensor.duplicate','unique_id':'unexpected'}))
    with pytest.raises(migration.MigrationError,match='duplicated'):migration.verify(backup)
