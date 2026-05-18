import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_quotation_sequence
from autarkic_systems.formal_quotation import numeral_to_natural
from autarkic_systems.formal_quotation_sequence import (
    REQUIRED_WILLARD_ANCHORS,
    load_quotation_sequence_examples,
    quote_token_sequence,
    validate_quotation_sequence_examples,
)


EXAMPLES = Path("language/formal_quotation_sequence_examples.json")
QUOTATION = Path("language/formal_quotation_examples.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalQuotationSequenceTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_quotation_sequence_examples(EXAMPLES)

    def test_checked_in_manifest_names_sequence_surface(self):
        self.assertEqual(self.examples.schema_version, 1)
        self.assertEqual(self.examples.sequence_set_id, "as-formal-quotation-sequence-v1")
        self.assertEqual(self.examples.quotation_examples_path, str(QUOTATION))
        self.assertEqual(self.examples.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(self.examples.sequence_kind, "token-numeral-sequence")
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
            ),
        )
        self.assertEqual(len(self.examples.examples), 2)

    def test_quote_token_sequence_wraps_numerals(self):
        sequence = quote_token_sequence((41, 1, 12))

        self.assertEqual(sequence["kind"], "token-numeral-sequence")
        self.assertEqual(sequence["token_count"], 3)
        self.assertEqual(numeral_to_natural(sequence["items"][0]), 41)
        self.assertEqual(numeral_to_natural(sequence["items"][-1]), 12)

    def test_checked_in_manifest_validates_dependencies(self):
        report = validate_quotation_sequence_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.example_count, 2)

    def test_json_payload_exposes_sequence_surface(self):
        report = validate_quotation_sequence_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = formal_quotation_sequence.quotation_sequence_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["sequence_set_id"], "as-formal-quotation-sequence-v1")
        self.assertEqual(payload["sequence_kind"], "token-numeral-sequence")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["example_count"], 2)

    def test_text_report_exposes_sequence_surface(self):
        report = validate_quotation_sequence_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = formal_quotation_sequence.format_quotation_sequence_report(report)

        self.assertIn("Formal quotation sequence: accepted", text)
        self.assertIn("Examples: as-formal-quotation-sequence-v1", text)
        self.assertIn("Example count: 2", text)
        self.assertNotIn("FAIL", text)

    def test_empty_token_sequence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["tokens"] = []
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_sequence_examples(examples_path)

            report = validate_quotation_sequence_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-sequence-example", report.failed_subjects)
        self.assertTrue(
            any("code tokens must be a non-empty sequence" in result.detail for result in report.results)
        )

    def test_endpoint_depth_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_last_token_depth"] = 99
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_sequence_examples(examples_path)

            report = validate_quotation_sequence_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-sequence-example", report.failed_subjects)
        self.assertTrue(
            any("expected last token depth mismatch" in result.detail for result in report.results)
        )

    def test_sequence_kind_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["sequence_kind"] = "raw-token-list"
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_sequence_examples(examples_path)

            report = validate_quotation_sequence_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-sequence-manifest", report.failed_subjects)
        self.assertTrue(
            any("unknown sequence kind: raw-token-list" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_quotation_sequence.run_quotation_sequence_cli(
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
        self.assertIn("Formal quotation sequence: accepted", output)

    def test_cli_returns_json_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_quotation_sequence.run_quotation_sequence_cli(
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
        self.assertEqual(payload["example_count"], 2)

    def test_module_execution_runs_sequence_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_quotation_sequence"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal quotation sequence: accepted", completed.stdout)

    def test_module_execution_runs_json_sequence_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_quotation_sequence",
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
        self.assertEqual(payload["sequence_set_id"], "as-formal-quotation-sequence-v1")


if __name__ == "__main__":
    unittest.main()
