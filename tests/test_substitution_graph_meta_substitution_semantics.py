import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_meta_substitution_semantics
from autarkic_systems.substitution_graph_meta_substitution_semantics import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_substitution_graph_meta_substitution_semantics,
    validate_substitution_graph_meta_substitution_semantics,
)


SEMANTICS = Path("claims/substitution_graph_meta_substitution_semantics.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FORMAL_SUBSTITUTION_EXAMPLES = Path("language/formal_substitution_examples.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")


class SubstitutionGraphMetaSubstitutionSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.semantics = load_substitution_graph_meta_substitution_semantics(
            SEMANTICS
        )

    def test_checked_in_manifest_names_semantics_domain(self):
        self.assertEqual(self.semantics.schema_version, 1)
        self.assertEqual(
            self.semantics.semantics_set_id,
            "as-substitution-graph-meta-substitution-semantics-v1",
        )
        self.assertEqual(self.semantics.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.semantics.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.semantics.formal_substitution_examples_path,
            str(FORMAL_SUBSTITUTION_EXAMPLES),
        )
        self.assertEqual(
            self.semantics.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.semantics.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(self.semantics.expected_subject_count, 6)
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

    def test_checked_in_manifest_validates_semantics_domain(self):
        report = validate_substitution_graph_meta_substitution_semantics(
            self.semantics,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.subject_count, 6)
        self.assertEqual(report.source_kind_counts["formula-candidate"], 3)
        self.assertEqual(report.source_kind_counts["finite-evaluation"], 3)
        self.assertTrue(
            any(
                result.subject == "semantics_subjects"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_semantic_subjects(self):
        report = validate_substitution_graph_meta_substitution_semantics(
            self.semantics,
            WILLARD_MAP,
        )

        payload = (
            substitution_graph_meta_substitution_semantics
            .substitution_graph_meta_substitution_semantics_report_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["subject_count"], 6)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["source_kind_counts"]["formula-candidate"], 3)
        self.assertEqual(payload["source_kind_counts"]["finite-evaluation"], 3)
        self.assertTrue(
            all(
                subject["observed_replacement_closed"]
                for subject in payload["subjects"]
            )
        )
        self.assertTrue(
            all(
                subject["observed_free_variables_preserved"]
                for subject in payload["subjects"]
            )
        )
        self.assertTrue(
            all(
                subject["observed_output_matches_expected_surface"]
                for subject in payload["subjects"]
            )
        )
        no_op_subjects = [
            subject
            for subject in payload["subjects"]
            if subject["subject_id"]
            == "AS-SUBST-GRAPH-EVAL-NOT-FREE.argument_substitution"
        ]
        self.assertEqual(len(no_op_subjects), 1)
        self.assertTrue(no_op_subjects[0]["observed_no_op_when_variable_not_free"])

    def test_text_report_exposes_semantics_boundary(self):
        report = validate_substitution_graph_meta_substitution_semantics(
            self.semantics,
            WILLARD_MAP,
        )

        text = (
            substitution_graph_meta_substitution_semantics
            .format_substitution_graph_meta_substitution_semantics_report(report)
        )

        self.assertIn("Substitution graph meta-substitution semantics: accepted", text)
        self.assertIn("Subjects: 6", text)
        self.assertIn("formula-candidate=3", text)
        self.assertIn("finite-evaluation=3", text)
        self.assertIn("Semantic failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_subject_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "semantics.json"
            data = json.loads(SEMANTICS.read_text(encoding="utf-8"))
            data["expected_subject_count"] = 5
            path.write_text(json.dumps(data), encoding="utf-8")
            semantics = load_substitution_graph_meta_substitution_semantics(path)

            report = validate_substitution_graph_meta_substitution_semantics(
                semantics,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("subject count mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "semantics.json"
            data = json.loads(SEMANTICS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            semantics = load_substitution_graph_meta_substitution_semantics(path)

            report = validate_substitution_graph_meta_substitution_semantics(
                semantics,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_semantics_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_meta_substitution_semantics
                .run_substitution_graph_meta_substitution_semantics_cli(
                    ["--semantics", str(SEMANTICS), "--willard-map", str(WILLARD_MAP)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph meta-substitution semantics: accepted", output)

    def test_cli_returns_json_for_checked_in_semantics_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_meta_substitution_semantics
                .run_substitution_graph_meta_substitution_semantics_cli(
                    [
                        "--semantics",
                        str(SEMANTICS),
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
        self.assertEqual(payload["subject_count"], 6)

    def test_module_execution_runs_semantics_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_meta_substitution_semantics",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Substitution graph meta-substitution semantics: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_semantics_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_meta_substitution_semantics",
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
        self.assertEqual(payload["subject_count"], 6)


if __name__ == "__main__":
    unittest.main()
