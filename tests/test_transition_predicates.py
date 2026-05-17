import unittest

from autarkic_systems.transition_predicates import (
    consumed_input_cleared,
    fixed_role_memory_rule,
    output_not_overwritten,
    stem_init_resets_to_stem,
)
from autarkic_systems.universal_cell import Cell, StepResult, step_fixed_cell


EMPTY = ("_", "_", "_")


class TransitionPredicateTests(unittest.TestCase):
    def test_output_not_overwritten_holds_for_blocked_transition(self):
        before = Cell(role="wire", memory="right", input=(1, 0, 0), output=(0, "_", "_"))
        result = step_fixed_cell(before)

        predicate = output_not_overwritten(before, result)

        self.assertEqual(predicate.name, "output_not_overwritten")
        self.assertTrue(predicate.holds)

    def test_output_not_overwritten_detects_bad_blocked_result(self):
        before = Cell(role="wire", memory="right", input=(1, 0, 0), output=(0, "_", "_"))
        bad = StepResult(
            status="blocked-output",
            cell=Cell(role="wire", memory="right", input=(1, 0, 0), output=(1, 1, 1)),
        )

        predicate = output_not_overwritten(before, bad)

        self.assertFalse(predicate.holds)
        self.assertIn("changed", predicate.detail)

    def test_consumed_input_cleared_holds_for_terminal_processing(self):
        for cell in [
            Cell(role="wire", memory="right", input=(1, 0, 1)),
            Cell(role="wire", memory="right", input=(1, "si", 0)),
            Cell(role="proc", memory="left", input=("_", "si", "_")),
        ]:
            with self.subTest(cell=cell):
                predicate = consumed_input_cleared(cell, step_fixed_cell(cell))
                self.assertTrue(predicate.holds)

    def test_consumed_input_cleared_detects_uncleared_routed_input(self):
        before = Cell(role="wire", memory="right", input=(1, 0, 1))
        bad = StepResult(status="routed", cell=Cell(role="wire", memory="right", input=(1, 0, 1)))

        predicate = consumed_input_cleared(before, bad)

        self.assertFalse(predicate.holds)

    def test_fixed_role_memory_rule_accepts_wire_preserve_and_proc_toggle(self):
        wire = Cell(role="wire", memory="right", input=(1, 0, 1))
        proc = Cell(role="proc", memory="left", input=(1, 0, 1))

        self.assertTrue(fixed_role_memory_rule(wire, step_fixed_cell(wire)).holds)
        self.assertTrue(fixed_role_memory_rule(proc, step_fixed_cell(proc)).holds)

    def test_fixed_role_memory_rule_detects_missing_proc_toggle(self):
        before = Cell(role="proc", memory="left", input=(1, 0, 1))
        bad = StepResult(status="routed", cell=Cell(role="proc", memory="left", output=(0, 1, 1)))

        predicate = fixed_role_memory_rule(before, bad)

        self.assertFalse(predicate.holds)
        self.assertIn("toggle", predicate.detail)

    def test_stem_init_resets_to_stem_holds(self):
        before = Cell(role="proc", memory="left", input=("_", "si", "_"))

        predicate = stem_init_resets_to_stem(before, step_fixed_cell(before))

        self.assertTrue(predicate.holds)

    def test_stem_init_resets_to_stem_detects_bad_result(self):
        before = Cell(role="proc", memory="left", input=("_", "si", "_"))
        bad = StepResult(status="stem-init", cell=Cell(role="proc", memory="left", input=EMPTY))

        predicate = stem_init_resets_to_stem(before, bad)

        self.assertFalse(predicate.holds)


if __name__ == "__main__":
    unittest.main()
