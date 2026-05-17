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
    stem_command_buffer_preserves_unsupported_completion,
)
from autarkic_systems.universal_cell import Cell, StepResult


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED"
EMPTY = ("_", "_", "_")


class CommandBufferUnsupportedClaimTests(unittest.TestCase):
    def test_predicate_accepts_self_non_init_completed_append_boundary(self):
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

        predicate = stem_command_buffer_preserves_unsupported_completion(
            before,
            result,
        )

        self.assertEqual(
            predicate.name,
            "stem_command_buffer_preserves_unsupported_completion",
        )
        self.assertTrue(predicate.holds)

    def test_predicate_ignores_neighbor_delivery_after_adr_0044(self):
        before = Cell(
            role="stem",
            memory="right",
            input=(0, 0, 1),
            control=(0, 0, 1),
            buffer=(0, 1, 0, 0),
        )
        result = StepResult(
            status="stem-command-buffer-neighbor-delivered",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=("stem-init", "_", "_"),
                automail="_",
                self_mailbox="_",
                control=(),
                buffer=(),
            ),
        )

        predicate = stem_command_buffer_preserves_unsupported_completion(
            before,
            result,
        )

        self.assertTrue(predicate.holds)
        self.assertIn("neighbor delivery", predicate.detail)

    def test_predicate_rejects_processed_status_or_mutated_append_boundary(self):
        before = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 1),
        )
        processed = StepResult(
            status="stem-command-buffer-self-processed",
            cell=Cell(role="stem", memory="right"),
        )
        wrong_buffer = StepResult(
            status="stem-buffer-appended",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=EMPTY,
                automail="_",
                self_mailbox="_",
                control=(0, 1, 0),
                buffer=(),
            ),
        )
        output_mutated = StepResult(
            status="stem-buffer-appended",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=(1, "_", "_"),
                automail="_",
                self_mailbox="_",
                control=(0, 1, 0),
                buffer=(0, 0, 1, 1, 1),
            ),
        )

        processed_result = stem_command_buffer_preserves_unsupported_completion(
            before,
            processed,
        )
        wrong_buffer_result = stem_command_buffer_preserves_unsupported_completion(
            before,
            wrong_buffer,
        )
        output_mutated_result = stem_command_buffer_preserves_unsupported_completion(
            before,
            output_mutated,
        )

        self.assertFalse(processed_result.holds)
        self.assertIn("stem-buffer-appended", processed_result.detail)
        self.assertFalse(wrong_buffer_result.holds)
        self.assertIn("expected buffer", wrong_buffer_result.detail)
        self.assertFalse(output_mutated_result.holds)
        self.assertIn("output", output_mutated_result.detail)

    def test_manifest_examples_cover_unsupported_command_buffer_claim(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        evaluations = evaluate_claim_examples([claim])

        self.assertEqual(
            claim.predicate,
            "stem_command_buffer_preserves_unsupported_completion",
        )
        self.assertEqual({example.expected for example in claim.examples}, {True, False})
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

    def test_proof_certificates_cover_unsupported_command_buffer_claim(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_unsupported_command_buffer_predicate(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn(
            "stem_command_buffer_preserves_unsupported_completion",
            predicates,
        )
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
