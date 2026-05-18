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
    self_mailbox_write_buffer_appends_literal,
    stem_command_buffer_executes_self_write_buffer,
)
from autarkic_systems.universal_cell import Cell, StepResult


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
SELF_MAILBOX_CLAIM_ID = "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED"
COMMAND_BUFFER_CLAIM_ID = "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED"
EMPTY = ("_", "_", "_")


class WriteBufferCommandExecutionClaimTests(unittest.TestCase):
    def test_self_mailbox_predicate_accepts_literal_write_buffer_append(self):
        before = Cell(
            role="stem",
            memory="right",
            self_mailbox="write-buf-one",
            control=(0, 1, 0),
            buffer=(1, 0),
        )
        result = StepResult(
            status="self-mailbox-write-buffer-appended",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=EMPTY,
                automail="_",
                self_mailbox="_",
                control=(0, 1, 0),
                buffer=(1, 0, 1),
            ),
        )

        predicate = self_mailbox_write_buffer_appends_literal(before, result)

        self.assertEqual(predicate.name, "self_mailbox_write_buffer_appends_literal")
        self.assertTrue(predicate.holds, predicate.detail)

    def test_self_mailbox_predicate_rejects_wrong_literal_bit(self):
        before = Cell(role="stem", memory="right", self_mailbox="write-buf-zero")
        result = StepResult(
            status="self-mailbox-write-buffer-appended",
            cell=Cell(role="stem", memory="right", self_mailbox="_", buffer=(1,)),
        )

        predicate = self_mailbox_write_buffer_appends_literal(before, result)

        self.assertFalse(predicate.holds)
        self.assertIn("expected buffer", predicate.detail)

    def test_command_buffer_predicate_accepts_self_write_buffer_append(self):
        before = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 1),
        )
        result = StepResult(
            status="stem-command-buffer-self-write-buffer-appended",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=EMPTY,
                automail="_",
                self_mailbox="_",
                control=(0, 1, 0),
                buffer=(1,),
            ),
        )

        predicate = stem_command_buffer_executes_self_write_buffer(before, result)

        self.assertEqual(
            predicate.name,
            "stem_command_buffer_executes_self_write_buffer",
        )
        self.assertTrue(predicate.holds, predicate.detail)

    def test_command_buffer_predicate_rejects_preserved_command_source(self):
        before = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 1),
        )
        result = StepResult(
            status="stem-buffer-appended",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=EMPTY,
                automail="_",
                self_mailbox="_",
                control=(0, 1, 0),
                buffer=(0, 0, 1, 1, 1),
            ),
        )

        predicate = stem_command_buffer_executes_self_write_buffer(before, result)

        self.assertFalse(predicate.holds)
        self.assertIn("stem-command-buffer-self-write-buffer-appended", predicate.detail)

    def test_manifest_and_proofs_cover_write_buffer_execution_claims(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        claims_by_id = {claim.claim_id: claim for claim in claims}

        self.assertIn(SELF_MAILBOX_CLAIM_ID, claims_by_id)
        self.assertIn(COMMAND_BUFFER_CLAIM_ID, claims_by_id)
        self.assertEqual(
            claims_by_id[SELF_MAILBOX_CLAIM_ID].predicate,
            "self_mailbox_write_buffer_appends_literal",
        )
        self.assertEqual(
            claims_by_id[COMMAND_BUFFER_CLAIM_ID].predicate,
            "stem_command_buffer_executes_self_write_buffer",
        )
        self.assertTrue(
            all(
                evaluation.matched
                for evaluation in evaluate_claim_examples(
                    [
                        claims_by_id[SELF_MAILBOX_CLAIM_ID],
                        claims_by_id[COMMAND_BUFFER_CLAIM_ID],
                    ]
                )
            )
        )

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(SELF_MAILBOX_CLAIM_ID, certificate_ids)
        self.assertIn(COMMAND_BUFFER_CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_write_buffer_execution_surface(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]
        statuses = language.syntax_classes["terms"]["statuses"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn("self_mailbox_write_buffer_appends_literal", predicates)
        self.assertIn("stem_command_buffer_executes_self_write_buffer", predicates)
        self.assertIn("self-mailbox-write-buffer-appended", statuses)
        self.assertIn("stem-command-buffer-self-write-buffer-appended", statuses)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
