import unittest

from autarkic_systems.universal_cell import Cell, step_fixed_cell


EMPTY = ("_", "_", "_")


class UniversalCellTransitionTests(unittest.TestCase):
    def test_wire_right_routes_standard_signal_without_memory_change(self):
        cell = Cell(role="wire", memory="right", input=(1, 0, 1))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "routed")
        self.assertEqual(result.cell.output, (1, 1, 0))
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.role, "wire")

    def test_processor_left_routes_standard_signal_and_toggles_memory(self):
        cell = Cell(role="proc", memory="left", input=(1, 0, 0))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "routed")
        self.assertEqual(result.cell.output, (0, 0, 1))
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.role, "proc")

    def test_occupied_output_blocks_processing_without_overwrite(self):
        cell = Cell(role="wire", memory="right", input=(1, 0, 0), output=(0, "_", "_"))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "blocked-output")
        self.assertEqual(result.cell.output, (0, "_", "_"))
        self.assertEqual(result.cell.input, (1, 0, 0))

    def test_empty_input_pulls_upstream_then_routes_and_clears_upstream(self):
        cell = Cell(role="wire", memory="left", upstream=(0, 1, 1))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "routed")
        self.assertEqual(result.cell.upstream, EMPTY)
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, (1, 1, 0))

    def test_stem_init_reconfigures_fixed_cell_to_stem(self):
        cell = Cell(role="proc", memory="left", input=("_", "si", "_"))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "stem-init")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)

    def test_malformed_input_is_rejected_and_cleared(self):
        cell = Cell(role="wire", memory="right", input=(1, "si", 0))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)

    def test_invalid_fixed_role_is_rejected(self):
        with self.assertRaises(ValueError):
            step_fixed_cell(Cell(role="stem", memory="right"))

    def test_invalid_memory_is_rejected(self):
        with self.assertRaises(ValueError):
            Cell(role="wire", memory="sideways")


if __name__ == "__main__":
    unittest.main()
