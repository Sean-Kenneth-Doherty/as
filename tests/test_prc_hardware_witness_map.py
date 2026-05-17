import unittest
from pathlib import Path

from autarkic_systems.prc_hardware_map import (
    REQUIRED_WITNESS_IDS,
    load_prc_hardware_witness_map,
    validate_prc_hardware_witness_map,
)


MAP = Path("sources/prc_hardware_witness_map.json")
PRC_ROOT = Path("/home/sean/Projects/_upstream/prc")


class PRCHardwareWitnessMapTests(unittest.TestCase):
    def setUp(self):
        self.witness_map = load_prc_hardware_witness_map(MAP)

    def test_required_hardware_witnesses_are_mapped(self):
        witnesses_by_id = self.witness_map.witnesses_by_id()

        self.assertEqual(
            REQUIRED_WITNESS_IDS,
            (
                "PRC-README-UC-CRITERIA",
                "PRC-GELC-GEOMETRY",
                "PRC-RLEM-LITERATURE",
                "PRC-CIRCULATOR-PHYSICAL",
                "PRC-RALA-RECONFIGURATION",
                "PRC-UC-FORMAL-MODEL",
                "PRC-ASM-SIMULATOR",
                "PRC-SCHEMATIC-FIGURES",
            ),
        )
        for witness_id in REQUIRED_WITNESS_IDS:
            with self.subTest(witness_id=witness_id):
                self.assertIn(witness_id, witnesses_by_id)

    def test_map_validates_source_paths_and_simulation_target(self):
        results = validate_prc_hardware_witness_map(
            self.witness_map,
            required_witness_ids=REQUIRED_WITNESS_IDS,
            witness_root=PRC_ROOT,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            self.witness_map.recommended_next_artifact,
            "single-node-triangular-rlem-schematic-and-uc-transition-trace",
        )

    def test_each_witness_names_hardware_role_and_as_relevance(self):
        for witness in self.witness_map.witnesses:
            with self.subTest(witness_id=witness.witness_id):
                self.assertTrue(witness.hardware_role)
                self.assertTrue(
                    any(
                        relevance.startswith("AFS-R") or relevance.startswith("P")
                        for relevance in witness.as_relevance
                    )
                )
                self.assertTrue(witness.next_as_action)

    def test_missing_required_witness_is_rejected(self):
        incomplete = self.witness_map.without_witness("PRC-CIRCULATOR-PHYSICAL")

        results = validate_prc_hardware_witness_map(
            incomplete,
            required_witness_ids=REQUIRED_WITNESS_IDS,
            witness_root=PRC_ROOT,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "PRC-CIRCULATOR-PHYSICAL"
                and "missing required witness" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
