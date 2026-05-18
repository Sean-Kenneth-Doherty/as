import unittest
from pathlib import Path

from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_language_manifest,
)
from autarkic_systems.universal_cell import Cell, step_stem_cell


LANGUAGE = Path("language/transition_claim_language.json")
EMPTY = ("_", "_", "_")


class SelfCommandBufferInitDispatchTests(unittest.TestCase):
    def test_completed_self_proc_left_init_buffer_reconfigures_and_clears_state(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            automail="_",
            self_mailbox="_",
            control=(0, 1, 0),
            buffer=(0, 0, 1, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-command-buffer-self-processed")
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_completed_self_stem_init_buffer_resets_to_stem_and_clears_state(self):
        cell = Cell(
            role="stem",
            memory="left",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(0, 0, 0, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-command-buffer-self-processed")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_completed_neighbor_buffer_delivers_command_without_neighbor_execution(self):
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
        self.assertEqual(result.cell.output, ("stem-init", "_", "_"))
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_completed_self_standard_signal_buffer_remains_append_boundary(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(1, 0, 0),
            buffer=(0, 0, 0, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-appended")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, (1, 0, 0))
        self.assertEqual(result.cell.buffer, (0, 0, 0, 0, 0))

    def test_transition_language_names_command_buffer_self_processed_status(self):
        language = load_transition_claim_language(LANGUAGE)
        statuses = language.syntax_classes["terms"]["statuses"]
        results = validate_language_manifest(language)

        self.assertIn("stem-command-buffer-self-processed", statuses)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
