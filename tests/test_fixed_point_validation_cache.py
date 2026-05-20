import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.fixed_point_bridge_equality_evaluation import (
    load_fixed_point_bridge_equality_evaluation,
    validate_fixed_point_bridge_equality_evaluation,
)
from autarkic_systems.fixed_point_construction_cases import (
    load_fixed_point_construction_cases,
    validate_fixed_point_construction_cases,
)


CASES = Path("claims/fixed_point_construction_cases.json")
EVALUATION = Path("claims/fixed_point_bridge_equality_evaluation.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointValidationCacheTests(unittest.TestCase):
    """Regression guard for process-local fixed-point validation caching."""

    def tearDown(self):
        validate_fixed_point_construction_cases.cache_clear()
        validate_fixed_point_bridge_equality_evaluation.cache_clear()

    def test_default_construction_case_validation_reuses_cached_report(self):
        """Cache equal default manifests while validating temp manifests alone."""

        validate_fixed_point_construction_cases.cache_clear()
        validate_fixed_point_bridge_equality_evaluation.cache_clear()
        first_manifest = load_fixed_point_construction_cases(CASES)
        second_manifest = load_fixed_point_construction_cases(CASES)

        first_report = validate_fixed_point_construction_cases(
            first_manifest,
            WILLARD_MAP,
        )
        after_first = validate_fixed_point_construction_cases.cache_info()
        second_report = validate_fixed_point_construction_cases(
            second_manifest,
            WILLARD_MAP,
        )
        after_second = validate_fixed_point_construction_cases.cache_info()

        self.assertTrue(first_report.accepted, first_report.results)
        self.assertIs(first_report, second_report)
        self.assertEqual(after_first.misses, 1)
        self.assertEqual(after_first.hits, 0)
        self.assertEqual(after_second.misses, 1)
        self.assertEqual(after_second.hits, 1)

        with tempfile.TemporaryDirectory() as tmp:
            temp_path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][3]["required_dependency_subjects"] = [
                "fixed_point_equation_bridge"
            ]
            temp_path.write_text(json.dumps(data), encoding="utf-8")
            modified_manifest = load_fixed_point_construction_cases(temp_path)

            modified_report = validate_fixed_point_construction_cases(
                modified_manifest,
                WILLARD_MAP,
            )
            after_modified = validate_fixed_point_construction_cases.cache_info()

        self.assertIsNot(first_report, modified_report)
        self.assertFalse(modified_report.accepted)
        self.assertIn(
            "fixed-point-construction-case-dependency",
            modified_report.failed_subjects,
        )
        self.assertEqual(after_modified.misses, 2)
        self.assertEqual(after_modified.hits, 1)

        final_report = validate_fixed_point_construction_cases(
            load_fixed_point_construction_cases(CASES),
            WILLARD_MAP,
        )
        after_final = validate_fixed_point_construction_cases.cache_info()

        self.assertIs(first_report, final_report)
        self.assertEqual(after_final.misses, 2)
        self.assertEqual(after_final.hits, 2)

    def test_default_bridge_equality_evaluation_reuses_cached_report(self):
        """Cache equal default evaluation manifests without masking stale facts."""

        validate_fixed_point_bridge_equality_evaluation.cache_clear()
        first_manifest = load_fixed_point_bridge_equality_evaluation(EVALUATION)
        second_manifest = load_fixed_point_bridge_equality_evaluation(EVALUATION)

        first_report = validate_fixed_point_bridge_equality_evaluation(
            first_manifest,
            WILLARD_MAP,
        )
        after_first = validate_fixed_point_bridge_equality_evaluation.cache_info()
        second_report = validate_fixed_point_bridge_equality_evaluation(
            second_manifest,
            WILLARD_MAP,
        )
        after_second = validate_fixed_point_bridge_equality_evaluation.cache_info()

        self.assertTrue(first_report.accepted, first_report.results)
        self.assertIs(first_report, second_report)
        self.assertEqual(after_first.misses, 1)
        self.assertEqual(after_first.hits, 0)
        self.assertEqual(after_second.misses, 1)
        self.assertEqual(after_second.hits, 1)

        with tempfile.TemporaryDirectory() as tmp:
            temp_path = Path(tmp) / "evaluation.json"
            data = json.loads(EVALUATION.read_text(encoding="utf-8"))
            data["expected_output_code_length"] = 297
            temp_path.write_text(json.dumps(data), encoding="utf-8")
            modified_manifest = load_fixed_point_bridge_equality_evaluation(
                temp_path
            )

            modified_report = validate_fixed_point_bridge_equality_evaluation(
                modified_manifest,
                WILLARD_MAP,
            )
            after_modified = (
                validate_fixed_point_bridge_equality_evaluation.cache_info()
            )

        self.assertIsNot(first_report, modified_report)
        self.assertFalse(modified_report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-evaluation-output-length",
            modified_report.failed_subjects,
        )
        self.assertEqual(after_modified.misses, 2)
        self.assertEqual(after_modified.hits, 1)

        final_report = validate_fixed_point_bridge_equality_evaluation(
            load_fixed_point_bridge_equality_evaluation(EVALUATION),
            WILLARD_MAP,
        )
        after_final = validate_fixed_point_bridge_equality_evaluation.cache_info()

        self.assertIs(first_report, final_report)
        self.assertEqual(after_final.misses, 2)
        self.assertEqual(after_final.hits, 2)


if __name__ == "__main__":
    unittest.main()
