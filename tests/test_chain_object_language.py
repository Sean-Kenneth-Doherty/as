import unittest
from pathlib import Path

from autarkic_systems.chain_claims import load_transition_chain_claims
from autarkic_systems.chain_object_language import (
    REQUIRED_CHAIN_SYNTAX_CLASSES,
    load_transition_chain_claim_language,
    validate_chain_claim_surface,
    validate_chain_language_manifest,
)
from autarkic_systems.proof_certificates import CertificateStep, load_proof_certificates


LANGUAGE = Path("language/transition_chain_claim_language.json")
CLAIMS = Path("claims/transition_chain_claims.json")
CERTIFICATES = Path("claims/transition_chain_proof_certificates.json")


class ChainObjectLanguageTests(unittest.TestCase):
    def setUp(self):
        self.language = load_transition_chain_claim_language(LANGUAGE)
        self.claims = load_transition_chain_claims(CLAIMS)
        self.certificates = load_proof_certificates(CERTIFICATES)

    def test_chain_language_manifest_names_required_syntax_classes(self):
        results = validate_chain_language_manifest(self.language)

        self.assertEqual(
            REQUIRED_CHAIN_SYNTAX_CLASSES,
            (
                "terms",
                "chain_formulae",
                "chain_sentences",
                "proof_objects",
                "substrate_chain_claims",
            ),
        )
        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_current_chain_claim_surface_validates_against_language(self):
        results = validate_chain_claim_surface(
            self.language,
            self.claims,
            self.certificates,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_unknown_chain_predicate_is_rejected(self):
        bad_claim = self.claims[0].with_checker("not_a_chain_predicate")

        results = validate_chain_claim_surface(
            self.language,
            [bad_claim],
            self.certificates,
        )

        self.assertFalse(results[0].accepted)
        self.assertIn("unknown chain predicate", results[0].detail)

    def test_unknown_proof_rule_is_rejected(self):
        first = self.certificates[0]
        bad_step = CertificateStep(
            rule="not-a-proof-rule",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad_certificate = first.with_steps((bad_step, *first.steps[1:]))

        results = validate_chain_claim_surface(
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

    def test_chain_status_vocabulary_must_cover_evaluated_examples(self):
        terms = dict(self.language.syntax_classes["terms"])
        terms["chain_statuses"] = ["neighbor-delivery-consumed"]
        bad_language = self.language.with_syntax_class("terms", terms)

        results = validate_chain_claim_surface(
            bad_language,
            self.claims,
            self.certificates,
        )

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(any("unknown chain status" in result.detail for result in results))


if __name__ == "__main__":
    unittest.main()
