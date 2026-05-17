import unittest
from pathlib import Path

from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_language_manifest,
)
from autarkic_systems.universal_cell import Cell, step_stem_cell


LANGUAGE = Path("language/transition_claim_language.json")
EMPTY = ("_", "_", "_")


class NeighborCommandBufferDeliveryTests(unittest.TestCase):
    def test_completed_neighbor_a_command_delivers_to_first_output_channel(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 0, 1),
            control=(0, 0, 1),
            buffer=(0, 1, 0, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-command-buffer-neighbor-delivered")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, ("stem-init", "_", "_"))
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_completed_neighbor_b_and_c_commands_deliver_to_matching_output_channels(self):
        cases = (
            (
                "neighbor-b proc-l-init",
                Cell(
                    role="stem",
                    memory="right",
                    input=(1, 0, 0),
                    control=(1, 0, 0),
                    buffer=(1, 0, 1, 0),
                ),
                ("_", "proc-l-init", "_"),
            ),
            (
                "neighbor-c write-buf-one",
                Cell(
                    role="stem",
                    memory="right",
                    input=(0, 1, 0),
                    control=(0, 1, 0),
                    buffer=(1, 1, 1, 1),
                ),
                ("_", "_", "write-buf-one"),
            ),
        )

        for name, cell, expected_output in cases:
            with self.subTest(name=name):
                result = step_stem_cell(cell)

                self.assertEqual(
                    result.status,
                    "stem-command-buffer-neighbor-delivered",
                )
                self.assertEqual(result.cell.output, expected_output)
                self.assertEqual(result.cell.input, EMPTY)
                self.assertEqual(result.cell.control, ())
                self.assertEqual(result.cell.buffer, ())

    def test_blocked_output_still_prevents_neighbor_delivery(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 0, 1),
            output=(1, "_", "_"),
            control=(0, 0, 1),
            buffer=(0, 1, 0, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "blocked-output")
        self.assertEqual(result.cell, cell)

    def test_self_non_init_command_still_remains_append_boundary(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 1),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-appended")
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.control, (0, 1, 0))
        self.assertEqual(result.cell.buffer, (0, 0, 1, 1, 1))

    def test_command_message_input_is_still_not_neighbor_side_execution(self):
        cell = Cell(role="stem", memory="right", input=("stem-init", "_", "_"))

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)

    def test_transition_language_names_neighbor_delivery_status(self):
        language = load_transition_claim_language(LANGUAGE)
        statuses = language.syntax_classes["terms"]["statuses"]
        results = validate_language_manifest(language)

        self.assertIn("stem-command-buffer-neighbor-delivered", statuses)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
