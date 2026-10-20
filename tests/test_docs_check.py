"""Broken paths, fragments and orphan guides must fail documentation CI."""

from pathlib import Path
import importlib.util

SPEC = importlib.util.spec_from_file_location(
    "docs_check", Path(__file__).resolve().parents[1] / "scripts" / "docs_check.py"
)
docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(docs)


def test_unicode_duplicates_and_explicit_anchors_ignore_code():
    text = '# Instal·lació i ús\n## Resin\n## Resin\n<a id="old-name"></a>\n```md\n## Fake\n```'
    assert docs.anchors(text) == {"installació-i-ús", "resin", "resin-1", "old-name"}


def test_valid_local_links_and_external_urls(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text('[Guide](docs/guide.md#water-usage) [Web](https://example.org/missing)')
    (tmp_path / "docs/guide.md").write_text('# Water usage\n[Home](../README.md)\n```md\n[Example](not-a-real-file.md)\n```')
    assert docs.check(tmp_path) == []


def test_missing_path_fragment_orphan_and_translation_are_reported(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text('[Guide](docs/guide.md#missing) [File](absent.md)')
    (tmp_path / "docs/guide.md").write_text('# Real heading')
    (tmp_path / "docs/orphan.ca.md").write_text('# Sense índex')
    errors = '\n'.join(docs.check(tmp_path))
    assert 'missing target: absent.md' in errors
    assert 'missing fragment: docs/guide.md#missing' in errors
    assert 'not reachable' in errors
    assert 'missing language counterpart: docs/orphan.md' in errors
    assert 'missing language counterpart: docs/orphan.es.md' in errors


def test_locale_landing_page_uses_root_english_readme(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text('[CA](docs/README.ca.md) [ES](docs/README.es.md)')
    for lang in ('ca', 'es'):
        (tmp_path / f'docs/README.{lang}.md').write_text('# Runxin Local')
    assert docs.check(tmp_path) == []


def test_legacy_entry_point_can_keep_anchor_without_being_indexed(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text('# Project')
    (tmp_path / "docs/old.md").write_text('<!-- compatibility-page -->\n<a id="old-section"></a>\n[Home](../README.md)')
    assert docs.check(tmp_path) == []


def test_repository_relative_link_and_encoded_fragment(tmp_path):
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'README.md').write_text('[Ús](docs/guide.md#%C3%BAs)')
    (tmp_path / 'docs/guide.md').write_text('# Ús')
    assert docs.check(tmp_path) == []


def test_site_root_link_is_rejected_even_when_local_target_exists(tmp_path):
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'README.md').write_text('[Guide](/docs/guide.md) [Valid](docs/guide.md)')
    (tmp_path / 'docs/guide.md').write_text('# Guide')
    assert docs.check(tmp_path) == [
        'README.md: site-root link requires a repository-relative path: /docs/guide.md'
    ]
