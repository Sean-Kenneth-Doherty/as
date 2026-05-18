import unittest
from pathlib import Path

from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_language_manifest,
)
from autarkic_systems.universal_cell import Cell, step_stem_cell


LANGUAGE = Path("language/transition_claim_language.json")
EMPTY = ("_", "_", "_")


class SelfMailboxInitCommandTests(unittest.TestCase):
    def test_self_mailbox_wire_init_reconfigures_stem(self):
        cell = Cell(
            role="stem",
            memory="right",
            self_mailbox="wire-l-init",
            control=(0, 1, 0),
            buffer=(1, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "self-mailbox-processed")
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_self_mailbox_processor_init_reconfigures_stem(self):
        cell = Cell(role="stem", memory="left", self_mailbox="proc-r-init")

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "self-mailbox-processed")
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.self_mailbox, "_")

    def test_self_mailbox_stem_init_resets_stem_state(self):
        cell = Cell(
            role="stem",
            memory="left",
            self_mailbox="stem-init",
            control=(1, 0, 0),
            buffer=(1, 1, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "self-mailbox-processed")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_standard_signal_self_mailbox_command_remains_unsupported_boundary(self):
        for command in ("standard-signal",):
            with self.subTest(command=command):
                cell = Cell(
                    role="stem",
                    memory="right",
                    self_mailbox=command,
                    buffer=(0, 1),
                )

                result = step_stem_cell(cell)

                self.assertEqual(result.status, "self-mailbox-unsupported")
                self.assertEqual(result.cell, cell)

    def test_occupied_output_blocks_self_mailbox_processing(self):
        cell = Cell(
            role="stem",
            memory="right",
            self_mailbox="wire-r-init",
            output=("proc-l-init", "_", "_"),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "blocked-output")
        self.assertEqual(result.cell, cell)

    def test_automail_reconfiguration_still_has_priority(self):
        cell = Cell(
            role="stem",
            memory="right",
            automail="pl",
            self_mailbox="wire-r-init",
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "automail-reconfigured")
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.self_mailbox, "_")

    def test_language_status_terms_include_self_mailbox_outcomes(self):
        language = load_transition_claim_language(LANGUAGE)
        statuses = language.syntax_classes["terms"]["statuses"]
        results = validate_language_manifest(language)

        self.assertIn("self-mailbox-processed", statuses)
        self.assertIn("self-mailbox-unsupported", statuses)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
