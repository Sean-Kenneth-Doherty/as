import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_quotation_term_closure
from autarkic_systems.substitution_graph_quotation_term_closure import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_substitution_graph_quotation_term_closure,
    validate_substitution_graph_quotation_term_closure,
)


CLOSURE = Path("claims/substitution_graph_quotation_term_closure.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
CODEBOOK = Path("language/formal_codebook.json")
QUOTATION_TERM_EXAMPLES = Path("language/formal_quotation_term_examples.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")


class SubstitutionGraphQuotationTermClosureTests(unittest.TestCase):
    def setUp(self):
        self.closure = load_substitution_graph_quotation_term_closure(CLOSURE)

    def test_checked_in_manifest_names_closure_domain(self):
        self.assertEqual(self.closure.schema_version, 1)
        self.assertEqual(
            self.closure.closure_set_id,
            "as-substitution-graph-quotation-term-closure-v1",
        )
        self.assertEqual(self.closure.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.closure.quotation_term_examples_path,
            str(QUOTATION_TERM_EXAMPLES),
        )
        self.assertEqual(
            self.closure.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.closure.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(self.closure.expected_subject_count, 12)
        self.assertEqual(
            REQUIRED_SOURCE_KINDS,
            (
                "formula-candidate",
                "finite-evaluation",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "formula-correctness-proof",
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
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

    def test_checked_in_manifest_validates_closure_domain(self):
        report = validate_substitution_graph_quotation_term_closure(
            self.closure,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.subject_count, 12)
        self.assertEqual(report.source_kind_counts["formula-candidate"], 3)
        self.assertEqual(report.source_kind_counts["finite-evaluation"], 9)
        self.assertTrue(
            any(
                result.subject == "closure_subjects"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_closure_subjects(self):
        report = validate_substitution_graph_quotation_term_closure(
            self.closure,
            WILLARD_MAP,
        )

        payload = (
            substitution_graph_quotation_term_closure
            .substitution_graph_quotation_term_closure_report_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["subject_count"], 12)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["source_kind_counts"]["formula-candidate"], 3)
        self.assertEqual(payload["source_kind_counts"]["finite-evaluation"], 9)
        self.assertTrue(
            all(subject["observed_closed"] for subject in payload["subjects"])
        )
        self.assertTrue(
            all(subject["observed_tokens_recovered"] for subject in payload["subjects"])
        )
        self.assertTrue(
            all(subject["observed_code_roundtrip_ok"] for subject in payload["subjects"])
        )

    def test_text_report_exposes_closure_boundary(self):
        report = validate_substitution_graph_quotation_term_closure(
            self.closure,
            WILLARD_MAP,
        )

        text = (
            substitution_graph_quotation_term_closure
            .format_substitution_graph_quotation_term_closure_report(report)
        )

        self.assertIn("Substitution graph quotation term closure: accepted", text)
        self.assertIn("Subjects: 12", text)
        self.assertIn("formula-candidate=3", text)
        self.assertIn("finite-evaluation=9", text)
        self.assertIn("Closure failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_subject_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "closure.json"
            data = json.loads(CLOSURE.read_text(encoding="utf-8"))
            data["expected_subject_count"] = 11
            path.write_text(json.dumps(data), encoding="utf-8")
            closure = load_substitution_graph_quotation_term_closure(path)

            report = validate_substitution_graph_quotation_term_closure(
                closure,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-quotation-term-closure-count", report.failed_subjects)
        self.assertTrue(
            any("subject count mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "closure.json"
            data = json.loads(CLOSURE.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            closure = load_substitution_graph_quotation_term_closure(path)

            report = validate_substitution_graph_quotation_term_closure(
                closure,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-quotation-term-closure-non-claim", report.failed_subjects)
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_closure_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_quotation_term_closure
                .run_substitution_graph_quotation_term_closure_cli(
                    ["--closure", str(CLOSURE), "--willard-map", str(WILLARD_MAP)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph quotation term closure: accepted", output)

    def test_cli_returns_json_for_checked_in_closure_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_quotation_term_closure
                .run_substitution_graph_quotation_term_closure_cli(
                    [
                        "--closure",
                        str(CLOSURE),
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
        self.assertEqual(payload["subject_count"], 12)

    def test_module_execution_runs_closure_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_quotation_term_closure"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Substitution graph quotation term closure: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_closure_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_quotation_term_closure",
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
        self.assertEqual(payload["subject_count"], 12)


if __name__ == "__main__":
    unittest.main()
