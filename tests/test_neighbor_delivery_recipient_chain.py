import unittest

from autarkic_systems.transition_chains import (
    execute_neighbor_delivery_recipient_chain,
)
from autarkic_systems.universal_cell import Cell


EMPTY = ("_", "_", "_")


class NeighborDeliveryRecipientChainTests(unittest.TestCase):
    def test_neighbor_b_proc_left_delivery_is_consumed_by_empty_fixed_recipient(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)

        self.assertTrue(chain.accepted, chain.detail)
        self.assertEqual(chain.status, "neighbor-delivery-consumed")
        self.assertEqual(
            chain.sender_result.status,
            "stem-command-buffer-neighbor-delivered",
        )
        self.assertIsNotNone(chain.recipient_before)
        self.assertEqual(chain.recipient_before.upstream, ("_", "proc-l-init", "_"))
        self.assertIsNotNone(chain.recipient_result)
        self.assertEqual(
            chain.recipient_result.status,
            "recipient-init-command-message-processed",
        )
        self.assertEqual(chain.recipient_result.cell.role, "proc")
        self.assertEqual(chain.recipient_result.cell.memory, "left")
        self.assertEqual(chain.recipient_result.cell.upstream, EMPTY)
        self.assertEqual(chain.recipient_result.cell.input, EMPTY)
        self.assertEqual(chain.recipient_result.cell.output, EMPTY)

    def test_sender_must_complete_neighbor_delivery(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(1, 0, 0),
            buffer=(0, 0, 0, 0),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)

        self.assertFalse(chain.accepted)
        self.assertEqual(chain.status, "sender-not-delivered")
        self.assertEqual(chain.sender_result.status, "stem-buffer-appended")
        self.assertIsNone(chain.recipient_before)
        self.assertIsNone(chain.recipient_result)
        self.assertIn("stem-command-buffer-neighbor-delivered", chain.detail)

    def test_recipient_must_be_empty_before_delivery_is_installed(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(
            role="wire",
            memory="right",
            upstream=(0, "_", "_"),
        )

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)

        self.assertFalse(chain.accepted)
        self.assertEqual(chain.status, "recipient-not-ready")
        self.assertIsNone(chain.recipient_before)
        self.assertIsNone(chain.recipient_result)
        self.assertIn("recipient input/upstream must be empty", chain.detail)

    def test_delivered_non_init_command_remains_unconsumed_boundary(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)

        self.assertFalse(chain.accepted)
        self.assertEqual(chain.status, "recipient-not-consumed")
        self.assertIsNotNone(chain.recipient_before)
        self.assertEqual(chain.recipient_before.upstream, ("_", "_", "write-buf-one"))
        self.assertIsNotNone(chain.recipient_result)
        self.assertEqual(chain.recipient_result.status, "rejected-input")
        self.assertEqual(chain.recipient_result.cell.role, "wire")
        self.assertEqual(chain.recipient_result.cell.memory, "right")
        self.assertIn("recipient-init-command-message-processed", chain.detail)


if __name__ == "__main__":
    unittest.main()
