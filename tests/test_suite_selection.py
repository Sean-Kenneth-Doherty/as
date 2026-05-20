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
    "tests.test_fixed_point_construction_cases",
    "tests.test_fixed_point_construction_frontier_status",
    "tests.test_fixed_point_diagonal_instance_candidate_surface",
    "tests.test_fixed_point_diagonal_instance_closure",
    "tests.test_fixed_point_equation_bridge",
    "tests.test_fixed_point_equation_candidate",
    "tests.test_fixed_point_equation_lifting_alignment",
    "tests.test_fixed_point_obstruction",
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
