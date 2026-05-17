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
    recipient_init_command_message_processed,
)
from autarkic_systems.universal_cell import Cell, StepResult, step_fixed_cell, step_stem_cell


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED"
EMPTY = ("_", "_", "_")
STATUS = "recipient-init-command-message-processed"


class RecipientInitCommandMessageClaimTests(unittest.TestCase):
    def test_predicate_accepts_fixed_direct_and_upstream_command_inputs(self):
        cases = (
            Cell(role="wire", memory="right", input=("_", "proc-l-init", "_")),
            Cell(role="proc", memory="left", upstream=("wire-r-init", "_", "_")),
        )

        for before in cases:
            with self.subTest(before=before):
                predicate = recipient_init_command_message_processed(
                    before,
                    step_fixed_cell(before),
                )

                self.assertEqual(predicate.name, "recipient_init_command_message_processed")
                self.assertTrue(predicate.holds, predicate.detail)

    def test_predicate_accepts_stem_recipient_command_state_clearing(self):
        before = Cell(
            role="stem",
            memory="right",
            input=("_", "wire-l-init", "_"),
            self_mailbox="proc-r-init",
            control=(0, 1, 0),
            buffer=(1, 0),
        )

        predicate = recipient_init_command_message_processed(
            before,
            step_stem_cell(before),
        )

        self.assertTrue(predicate.holds, predicate.detail)

    def test_predicate_rejects_wrong_target_uncleared_state_and_wrong_status(self):
        before = Cell(role="wire", memory="right", input=("proc-l-init", "_", "_"))
        wrong_target = StepResult(
            status=STATUS,
            cell=Cell(role="wire", memory="left"),
        )
        uncleared_state = StepResult(
            status=STATUS,
            cell=Cell(
                role="proc",
                memory="left",
                input=EMPTY,
                self_mailbox="wire-r-init",
                control=(1, 0, 0),
            ),
        )
        wrong_status = StepResult(
            status="rejected-input",
            cell=Cell(role="proc", memory="left"),
        )

        wrong_target_result = recipient_init_command_message_processed(
            before,
            wrong_target,
        )
        uncleared_state_result = recipient_init_command_message_processed(
            before,
            uncleared_state,
        )
        wrong_status_result = recipient_init_command_message_processed(
            before,
            wrong_status,
        )

        self.assertFalse(wrong_target_result.holds)
        self.assertIn("expected", wrong_target_result.detail)
        self.assertFalse(uncleared_state_result.holds)
        self.assertIn("command state", uncleared_state_result.detail)
        self.assertFalse(wrong_status_result.holds)
        self.assertIn(STATUS, wrong_status_result.detail)

    def test_predicate_ignores_non_init_and_multi_command_inputs(self):
        cases = (
            Cell(role="stem", memory="right", input=("write-buf-one", "_", "_")),
            Cell(role="stem", memory="right", input=("wire-r-init", "proc-l-init", "_")),
            Cell(role="wire", memory="right", input=(1, 0, 1)),
        )

        for before in cases:
            with self.subTest(before=before):
                predicate = recipient_init_command_message_processed(
                    before,
                    StepResult(status="rejected-input", cell=before),
                )

                self.assertTrue(predicate.holds)
                self.assertIn("precondition not active", predicate.detail)

    def test_manifest_examples_cover_recipient_init_command_claim(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        evaluations = evaluate_claim_examples([claim])

        self.assertEqual(
            claim.predicate,
            "recipient_init_command_message_processed",
        )
        self.assertEqual({example.expected for example in claim.examples}, {True, False})
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

    def test_proof_certificates_cover_recipient_init_command_claim(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_recipient_init_command_predicate(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn("recipient_init_command_message_processed", predicates)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
