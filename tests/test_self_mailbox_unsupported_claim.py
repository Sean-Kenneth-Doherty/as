import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import (
    evaluate_claim_examples,
    load_transition_claims,
)
from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_claim_surface,
)
from autarkic_systems.proof_certificates import (
    load_proof_certificates,
    verify_claim_certificates,
)
from autarkic_systems.transition_predicates import (
    self_mailbox_preserves_unsupported_command,
)
from autarkic_systems.universal_cell import Cell, StepResult


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED"
UNSUPPORTED_COMMANDS = {"standard-signal"}


class SelfMailboxUnsupportedClaimTests(unittest.TestCase):
    def test_predicate_accepts_preserved_unsupported_mailbox_command(self):
        before = Cell(
            role="stem",
            memory="right",
            self_mailbox="standard-signal",
            control=(1, 0, 0),
            buffer=(0,),
        )
        result = StepResult(status="self-mailbox-unsupported", cell=before)

        predicate = self_mailbox_preserves_unsupported_command(before, result)

        self.assertEqual(predicate.name, "self_mailbox_preserves_unsupported_command")
        self.assertTrue(predicate.holds)

    def test_predicate_rejects_cleared_or_mutated_unsupported_command(self):
        before = Cell(role="stem", memory="right", self_mailbox="standard-signal")
        cleared = StepResult(
            status="self-mailbox-unsupported",
            cell=Cell(role="stem", memory="right", self_mailbox="_"),
        )
        wrong_status = StepResult(status="self-mailbox-processed", cell=before)

        cleared_result = self_mailbox_preserves_unsupported_command(before, cleared)
        wrong_status_result = self_mailbox_preserves_unsupported_command(
            before,
            wrong_status,
        )

        self.assertFalse(cleared_result.holds)
        self.assertIn("changed", cleared_result.detail)
        self.assertFalse(wrong_status_result.holds)
        self.assertIn("self-mailbox-unsupported", wrong_status_result.detail)

    def test_manifest_examples_cover_unsupported_mailbox_claim(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        evaluations = evaluate_claim_examples([claim])

        self.assertEqual(
            claim.predicate,
            "self_mailbox_preserves_unsupported_command",
        )
        self.assertEqual({example.expected for example in claim.examples}, {True, False})
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

    def test_manifest_positive_examples_cover_each_unsupported_mailbox_command(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        positive_commands = {
            example.before.self_mailbox
            for example in claim.examples
            if example.expected
        }

        self.assertEqual(positive_commands, UNSUPPORTED_COMMANDS)

    def test_proof_certificates_cover_unsupported_mailbox_claim(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_unsupported_mailbox_predicate(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn("self_mailbox_preserves_unsupported_command", predicates)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
