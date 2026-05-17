import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.stem_command_map import (
    COMMAND_BUFFER_WIDTH,
    load_stem_command_buffer_map,
    validate_stem_command_buffer_map,
)


MAP = Path("sources/stem_command_buffer_map.json")


class StemCommandBufferMapTests(unittest.TestCase):
    def setUp(self):
        self.command_map = load_stem_command_buffer_map(MAP)

    def test_map_records_prc_source_anchor_and_bit_order(self):
        self.assertEqual(COMMAND_BUFFER_WIDTH, 5)
        self.assertEqual(self.command_map.source_witness_id, "PRC-UC-FORMAL-MODEL")
        self.assertEqual(self.command_map.bit_order, "accumulated-msb-first")
        self.assertIn("formal-model.txt", self.command_map.local_witness)

    def test_map_validates_complete_target_and_command_surface(self):
        results = validate_stem_command_buffer_map(self.command_map)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(len(self.command_map.decode_cases()), 32)
        self.assertEqual(
            {case.value for case in self.command_map.decode_cases()},
            set(range(32)),
        )

    def test_representative_buffers_decode_to_target_and_command(self):
        examples = {
            (0, 0, 0, 0, 0): ("self", "standard-signal", 0),
            (0, 0, 1, 0, 1): ("self", "proc-l-init", 5),
            (0, 1, 0, 0, 0): ("neighbor-a", "standard-signal", 8),
            (1, 0, 1, 0, 1): ("neighbor-b", "proc-l-init", 21),
            (1, 1, 1, 1, 1): ("neighbor-c", "write-buf-one", 31),
        }

        for buffer, expected in examples.items():
            with self.subTest(buffer=buffer):
                decoded = self.command_map.decode_buffer(buffer)
                self.assertEqual(
                    (decoded.target_id, decoded.command_id, decoded.value),
                    expected,
                )

    def test_invalid_buffer_width_or_bits_are_rejected(self):
        with self.assertRaises(ValueError):
            self.command_map.decode_buffer((0, 1, 0))

        with self.assertRaises(ValueError):
            self.command_map.decode_buffer((0, 1, 0, 2, 1))

    def test_incomplete_target_coverage_is_rejected(self):
        bad_map = replace(self.command_map, target_ranges=self.command_map.target_ranges[:-1])

        results = validate_stem_command_buffer_map(bad_map)

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(
            any(
                not result.accepted and result.subject == "target_ranges"
                for result in results
            ),
            results,
        )

    def test_noncanonical_target_ranges_are_rejected(self):
        bad_map = replace(
            self.command_map,
            target_ranges=(
                replace(self.command_map.target_ranges[0], value_end=15),
                *self.command_map.target_ranges[2:],
            ),
        )

        results = validate_stem_command_buffer_map(bad_map)

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(
            any(
                not result.accepted and result.subject == "target_ranges"
                for result in results
            ),
            results,
        )

    def test_incomplete_command_offsets_are_rejected(self):
        bad_map = replace(self.command_map, commands=self.command_map.commands[:-1])

        results = validate_stem_command_buffer_map(bad_map)

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(
            any(
                not result.accepted and result.subject == "commands"
                for result in results
            ),
            results,
        )

    def test_noncanonical_command_ids_are_rejected(self):
        bad_map = replace(
            self.command_map,
            commands=(
                replace(self.command_map.commands[0], command_id="ordinary-signal"),
                *self.command_map.commands[1:],
            ),
        )

        results = validate_stem_command_buffer_map(bad_map)

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(
            any(
                not result.accepted and result.subject == "commands"
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
