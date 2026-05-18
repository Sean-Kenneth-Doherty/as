import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import claim_manifest
from autarkic_systems.claim_manifest import (
    evaluate_claim_examples,
    load_transition_claims,
)


MANIFEST = Path("claims/transition_claims.json")


class ClaimManifestTests(unittest.TestCase):
    def test_manifest_loads_claims_with_unique_ids(self):
        claims = load_transition_claims(MANIFEST)

        ids = [claim.claim_id for claim in claims]

        self.assertGreaterEqual(len(claims), 4)
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_claim_has_executable_positive_and_negative_examples(self):
        claims = load_transition_claims(MANIFEST)

        for claim in claims:
            with self.subTest(claim=claim.claim_id):
                expected_values = {example.expected for example in claim.examples}
                self.assertEqual(expected_values, {True, False})

    def test_claim_examples_evaluate_to_manifest_expectations(self):
        claims = load_transition_claims(MANIFEST)

        results = evaluate_claim_examples(claims)

        self.assertTrue(results)
        self.assertTrue(all(result.matched for result in results))

    def test_report_formats_successful_claim_validation(self):
        report = claim_manifest.validate_transition_claim_project(claims_path=MANIFEST)

        text = claim_manifest.format_transition_claim_report(report)

        self.assertIn("Transition claims:", text)
        self.assertIn("OK UC-FIXED-OUTPUT-PRESERVED / blocked output preserved:", text)
        self.assertIn("matched expected True", text)
        self.assertNotIn("FAIL", text)

    def test_json_payload_records_successful_claim_validation(self):
        report = claim_manifest.validate_transition_claim_project(claims_path=MANIFEST)

        payload = claim_manifest.transition_claim_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], len(self.claims_from_manifest()))
        self.assertEqual(payload["example_count"], len(report.results))
        self.assertEqual(payload["matched_count"], len(report.results))
        self.assertTrue(
            any(
                result["claim_id"] == "UC-FIXED-OUTPUT-PRESERVED"
                and result["example_name"] == "blocked output preserved"
                and result["matched"]
                for result in payload["results"]
            )
        )

    def test_cli_returns_zero_for_checked_in_claim_manifest(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = claim_manifest.run_transition_claim_cli(
                ["--claims", str(MANIFEST)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Transition claims:", output)
        self.assertIn("OK UC-FIXED-OUTPUT-PRESERVED", output)

    def test_cli_returns_json_for_checked_in_claim_manifest(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = claim_manifest.run_transition_claim_cli(
                ["--claims", str(MANIFEST), "--format", "json"]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], len(self.claims_from_manifest()))
        self.assertNotIn("OK ", stdout.getvalue())

    def test_cli_returns_one_for_flipped_claim_expectation(self):
        with tempfile.TemporaryDirectory() as tmp:
            claim_path = Path(tmp) / "transition_claims.json"
            data = json.loads(MANIFEST.read_text(encoding="utf-8"))
            data["claims"][0]["examples"][0]["expected"] = False
            claim_path.write_text(json.dumps(data), encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = claim_manifest.run_transition_claim_cli(
                    ["--claims", str(claim_path)]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("FAIL UC-FIXED-OUTPUT-PRESERVED", output)
        self.assertIn("expected False, observed True", output)

    def test_module_execution_runs_claim_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.claim_manifest",
                "--claims",
                str(MANIFEST),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Transition claims:", completed.stdout)
        self.assertIn("OK UC-FIXED-OUTPUT-PRESERVED", completed.stdout)

    def test_module_execution_runs_json_claim_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.claim_manifest",
                "--claims",
                str(MANIFEST),
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
        self.assertEqual(payload["claim_count"], len(self.claims_from_manifest()))

    def test_missing_checker_is_reported(self):
        claims = load_transition_claims(MANIFEST)
        bad = claims[0].with_checker("missing_checker")

        with self.assertRaises(ValueError):
            evaluate_claim_examples([bad])

    def claims_from_manifest(self):
        return load_transition_claims(MANIFEST)


if __name__ == "__main__":
    unittest.main()
