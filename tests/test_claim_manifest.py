import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import (
    evaluate_claim_examples,
    load_transition_claims,
)


MANIFEST = Path("claims/transition_claims.json")


class ClaimManifestTests(unittest.TestCase):
    def test_manifest_loads_claims_with_unique_ids(self):
        claims = load_transition_claims(MANIFEST)

        ids = [claim.claim_id for claim in claims]

        self.assertGreaterEqual(len(claims), 4)
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_claim_has_executable_positive_and_negative_examples(self):
        claims = load_transition_claims(MANIFEST)

        for claim in claims:
            with self.subTest(claim=claim.claim_id):
                expected_values = {example.expected for example in claim.examples}
                self.assertEqual(expected_values, {True, False})

    def test_claim_examples_evaluate_to_manifest_expectations(self):
        claims = load_transition_claims(MANIFEST)

        results = evaluate_claim_examples(claims)

        self.assertTrue(results)
        self.assertTrue(all(result.matched for result in results))

    def test_missing_checker_is_reported(self):
        claims = load_transition_claims(MANIFEST)
        bad = claims[0].with_checker("missing_checker")

        with self.assertRaises(ValueError):
            evaluate_claim_examples([bad])


if __name__ == "__main__":
    unittest.main()
