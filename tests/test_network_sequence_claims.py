import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.network_sequence_claims import (
    evaluate_network_sequence_claim_examples,
    format_network_sequence_claim_validation_report,
    load_network_sequence_claims,
    network_sequence_claim_validation_report_payload,
    run_network_sequence_claim_cli,
    validate_network_sequence_claim_project,
)
from autarkic_systems.network_sequence_predicates import (
    post_handoff_signal_routed,
)
from autarkic_systems.network_sequence import (
    execute_post_handoff_signal_witness,
)
from autarkic_systems.universal_cell import Cell


CLAIMS = Path("claims/network_sequence_claims.json")
CERTIFICATES = Path("claims/network_sequence_proof_certificates.json")
CLAIM_ID = "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED"
PREDICATE = "post_handoff_signal_routed"


class NetworkSequenceClaimTests(unittest.TestCase):
    def test_predicate_accepts_post_handoff_routing_witness(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        result = post_handoff_signal_routed(
            execute_post_handoff_signal_witness(sender, recipient)
        )

        self.assertEqual(result.name, PREDICATE)
        self.assertTrue(result.holds, result.detail)
        self.assertIn("routed", result.detail)

    def test_predicate_rejects_non_init_handoff_and_malformed_followup(self):
        write_buffer_sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        )
        init_sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        non_init = post_handoff_signal_routed(
            execute_post_handoff_signal_witness(write_buffer_sender, recipient)
        )
        malformed = post_handoff_signal_routed(
            execute_post_handoff_signal_witness(
                init_sender,
                recipient,
                followup_input=("standard-signal", "_", "_"),
            )
        )

        self.assertFalse(non_init.holds)
        self.assertIn("handoff-not-init-consumed", non_init.detail)
        self.assertFalse(malformed.holds)
        self.assertIn("followup-not-routed", malformed.detail)

    def test_claim_manifest_loads_post_handoff_sequence_claim(self):
        claims = load_network_sequence_claims(CLAIMS)

        self.assertEqual(len(claims), 1)
        claim = claims[0]
        self.assertEqual(claim.claim_id, CLAIM_ID)
        self.assertEqual(claim.predicate, PREDICATE)
        self.assertEqual(len(claim.examples), 3)
        self.assertEqual(
            [example.expected for example in claim.examples],
            [True, False, False],
        )
        self.assertEqual(claim.examples[0].followup_input, (1, 0, 0))

    def test_claim_examples_evaluate_against_predicate(self):
        claims = load_network_sequence_claims(CLAIMS)

        evaluations = evaluate_network_sequence_claim_examples(claims)

        self.assertEqual(len(evaluations), 3)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)
        self.assertEqual(
            {evaluation.example_name for evaluation in evaluations},
            {
                "proc left init handoff routes later binary signal",
                "write buffer handoff is not post init signal routing",
                "malformed followup input does not route after init handoff",
            },
        )

    def test_network_sequence_claim_project_validates_examples_and_certificates(self):
        report = validate_network_sequence_claim_project(
            claims_path=CLAIMS,
            certificates_path=CERTIFICATES,
        )

        text = format_network_sequence_claim_validation_report(report)

        self.assertTrue(all(result.accepted for result in report.results), text)
        self.assertEqual(report.claim_count, 1)
        self.assertEqual(report.certificate_count, 1)
        self.assertIn("OK sequence-examples: evaluated 3 examples", text)
        self.assertIn("OK sequence-certificates: verified 1 certificates", text)

    def test_json_payload_records_successful_project_validation(self):
        report = validate_network_sequence_claim_project(
            claims_path=CLAIMS,
            certificates_path=CERTIFICATES,
        )

        payload = network_sequence_claim_validation_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], 1)
        self.assertEqual(payload["certificate_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["result_count"], len(report.results))

    def test_cli_returns_zero_for_checked_in_sequence_claim_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_sequence_claim_cli(
                [
                    "--claims",
                    str(CLAIMS),
                    "--certificates",
                    str(CERTIFICATES),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Network sequence claims:", output)
        self.assertIn("OK sequence-certificates", output)

    def test_cli_returns_json_for_checked_in_sequence_claim_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_sequence_claim_cli(
                [
                    "--claims",
                    str(CLAIMS),
                    "--certificates",
                    str(CERTIFICATES),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], 1)
        self.assertNotIn("OK ", stdout.getvalue())

    def test_incomplete_certificate_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            certificate_path = Path(tmp) / "network_sequence_proof_certificates.json"
            certificate_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "certificates": [
                            {
                                "claim_id": CLAIM_ID,
                                "steps": [
                                    {
                                        "rule": "predicate-result",
                                        "example": "proc left init handoff routes later binary signal",
                                        "expected": True,
                                        "predicate": PREDICATE,
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_network_sequence_claim_project(
                claims_path=CLAIMS,
                certificates_path=certificate_path,
            )

        text = format_network_sequence_claim_validation_report(report)
        self.assertFalse(all(result.accepted for result in report.results))
        self.assertIn("FAIL sequence-certificates", text)
        self.assertIn("missing examples", text)

    def test_module_execution_runs_json_sequence_claim_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_claims",
                "--claims",
                str(CLAIMS),
                "--certificates",
                str(CERTIFICATES),
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], 1)


if __name__ == "__main__":
    unittest.main()
