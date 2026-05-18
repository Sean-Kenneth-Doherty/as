import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import load_transition_claims
from autarkic_systems import proof_certificates
from autarkic_systems.proof_certificates import (
    CertificateStep,
    ClaimCertificate,
    load_proof_certificates,
    verify_claim_certificates,
)


MANIFEST = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")


class ProofCertificateTests(unittest.TestCase):
    def setUp(self):
        self.claims = load_transition_claims(MANIFEST)

    def test_certificate_manifest_accepts_current_claim_surface(self):
        certificates = load_proof_certificates(CERTIFICATES)

        results = verify_claim_certificates(self.claims, certificates)

        self.assertEqual(len(results), len(self.claims))
        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertTrue(
            any(
                step.rule == "predicate-result"
                for certificate in certificates
                for step in certificate.steps
            )
        )

    def test_consumed_input_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-FIXED-CONSUMED-INPUT-CLEARED"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"consumed_input_cleared"},
        )

    def test_memory_rule_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-FIXED-MEMORY-RULE"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"fixed_role_memory_rule"},
        )

    def test_stem_init_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-FIXED-STEM-INIT-RESET"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"stem_init_resets_to_stem"},
        )

    def test_automail_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-AUTOMAIL-RECONFIGURES"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"automail_reconfigures_stem"},
        )

    def test_stem_buffer_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-BUFFER-ACCUMULATES"]

        self.assertEqual(len(certificate.steps), 4)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"stem_buffer_accumulates"},
        )

    def test_self_mailbox_init_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-SELF-MAILBOX-INIT-COMMAND"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"self_mailbox_executes_init_command"},
        )

    def test_self_mailbox_unsupported_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"self_mailbox_preserves_unsupported_command"},
        )

    def test_self_mailbox_write_buffer_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED"]

        self.assertEqual(len(certificate.steps), 3)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"self_mailbox_write_buffer_appends_literal"},
        )

    def test_self_command_buffer_init_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-COMMAND-BUFFER-SELF-INIT"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"stem_command_buffer_executes_self_init"},
        )

    def test_command_buffer_unsupported_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"stem_command_buffer_preserves_unsupported_completion"},
        )

    def test_self_command_buffer_write_buffer_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates[
            "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED"
        ]

        self.assertEqual(len(certificate.steps), 3)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"stem_command_buffer_executes_self_write_buffer"},
        )

    def test_neighbor_command_buffer_delivery_claim_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates["UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED"]

        self.assertEqual(len(certificate.steps), 2)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"stem_command_buffer_delivers_neighbor_command"},
        )

    def test_report_formats_successful_proof_certificate_validation(self):
        report = proof_certificates.validate_proof_certificate_project(
            claims_path=MANIFEST,
            certificates_path=CERTIFICATES,
        )

        text = proof_certificates.format_proof_certificate_report(report)

        self.assertIn("Transition proof certificates:", text)
        self.assertIn("OK UC-FIXED-OUTPUT-PRESERVED:", text)
        self.assertIn("OK UC-FIXED-CONSUMED-INPUT-CLEARED:", text)
        self.assertIn("OK UC-FIXED-MEMORY-RULE:", text)
        self.assertIn("OK UC-FIXED-STEM-INIT-RESET:", text)
        self.assertIn("OK UC-STEM-AUTOMAIL-RECONFIGURES:", text)
        self.assertIn("OK UC-STEM-BUFFER-ACCUMULATES:", text)
        self.assertIn("OK UC-STEM-SELF-MAILBOX-INIT-COMMAND:", text)
        self.assertIn("OK UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED:", text)
        self.assertIn("OK UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED:", text)
        self.assertIn("OK UC-STEM-COMMAND-BUFFER-SELF-INIT:", text)
        self.assertIn("OK UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED:", text)
        self.assertIn(
            "OK UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED:",
            text,
        )
        self.assertIn("OK UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED:", text)
        self.assertIn("predicate-result", text)
        self.assertNotIn("FAIL", text)

    def test_json_payload_records_successful_proof_certificate_validation(self):
        report = proof_certificates.validate_proof_certificate_project(
            claims_path=MANIFEST,
            certificates_path=CERTIFICATES,
        )

        payload = proof_certificates.proof_certificate_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], len(self.claims))
        self.assertEqual(payload["certificate_count"], len(self.claims))
        self.assertEqual(payload["result_count"], len(report.results))
        self.assertTrue(
            any(
                result["claim_id"] == "UC-FIXED-OUTPUT-PRESERVED"
                and result["accepted"]
                for result in payload["results"]
            )
        )
        consumed = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-FIXED-CONSUMED-INPUT-CLEARED"
        )
        self.assertTrue(consumed["accepted"])
        self.assertEqual(
            consumed["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        memory_rule = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-FIXED-MEMORY-RULE"
        )
        self.assertTrue(memory_rule["accepted"])
        self.assertEqual(
            memory_rule["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        stem_init = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-FIXED-STEM-INIT-RESET"
        )
        self.assertTrue(stem_init["accepted"])
        self.assertEqual(
            stem_init["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        automail = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-AUTOMAIL-RECONFIGURES"
        )
        self.assertTrue(automail["accepted"])
        self.assertEqual(
            automail["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        stem_buffer = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-BUFFER-ACCUMULATES"
        )
        self.assertTrue(stem_buffer["accepted"])
        self.assertEqual(
            stem_buffer["detail"],
            "verified 4 certificate steps: 4 predicate-result steps",
        )
        self_mailbox_init = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-SELF-MAILBOX-INIT-COMMAND"
        )
        self.assertTrue(self_mailbox_init["accepted"])
        self.assertEqual(
            self_mailbox_init["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        self_mailbox_unsupported = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED"
        )
        self.assertTrue(self_mailbox_unsupported["accepted"])
        self.assertEqual(
            self_mailbox_unsupported["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        self_mailbox_write_buffer = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED"
        )
        self.assertTrue(self_mailbox_write_buffer["accepted"])
        self.assertEqual(
            self_mailbox_write_buffer["detail"],
            "verified 3 certificate steps: 3 predicate-result steps",
        )
        self_command_buffer_init = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-COMMAND-BUFFER-SELF-INIT"
        )
        self.assertTrue(self_command_buffer_init["accepted"])
        self.assertEqual(
            self_command_buffer_init["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        command_buffer_unsupported = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED"
        )
        self.assertTrue(command_buffer_unsupported["accepted"])
        self.assertEqual(
            command_buffer_unsupported["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )
        self_command_buffer_write_buffer = next(
            result
            for result in payload["results"]
            if result["claim_id"]
            == "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED"
        )
        self.assertTrue(self_command_buffer_write_buffer["accepted"])
        self.assertEqual(
            self_command_buffer_write_buffer["detail"],
            "verified 3 certificate steps: 3 predicate-result steps",
        )
        neighbor_command_buffer_delivery = next(
            result
            for result in payload["results"]
            if result["claim_id"] == "UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED"
        )
        self.assertTrue(neighbor_command_buffer_delivery["accepted"])
        self.assertEqual(
            neighbor_command_buffer_delivery["detail"],
            "verified 2 certificate steps: 2 predicate-result steps",
        )

    def test_cli_returns_zero_for_checked_in_proof_certificates(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = proof_certificates.run_proof_certificate_cli(
                [
                    "--claims",
                    str(MANIFEST),
                    "--certificates",
                    str(CERTIFICATES),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Transition proof certificates:", output)
        self.assertIn("OK UC-FIXED-OUTPUT-PRESERVED:", output)

    def test_cli_returns_json_for_checked_in_proof_certificates(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = proof_certificates.run_proof_certificate_cli(
                [
                    "--claims",
                    str(MANIFEST),
                    "--certificates",
                    str(CERTIFICATES),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], len(self.claims))
        self.assertNotIn("OK ", stdout.getvalue())

    def test_cli_returns_one_for_incomplete_certificate_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            certificate_path = Path(tmp) / "proof_certificates.json"
            certificate_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "certificates": [
                            {
                                "claim_id": "UC-FIXED-OUTPUT-PRESERVED",
                                "steps": [
                                    {
                                        "rule": "predicate-result",
                                        "example": "blocked output preserved",
                                        "expected": True,
                                        "predicate": "output_not_overwritten",
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
                exit_code = proof_certificates.run_proof_certificate_cli(
                    [
                        "--claims",
                        str(MANIFEST),
                        "--certificates",
                        str(certificate_path),
                    ]
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("FAIL UC-FIXED-OUTPUT-PRESERVED:", output)
        self.assertIn("missing examples", output)

    def test_module_execution_runs_proof_certificate_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.proof_certificates",
                "--claims",
                str(MANIFEST),
                "--certificates",
                str(CERTIFICATES),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Transition proof certificates:", completed.stdout)
        self.assertIn("OK UC-FIXED-OUTPUT-PRESERVED:", completed.stdout)

    def test_module_execution_runs_json_proof_certificate_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.proof_certificates",
                "--claims",
                str(MANIFEST),
                "--certificates",
                str(CERTIFICATES),
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
        self.assertEqual(payload["claim_count"], len(self.claims))

    def test_predicate_result_rule_verifies_named_predicate(self):
        first_claim = self.claims[0]
        predicate_steps = tuple(
            CertificateStep(
                rule="predicate-result",
                example=example.name,
                expected=example.expected,
                predicate=first_claim.predicate,
            )
            for example in first_claim.examples
        )
        certificate = ClaimCertificate(
            claim_id=first_claim.claim_id,
            steps=predicate_steps,
        )

        results = verify_claim_certificates(
            self.claims,
            [certificate, *load_proof_certificates(CERTIFICATES)[1:]],
        )

        self.assertTrue(results[0].accepted, results[0].detail)
        self.assertIn("predicate-result", results[0].detail)

    def test_predicate_result_rule_requires_predicate_name(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="predicate-result",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("predicate", results[0].detail)

    def test_predicate_result_rule_rejects_mismatched_predicate_name(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="predicate-result",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
            predicate="not_the_claim_predicate",
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("predicate mismatch", results[0].detail)

    def test_missing_claim_certificate_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)

        results = verify_claim_certificates(self.claims, certificates[:-1])

        missing = results[-1]
        self.assertFalse(missing.accepted)
        self.assertIn("missing certificate", missing.detail)

    def test_unknown_claim_certificate_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        bad = ClaimCertificate(
            claim_id="UNKNOWN-CLAIM",
            steps=(CertificateStep(rule="manifest-example", example="none", expected=True),),
        )

        results = verify_claim_certificates(self.claims, [*certificates, bad])

        unknown = results[-1]
        self.assertEqual(unknown.claim_id, "UNKNOWN-CLAIM")
        self.assertFalse(unknown.accepted)
        self.assertIn("unknown claim", unknown.detail)

    def test_unknown_rule_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="not-a-rule",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("unknown certificate rule", results[0].detail)

    def test_mismatched_expected_result_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule=first.steps[0].rule,
            example=first.steps[0].example,
            expected=not first.steps[0].expected,
            predicate=first.steps[0].predicate,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("expectation mismatch", results[0].detail)

    def test_missing_example_coverage_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad = first.with_steps(first.steps[:1])

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("missing examples", results[0].detail)


if __name__ == "__main__":
    unittest.main()
