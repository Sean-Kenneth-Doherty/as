import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import network_sequence_object_language
from autarkic_systems.network_sequence_claims import load_network_sequence_claims
from autarkic_systems.network_sequence_object_language import (
    REQUIRED_SEQUENCE_SYNTAX_CLASSES,
    load_network_sequence_claim_language,
    validate_sequence_claim_surface,
    validate_sequence_language_manifest,
)
from autarkic_systems.proof_certificates import CertificateStep, load_proof_certificates


LANGUAGE = Path("language/network_sequence_claim_language.json")
CLAIMS = Path("claims/network_sequence_claims.json")
CERTIFICATES = Path("claims/network_sequence_proof_certificates.json")


class NetworkSequenceObjectLanguageTests(unittest.TestCase):
    def setUp(self):
        self.language = load_network_sequence_claim_language(LANGUAGE)
        self.claims = load_network_sequence_claims(CLAIMS)
        self.certificates = load_proof_certificates(CERTIFICATES)

    def test_sequence_language_manifest_names_required_syntax_classes(self):
        results = validate_sequence_language_manifest(self.language)

        self.assertEqual(
            REQUIRED_SEQUENCE_SYNTAX_CLASSES,
            (
                "terms",
                "sequence_formulae",
                "sequence_sentences",
                "proof_objects",
                "substrate_sequence_claims",
            ),
        )
        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_current_sequence_claim_surface_validates_against_language(self):
        results = validate_sequence_claim_surface(
            self.language,
            self.claims,
            self.certificates,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertIn(
            "predicate-result",
            self.language.syntax_classes["proof_objects"]["rules"],
        )

    def test_report_formats_successful_sequence_language_validation(self):
        report = (
            network_sequence_object_language
            .validate_network_sequence_claim_language_project(
                language_path=LANGUAGE,
                claims_path=CLAIMS,
                certificates_path=CERTIFICATES,
            )
        )

        text = (
            network_sequence_object_language
            .format_network_sequence_claim_language_report(report)
        )

        self.assertIn(
            "Network sequence claim language: as-network-sequence-claim-v1",
            text,
        )
        self.assertIn("OK terms.roles:", text)
        self.assertIn("OK UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED:", text)
        self.assertNotIn("FAIL", text)

    def test_json_payload_records_successful_sequence_language_validation(self):
        report = (
            network_sequence_object_language
            .validate_network_sequence_claim_language_project(
                language_path=LANGUAGE,
                claims_path=CLAIMS,
                certificates_path=CERTIFICATES,
            )
        )

        payload = (
            network_sequence_object_language
            .network_sequence_claim_language_report_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["language_id"], "as-network-sequence-claim-v1")
        self.assertEqual(payload["claim_count"], len(self.claims))
        self.assertEqual(payload["certificate_count"], len(self.certificates))
        self.assertEqual(payload["result_count"], len(report.results))
        self.assertTrue(
            any(
                result["subject"] == "proof_objects.rules"
                and result["accepted"]
                and "predicate-result" in result["detail"]
                for result in payload["results"]
            )
        )

    def test_cli_returns_zero_for_checked_in_sequence_language_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                network_sequence_object_language
                .run_network_sequence_claim_language_cli(
                    [
                        "--language",
                        str(LANGUAGE),
                        "--claims",
                        str(CLAIMS),
                        "--certificates",
                        str(CERTIFICATES),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Network sequence claim language:", output)
        self.assertIn("OK UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED:", output)

    def test_cli_returns_json_for_checked_in_sequence_language_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                network_sequence_object_language
                .run_network_sequence_claim_language_cli(
                    [
                        "--language",
                        str(LANGUAGE),
                        "--claims",
                        str(CLAIMS),
                        "--certificates",
                        str(CERTIFICATES),
                        "--format",
                        "json",
                    ]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], len(self.claims))
        self.assertNotIn("OK ", stdout.getvalue())

    def test_cli_returns_one_for_missing_sequence_language_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "network_sequence_claim_language.json"
            data = json.loads(LANGUAGE.read_text(encoding="utf-8"))
            del data["syntax_classes"]["sequence_formulae"]
            language_path.write_text(json.dumps(data), encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = (
                    network_sequence_object_language
                    .run_network_sequence_claim_language_cli(
                        [
                            "--language",
                            str(language_path),
                            "--claims",
                            str(CLAIMS),
                            "--certificates",
                            str(CERTIFICATES),
                        ]
                    )
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn(
            "FAIL sequence_formulae: missing syntax class: sequence_formulae",
            output,
        )

    def test_module_execution_runs_sequence_language_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_object_language",
                "--language",
                str(LANGUAGE),
                "--claims",
                str(CLAIMS),
                "--certificates",
                str(CERTIFICATES),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Network sequence claim language:", completed.stdout)
        self.assertIn(
            "OK UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED:",
            completed.stdout,
        )

    def test_module_execution_runs_json_sequence_language_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_object_language",
                "--language",
                str(LANGUAGE),
                "--claims",
                str(CLAIMS),
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
        self.assertEqual(payload["language_id"], "as-network-sequence-claim-v1")

    def test_unknown_sequence_predicate_is_rejected(self):
        bad_claim = self.claims[0].with_checker("not_a_sequence_predicate")

        results = validate_sequence_claim_surface(
            self.language,
            [bad_claim],
            self.certificates,
        )

        self.assertFalse(results[0].accepted)
        self.assertIn("unknown sequence predicate", results[0].detail)

    def test_unknown_proof_rule_is_rejected(self):
        first = self.certificates[0]
        bad_step = CertificateStep(
            rule="not-a-proof-rule",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad_certificate = first.with_steps((bad_step, *first.steps[1:]))

        results = validate_sequence_claim_surface(
            self.language,
            self.claims,
            [bad_certificate],
        )

        self.assertTrue(
            any(
                not result.accepted
                and "unknown proof object rule" in result.detail
                for result in results
            ),
            results,
        )

    def test_sequence_status_vocabulary_must_cover_evaluated_examples(self):
        terms = dict(self.language.syntax_classes["terms"])
        terms["sequence_statuses"] = ["handoff-not-init-consumed"]
        bad_language = self.language.with_syntax_class("terms", terms)

        results = validate_sequence_claim_surface(
            bad_language,
            self.claims,
            self.certificates,
        )

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(
            any("unknown sequence status" in result.detail for result in results),
            results,
        )


if __name__ == "__main__":
    unittest.main()
