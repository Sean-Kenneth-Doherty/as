import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import (
    substitution_graph_diagonal_witness_composition_frontier_status,
)
from autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status import (
    REQUIRED_CASE_KIND,
    REQUIRED_CASE_SUPPORT_SUBJECTS,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_substitution_graph_diagonal_witness_composition_frontier_status,
    validate_substitution_graph_diagonal_witness_composition_frontier_status,
)


STATUS = Path(
    "claims/substitution_graph_diagonal_witness_composition_frontier_status.json"
)
CASES = Path("claims/substitution_graph_correctness_cases.json")
COMPOSITION = Path("claims/substitution_graph_diagonal_witness_composition.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
CORRECTNESS_TARGETS = Path("claims/substitution_graph_correctness_targets.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
FORMULA_SCHEMA_RELATION = Path(
    "claims/substitution_graph_formula_schema_relation.json"
)
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")


class SubstitutionGraphDiagonalWitnessCompositionFrontierStatusTests(
    unittest.TestCase
):
    def setUp(self):
        self.status = (
            load_substitution_graph_diagonal_witness_composition_frontier_status(
                STATUS
            )
        )

    def test_checked_in_manifest_names_diagonal_witness_frontier(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            (
                "as-substitution-graph-diagonal-witness-composition-"
                "frontier-status-v1"
            ),
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(
            self.status.frontier_blocked_by,
            "diagonal-witness-composition",
        )
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(
            self.status.diagonal_witness_composition_path,
            str(COMPOSITION),
        )
        self.assertEqual(self.status.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.status.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.status.correctness_targets_path,
            str(CORRECTNESS_TARGETS),
        )
        self.assertEqual(
            self.status.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.status.formula_schema_relation_path,
            str(FORMULA_SCHEMA_RELATION),
        )
        self.assertEqual(
            self.status.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            self.status.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(self.status.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(self.status.expected_support_surface_count, 2)
        self.assertEqual(self.status.expected_composition_count, 1)
        self.assertEqual(REQUIRED_CASE_KIND, "diagonal-witness-composition")
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "substitution_graph_correctness_cases",
                "diagonal_witness_composition",
            ),
        )
        self.assertEqual(
            REQUIRED_CASE_SUPPORT_SUBJECTS,
            (
                "correctness_target",
                "substitution_representability",
                "diagonal_witness_composition",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no formula correctness proof",
                "no substitution representability proof",
                "no diagonal lemma proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_frontier_status(self):
        report = (
            validate_substitution_graph_diagonal_witness_composition_frontier_status(
                self.status
            )
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "diagonal-witness-composition")
        self.assertEqual(
            report.proof_case.case_id,
            "AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION",
        )
        self.assertEqual(report.proof_case.case_kind, "diagonal-witness-composition")
        self.assertEqual(report.proof_case.status, "proof-case-open")
        self.assertEqual(
            report.proof_case.required_dependency_subjects,
            REQUIRED_CASE_SUPPORT_SUBJECTS,
        )
        self.assertEqual(report.support_surface_count, 2)
        self.assertEqual(report.composition_count, 1)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))

    def test_json_payload_exposes_compact_handoff(self):
        report = (
            validate_substitution_graph_diagonal_witness_composition_frontier_status(
                self.status
            )
        )

        payload = (
            substitution_graph_diagonal_witness_composition_frontier_status
            .substitution_graph_diagonal_witness_composition_frontier_status_payload(
                report
            )
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(
            payload["frontier_blocked_by"],
            "diagonal-witness-composition",
        )
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 2)
        self.assertEqual(payload["composition_count"], 1)
        self.assertEqual(
            payload["proof_case"]["case_id"],
            "AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION",
        )
        self.assertEqual(payload["proof_case"]["status"], "proof-case-open")
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            (
                payload["support_facts"]["diagonal_witness_composition"]
                ["composition_set_id"]
            ),
            "as-substitution-graph-diagonal-witness-composition-v1",
        )
        self.assertEqual(
            (
                payload["support_facts"]["diagonal_witness_composition"]
                ["source_kind_counts"]
            ),
            {"diagonal-witness": 1},
        )
        self.assertEqual(
            (
                payload["support_facts"]["diagonal_witness_composition"]
                ["failed_subjects"]
            ),
            [],
        )

    def test_text_report_exposes_blocked_boundary(self):
        report = (
            validate_substitution_graph_diagonal_witness_composition_frontier_status(
                self.status
            )
        )

        text = (
            substitution_graph_diagonal_witness_composition_frontier_status
            .format_substitution_graph_diagonal_witness_composition_frontier_status_report(
                report
            )
        )

        self.assertIn(
            (
                "Substitution graph diagonal-witness-composition frontier "
                "status: accepted"
            ),
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: diagonal-witness-composition", text)
        self.assertIn(
            "Proof case: AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION",
            text,
        )
        self.assertIn("Case status: proof-case-open", text)
        self.assertIn("Compositions: 1", text)
        self.assertIn("Failed subjects: none", text)
        self.assertIn("Non-claims: no formula correctness proof", text)
        self.assertNotIn("FAIL", text)

    def test_composition_support_is_accepted_and_non_promotional(self):
        report = (
            validate_substitution_graph_diagonal_witness_composition_frontier_status(
                self.status
            )
        )

        facts = report.support_facts["diagonal_witness_composition"]

        self.assertEqual(
            facts["composition_set_id"],
            "as-substitution-graph-diagonal-witness-composition-v1",
        )
        self.assertEqual(facts["composition_count"], 1)
        self.assertEqual(facts["source_kind_counts"], {"diagonal-witness": 1})
        self.assertEqual(facts["failed_subjects"], [])
        self.assertGreaterEqual(facts["non_claim_count"], 5)
        self.assertIn(
            "no arithmetized proof predicate",
            report.manifest.non_claims,
        )

    def test_proof_promotion_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "diagonal-lemma-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    path
                )
            )

            report = (
                validate_substitution_graph_diagonal_witness_composition_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "proof-promotion frontier status" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    path
                )
            )

            report = (
                validate_substitution_graph_diagonal_witness_composition_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_empty_non_claims_are_rejected_by_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = []
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    path
                )

    def test_stale_composition_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["diagonal_witness_composition_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    path
                )
            )

            report = (
                validate_substitution_graph_diagonal_witness_composition_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-frontier-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "diagonal_witness_composition_path"
                and not result.accepted
                for result in report.results
            )
        )

    def test_closed_diagonal_witness_composition_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "diagonal-witness-composition":
                    case["status"] = "fixed-point-equation-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_diagonal_witness_composition_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("case is not open" in result.detail for result in report.results)
        )

    def test_diagonal_witness_case_dependency_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "diagonal-witness-composition":
                    case["required_dependency_subjects"] = [
                        "correctness_target",
                        "diagonal_witness_composition",
                    ]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_diagonal_witness_composition_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-frontier-case-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any("support subjects mismatch" in result.detail for result in report.results)
        )

    def test_composition_support_failed_subjects_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            composition_path = Path(tmp) / "composition.json"
            composition_data = json.loads(COMPOSITION.read_text(encoding="utf-8"))
            composition_data["expected_composition_count"] = 2
            composition_path.write_text(json.dumps(composition_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["diagonal_witness_composition_path"] = str(composition_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_diagonal_witness_composition_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_diagonal_witness_composition_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-diagonal-witness-composition-frontier-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "diagonal_witness_composition"
                and "failed subjects" in result.detail
                for result in report.results
            )
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_diagonal_witness_composition_frontier_status
                .run_substitution_graph_diagonal_witness_composition_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            (
                "Substitution graph diagonal-witness-composition frontier "
                "status: accepted"
            ),
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_diagonal_witness_composition_frontier_status
                .run_substitution_graph_diagonal_witness_composition_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["frontier_blocked_by"],
            "diagonal-witness-composition",
        )
        self.assertEqual(payload["composition_count"], 1)

    def test_module_execution_runs_text_and_json_frontier_status_validation(self):
        text = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_diagonal_witness_composition_frontier_status"
                ),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn(
            (
                "Substitution graph diagonal-witness-composition frontier "
                "status: accepted"
            ),
            text.stdout,
        )

        json_run = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_diagonal_witness_composition_frontier_status"
                ),
                "--format",
                "json",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        payload = json.loads(json_run.stdout)
        self.assertEqual(json_run.returncode, 0, json_run.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["support_surface_count"], 2)


if __name__ == "__main__":
    unittest.main()
