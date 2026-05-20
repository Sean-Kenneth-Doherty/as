import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_construction_frontier_status
from autarkic_systems.fixed_point_construction_frontier_status import (
    REQUIRED_DEPENDENCY_SUBJECTS,
    REQUIRED_NON_CLAIMS,
    SUPPORT_BY_CASE_KIND,
    load_fixed_point_construction_frontier_status,
    validate_fixed_point_construction_frontier_status,
)


STATUS = Path("claims/fixed_point_construction_frontier_status.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
DIAGONAL_CANDIDATE = Path(
    "claims/fixed_point_diagonal_instance_candidate_surface.json"
)
SUBSTITUTION_WITNESS_BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")
SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE = Path(
    "claims/fixed_point_substitution_graph_correctness_bridge.json"
)
BRIDGE_EQUALITY_ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
BRIDGE_EQUALITY_EVALUATION = Path("claims/fixed_point_bridge_equality_evaluation.json")
EQUATION_LIFTING_ALIGNMENT = Path("claims/fixed_point_equation_lifting_alignment.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointConstructionFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_fixed_point_construction_frontier_status(STATUS)

    def test_checked_in_manifest_names_current_frontier_dependencies(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-fixed-point-construction-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(self.status.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(
            self.status.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.status.diagonal_instance_candidate_surface_path,
            str(DIAGONAL_CANDIDATE),
        )
        self.assertEqual(
            self.status.substitution_witness_bridge_path,
            str(SUBSTITUTION_WITNESS_BRIDGE),
        )
        self.assertEqual(
            self.status.substitution_graph_correctness_bridge_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE),
        )
        self.assertEqual(
            self.status.bridge_equality_alignment_path,
            str(BRIDGE_EQUALITY_ALIGNMENT),
        )
        self.assertEqual(
            self.status.bridge_equality_evaluation_path,
            str(BRIDGE_EQUALITY_EVALUATION),
        )
        self.assertEqual(
            self.status.equation_lifting_alignment_path,
            str(EQUATION_LIFTING_ALIGNMENT),
        )
        self.assertEqual(
            REQUIRED_DEPENDENCY_SUBJECTS,
            (
                "fixed_point_construction_cases",
                "diagonal_instance_candidate_surface",
                "substitution_witness_bridge",
                "substitution_graph_correctness_bridge",
                "bridge_equality_alignment",
                "bridge_equality_evaluation",
                "equation_lifting_alignment",
            ),
        )
        self.assertEqual(
            SUPPORT_BY_CASE_KIND["diagonal-instance-closure"],
            ("diagonal_instance_candidate_surface",),
        )
        self.assertEqual(
            SUPPORT_BY_CASE_KIND["bridge-equality-proof"],
            ("bridge_equality_alignment", "bridge_equality_evaluation"),
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

    def test_checked_in_manifest_validates_frontier_status(self):
        report = validate_fixed_point_construction_frontier_status(
            self.status,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(report.case_count, 5)
        self.assertEqual(report.open_case_count, 5)
        self.assertEqual(report.support_surface_count, 7)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))
        self.assertEqual(
            tuple(case.status for case in report.case_supports),
            ("proof-case-open",) * 5,
        )

    def test_json_payload_exposes_per_case_finite_support(self):
        report = validate_fixed_point_construction_frontier_status(
            self.status,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_construction_frontier_status
            .fixed_point_construction_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-construction")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 7)
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["open_case_count"], 5)
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_DEPENDENCY_SUBJECTS),
        )
        self.assertTrue(
            all(surface["accepted"] for surface in payload["support_surfaces"])
        )

        supports = {
            case["case_kind"]: case["finite_support_subjects"]
            for case in payload["case_supports"]
        }
        self.assertEqual(
            supports["diagonal-instance-closure"],
            ["diagonal_instance_candidate_surface"],
        )
        self.assertEqual(
            supports["substitution-representability-proof"],
            ["substitution_witness_bridge"],
        )
        self.assertEqual(
            supports["substitution-graph-correctness-proof"],
            ["substitution_graph_correctness_bridge"],
        )
        self.assertEqual(
            supports["bridge-equality-proof"],
            ["bridge_equality_alignment", "bridge_equality_evaluation"],
        )
        self.assertEqual(
            supports["fixed-point-equation-lifting"],
            ["equation_lifting_alignment"],
        )

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_fixed_point_construction_frontier_status(
            self.status,
            WILLARD_MAP,
        )

        text = (
            fixed_point_construction_frontier_status
            .format_fixed_point_construction_frontier_status_report(report)
        )

        self.assertIn("Fixed-point construction frontier status: accepted", text)
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: fixed-point-construction", text)
        self.assertIn("Open construction cases: 5/5", text)
        self.assertIn("Support surfaces: 7", text)
        self.assertIn("bridge-equality-proof", text)
        self.assertIn(
            "Finite support: bridge_equality_alignment, bridge_equality_evaluation",
            text,
        )
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("FAIL", text)

    def test_overclaiming_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("overclaiming frontier status" in result.detail for result in report.results)
        )

    def test_construction_case_not_open_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            case_data["cases"][4]["status"] = "fixed-point-equation-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(status_path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("construction case is not open" in result.detail for result in report.results)
        )

    def test_missing_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["bridge_equality_evaluation_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "bridge_equality_evaluation"
                and not result.accepted
                and "fixed-point-bridge-equality-evaluation-load" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_construction_frontier_status
                .run_fixed_point_construction_frontier_status_cli(
                    [
                        "--status",
                        str(STATUS),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point construction frontier status: accepted", output)

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_construction_frontier_status
                .run_fixed_point_construction_frontier_status_cli(
                    [
                        "--status",
                        str(STATUS),
                        "--willard-map",
                        str(WILLARD_MAP),
                        "--format",
                        "json",
                    ]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-construction")

    def test_module_execution_runs_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_construction_frontier_status",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point construction frontier status: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_construction_frontier_status",
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
            payload["status_set_id"],
            "as-fixed-point-construction-frontier-status-v1",
        )


if __name__ == "__main__":
    unittest.main()
