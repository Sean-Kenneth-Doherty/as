import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from autarkic_systems.schematic_trace import load_schematic_trace
from autarkic_systems.schematic_svg import (
    SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT,
    SVG_NAMESPACE,
    render_schematic_svg,
    validate_schematic_svg,
)


TRACE_ARTIFACT = Path("schematics/self_mailbox_unsupported_trace.json")


class SelfMailboxUnsupportedSvgTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(TRACE_ARTIFACT)
        self.svg_text = render_schematic_svg(self.trace)

    def test_svg_is_nonblank_xml_with_unsupported_trace_metadata(self):
        self.assertGreater(len(self.svg_text), 1000)

        root = ET.fromstring(self.svg_text)

        self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
        self.assertEqual(root.attrib["data-artifact-id"], self.trace.artifact_id)
        self.assertEqual(root.attrib["data-trace-id"], self.trace.trace.trace_id)

    def test_svg_labels_unsupported_ports_from_trace(self):
        root = ET.fromstring(self.svg_text)
        ports = root.findall(f".//{{{SVG_NAMESPACE}}}g[@class='port']")

        self.assertEqual(len(ports), 3)
        self.assertEqual(
            {port.attrib["data-port-id"] for port in ports},
            {port.port_id for port in self.trace.schematic.ports},
        )
        self.assertEqual(
            {port.attrib["data-orientation"] for port in ports},
            {port.orientation for port in self.trace.schematic.ports},
        )

    def test_svg_records_unsupported_mailbox_preservation_and_flow(self):
        self.assertIn("role: stem", self.svg_text)
        self.assertIn("status: self-mailbox-unsupported", self.svg_text)
        self.assertIn("self_mailbox before: standard-signal", self.svg_text)
        self.assertIn("self_mailbox after: standard-signal", self.svg_text)
        self.assertIn("control before: [1, 0, 0]", self.svg_text)
        self.assertIn("control after: [1, 0, 0]", self.svg_text)
        self.assertIn("buffer before: [0]", self.svg_text)
        self.assertIn("buffer after: [0]", self.svg_text)
        self.assertIn("transition: step_stem_cell", self.svg_text)
        root = ET.fromstring(self.svg_text)
        visible_text = "\n".join(root.itertext())
        for flow in self.trace.trace.routed_signal_flow:
            with self.subTest(flow=flow):
                self.assertIn(flow, visible_text)

    def test_svg_exposes_unsupported_interpretive_layer_ids(self):
        root = ET.fromstring(self.svg_text)
        layers = root.findall(f".//{{{SVG_NAMESPACE}}}g[@class='interpretive-layer']")

        self.assertEqual(
            {layer.attrib["data-layer-id"] for layer in layers},
            {layer.layer_id for layer in self.trace.schematic.layers},
        )

    def test_committed_unsupported_svg_matches_renderer_output(self):
        committed = SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT.read_text(encoding="utf-8")

        self.assertEqual(committed, self.svg_text)

    def test_unsupported_svg_validator_accepts_committed_svg(self):
        results = validate_schematic_svg(
            self.trace,
            svg_text=SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT.read_text(encoding="utf-8"),
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_unsupported_svg_validator_rejects_drifted_mailbox(self):
        drifted = self.svg_text.replace(
            "self_mailbox after: standard-signal",
            "self_mailbox after: _",
        )

        results = validate_schematic_svg(self.trace, svg_text=drifted)

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
