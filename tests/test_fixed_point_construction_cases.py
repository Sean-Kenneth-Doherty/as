import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_construction_cases
from autarkic_systems.fixed_point_construction_cases import (
    REQUIRED_CASE_KINDS,
    REQUIRED_DEPENDENCIES_BY_KIND,
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_construction_cases,
    validate_fixed_point_construction_cases,
)


CASES = Path("claims/fixed_point_construction_cases.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")
SUBSTITUTION_GRAPH_CORRECTNESS = Path("claims/substitution_graph_correctness_targets.json")
SUBSTITUTION_GRAPH_CORRECTNESS_CASES = Path("claims/substitution_graph_correctness_cases.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
DIAGONAL_INSTANCE_CLOSURE = Path("claims/fixed_point_diagonal_instance_closure.json")
SUBSTITUTION_WITNESS_BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")
SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE = Path(
    "claims/fixed_point_substitution_graph_correctness_bridge.json"
)
BRIDGE_EQUALITY_ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
BRIDGE_EQUALITY_EVALUATION = Path(
    "claims/fixed_point_bridge_equality_evaluation.json"
)
EQUATION_LIFTING_ALIGNMENT = Path(
    "claims/fixed_point_equation_lifting_alignment.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointConstructionCaseTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_fixed_point_construction_cases(CASES)

    def test_checked_in_manifest_names_construction_case_map(self):
        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.case_set_id,
            "as-fixed-point-construction-cases-v1",
        )
        self.assertEqual(self.manifest.formal_language_path, str(LANGUAGE))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(self.manifest.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(
            self.manifest.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(
            self.manifest.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            self.manifest.substitution_graph_correctness_targets_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS),
        )
        self.assertEqual(
            self.manifest.substitution_graph_correctness_cases_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_CASES),
        )
        self.assertEqual(
            self.manifest.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.manifest.diagonal_instance_closure_path,
            str(DIAGONAL_INSTANCE_CLOSURE),
        )
        self.assertEqual(
            self.manifest.substitution_witness_bridge_path,
            str(SUBSTITUTION_WITNESS_BRIDGE),
        )
        self.assertEqual(
            self.manifest.substitution_graph_correctness_bridge_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE),
        )
        self.assertEqual(
            self.manifest.bridge_equality_alignment_path,
            str(BRIDGE_EQUALITY_ALIGNMENT),
        )
        self.assertEqual(
            self.manifest.bridge_equality_evaluation_path,
            str(BRIDGE_EQUALITY_EVALUATION),
        )
        self.assertEqual(
            self.manifest.equation_lifting_alignment_path,
            str(EQUATION_LIFTING_ALIGNMENT),
        )
        self.assertEqual(
            REQUIRED_CASE_KINDS,
            (
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
                "fixed-point-equation-lifting",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["diagonal-instance-closure"],
            (
                "fixed_point",
                "diagonal_construction",
                "fixed_point_equation_bridge",
                "diagonal_instance_closure",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["substitution-representability-proof"],
            (
                "substitution_representability",
                "substitution_graph_correctness_cases",
                "fixed_point_equation_bridge",
                "substitution_witness_bridge",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["bridge-equality-proof"],
            (
                "fixed_point_equation_bridge",
                "substitution_representability",
                "substitution_graph_correctness_cases",
                "bridge_equality_alignment",
                "bridge_equality_evaluation",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["fixed-point-equation-lifting"],
            (
                "fixed_point",
                "fixed_point_equation_bridge",
                "codebook",
                "equation_lifting_alignment",
            ),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCIES_BY_KIND["substitution-graph-correctness-proof"],
            (
                "substitution_graph_correctness",
                "substitution_graph_correctness_cases",
                "substitution_graph_correctness_bridge",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution representability proof",
                "no substitution graph correctness proof",
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_records_five_open_cases(self):
        self.assertEqual(len(self.manifest.cases), 5)
        self.assertEqual(
            tuple(case.case_kind for case in self.manifest.cases),
            REQUIRED_CASE_KINDS,
        )
        for case in self.manifest.cases:
            self.assertEqual(case.status, "proof-case-open")
            self.assertEqual(case.target_id, "AS-FIXED-POINT-SELFCONS1-TARGET")
            self.assertIn("no fixed-point equation proof", case.non_claims)

    def test_checked_in_manifest_validates_construction_cases(self):
        report = validate_fixed_point_construction_cases(
            self.manifest,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.case_count, 5)
        self.assertTrue(
            any(
                result.subject == "fixed_point_equation_bridge"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "diagonal_instance_closure"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "substitution_witness_bridge"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "substitution_graph_correctness_bridge"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "bridge_equality_alignment"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "bridge_equality_evaluation"
                and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "equation_lifting_alignment"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_case_dependencies(self):
        report = validate_fixed_point_construction_cases(
            self.manifest,
            WILLARD_MAP,
        )

        payload = fixed_point_construction_cases.fixed_point_construction_cases_payload(
            report
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["cases"][0]["observed_dependency_count"], 4)
        self.assertEqual(payload["cases"][1]["observed_dependency_count"], 4)
        self.assertEqual(payload["cases"][2]["observed_dependency_count"], 3)
        self.assertEqual(payload["cases"][3]["observed_dependency_count"], 5)
        self.assertEqual(payload["cases"][4]["observed_dependency_count"], 4)
        self.assertIn(
            "bridge_equality_evaluation",
            payload["cases"][3]["required_dependency_subjects"],
        )
        self.assertIn(
            "equation_lifting_alignment",
            payload["cases"][4]["required_dependency_subjects"],
        )

    def test_text_report_exposes_open_cases(self):
        report = validate_fixed_point_construction_cases(
            self.manifest,
            WILLARD_MAP,
        )

        text = fixed_point_construction_cases.format_fixed_point_construction_cases_report(
            report
        )

        self.assertIn("Fixed-point construction cases: accepted", text)
        self.assertIn("Cases: 5", text)
        self.assertIn("bridge-equality-proof", text)
        self.assertIn(
            "Dependencies: fixed_point_equation_bridge, substitution_representability, substitution_graph_correctness_cases, bridge_equality_alignment, bridge_equality_evaluation",
            text,
        )
        self.assertIn(
            "Dependencies: fixed_point, fixed_point_equation_bridge, codebook, equation_lifting_alignment",
            text,
        )
        self.assertNotIn("FAIL", text)

    def test_stale_dependency_list_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][3]["required_dependency_subjects"] = [
                "fixed_point_equation_bridge"
            ]
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_construction_cases(path)

            report = validate_fixed_point_construction_cases(
                manifest,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-construction-case-dependency", report.failed_subjects)
        self.assertTrue(
            any("dependency list mismatch" in result.detail for result in report.results)
        )

    def test_missing_bridge_equality_evaluation_dependency_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["bridge_equality_evaluation_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_construction_cases(path)

            report = validate_fixed_point_construction_cases(
                manifest,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-construction-case-dependency", report.failed_subjects)
        self.assertTrue(
            any(
                result.subject == "bridge_equality_evaluation"
                and not result.accepted
                and "fixed-point-bridge-equality-evaluation-load" in result.detail
                for result in report.results
            )
        )

    def test_overclaiming_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.json"
            data = json.loads(CASES.read_text(encoding="utf-8"))
            data["cases"][4]["status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_construction_cases(path)

            report = validate_fixed_point_construction_cases(
                manifest,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-construction-case-status", report.failed_subjects)
        self.assertTrue(
            any("proved fixed-point construction cases are not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_cases(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_construction_cases.run_fixed_point_construction_cases_cli(
                [
                    "--cases",
                    str(CASES),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point construction cases: accepted", output)

    def test_cli_returns_json_for_checked_in_cases(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_construction_cases.run_fixed_point_construction_cases_cli(
                [
                    "--cases",
                    str(CASES),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["case_count"], 5)

    def test_module_execution_runs_case_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point_construction_cases"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fixed-point construction cases: accepted", completed.stdout)

    def test_module_execution_runs_json_case_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_construction_cases",
                "--format",
                "json",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["case_set_id"],
            "as-fixed-point-construction-cases-v1",
        )


if __name__ == "__main__":
    unittest.main()
