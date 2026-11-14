"""Shared implementations and release gates must retain the shipped behavior."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch
import ast
import json
import subprocess
import sys

from erpdevelopers import catalog, catalog_support, event_media, events_catalog
from erpdevelopers import publication_rules, publications, public_media, taxonomy, event_rules

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location('release_policy', ROOT / 'scripts/release_policy.py')
POLICY = module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)
SHA = 'a' * 40


class TestSharedCatalogBoundaries(TestCase):
    def test_one_schema_implementation_for_all_public_directories(self):
        for module in (catalog, events_catalog, publications):
            self.assertIs(module._schema_status, catalog_support.schema_status)

    def test_one_image_boundary_preserves_compatibility_names(self):
        for module in (event_media, publications):
            self.assertIs(module.image_path, public_media.image_path)
            self.assertIs(module._public_files, public_media.public_files)
            self.assertIs(module._verify_file, public_media.verify_public_image)
        self.assertIs(event_media._caption, public_media.validate_caption)
        self.assertIs(publications.normalize_publication, publication_rules.normalize_publication)
        self.assertIs(publications.TOPICS, taxonomy.TOPICS)
        self.assertIs(event_rules.TOPICS, taxonomy.TOPICS)

    def test_pagination_keeps_distinct_existing_limits(self):
        for value in (None, '', 'bad', [], {}, '-9'):
            self.assertEqual(catalog_support.page_number(value), 1)
        self.assertEqual(catalog_support.page_number('100000', maximum=1000), 1000)
        self.assertEqual(catalog_support.page_number('100000', maximum=10000), 10000)
        self.assertEqual(catalog_support.page_number(' 12 '), 12)
        with self.assertRaises(ValueError):
            catalog_support.page_number(1, maximum=0)

    def test_schema_checks_are_fresh_and_errors_are_not_hidden(self):
        fake = ModuleType('frappe')
        fake.db = SimpleNamespace(table_exists=Mock(return_value=True),
            get_table_columns=Mock(return_value=['title', 'published', 'sort_order', 'modified']))
        with patch.dict(sys.modules, {'frappe': fake}):
            self.assertEqual(catalog_support.schema_status('Editorial', ['title']),
                             {'table_present': True, 'missing_columns': []})
            fake.db.table_exists.assert_called_once_with('Editorial', cached=False)
            fake.db.get_table_columns.side_effect = RuntimeError('database offline')
            with self.assertRaisesRegex(RuntimeError, 'database offline'):
                catalog_support.schema_status('Editorial', ['title'])

    def test_plain_dictionary_resources_do_not_require_frappe_attribute_rows(self):
        fake = ModuleType('frappe')
        fake.db = SimpleNamespace(table_exists=lambda *a, **k: True)
        fake.get_all = Mock(side_effect=[
            [{'name': 'Article', 'route': 'reviewed-article'}],
        ])
        rows = [{'source_kind': 'Original Article', 'web_page': 'Article'}]
        with patch.dict(sys.modules, {'frappe': fake}), patch.object(catalog, '_published_rows', return_value=rows):
            result = catalog.public_resources()
        self.assertEqual(result[0]['href'], '/reviewed-article')
        self.assertFalse(result[0]['external'])

    def test_rules_import_without_a_frappe_runtime(self):
        code = "import sys; sys.modules['frappe']=None; from erpdevelopers.publication_rules import normalize_publication"
        result = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_deferred_entities_and_operational_project_links_are_not_created(self):
        schemas = list((ROOT / 'erpdevelopers/erp_developers/doctype').glob('*/*.json'))
        for path in schemas:
            schema = json.loads(path.read_text())
            self.assertNotIn(schema['name'], ('ERP Developers Entity', 'ERP Developers Project Portal'))
            for field in schema['fields']:
                if field.get('fieldtype') == 'Link':
                    self.assertNotIn(field.get('options'), ('Project', 'Task'))

    def test_removed_playlist_css_is_not_a_second_override(self):
        css = (ROOT / 'erpdevelopers/public/css/portal.css').read_text()
        self.assertEqual(css.count('.ed-playlist-play-icon{'), 1)
        self.assertEqual(css.count('.ed-playlist-watch{display:'), 1)
        self.assertNotIn('.ed-player-status{', css)
        self.assertNotIn('.ed-card-bottom a.ed-playlist-watch', css)


class TestReleasePolicy(TestCase):
    def test_pinned_updates_on_same_release_branch(self):
        for branch in POLICY.RELEASE_BRANCHES:
            POLICY.validate_transition(branch, branch, SHA)

    def test_only_explicit_forward_production_switch(self):
        with self.assertRaises(ValueError):
            POLICY.validate_transition('version-16', 'production-v16', SHA)
        POLICY.validate_transition('version-16', 'production-v16', SHA, True)
        with self.assertRaises(ValueError):
            POLICY.validate_transition('production-v16', 'version-16', SHA, True)

    def test_unknown_detached_or_unpinned_targets_fail(self):
        for branch in ('', 'main', 'feature/test', '-bad'):
            with self.subTest(branch=branch), self.assertRaises(ValueError):
                POLICY.validate_transition(branch, 'production-v16', SHA, True)
        for sha in ('', 'abc123', 'z' * 40, 'a' * 41, None):
            with self.subTest(sha=sha), self.assertRaises(ValueError):
                POLICY.validate_transition('production-v16', 'production-v16', sha)

    def test_cli_denies_switch_and_accepts_opt_in(self):
        command = [sys.executable, str(ROOT/'scripts/release_policy.py'), 'version-16', 'production-v16', SHA]
        denied = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(denied.returncode, 2)
        self.assertIn('ALLOW_BRANCH_SWITCH', denied.stderr)
        allowed = subprocess.run(command + ['--allow-switch', '1'], capture_output=True, text=True)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_policy_precedes_mutations_and_shared_checks_precede_migration(self):
        source = (ROOT/'scripts/update_erptest_lightnode.sh').read_text()
        policy = source.index('"$POLICY_DIR/policy.py" "$CURRENT_BRANCH"')
        self.assertLess(policy, source.index('backup --with-files'))
        self.assertLess(policy, source.index('git -C "$APP" switch'))
        self.assertLess(source.index('backup --with-files'), source.index('merge --ff-only'))
        self.assertLess(source.index('scripts/check_source.sh'), source.index('bench --site "$SITE" migrate'))
        self.assertNotIn('git reset', source)
        self.assertNotIn('--skip-failing', source)

    def test_source_check_runner_does_not_mutate_a_site(self):
        source = (ROOT/'scripts/check_source.sh').read_text()
        for forbidden in ('bench --site', 'supervisorctl', 'git push', 'pip install'):
            self.assertNotIn(forbidden, source)
        self.assertIn("find erpdevelopers -name '*.js'", source)
        self.assertIn('unittest discover', source)
