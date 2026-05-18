import contextlib
import io
import json
import subprocess
import sys
import unittest

from autarkic_systems.network_witness import (
    execute_two_cell_neighbor_delivery_witness,
    format_two_cell_network_witness,
    run_network_witness_cli,
    two_cell_network_witness_payload,
)
from autarkic_systems.universal_cell import Cell


EMPTY = ("_", "_", "_")


class TwoCellNetworkWitnessTests(unittest.TestCase):
    def test_consumed_init_delivery_records_sender_handoff_and_recipient_events(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_two_cell_neighbor_delivery_witness(
            sender,
            recipient,
            sender_id="sender-a",
            recipient_id="recipient-b",
        )

        self.assertTrue(witness.accepted, witness.detail)
        self.assertEqual(witness.status, "neighbor-delivery-consumed")
        self.assertEqual(witness.delivered_tuple, ("_", "proc-l-init", "_"))
        self.assertEqual(
            [(event.phase, event.actor, event.status) for event in witness.events],
            [
                (
                    "sender-step",
                    "sender-a",
                    "stem-command-buffer-neighbor-delivered",
                ),
                ("handoff", "sender-a->recipient-b", "installed-upstream"),
                (
                    "recipient-step",
                    "recipient-b",
                    "recipient-init-command-message-processed",
                ),
            ],
        )
        self.assertIsNotNone(witness.recipient_before_step)
        self.assertEqual(witness.recipient_before_step.upstream, ("_", "proc-l-init", "_"))
        self.assertEqual(witness.recipient_after.role, "proc")
        self.assertEqual(witness.recipient_after.memory, "left")
        self.assertEqual(witness.recipient_after.upstream, EMPTY)
        self.assertEqual(witness.recipient_after.input, EMPTY)

    def test_write_buffer_delivery_records_append_without_new_command_semantics(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_two_cell_neighbor_delivery_witness(sender, recipient)

        self.assertTrue(witness.accepted, witness.detail)
        self.assertEqual(witness.delivered_tuple, ("_", "_", "write-buf-one"))
        self.assertIsNotNone(witness.recipient_result)
        self.assertEqual(
            witness.recipient_result.status,
            "recipient-write-buffer-command-message-appended",
        )
        self.assertEqual(witness.recipient_after.buffer, (1,))

    def test_standard_signal_delivery_records_existing_rejection_boundary(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 0, 0),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_two_cell_neighbor_delivery_witness(sender, recipient)

        self.assertFalse(witness.accepted)
        self.assertEqual(witness.status, "recipient-not-consumed")
        self.assertEqual(witness.delivered_tuple, ("_", "_", "standard-signal"))
        self.assertIsNotNone(witness.recipient_result)
        self.assertEqual(witness.recipient_result.status, "rejected-input")
        self.assertEqual(witness.recipient_after.upstream, EMPTY)
        self.assertEqual(witness.recipient_after.input, EMPTY)
        self.assertIn("recipient must produce", witness.detail)

    def test_recipient_not_ready_blocks_delivery_installation_and_recipient_step(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right", upstream=(0, "_", "_"))

        witness = execute_two_cell_neighbor_delivery_witness(sender, recipient)

        self.assertFalse(witness.accepted)
        self.assertEqual(witness.status, "recipient-not-ready")
        self.assertIsNone(witness.delivered_tuple)
        self.assertIsNone(witness.recipient_before_step)
        self.assertIsNone(witness.recipient_result)
        self.assertEqual(witness.recipient_after, recipient)
        self.assertEqual(
            [(event.phase, event.actor, event.status) for event in witness.events],
            [
                ("sender-step", "sender", "stem-command-buffer-neighbor-delivered"),
                ("handoff-blocked", "sender->recipient", "recipient-not-ready"),
            ],
        )

    def test_sender_not_delivered_records_sender_only_failure(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(1, 0, 0),
            buffer=(0, 0, 0, 0),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_two_cell_neighbor_delivery_witness(sender, recipient)

        self.assertFalse(witness.accepted)
        self.assertEqual(witness.status, "sender-not-delivered")
        self.assertIsNone(witness.delivered_tuple)
        self.assertEqual(witness.sender_after.buffer, (0, 0, 0, 0, 0))
        self.assertEqual(witness.recipient_after, recipient)
        self.assertEqual(
            [(event.phase, event.actor, event.status) for event in witness.events],
            [("sender-step", "sender", "stem-buffer-appended")],
        )

    def test_payload_records_events_delivered_tuple_and_final_cells(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        )
        recipient = Cell(role="wire", memory="right")

        payload = two_cell_network_witness_payload(
            execute_two_cell_neighbor_delivery_witness(sender, recipient)
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "neighbor-delivery-consumed")
        self.assertEqual(payload["delivered_tuple"], ["_", "_", "write-buf-one"])
        self.assertEqual(payload["sender"]["after_step"]["output"], ["_", "_", "write-buf-one"])
        self.assertEqual(payload["recipient"]["after"]["buffer"], [1])
        self.assertEqual(
            [event["phase"] for event in payload["events"]],
            ["sender-step", "handoff", "recipient-step"],
        )

    def test_text_report_summarizes_handoff_and_final_recipient(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        report = format_two_cell_network_witness(
            execute_two_cell_neighbor_delivery_witness(sender, recipient)
        )

        self.assertIn("Two-cell network witness: neighbor-delivery-consumed", report)
        self.assertIn("Accepted: yes", report)
        self.assertIn("Delivered tuple: _, proc-l-init, _", report)
        self.assertIn("sender-step sender: stem-command-buffer-neighbor-delivered", report)
        self.assertIn("recipient-step recipient: recipient-init-command-message-processed", report)
        self.assertIn("Recipient after: role=proc memory=left", report)

    def test_cli_emits_json_for_write_buffer_fixture(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_witness",
                "--case",
                "write-buffer-one-consumed",
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["delivered_tuple"], ["_", "_", "write-buf-one"])
        self.assertEqual(payload["recipient"]["after"]["buffer"], [1])

    def test_cli_returns_failure_for_rejection_fixture(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_witness_cli(
                ["--case", "standard-signal-rejected"]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("Two-cell network witness: recipient-not-consumed", output)
        self.assertIn("Accepted: no", output)

    def test_cli_emits_json_for_recipient_not_ready_fixture(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_witness",
                "--case",
                "recipient-not-ready",
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["status"], "recipient-not-ready")
        self.assertIsNone(payload["delivered_tuple"])
        self.assertIsNone(payload["recipient"]["before_step"])
        self.assertEqual(
            [event["phase"] for event in payload["events"]],
            ["sender-step", "handoff-blocked"],
        )

    def test_cli_emits_text_for_sender_not_delivered_fixture(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_witness_cli(["--case", "sender-not-delivered"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("Two-cell network witness: sender-not-delivered", output)
        self.assertIn("Accepted: no", output)
        self.assertIn("Delivered tuple: none", output)
        self.assertIn("sender-step sender: stem-buffer-appended", output)
        self.assertNotIn("recipient-step recipient:", output)


if __name__ == "__main__":
    unittest.main()
