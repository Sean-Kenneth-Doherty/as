import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import test_suite_selection as selector
from autarkic_systems.test_suite_selection import SuiteManifestError


MANIFEST_PATH = Path("tests/suite_manifest.json")
TESTS_ROOT = Path("tests")
EXPECTED_EXTENDED_MODULES = {
    "tests.test_fixed_point_bridge_equality_alignment",
    "tests.test_fixed_point_bridge_equality_evaluation",
    "tests.test_fixed_point_bridge_equality_frontier_status",
    "tests.test_fixed_point_construction_cases",
    "tests.test_fixed_point_construction_frontier_status",
    "tests.test_fixed_point_diagonal_instance_candidate_surface",
    "tests.test_fixed_point_diagonal_instance_closure",
    "tests.test_fixed_point_diagonal_instance_closure_frontier_status",
    "tests.test_fixed_point_equation_bridge",
    "tests.test_fixed_point_equation_candidate",
    "tests.test_fixed_point_equation_lifting_alignment",
    "tests.test_fixed_point_equation_lifting_frontier_status",
    "tests.test_fixed_point_obstruction",
    "tests.test_fixed_point_substitution_representability_frontier_status",
    "tests.test_fixed_point_substitution_graph_correctness_bridge",
    "tests.test_fixed_point_substitution_witness_bridge",
    "tests.test_fixed_point_target",
    "tests.test_fixed_point_validation_cache",
    "tests.test_formal_confidence_target",
    "tests.test_handoff_status",
    "tests.test_project_status_report",
    "tests.test_vertical_demo_digest",
}
EXPECTED_EXTENDED_AGGREGATE_MODULES = {
    "tests.test_formal_confidence_target",
    "tests.test_handoff_status",
    "tests.test_project_status_report",
    "tests.test_vertical_demo_digest",
}


class _SuccessfulResult:
    def wasSuccessful(self):
        return True


class _RecordingLoader:
    def __init__(self):
        self.loaded_names = None

    def loadTestsFromNames(self, names):
        self.loaded_names = tuple(names)
        return unittest.TestSuite()


class _RecordingRunner:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.was_run = False
        self.suite = None

    def run(self, suite):
        self.was_run = True
        self.suite = suite
        return _SuccessfulResult()


class TestSuiteSelectionTests(unittest.TestCase):
    """Coverage for the repo-native fast/extended test selector."""

    def _current_plan(self):
        manifest = selector.load_suite_manifest(MANIFEST_PATH)
        discovered = selector.discover_test_modules(TESTS_ROOT)
        return manifest, selector.build_suite_plan(manifest, discovered)

    def _write_temp_manifest(self, data):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        temp_path = Path(temp_dir.name) / "suite_manifest.json"
        temp_path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return temp_path

    def test_manifest_classifies_every_discovered_test_exactly_once(self):
        manifest = selector.load_suite_manifest(MANIFEST_PATH)
        discovered = selector.discover_test_modules(TESTS_ROOT)
        plan = selector.build_suite_plan(manifest, discovered)

        fast_modules = set(plan.selected_modules("fast"))
        extended_modules = set(plan.selected_modules("extended-fixed-point"))
        all_modules = set(plan.selected_modules("all"))
        fixed_point_modules = {
            module_name
            for module_name in discovered
            if module_name.startswith("tests.test_fixed_point_")
        }

        self.assertTrue(EXPECTED_EXTENDED_MODULES <= extended_modules)
        self.assertEqual(
            fixed_point_modules,
            extended_modules - EXPECTED_EXTENDED_AGGREGATE_MODULES,
        )
        self.assertIn("tests.test_substitution_graph_formula", fast_modules)
        self.assertIn("tests.test_substitution_graph_target", fast_modules)
        self.assertFalse(fast_modules & extended_modules)
        self.assertEqual(set(discovered), fast_modules | extended_modules)
        self.assertEqual(set(discovered), all_modules)
        self.assertIn("tests.test_suite_selection", fast_modules)

    def test_stale_explicit_extended_module_fails_closed(self):
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        data["leaf_suites"]["extended-fixed-point"]["modules"].append(
            "tests.test_missing_fixed_point_regression"
        )
        temp_manifest = self._write_temp_manifest(data)

        manifest = selector.load_suite_manifest(temp_manifest)
        discovered = selector.discover_test_modules(TESTS_ROOT)

        with self.assertRaisesRegex(SuiteManifestError, "not discovered"):
            selector.build_suite_plan(manifest, discovered)

    def test_leaf_suite_overlap_fails_closed(self):
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        data["leaf_suites"]["fast"]["exclude_suites"] = []
        temp_manifest = self._write_temp_manifest(data)

        manifest = selector.load_suite_manifest(temp_manifest)
        discovered = selector.discover_test_modules(TESTS_ROOT)

        with self.assertRaisesRegex(SuiteManifestError, "classified more than once"):
            selector.build_suite_plan(manifest, discovered)

    def test_list_mode_does_not_construct_or_run_unittest_runner(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        def forbidden_runner_factory(**kwargs):
            raise AssertionError("list mode must not construct a unittest runner")

        exit_code = selector.run_cli(
            ["--suite", "extended-fixed-point", "--list"],
            stdout=stdout,
            stderr=stderr,
            runner_factory=forbidden_runner_factory,
        )

        self.assertEqual(exit_code, 0, stderr.getvalue())
        output = stdout.getvalue()
        self.assertIn("suite: extended-fixed-point", output)
        self.assertNotIn("Ran ", output)
        for module_name in EXPECTED_EXTENDED_MODULES:
            self.assertIn(module_name, output)

    def test_text_list_mode_keeps_adr0272_line_format(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        manifest, plan = self._current_plan()
        expected_modules = plan.selected_modules("fast")

        exit_code = selector.run_cli(
            ["--suite", "fast", "--list"],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 0, stderr.getvalue())
        lines = stdout.getvalue().splitlines()
        self.assertEqual(lines[0], f"manifest: {manifest.manifest_id}")
        self.assertEqual(lines[1], "suite: fast")
        self.assertEqual(lines[2], f"module_count: {len(expected_modules)}")
        self.assertEqual(lines[3], "modules:")
        self.assertEqual(lines[4:], [f"- {name}" for name in expected_modules])

    def test_json_list_mode_emits_fast_suite_plan(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        manifest, plan = self._current_plan()
        expected_modules = plan.selected_modules("fast")

        exit_code = selector.run_cli(
            ["--suite", "fast", "--list", "--format", "json"],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 0, stderr.getvalue())
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["manifest_id"], manifest.manifest_id)
        self.assertEqual(payload["manifest_schema_version"], manifest.schema_version)
        self.assertEqual(payload["suite"], "fast")
        self.assertEqual(payload["module_count"], len(expected_modules))
        self.assertEqual(payload["modules"], list(expected_modules))
        self.assertEqual(
            payload["discovered_module_count"],
            len(plan.discovered_modules),
        )
        self.assertIn("tests.test_suite_selection", payload["modules"])
        self.assertEqual(payload["command"]["program"], "python")
        self.assertEqual(payload["command"]["module"], "unittest")
        self.assertEqual(payload["command"]["module_count"], len(expected_modules))
        self.assertEqual(payload["command"]["argv"][:3], ["python", "-m", "unittest"])
        self.assertEqual(payload["command"]["argv"][3:], list(expected_modules))

    def test_json_list_mode_emits_extended_suite_plan(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        manifest, plan = self._current_plan()
        expected_modules = plan.selected_modules("extended-fixed-point")

        exit_code = selector.run_cli(
            ["--suite", "extended-fixed-point", "--list", "--format", "json"],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 0, stderr.getvalue())
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["manifest_id"], manifest.manifest_id)
        self.assertEqual(payload["manifest_schema_version"], manifest.schema_version)
        self.assertEqual(payload["suite"], "extended-fixed-point")
        self.assertEqual(payload["module_count"], len(expected_modules))
        self.assertEqual(payload["modules"], list(expected_modules))
        self.assertTrue(EXPECTED_EXTENDED_MODULES <= set(payload["modules"]))
        self.assertEqual(payload["command"]["module_count"], len(expected_modules))
        self.assertEqual(payload["command"]["argv"][3:], list(expected_modules))

    def test_json_suite_index_lists_all_selectable_suites(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        manifest, plan = self._current_plan()

        exit_code = selector.run_cli(
            ["--list-suites", "--format", "json"],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 0, stderr.getvalue())
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["manifest_id"], manifest.manifest_id)
        self.assertEqual(payload["manifest_schema_version"], manifest.schema_version)
        self.assertEqual(payload["index_schema_version"], 1)
        self.assertEqual(
            payload["discovered_module_count"],
            len(plan.discovered_modules),
        )
        self.assertEqual(
            payload["selectable_suites"],
            ["fast", "extended-fixed-point", "all"],
        )
        self.assertEqual(
            set(payload["suites"]),
            {"fast", "extended-fixed-point", "all"},
        )
        for suite_name in payload["selectable_suites"]:
            expected = selector.build_suite_list_payload(plan, suite_name)
            self.assertEqual(payload["suites"][suite_name], expected)

    def test_suite_index_requires_json_format(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = selector.run_cli(
            ["--list-suites"],
            stdout=stdout,
            stderr=stderr,
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("--list-suites requires --format json", stderr.getvalue())

    def test_run_mode_loads_selected_modules_through_unittest(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        loader = _RecordingLoader()
        runner_holder = {}

        def runner_factory(**kwargs):
            runner = _RecordingRunner(**kwargs)
            runner_holder["runner"] = runner
            return runner

        exit_code = selector.run_cli(
            ["--suite", "extended-fixed-point"],
            stdout=stdout,
            stderr=stderr,
            loader=loader,
            runner_factory=runner_factory,
        )

        manifest = selector.load_suite_manifest(MANIFEST_PATH)
        plan = selector.build_suite_plan(
            manifest,
            selector.discover_test_modules(TESTS_ROOT),
        )
        expected_modules = set(plan.selected_modules("extended-fixed-point"))

        self.assertEqual(exit_code, 0, stderr.getvalue())
        self.assertEqual(set(loader.loaded_names), expected_modules)
        self.assertTrue(EXPECTED_EXTENDED_MODULES <= set(loader.loaded_names))
        self.assertTrue(runner_holder["runner"].was_run)


if __name__ == "__main__":
    unittest.main()
