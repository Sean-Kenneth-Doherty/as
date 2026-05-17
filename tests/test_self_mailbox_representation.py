import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import load_transition_claims
from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_language_manifest,
)
from autarkic_systems.schematic_trace import (
    REQUIRED_CELL_FIELDS,
    load_schematic_trace,
)
from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


LANGUAGE = Path("language/transition_claim_language.json")
CLAIMS = Path("claims/transition_claims.json")
TRACE = Path("schematics/stem_buffer_accumulation_trace.json")
EMPTY = ("_", "_", "_")


class SelfMailboxRepresentationTests(unittest.TestCase):
    def test_cell_defaults_to_empty_self_mailbox_and_accepts_command_ids(self):
        self.assertEqual(Cell(role="stem", memory="right").self_mailbox, "_")

        cell = Cell(
            role="stem",
            memory="right",
            self_mailbox="proc-l-init",
        )

        self.assertEqual(cell.self_mailbox, "proc-l-init")

    def test_unknown_self_mailbox_value_is_rejected(self):
        with self.assertRaises(ValueError):
            Cell(role="stem", memory="right", self_mailbox="neighbor-a")

    def test_existing_reset_transitions_clear_self_mailbox(self):
        fixed = Cell(
            role="proc",
            memory="left",
            input=("_", "si", "_"),
            self_mailbox="write-buf-one",
        )
        stem = Cell(
            role="stem",
            memory="right",
            automail="wl",
            self_mailbox="proc-r-init",
        )

        fixed_result = step_fixed_cell(fixed)
        stem_result = step_stem_cell(stem)

        self.assertEqual(fixed_result.status, "stem-init")
        self.assertEqual(fixed_result.cell.self_mailbox, "_")
        self.assertEqual(stem_result.status, "automail-reconfigured")
        self.assertEqual(stem_result.cell.self_mailbox, "_")

    def test_non_execution_transitions_preserve_self_mailbox(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1,),
            self_mailbox="stem-init",
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "stem-buffer-appended")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.buffer, (1, 1))
        self.assertEqual(result.cell.self_mailbox, "stem-init")

    def test_claim_manifest_loader_preserves_self_mailbox_default(self):
        claims = load_transition_claims(CLAIMS)

        cells = [
            example.before
            for claim in claims
            for example in claim.examples
        ] + [
            example.result.cell
            for claim in claims
            for example in claim.examples
        ]

        self.assertTrue(cells)
        self.assertTrue(all(cell.self_mailbox == "_" for cell in cells))

    def test_object_language_names_self_mailbox_terms_and_field(self):
        language = load_transition_claim_language(LANGUAGE)
        terms = language.syntax_classes["terms"]
        results = validate_language_manifest(language)

        self.assertIn("self_mailbox", terms["cell_fields"])
        self.assertEqual(
            terms["command_messages"],
            [
                "_",
                "standard-signal",
                "stem-init",
                "wire-r-init",
                "wire-l-init",
                "proc-r-init",
                "proc-l-init",
                "write-buf-zero",
                "write-buf-one",
            ],
        )
        self.assertTrue(all(result.accepted for result in results), results)

    def test_schematic_trace_maps_self_mailbox_field(self):
        trace = load_schematic_trace(TRACE)

        self.assertIn("self_mailbox", REQUIRED_CELL_FIELDS)
        self.assertEqual(trace.trace.cell_fields, REQUIRED_CELL_FIELDS)
        self.assertEqual(trace.trace.before_cell["self_mailbox"], "_")
        self.assertEqual(trace.trace.expected_after_cell["self_mailbox"], "_")


if __name__ == "__main__":
    unittest.main()
