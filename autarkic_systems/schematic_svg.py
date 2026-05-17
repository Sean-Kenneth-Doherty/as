"""SVG rendering for structured PRC schematic traces.

The renderer keeps the JSON schematic trace as the source of truth. Checked-in
SVG artifacts must match this module's output exactly, so visual artifacts
cannot silently drift away from the executable traces.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET

from autarkic_systems.schematic_trace import (
    COMMAND_BUFFER_UNSUPPORTED_TRACE_ARTIFACT_ID,
    NEIGHBOR_COMMAND_BUFFER_DELIVERY_TRACE_ARTIFACT_ID,
    SchematicPort,
    SingleNodeSchematicTrace,
)


SVG_ARTIFACT = Path("schematics/single_node_triangular_rlem_trace.svg")
PROCESSOR_SVG_ARTIFACT = Path("schematics/processor_memory_toggle_trace.svg")
STEM_AUTOMAIL_SVG_ARTIFACT = Path(
    "schematics/stem_automail_reconfiguration_trace.svg"
)
STEM_BUFFER_SVG_ARTIFACT = Path("schematics/stem_buffer_accumulation_trace.svg")
SELF_MAILBOX_INIT_SVG_ARTIFACT = Path("schematics/self_mailbox_init_trace.svg")
SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT = Path(
    "schematics/self_mailbox_unsupported_trace.svg"
)
SELF_COMMAND_BUFFER_INIT_SVG_ARTIFACT = Path(
    "schematics/self_command_buffer_init_trace.svg"
)
COMMAND_BUFFER_UNSUPPORTED_SVG_ARTIFACT = Path(
    "schematics/command_buffer_unsupported_trace.svg"
)
NEIGHBOR_COMMAND_BUFFER_DELIVERY_SVG_ARTIFACT = Path(
    "schematics/neighbor_command_buffer_delivery_trace.svg"
)
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

PORT_LAYOUT = {
    "north": {
        "cx": 480,
        "cy": 112,
        "label_x": 480,
        "label_y": 72,
        "anchor": "middle",
    },
    "east": {
        "cx": 704,
        "cy": 432,
        "label_x": 756,
        "label_y": 448,
        "anchor": "start",
    },
    "west": {
        "cx": 256,
        "cy": 432,
        "label_x": 204,
        "label_y": 448,
        "anchor": "end",
    },
}


@dataclass(frozen=True)
class SchematicSvgValidation:
    """One validation result for the rendered schematic SVG."""

    subject: str
    accepted: bool
    detail: str


def render_single_node_schematic_svg(trace: SingleNodeSchematicTrace) -> str:
    """Render the original ADR-0017 SVG view."""

    return render_schematic_svg(trace)


def render_schematic_svg(trace: SingleNodeSchematicTrace) -> str:
    """Render one SVG view from a structured schematic trace."""

    before = trace.trace.before_cell
    after = trace.trace.expected_after_cell

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="{SVG_NAMESPACE}" width="960" height="640" '
            'viewBox="0 0 960 640" role="img" aria-labelledby="title desc" '
            f'data-artifact-id="{_attr(trace.artifact_id)}" '
            f'data-trace-id="{_attr(trace.trace.trace_id)}">'
        ),
        f"  <title id=\"title\">{_text(trace.schematic.node_id)}</title>",
        (
            "  <desc id=\"desc\">Generated from "
            f"{_text(trace.artifact_id)}; trace {_text(trace.trace.trace_id)}."
            "</desc>"
        ),
        "  <style>",
        "    .node { fill: #f7f4ea; stroke: #1e3a3a; stroke-width: 4; }",
        "    .port-dot { fill: #f06449; stroke: #1e3a3a; stroke-width: 3; }",
        "    .route { fill: none; stroke: #2f80ed; stroke-width: 4; marker-end: url(#arrow); }",
        "    .label { fill: #162020; font: 700 18px sans-serif; }",
        "    .small { fill: #162020; font: 14px monospace; }",
        "    .layer { fill: #fffdf6; stroke: #8a8f98; stroke-width: 1.5; }",
        "    .layer-title { fill: #162020; font: 700 13px sans-serif; }",
        "    .layer-body { fill: #384444; font: 12px sans-serif; }",
        "  </style>",
        "  <defs>",
        '    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">',
        '      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2f80ed" />',
        "    </marker>",
        "  </defs>",
        '  <rect x="24" y="24" width="912" height="592" rx="10" fill="#fbfaf5" '
        'stroke="#d0d5dd" />',
        '  <g class="schematic-node" data-node-id="'
        f'{_attr(trace.schematic.node_id)}">',
        '    <polygon class="node" points="480,112 704,432 256,432" />',
        "    <path class=\"route\" d=\"M 628 404 C 560 332 504 240 480 112\" />",
        "    <path class=\"route\" d=\"M 480 112 C 416 232 336 336 256 432\" />",
        "    <path class=\"route\" d=\"M 256 432 C 386 476 574 476 704 432\" />",
        f"    <text class=\"label\" x=\"480\" y=\"324\" text-anchor=\"middle\">memory: {_text(trace.schematic.memory_direction)}</text>",
        f"    <text class=\"small\" x=\"480\" y=\"350\" text-anchor=\"middle\">role: {_text(before['role'])}</text>",
        f"    <text class=\"small\" x=\"480\" y=\"374\" text-anchor=\"middle\">transition: {_text(trace.trace.transition_function)}</text>",
    ]

    for port in trace.schematic.ports:
        lines.extend(_render_port(port))

    lines.extend(
        [
            "  </g>",
            '  <g class="trace-summary" data-trace-id="'
            f'{_attr(trace.trace.trace_id)}">',
            f"    <text class=\"label\" x=\"52\" y=\"72\">trace: {_text(trace.trace.trace_id)}</text>",
            f"    <text class=\"small\" x=\"52\" y=\"100\">status: {_text(trace.trace.expected_status)}</text>",
            f"    <text class=\"small\" x=\"52\" y=\"124\">input: {_text(_cell_field(trace.trace.before_cell, 'input'))}</text>",
            f"    <text class=\"small\" x=\"52\" y=\"148\">output: {_text(_cell_field(trace.trace.expected_after_cell, 'output'))}</text>",
            f"    <text class=\"small\" x=\"52\" y=\"172\">memory before: {_text(before['memory'])}</text>",
            f"    <text class=\"small\" x=\"52\" y=\"196\">memory after: {_text(after['memory'])}</text>",
        ]
    )
    next_y = 232
    if _shows_neighbor_command_buffer_delivery(trace):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">role after: {_text(after['role'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">self_mailbox before: {_text(before['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">self_mailbox after: {_text(after['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"292\">control before: {_text(_cell_field(before, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"316\">buffer before: {_text(_cell_field(before, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"340\">input after: {_text(_cell_field(after, 'input'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"364\">output after: {_text(_cell_field(after, 'output'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"388\">control after: {_text(_cell_field(after, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"412\">buffer after: {_text(_cell_field(after, 'buffer'))}</text>",
            ]
        )
        next_y = 448
    elif _shows_command_buffer_unsupported(trace):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">role after: {_text(after['role'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">self_mailbox before: {_text(before['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">self_mailbox after: {_text(after['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"292\">control before: {_text(_cell_field(before, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"316\">buffer before: {_text(_cell_field(before, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"340\">input after: {_text(_cell_field(after, 'input'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"364\">control after: {_text(_cell_field(after, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"388\">buffer after: {_text(_cell_field(after, 'buffer'))}</text>",
            ]
        )
        next_y = 424
    elif _shows_self_command_buffer_init(trace):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">role after: {_text(after['role'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">self_mailbox before: {_text(before['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">self_mailbox after: {_text(after['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"292\">control before: {_text(_cell_field(before, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"316\">buffer before: {_text(_cell_field(before, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"340\">input after: {_text(_cell_field(after, 'input'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"364\">control after: {_text(_cell_field(after, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"388\">buffer after: {_text(_cell_field(after, 'buffer'))}</text>",
            ]
        )
        next_y = 424
    elif _shows_self_mailbox_unsupported(trace):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">self_mailbox before: {_text(before['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">self_mailbox after: {_text(after['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">control before: {_text(_cell_field(before, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"292\">control after: {_text(_cell_field(after, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"316\">buffer before: {_text(_cell_field(before, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"340\">buffer after: {_text(_cell_field(after, 'buffer'))}</text>",
            ]
        )
        next_y = 376
    elif _shows_self_mailbox_init(before, after):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">role after: {_text(after['role'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">self_mailbox before: {_text(before['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">self_mailbox after: {_text(after['self_mailbox'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"292\">control before: {_text(_cell_field(before, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"316\">buffer before: {_text(_cell_field(before, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"340\">control after: {_text(_cell_field(after, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"364\">buffer after: {_text(_cell_field(after, 'buffer'))}</text>",
            ]
        )
        next_y = 400
    elif _shows_reconfiguration(before, after):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">role after: {_text(after['role'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">automail before: {_text(before['automail'])}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">automail after: {_text(after['automail'])}</text>",
            ]
        )
        next_y = 304
    elif _shows_buffer_accumulation(before, after):
        lines.extend(
            [
                f"    <text class=\"small\" x=\"52\" y=\"220\">control before: {_text(_cell_field(before, 'control'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"244\">buffer before: {_text(_cell_field(before, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"268\">buffer after: {_text(_cell_field(after, 'buffer'))}</text>",
                f"    <text class=\"small\" x=\"52\" y=\"292\">input after: {_text(_cell_field(after, 'input'))}</text>",
            ]
        )
        next_y = 328
    lines.append(f'    <text class="small" x="52" y="{next_y}">routed signal flow</text>')
    for index, flow in enumerate(trace.trace.routed_signal_flow):
        y = next_y + 26 + index * 24
        lines.append(f"    <text class=\"small\" x=\"72\" y=\"{y}\">{_text(flow)}</text>")
    lines.append("  </g>")

    lines.append('  <g class="interpretive-layers">')
    for index, layer in enumerate(trace.schematic.layers):
        lines.extend(_render_layer(index, layer.layer_id, layer.summary))
    lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def validate_single_node_schematic_svg(
    trace: SingleNodeSchematicTrace,
    *,
    svg_text: str,
) -> list[SchematicSvgValidation]:
    """Validate the original ADR-0017 SVG view."""

    return validate_schematic_svg(trace, svg_text=svg_text)


def validate_schematic_svg(
    trace: SingleNodeSchematicTrace,
    *,
    svg_text: str,
) -> list[SchematicSvgValidation]:
    """Validate that an SVG is parseable and exactly matches renderer output."""

    results: list[SchematicSvgValidation] = []
    expected = render_schematic_svg(trace)

    if svg_text != expected:
        results.append(_rejected("rendered-svg", "SVG does not match renderer output"))
    else:
        results.append(_accepted("rendered-svg", "SVG matches renderer output"))

    try:
        root = ET.fromstring(svg_text)
    except ET.ParseError as exc:
        return results + [_rejected("xml", f"SVG is not parseable XML: {exc}")]

    if root.tag != f"{{{SVG_NAMESPACE}}}svg":
        results.append(_rejected("svg", "root element is not SVG"))
    else:
        results.append(_accepted("svg", "root element is SVG"))

    if root.attrib.get("data-artifact-id") != trace.artifact_id:
        results.append(_rejected("data-artifact-id", "artifact id missing or wrong"))
    else:
        results.append(_accepted("data-artifact-id", "artifact id present"))

    if root.attrib.get("data-trace-id") != trace.trace.trace_id:
        results.append(_rejected("data-trace-id", "trace id missing or wrong"))
    else:
        results.append(_accepted("data-trace-id", "trace id present"))

    port_groups = root.findall(f".//{{{SVG_NAMESPACE}}}g[@class='port']")
    if len(port_groups) != len(trace.schematic.ports):
        results.append(_rejected("ports", "port group count does not match trace"))
    else:
        results.append(_accepted("ports", "port group count matches trace"))

    layer_groups = root.findall(
        f".//{{{SVG_NAMESPACE}}}g[@class='interpretive-layer']"
    )
    if len(layer_groups) != len(trace.schematic.layers):
        results.append(_rejected("layers", "layer group count does not match trace"))
    else:
        results.append(_accepted("layers", "layer group count matches trace"))

    return results


def _render_port(port: SchematicPort) -> list[str]:
    orientation = port.orientation
    layout = PORT_LAYOUT[orientation]
    return [
        (
            f'    <g class="port" data-port-id="{_attr(port.port_id)}" '
            f'data-orientation="{_attr(orientation)}" '
            f'data-signal-index="{port.signal_index}">'
        ),
        f'      <circle class="port-dot" cx="{layout["cx"]}" cy="{layout["cy"]}" r="14" />',
        (
            f'      <text class="label" x="{layout["label_x"]}" '
            f'y="{layout["label_y"]}" text-anchor="{layout["anchor"]}">'
            f'{_text(port.label)} p{port.signal_index}</text>'
        ),
        f"      <title>{_text(port.summary)}</title>",
        "    </g>",
    ]


def _render_layer(index: int, layer_id: str, summary: str) -> list[str]:
    x = 560
    y = 72 + index * 88
    return [
        (
            f'    <g class="interpretive-layer" data-layer-id="{_attr(layer_id)}">'
        ),
        f'      <rect class="layer" x="{x}" y="{y}" width="348" height="68" rx="6" />',
        f'      <text class="layer-title" x="{x + 16}" y="{y + 24}">{_text(layer_id)}</text>',
        f'      <text class="layer-body" x="{x + 16}" y="{y + 48}">{_text(_shorten(summary, 54))}</text>',
        "    </g>",
    ]


def _cell_field(cell: dict[str, object], field: str) -> str:
    value = cell[field]
    if isinstance(value, list):
        return "[" + ", ".join(str(item) for item in value) + "]"
    return str(value)


def _shows_reconfiguration(
    before: dict[str, object],
    after: dict[str, object],
) -> bool:
    """Return true when a trace changes role or consumes an automail marker."""

    return before["role"] != after["role"] or before["automail"] != after["automail"]


def _shows_self_mailbox_init(
    before: dict[str, object],
    after: dict[str, object],
) -> bool:
    """Return true for traces that consume a self-mailbox command."""

    return before["self_mailbox"] != "_" and after["self_mailbox"] == "_"


def _shows_self_mailbox_unsupported(trace: SingleNodeSchematicTrace) -> bool:
    """Return true for traces that preserve an unsupported mailbox command."""

    before = trace.trace.before_cell
    after = trace.trace.expected_after_cell
    return (
        trace.trace.expected_status == "self-mailbox-unsupported"
        and before["self_mailbox"] != "_"
        and before["self_mailbox"] == after["self_mailbox"]
    )


def _shows_self_command_buffer_init(trace: SingleNodeSchematicTrace) -> bool:
    """Return true for traces that consume a completed self-init buffer."""

    return trace.trace.expected_status == "stem-command-buffer-self-processed"


def _shows_command_buffer_unsupported(trace: SingleNodeSchematicTrace) -> bool:
    """Return true for traces that preserve an unsupported command buffer."""

    return trace.artifact_id == COMMAND_BUFFER_UNSUPPORTED_TRACE_ARTIFACT_ID


def _shows_neighbor_command_buffer_delivery(trace: SingleNodeSchematicTrace) -> bool:
    """Return true for traces that deliver a completed neighbor command buffer."""

    return trace.artifact_id == NEIGHBOR_COMMAND_BUFFER_DELIVERY_TRACE_ARTIFACT_ID


def _shows_buffer_accumulation(
    before: dict[str, object],
    after: dict[str, object],
) -> bool:
    """Return true when a trace changes the stem command buffer."""

    return before["buffer"] != after["buffer"]


def _shorten(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _text(value: object) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _attr(value: object) -> str:
    return _text(value).replace('"', "&quot;")


def _accepted(subject: str, detail: str) -> SchematicSvgValidation:
    return SchematicSvgValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> SchematicSvgValidation:
    return SchematicSvgValidation(subject=subject, accepted=False, detail=detail)
