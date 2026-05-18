import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from autarkic_systems.network_sequence_svg import (
    POST_HANDOFF_SIGNAL_SEQUENCE_SVG_ARTIFACT,
    SVG_NAMESPACE,
    render_network_sequence_svg,
    validate_network_sequence_svg,
)
from autarkic_systems.network_sequence_trace import load_network_sequence_trace


TRACE_ARTIFACT = Path("schematics/sequences/post_handoff_signal_sequence_trace.json")


class PostHandoffSequenceSvgTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_network_sequence_trace(TRACE_ARTIFACT)
        self.svg_text = render_network_sequence_svg(self.trace)

    def test_svg_is_nonblank_xml_with_sequence_metadata(self):
        self.assertGreater(len(self.svg_text), 1000)

        root = ET.fromstring(self.svg_text)

        self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
        self.assertEqual(root.attrib["data-artifact-id"], self.trace.artifact_id)
        self.assertEqual(
            root.attrib["data-sequence-claim-id"],
            self.trace.sequence_claim_id,
        )
        self.assertEqual(root.attrib["data-sequence-helper"], self.trace.sequence_helper)

    def test_svg_records_delivery_followup_and_recipient_state(self):
        self.assertIn("status: post-handoff-signal-routed", self.svg_text)
        self.assertIn("delivery status: neighbor-delivery-consumed", self.svg_text)
        self.assertIn("delivered tuple: [_, proc-l-init, _]", self.svg_text)
        self.assertIn("follow-up input: [1, 0, 0]", self.svg_text)
        self.assertIn("follow-up status: routed", self.svg_text)
        self.assertIn("before follow-up role: proc", self.svg_text)
        self.assertIn("before follow-up memory: left", self.svg_text)
        self.assertIn("after follow-up memory: right", self.svg_text)
        self.assertIn("after follow-up output: [0, 0, 1]", self.svg_text)

    def test_svg_records_followup_signal_flow(self):
        root = ET.fromstring(self.svg_text)
        visible_text = "\n".join(root.itertext())

        for flow in self.trace.routed_signal_flow:
            with self.subTest(flow=flow):
                self.assertIn(flow, visible_text)

    def test_committed_sequence_svg_matches_renderer_output(self):
        committed = POST_HANDOFF_SIGNAL_SEQUENCE_SVG_ARTIFACT.read_text(
            encoding="utf-8",
        )

        self.assertEqual(committed, self.svg_text)

    def test_sequence_svg_validator_accepts_committed_svg(self):
        results = validate_network_sequence_svg(
            self.trace,
            svg_text=POST_HANDOFF_SIGNAL_SEQUENCE_SVG_ARTIFACT.read_text(
                encoding="utf-8",
            ),
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "xml",
                "metadata",
                "rendered-svg",
                "sequence-labels",
                "followup-flow",
            },
        )

    def test_sequence_svg_validator_rejects_drifted_followup_text(self):
        drifted = self.svg_text.replace(
            "follow-up status: routed",
            "follow-up status: rejected-input",
        )

        results = validate_network_sequence_svg(self.trace, svg_text=drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "rendered-svg"
                and "does not match" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
