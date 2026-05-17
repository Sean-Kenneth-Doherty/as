import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.chain_claims import (
    chain_claim_validation_report_payload,
    format_chain_claim_validation_report,
    run_chain_claim_cli,
    validate_transition_chain_claim_project,
)


CLAIMS = Path("claims/transition_chain_claims.json")
CERTIFICATES = Path("claims/transition_chain_proof_certificates.json")
LANGUAGE = Path("language/transition_chain_claim_language.json")


class TransitionChainClaimCliTests(unittest.TestCase):
    def test_report_formats_successful_chain_claim_validation(self):
        report = validate_transition_chain_claim_project(
            claims_path=CLAIMS,
            certificates_path=CERTIFICATES,
            language_path=LANGUAGE,
        )

        text = format_chain_claim_validation_report(report)

        self.assertIn("Transition chain claims: as-transition-chain-claim-v1", text)
        self.assertIn("OK chain-language-manifest:", text)
        self.assertIn("OK chain-examples: evaluated 7 examples", text)
        self.assertIn("OK chain-certificates: verified 2 certificates", text)
        self.assertIn("OK chain-surface: validated 2 chain claims", text)
        self.assertNotIn("FAIL", text)

    def test_json_payload_records_successful_chain_claim_validation(self):
        report = validate_transition_chain_claim_project(
            claims_path=CLAIMS,
            certificates_path=CERTIFICATES,
            language_path=LANGUAGE,
        )

        payload = chain_claim_validation_report_payload(report)

        self.assertEqual(payload["language_id"], "as-transition-chain-claim-v1")
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], 2)
        self.assertEqual(payload["certificate_count"], 2)
        self.assertEqual(payload["result_count"], len(report.results))
        self.assertTrue(
            any(
                result["subject"] == "chain-surface" and result["accepted"]
                for result in payload["results"]
            )
        )

    def test_cli_returns_zero_for_checked_in_chain_claim_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_chain_claim_cli(
                [
                    "--claims",
                    str(CLAIMS),
                    "--certificates",
                    str(CERTIFICATES),
                    "--language",
                    str(LANGUAGE),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Transition chain claims:", output)
        self.assertIn("OK chain-certificates", output)

    def test_cli_returns_json_for_checked_in_chain_claim_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_chain_claim_cli(
                [
                    "--claims",
                    str(CLAIMS),
                    "--certificates",
                    str(CERTIFICATES),
                    "--language",
                    str(LANGUAGE),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], 2)
        self.assertEqual(payload["certificate_count"], 2)
        self.assertNotIn("OK chain", stdout.getvalue())

    def test_cli_returns_one_for_incomplete_certificate_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            certificate_path = Path(tmp) / "transition_chain_proof_certificates.json"
            certificate_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "certificates": [
                            {
                                "claim_id": "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED",
                                "steps": [
                                    {
                                        "rule": "manifest-example",
                                        "example": "neighbor b proc left delivery consumed by empty recipient",
                                        "expected": True,
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_chain_claim_cli(
                    [
                        "--claims",
                        str(CLAIMS),
                        "--certificates",
                        str(certificate_path),
                        "--language",
                        str(LANGUAGE),
                    ]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("FAIL chain-certificates", output)
        self.assertIn("missing examples", output)

    def test_module_execution_runs_chain_claim_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_claims",
                "--claims",
                str(CLAIMS),
                "--certificates",
                str(CERTIFICATES),
                "--language",
                str(LANGUAGE),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Transition chain claims:", completed.stdout)
        self.assertIn("OK chain-surface", completed.stdout)

    def test_module_execution_runs_json_chain_claim_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_claims",
                "--claims",
                str(CLAIMS),
                "--certificates",
                str(CERTIFICATES),
                "--language",
                str(LANGUAGE),
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
        self.assertEqual(payload["claim_count"], 2)


if __name__ == "__main__":
    unittest.main()
