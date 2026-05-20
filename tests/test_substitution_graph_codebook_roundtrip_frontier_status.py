import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_codebook_roundtrip_frontier_status
from autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_substitution_graph_codebook_roundtrip_frontier_status,
    validate_substitution_graph_codebook_roundtrip_frontier_status,
)


STATUS = Path("claims/substitution_graph_codebook_roundtrip_frontier_status.json")
CASES = Path("claims/substitution_graph_correctness_cases.json")
ROUNDTRIP = Path("claims/substitution_graph_codebook_roundtrip.json")
CODEBOOK = Path("language/formal_codebook.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")


class SubstitutionGraphCodebookRoundtripFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_substitution_graph_codebook_roundtrip_frontier_status(
            STATUS
        )

    def test_checked_in_manifest_names_current_frontier_dependencies(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-substitution-graph-codebook-roundtrip-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(self.status.frontier_blocked_by, "codebook-roundtrip")
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(self.status.codebook_roundtrip_path, str(ROUNDTRIP))
        self.assertEqual(self.status.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.status.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.status.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(self.status.required_case_kind, "codebook-roundtrip")
        self.assertEqual(self.status.required_case_status, "proof-case-open")
        self.assertEqual(self.status.expected_roundtrip_subject_count, 12)
        self.assertEqual(self.status.expected_support_surface_count, 2)
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "substitution_graph_correctness_cases",
                "codebook_roundtrip",
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
        report = validate_substitution_graph_codebook_roundtrip_frontier_status(
            self.status
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "codebook-roundtrip")
        self.assertEqual(
            report.proof_case.case_id,
            "AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP",
        )
        self.assertEqual(report.proof_case.case_kind, "codebook-roundtrip")
        self.assertEqual(report.proof_case.status, "proof-case-open")
        self.assertEqual(
            report.proof_case.required_dependency_subjects,
            ("correctness_target", "codebook", "codebook_roundtrip"),
        )
        self.assertEqual(report.support_surface_count, 2)
        self.assertEqual(report.roundtrip_subject_count, 12)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))

    def test_json_payload_exposes_compact_frontier_summary(self):
        report = validate_substitution_graph_codebook_roundtrip_frontier_status(
            self.status
        )

        payload = (
            substitution_graph_codebook_roundtrip_frontier_status
            .substitution_graph_codebook_roundtrip_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "codebook-roundtrip")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 2)
        self.assertEqual(payload["roundtrip_subject_count"], 12)
        self.assertEqual(
            payload["proof_case"]["case_id"],
            "AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP",
        )
        self.assertEqual(payload["proof_case"]["status"], "proof-case-open")
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            payload["support_facts"]["codebook_roundtrip"]["roundtrip_set_id"],
            "as-substitution-graph-codebook-roundtrip-v1",
        )
        self.assertEqual(
            payload["support_facts"]["codebook_roundtrip"]["source_kind_counts"],
            {"finite-evaluation": 9, "formula-candidate": 3},
        )

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_substitution_graph_codebook_roundtrip_frontier_status(
            self.status
        )

        text = (
            substitution_graph_codebook_roundtrip_frontier_status
            .format_substitution_graph_codebook_roundtrip_frontier_status_report(
                report
            )
        )

        self.assertIn(
            "Substitution graph codebook roundtrip frontier status: accepted",
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: codebook-roundtrip", text)
        self.assertIn(
            "Proof case: AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP",
            text,
        )
        self.assertIn("Case status: proof-case-open", text)
        self.assertIn("Roundtrip subjects: 12", text)
        self.assertIn("Failed subjects: none", text)
        self.assertIn("Non-claims: no formula correctness proof", text)
        self.assertNotIn("FAIL", text)

    def test_roundtrip_support_is_accepted_and_non_promotional(self):
        report = validate_substitution_graph_codebook_roundtrip_frontier_status(
            self.status
        )

        roundtrip_facts = report.support_facts["codebook_roundtrip"]

        self.assertEqual(
            roundtrip_facts["roundtrip_set_id"],
            "as-substitution-graph-codebook-roundtrip-v1",
        )
        self.assertEqual(roundtrip_facts["subject_count"], 12)
        self.assertEqual(roundtrip_facts["failed_subjects"], [])
        self.assertGreaterEqual(roundtrip_facts["non_claim_count"], 5)
        self.assertIn(
            "no arithmetized proof predicate",
            report.manifest.non_claims,
        )

    def test_proof_promotion_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "formula-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_codebook_roundtrip_frontier_status(path)

            report = (
                validate_substitution_graph_codebook_roundtrip_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-codebook-roundtrip-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "proof-promotion frontier status" in result.detail
                for result in report.results
            )
        )

    def test_missing_status_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_codebook_roundtrip_frontier_status(path)

            report = (
                validate_substitution_graph_codebook_roundtrip_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-codebook-roundtrip-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_empty_status_non_claim_is_rejected_at_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"][0] = ""
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_substitution_graph_codebook_roundtrip_frontier_status(path)

    def test_stale_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["codebook_roundtrip_path"] = (
                "claims/substitution_graph_quotation_term_closure.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_codebook_roundtrip_frontier_status(path)

            report = (
                validate_substitution_graph_codebook_roundtrip_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-codebook-roundtrip-frontier-dependency",
            report.failed_subjects,
        )

    def test_closed_codebook_roundtrip_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["status"] = "formula-correctness-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_codebook_roundtrip_frontier_status(
                status_path
            )

            report = (
                validate_substitution_graph_codebook_roundtrip_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-codebook-roundtrip-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("proof case is not open" in result.detail for result in report.results)
        )

    def test_codebook_roundtrip_case_dependency_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["required_dependency_subjects"] = [
                "correctness_target",
                "codebook",
            ]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_codebook_roundtrip_frontier_status(
                status_path
            )

            report = (
                validate_substitution_graph_codebook_roundtrip_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-codebook-roundtrip-frontier-case-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any("dependency subjects mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_codebook_roundtrip_frontier_status
                .run_substitution_graph_codebook_roundtrip_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Substitution graph codebook roundtrip frontier status: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_codebook_roundtrip_frontier_status
                .run_substitution_graph_codebook_roundtrip_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_blocked_by"], "codebook-roundtrip")
        self.assertEqual(payload["roundtrip_subject_count"], 12)

    def test_module_execution_runs_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_codebook_roundtrip_frontier_status"
                ),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Substitution graph codebook roundtrip frontier status: accepted",
            completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
