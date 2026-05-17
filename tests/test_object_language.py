import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import load_transition_claims
from autarkic_systems.object_language import (
    REQUIRED_SYNTAX_CLASSES,
    load_transition_claim_language,
    validate_claim_surface,
    validate_language_manifest,
)
from autarkic_systems.proof_certificates import (
    CertificateStep,
    load_proof_certificates,
)


LANGUAGE = Path("language/transition_claim_language.json")
CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")


class ObjectLanguageTests(unittest.TestCase):
    def setUp(self):
        self.language = load_transition_claim_language(LANGUAGE)
        self.claims = load_transition_claims(CLAIMS)
        self.certificates = load_proof_certificates(CERTIFICATES)

    def test_language_manifest_names_required_syntax_classes(self):
        results = validate_language_manifest(self.language)

        self.assertEqual(
            REQUIRED_SYNTAX_CLASSES,
            ("terms", "formulae", "sentences", "proof_objects", "substrate_claims"),
        )
        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_current_claim_surface_validates_against_language(self):
        results = validate_claim_surface(self.language, self.claims, self.certificates)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_missing_syntax_class_is_rejected(self):
        bad_language = self.language.without_syntax_class("formulae")

        results = validate_language_manifest(bad_language)

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(
            any("missing syntax class: formulae" in result.detail for result in results)
        )

    def test_unknown_predicate_symbol_is_rejected(self):
        bad_claim = self.claims[0].with_checker("not_a_language_predicate")

        results = validate_claim_surface(
            self.language, [bad_claim, *self.claims[1:]], self.certificates
        )

        self.assertFalse(results[0].accepted)
        self.assertIn("unknown predicate", results[0].detail)

    def test_unknown_proof_object_rule_is_rejected(self):
        first = self.certificates[0]
        bad_step = CertificateStep(
            rule="not-a-proof-rule",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad_certificate = first.with_steps((bad_step, *first.steps[1:]))

        results = validate_claim_surface(
            self.language, self.claims, [bad_certificate, *self.certificates[1:]]
        )

        unknown_rule_results = [
            result
            for result in results
            if result.detail.startswith("unknown proof object rule")
        ]
        self.assertEqual(len(unknown_rule_results), 1)
        self.assertFalse(unknown_rule_results[0].accepted)

    def test_language_term_vocabulary_must_cover_claim_examples(self):
        terms = dict(self.language.syntax_classes["terms"])
        terms["roles"] = ["wire", "proc"]
        bad_language = self.language.with_syntax_class("terms", terms)

        results = validate_claim_surface(bad_language, self.claims, self.certificates)

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(any("unknown role" in result.detail for result in results))


if __name__ == "__main__":
    unittest.main()
