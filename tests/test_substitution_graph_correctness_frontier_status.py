import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_correctness_frontier_status
from autarkic_systems.substitution_graph_correctness_frontier_status import (
    FINITE_SUPPORT_BY_CASE_KIND,
    REQUIRED_FRONTIER_BLOCKER,
    REQUIRED_FRONTIER_STATUS,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_substitution_graph_correctness_frontier_status,
    validate_substitution_graph_correctness_frontier_status,
)


STATUS = Path("claims/substitution_graph_correctness_frontier_status.json")
CASES = Path("claims/substitution_graph_correctness_cases.json")


class SubstitutionGraphCorrectnessFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_substitution_graph_correctness_frontier_status(STATUS)

    def test_checked_in_manifest_names_frontier_boundary(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-substitution-graph-correctness-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, REQUIRED_FRONTIER_STATUS)
        self.assertEqual(self.status.frontier_blocked_by, REQUIRED_FRONTIER_BLOCKER)
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "correctness_target",
                "codebook",
                "quotation_term",
                "formal_substitution",
                "formula_candidate",
                "substitution_representability",
                "codebook_roundtrip",
                "quotation_term_closure",
                "meta_substitution_semantics",
                "formula_schema_relation",
                "diagonal_witness_composition",
            ),
        )
        self.assertEqual(
            FINITE_SUPPORT_BY_CASE_KIND["codebook-roundtrip"],
            ("codebook_roundtrip",),
        )
        self.assertEqual(
            FINITE_SUPPORT_BY_CASE_KIND["diagonal-witness-composition"],
            ("diagonal_witness_composition",),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no formula correctness proof",
                "no substitution representability proof",
                "no diagonal lemma proof",
                "no fixed-point equation proof",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_frontier_status(self):
        report = validate_substitution_graph_correctness_frontier_status(self.status)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(
            report.frontier_blocked_by,
            "substitution-graph-correctness",
        )
        self.assertEqual(report.case_count, 5)
        self.assertEqual(report.open_case_count, 5)
        self.assertEqual(report.support_surface_count, 11)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))
        self.assertEqual(
            tuple(case.status for case in report.case_supports),
            ("proof-case-open",) * 5,
        )

    def test_json_payload_exposes_per_case_support_summary(self):
        report = validate_substitution_graph_correctness_frontier_status(self.status)

        payload = (
            substitution_graph_correctness_frontier_status
            .substitution_graph_correctness_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(
            payload["frontier_blocked_by"],
            "substitution-graph-correctness",
        )
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["open_case_count"], 5)
        self.assertEqual(payload["support_surface_count"], 11)
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        supports = {
            case["case_kind"]: case["support_subjects"]
            for case in payload["case_supports"]
        }
        finite_supports = {
            case["case_kind"]: case["finite_support_subjects"]
            for case in payload["case_supports"]
        }
        self.assertEqual(
            supports["codebook-roundtrip"],
            ["correctness_target", "codebook", "codebook_roundtrip"],
        )
        self.assertEqual(
            supports["quotation-term-closure"],
            [
                "correctness_target",
                "codebook",
                "quotation_term",
                "quotation_term_closure",
            ],
        )
        self.assertEqual(
            supports["meta-substitution-semantics"],
            [
                "correctness_target",
                "formal_substitution",
                "meta_substitution_semantics",
            ],
        )
        self.assertEqual(
            supports["formula-schema-relation"],
            [
                "correctness_target",
                "formula_candidate",
                "formula_schema_relation",
            ],
        )
        self.assertEqual(
            supports["diagonal-witness-composition"],
            [
                "correctness_target",
                "substitution_representability",
                "diagonal_witness_composition",
            ],
        )
        self.assertEqual(
            finite_supports["formula-schema-relation"],
            ["formula_schema_relation"],
        )

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_substitution_graph_correctness_frontier_status(self.status)

        text = (
            substitution_graph_correctness_frontier_status
            .format_substitution_graph_correctness_frontier_status_report(report)
        )

        self.assertIn(
            "Substitution graph correctness frontier status: accepted",
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: substitution-graph-correctness", text)
        self.assertIn("Open correctness cases: 5/5", text)
        self.assertIn("Support surfaces: 11", text)
        self.assertIn("Case kind: formula-schema-relation", text)
        self.assertIn(
            "Support: correctness_target, formula_candidate, formula_schema_relation",
            text,
        )
        self.assertIn("Finite support: formula_schema_relation", text)
        self.assertIn("Failed subjects: none", text)
        self.assertNotIn("FAIL", text)

    def test_overclaiming_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "substitution-graph-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("overclaiming frontier status" in result.detail for result in report.results)
        )

    def test_proof_promotion_case_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["status"] = "formula-correctness-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("proof promotion status" in result.detail for result in report.results)
        )

    def test_missing_support_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["codebook_roundtrip_path"] = str(Path(tmp) / "missing.json")
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "codebook_roundtrip"
                and not result.accepted
                and "support artifact missing or invalid" in result.detail
                for result in report.results
            )
        )

    def test_missing_status_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-non-claim",
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
                load_substitution_graph_correctness_frontier_status(path)

    def test_missing_case_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["non_claims"] = case_data["cases"][0]["non_claims"][:-1]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_correctness_frontier_status
                .run_substitution_graph_correctness_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Substitution graph correctness frontier status: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_correctness_frontier_status
                .run_substitution_graph_correctness_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["frontier_blocked_by"],
            "substitution-graph-correctness",
        )

    def test_module_execution_runs_text_and_json_frontier_status_validation(self):
        text = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_correctness_frontier_status",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn(
            "Substitution graph correctness frontier status: accepted",
            text.stdout,
        )

        json_run = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_correctness_frontier_status",
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
        self.assertEqual(payload["case_count"], 5)


if __name__ == "__main__":
    unittest.main()
