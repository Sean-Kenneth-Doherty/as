import unittest
from pathlib import Path

from autarkic_systems.willard_map import (
    REQUIRED_CORE_SOURCES,
    load_willard_definition_map,
    validate_willard_definition_map,
)


MAP = Path("sources/willard_definition_map.json")
SJAS_ROOT = Path("/home/sean/Projects/_upstream/sjas")


class WillardDefinitionMapTests(unittest.TestCase):
    def setUp(self):
        self.definition_map = load_willard_definition_map(MAP)

    def test_core_willard_sources_are_mapped_at_definition_granularity(self):
        anchors_by_source = self.definition_map.anchors_by_source()

        self.assertEqual(
            REQUIRED_CORE_SOURCES,
            ("Willard2001", "Willard2011", "Willard2016", "Willard2020"),
        )
        for source_id in REQUIRED_CORE_SOURCES:
            with self.subTest(source_id=source_id):
                anchors = anchors_by_source[source_id]
                self.assertGreaterEqual(len(anchors), 3)
                self.assertTrue(
                    any(anchor.kind == "definition" for anchor in anchors),
                    anchors,
                )
                self.assertTrue(
                    any(anchor.kind in {"theorem", "construction"} for anchor in anchors),
                    anchors,
                )

    def test_map_validates_local_witness_paths_and_as_relevance(self):
        results = validate_willard_definition_map(
            self.definition_map,
            required_sources=REQUIRED_CORE_SOURCES,
            witness_root=SJAS_ROOT,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_missing_required_source_is_rejected(self):
        incomplete = self.definition_map.without_source("Willard2020")

        results = validate_willard_definition_map(
            incomplete,
            required_sources=REQUIRED_CORE_SOURCES,
            witness_root=SJAS_ROOT,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "Willard2020"
                and "missing required source" in result.detail
                for result in results
            ),
            results,
        )

    def test_anchor_ids_and_loci_are_unique(self):
        anchor_ids = [anchor.anchor_id for anchor in self.definition_map.anchors]
        loci = [
            (anchor.source_id, anchor.locus)
            for anchor in self.definition_map.anchors
        ]

        self.assertEqual(len(anchor_ids), len(set(anchor_ids)))
        self.assertEqual(len(loci), len(set(loci)))


if __name__ == "__main__":
    unittest.main()
