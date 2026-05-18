import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_substitution
from autarkic_systems.formal_substitution import (
    REQUIRED_WILLARD_ANCHORS,
    free_variables,
    load_substitution_examples,
    substitute_node,
    validate_substitution_examples,
)


EXAMPLES = Path("language/formal_substitution_examples.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalSubstitutionTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_substitution_examples(EXAMPLES)

    def test_checked_in_manifest_names_substitution_surface(self):
        self.assertEqual(self.examples.schema_version, 1)
        self.assertEqual(self.examples.example_set_id, "as-formal-substitution-v1")
        self.assertEqual(self.examples.codebook_id, "as-formal-codebook-v1")
        self.assertEqual(
            self.examples.semantics,
            "capture-avoiding-free-variable-substitution",
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
            ),
        )
        self.assertEqual(len(self.examples.examples), 4)

    def test_checked_in_manifest_validates_against_codebook(self):
        report = validate_substitution_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(
            any(
                result.subject == "examples" and result.accepted
                for result in report.results
            )
        )

    def test_free_variables_respect_bounded_binders(self):
        node = {
            "kind": "bounded_exists",
            "variable": "y",
            "bound": {"kind": "variable", "name": "n"},
            "body": {
                "kind": "equals",
                "left": {"kind": "variable", "name": "y"},
                "right": {"kind": "variable", "name": "x"},
            },
        }

        self.assertEqual(free_variables(node), frozenset({"n", "x"}))

    def test_substitutes_inside_terms(self):
        node = {"kind": "successor", "term": {"kind": "variable", "name": "x"}}
        replacement = {"kind": "variable", "name": "n"}

        substituted = substitute_node(node, "x", replacement)

        self.assertEqual(
            substituted,
            {"kind": "successor", "term": {"kind": "variable", "name": "n"}},
        )

    def test_substitutes_inside_sequence_terms(self):
        node = {
            "kind": "sequence_cons",
            "head": {"kind": "variable", "name": "x"},
            "tail": {"kind": "sequence_nil"},
        }
        replacement = {"kind": "successor", "term": {"kind": "zero"}}

        substituted = substitute_node(node, "x", replacement)

        self.assertEqual(
            substituted,
            {
                "kind": "sequence_cons",
                "head": {"kind": "successor", "term": {"kind": "zero"}},
                "tail": {"kind": "sequence_nil"},
            },
        )
        self.assertEqual(free_variables(substituted), frozenset())

    def test_substitutes_inside_formulae(self):
        node = {
            "kind": "bounded_exists",
            "variable": "y",
            "bound": {"kind": "variable", "name": "n"},
            "body": {
                "kind": "equals",
                "left": {"kind": "variable", "name": "y"},
                "right": {"kind": "variable", "name": "x"},
            },
        }
        replacement = {"kind": "successor", "term": {"kind": "zero"}}

        substituted = substitute_node(node, "x", replacement)

        self.assertEqual(
            substituted["body"]["right"],
            {"kind": "successor", "term": {"kind": "zero"}},
        )

    def test_bound_variable_blocks_substitution_in_body(self):
        node = {
            "kind": "forall",
            "variable": "x",
            "body": {
                "kind": "equals",
                "left": {"kind": "variable", "name": "x"},
                "right": {"kind": "variable", "name": "y"},
            },
        }
        replacement = {"kind": "variable", "name": "n"}

        substituted = substitute_node(node, "x", replacement)

        self.assertEqual(substituted, node)

    def test_capture_is_rejected(self):
        node = {
            "kind": "forall",
            "variable": "y",
            "body": {
                "kind": "equals",
                "left": {"kind": "variable", "name": "x"},
                "right": {"kind": "variable", "name": "y"},
            },
        }
        replacement = {"kind": "variable", "name": "y"}

        with self.assertRaisesRegex(ValueError, "substitution would capture variable: y"):
            substitute_node(node, "x", replacement)

    def test_substitutes_inside_proof_line_formula(self):
        node = {
            "kind": "proof_line",
            "line": 1,
            "rule": "assumption",
            "formula": {
                "kind": "pi1",
                "variable": "x",
                "body": {
                    "kind": "less_than",
                    "left": {"kind": "variable", "name": "x"},
                    "right": {"kind": "variable", "name": "n"},
                },
            },
            "premises": [],
        }
        replacement = {"kind": "successor", "term": {"kind": "variable", "name": "n"}}

        substituted = substitute_node(node, "n", replacement)

        self.assertEqual(
            substituted["formula"]["body"]["right"],
            {"kind": "successor", "term": {"kind": "variable", "name": "n"}},
        )

    def test_json_payload_exposes_substitution_surface(self):
        report = validate_substitution_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = formal_substitution.substitution_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["example_set_id"], "as-formal-substitution-v1")
        self.assertEqual(payload["codebook_id"], "as-formal-codebook-v1")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["example_count"], 4)

    def test_text_report_exposes_substitution_surface(self):
        report = validate_substitution_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = formal_substitution.format_substitution_report(report)

        self.assertIn("Formal substitution: accepted", text)
        self.assertIn("Examples: as-formal-substitution-v1", text)
        self.assertIn("Codebook: as-formal-codebook-v1", text)
        self.assertIn("Example count: 4", text)
        self.assertNotIn("FAIL", text)

    def test_capture_example_is_rejected_by_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["node"] = {
                "kind": "forall",
                "variable": "y",
                "body": {
                    "kind": "equals",
                    "left": {"kind": "variable", "name": "x"},
                    "right": {"kind": "variable", "name": "y"},
                },
            }
            data["examples"][0]["replacement"] = {"kind": "variable", "name": "y"}
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_substitution_examples(examples_path)

            report = validate_substitution_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-substitution-example", report.failed_subjects)
        self.assertTrue(
            any("substitution would capture variable: y" in result.detail for result in report.results)
        )

    def test_expected_code_mismatch_is_rejected_by_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_code"] = [99]
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_substitution_examples(examples_path)

            report = validate_substitution_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-substitution-example", report.failed_subjects)
        self.assertTrue(
            any("expected code mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_substitution.run_substitution_cli(
                [
                    "--examples",
                    str(EXAMPLES),
                    "--codebook",
                    str(CODEBOOK),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Formal substitution: accepted", output)

    def test_cli_returns_json_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_substitution.run_substitution_cli(
                [
                    "--examples",
                    str(EXAMPLES),
                    "--codebook",
                    str(CODEBOOK),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["example_count"], 4)

    def test_module_execution_runs_substitution_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_substitution"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal substitution: accepted", completed.stdout)

    def test_module_execution_runs_json_substitution_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_substitution",
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
        self.assertEqual(payload["example_set_id"], "as-formal-substitution-v1")


if __name__ == "__main__":
    unittest.main()
