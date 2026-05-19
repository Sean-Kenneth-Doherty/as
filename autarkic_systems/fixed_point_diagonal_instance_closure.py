"""Finite closure evidence for the current AS fixed-point diagonal instance.

This module checks the first fixed-point construction case against executable
syntax facts. It derives the current diagonal instance, verifies it is closed
and codebook-stable, and checks that the bridge target names the same finite
surface. It is not a substitution representability proof, bridge equality
proof, fixed-point equation proof, or self-consistency theorem.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    DiagonalConstructionTarget,
    build_diagonal_instance_code,
    build_diagonal_seed_node,
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import (
    FixedPointTarget,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.fixed_point_equation_bridge import (
    FixedPointEquationBridgeObservation,
    FixedPointEquationBridgeTarget,
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.formal_code import (
    FormalCodebook,
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import free_variables, substitute_node


DEFAULT_CLOSURE = Path("claims/fixed_point_diagonal_instance_closure.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SOURCE_KINDS = ("diagonal-instance",)
REQUIRED_FUTURE_WORK = (
    "substitution-representability-proof",
    "substitution-graph-correctness-proof",
    "bridge-equality-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureManifest:
    """Loaded manifest for finite diagonal-instance closure evidence."""

    path: Path
    schema_version: int
    closure_set_id: str
    reviewed_at: str
    purpose: str
    formal_language_path: str
    codebook_path: str
    fixed_point_targets_path: str
    diagonal_construction_targets_path: str
    fixed_point_equation_bridge_targets_path: str
    expected_closure_count: int
    expected_diagonal_instance_code_length: int
    expected_diagonal_instance_code_prefix: tuple[int, ...]
    required_source_kinds: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureValidation:
    """One validation result for diagonal-instance closure evidence."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosure:
    """One finite checked diagonal-instance closure point."""

    closure_id: str
    source_kind: str
    target_id: str
    construction_id: str
    bridge_id: str
    template_variable: str
    seed_code_length: int
    diagonal_instance_code_length: int
    diagonal_instance_code_prefix: tuple[int, ...]
    diagonal_instance_free_variables: tuple[str, ...]
    diagonal_instance_closed: bool
    codebook_roundtrip: bool
    target_skeleton_preserved: bool
    diagonal_slot_is_quoted_seed_substitution: bool
    bridge_matches_diagonal_instance: bool
    bridge_target_closed: bool


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureReport:
    """Validation report over finite diagonal-instance closure evidence."""

    manifest: FixedPointDiagonalInstanceClosureManifest
    formal_language_path: Path
    codebook_path: Path
    fixed_point_targets_path: Path
    diagonal_construction_targets_path: Path
    fixed_point_equation_bridge_targets_path: Path
    willard_map_path: Path
    results: tuple[FixedPointDiagonalInstanceClosureValidation, ...]
    closures: tuple[FixedPointDiagonalInstanceClosure, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every closure validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def closure_count(self) -> int:
        """Return the number of checked closure points."""

        return len(self.closures)

    @property
    def source_kind_counts(self) -> dict[str, int]:
        """Return observed closure counts grouped by source kind."""

        counts = {source_kind: 0 for source_kind in REQUIRED_SOURCE_KINDS}
        for closure in self.closures:
            counts[closure.source_kind] = counts.get(closure.source_kind, 0) + 1
        return counts

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


def load_fixed_point_diagonal_instance_closure(
    path: Path | str = DEFAULT_CLOSURE,
) -> FixedPointDiagonalInstanceClosureManifest:
    """Load the diagonal-instance closure manifest from JSON."""

    closure_path = Path(path)
    data = json.loads(closure_path.read_text(encoding="utf-8"))
    return FixedPointDiagonalInstanceClosureManifest(
        path=closure_path,
        schema_version=_required_int(data, "schema_version"),
        closure_set_id=_required_text(data, "closure_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        formal_language_path=_required_text(data, "formal_language_path"),
        codebook_path=_required_text(data, "codebook_path"),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        diagonal_construction_targets_path=_required_text(
            data,
            "diagonal_construction_targets_path",
        ),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        expected_closure_count=_required_int(data, "expected_closure_count"),
        expected_diagonal_instance_code_length=_required_int(
            data,
            "expected_diagonal_instance_code_length",
        ),
        expected_diagonal_instance_code_prefix=tuple(
            _required_int_list(data, "expected_diagonal_instance_code_prefix")
        ),
        required_source_kinds=tuple(_required_text_list(data, "required_source_kinds")),
        required_future_work=tuple(_required_text_list(data, "required_future_work")),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_diagonal_instance_closure(
    manifest: FixedPointDiagonalInstanceClosureManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDiagonalInstanceClosureReport:
    """Validate finite diagonal-instance closure evidence."""

    checked_willard_map_path = Path(willard_map_path)
    checked_language_path = Path(manifest.formal_language_path)
    checked_codebook_path = Path(manifest.codebook_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_bridge_path = Path(manifest.fixed_point_equation_bridge_targets_path)

    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_targets,
        checked_willard_map_path,
        checked_language_path,
    )
    diagonal_targets = load_diagonal_construction_targets(checked_diagonal_path)
    diagonal_report = validate_diagonal_construction_targets(
        diagonal_targets,
        checked_language_path,
        checked_willard_map_path,
    )
    bridge_targets = load_fixed_point_equation_bridge_targets(checked_bridge_path)
    bridge_report = validate_fixed_point_equation_bridge_targets(
        bridge_targets,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[FixedPointDiagonalInstanceClosureValidation] = [
        _accepted("manifest", "loaded diagonal-instance closure manifest")
    ]
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            codebook_report,
            fixed_point_report,
            diagonal_report,
            bridge_report,
        )
    )
    closures: tuple[FixedPointDiagonalInstanceClosure, ...] = ()
    if (
        codebook_report.accepted
        and fixed_point_report.accepted
        and diagonal_report.accepted
        and bridge_report.accepted
    ):
        closure_results, closures = _validate_closures(
            manifest,
            codebook,
            fixed_point_targets.targets,
            diagonal_targets.constructions,
            bridge_targets.bridges,
            bridge_report.observations,
            checked_diagonal_path,
            checked_fixed_point_path,
            checked_bridge_path,
        )
        results.extend(closure_results)
    else:
        results.append(
            _rejected(
                "closures.dependencies",
                "accepted dependencies are required before closure checks",
            )
        )

    return FixedPointDiagonalInstanceClosureReport(
        manifest=manifest,
        formal_language_path=checked_language_path,
        codebook_path=checked_codebook_path,
        fixed_point_targets_path=checked_fixed_point_path,
        diagonal_construction_targets_path=checked_diagonal_path,
        fixed_point_equation_bridge_targets_path=checked_bridge_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        closures=closures,
    )


def fixed_point_diagonal_instance_closure_payload(
    report: FixedPointDiagonalInstanceClosureReport,
) -> dict[str, Any]:
    """Return a JSON-ready diagonal-instance closure payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "closure_manifest": str(report.manifest.path),
        "closure_set_id": report.manifest.closure_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "formal_language_path": str(report.formal_language_path),
        "codebook_path": str(report.codebook_path),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
        ),
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_closure_count": report.manifest.expected_closure_count,
        "closure_count": report.closure_count,
        "source_kind_counts": report.source_kind_counts,
        "failed_subjects": list(report.failed_subjects),
        "closures": [_closure_payload(closure) for closure in report.closures],
        "result_count": len(report.results),
        "results": [
            {
                "subject": result.subject,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }


def format_fixed_point_diagonal_instance_closure_report(
    report: FixedPointDiagonalInstanceClosureReport,
) -> str:
    """Format a concise human-readable closure report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point diagonal instance closure: {status}",
        f"Closure set: {report.manifest.closure_set_id}",
        f"Closures: {report.closure_count}",
        "Source kinds: "
        + ", ".join(
            f"{kind}={count}" for kind, count in report.source_kind_counts.items()
        ),
        f"Closure failures: {_joined_or_none(report.failed_subjects)}",
    ]
    for closure in report.closures:
        lines.extend([
            f"- {closure.closure_id}",
            f"  Target: {closure.target_id}",
            f"  Construction: {closure.construction_id}",
            f"  Bridge: {closure.bridge_id}",
            f"  Diagonal instance length: {closure.diagonal_instance_code_length}",
            f"  Closed: {closure.diagonal_instance_closed}",
            f"  Codebook roundtrip: {closure.codebook_roundtrip}",
            f"  Bridge target closed: {closure.bridge_target_closed}",
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_diagonal_instance_closure_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point diagonal-instance closure validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_diagonal_instance_closure",
        description="Validate AS fixed-point diagonal-instance closure evidence.",
    )
    parser.add_argument(
        "--closure",
        default=str(DEFAULT_CLOSURE),
        help="Path to the fixed-point diagonal-instance closure manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_diagonal_instance_closure(args.closure)
    report = validate_fixed_point_diagonal_instance_closure(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(fixed_point_diagonal_instance_closure_payload(report), sort_keys=True))
    else:
        print(format_fixed_point_diagonal_instance_closure_report(report))
    return 0 if report.accepted else 1


def _validate_references(
    manifest: FixedPointDiagonalInstanceClosureManifest,
) -> list[FixedPointDiagonalInstanceClosureValidation]:
    expected = (
        ("formal_language_path", manifest.formal_language_path, "language/formal_arithmetic_language.json"),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        (
            "diagonal_construction_targets_path",
            manifest.diagonal_construction_targets_path,
            "claims/diagonal_construction_targets.json",
        ),
        (
            "fixed_point_equation_bridge_targets_path",
            manifest.fixed_point_equation_bridge_targets_path,
            "claims/fixed_point_equation_bridge_targets.json",
        ),
    )
    results: list[FixedPointDiagonalInstanceClosureValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(_rejected(subject, f"expected {expected_value} but found {actual}"))
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    codebook_report: Any,
    fixed_point_report: Any,
    diagonal_report: Any,
    bridge_report: Any,
) -> list[FixedPointDiagonalInstanceClosureValidation]:
    checks = (
        ("codebook", codebook_report, "formal codebook"),
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("fixed_point_equation_bridge", bridge_report, "fixed-point equation bridge"),
    )
    results: list[FixedPointDiagonalInstanceClosureValidation] = []
    for subject, report, label in checks:
        if report.accepted:
            results.append(_accepted(subject, f"{label} accepted"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results


def _validate_closures(
    manifest: FixedPointDiagonalInstanceClosureManifest,
    codebook: FormalCodebook,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    diagonal_constructions: tuple[DiagonalConstructionTarget, ...],
    bridges: tuple[FixedPointEquationBridgeTarget, ...],
    bridge_observations: tuple[FixedPointEquationBridgeObservation, ...],
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
    bridge_targets_path: Path,
) -> tuple[
    list[FixedPointDiagonalInstanceClosureValidation],
    tuple[FixedPointDiagonalInstanceClosure, ...],
]:
    closures: list[FixedPointDiagonalInstanceClosure] = []
    results: list[FixedPointDiagonalInstanceClosureValidation] = []
    bridge_observations_by_id = {
        observation.bridge_id: observation for observation in bridge_observations
    }
    for bridge in bridges:
        target = _find_by_id(fixed_point_targets, "target_id", bridge.target_id)
        construction = _find_by_id(
            diagonal_constructions,
            "construction_id",
            bridge.construction_id,
        )
        observation = bridge_observations_by_id[bridge.bridge_id]
        closures.append(
            _build_closure(
                target,
                construction,
                bridge,
                observation,
                codebook,
                manifest.expected_diagonal_instance_code_prefix,
                diagonal_targets_path,
                fixed_point_targets_path,
            )
        )

    if manifest.expected_closure_count != len(closures):
        results.append(
            _rejected(
                "closure_count",
                "closure count mismatch: expected "
                + str(manifest.expected_closure_count)
                + " got "
                + str(len(closures)),
            )
        )
    else:
        results.append(_accepted("closure_count", f"checked {len(closures)} closure(s)"))

    if manifest.required_source_kinds != REQUIRED_SOURCE_KINDS:
        results.append(
            _rejected(
                "required_source_kinds",
                "source kinds mismatch: " + ", ".join(manifest.required_source_kinds),
            )
        )
    else:
        results.append(_accepted("required_source_kinds", "source kinds are current"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in manifest.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                "required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted("required_future_work", "future work is explicit"))

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected("non_claims", "missing non-claims: " + ", ".join(missing_non_claims))
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))

    for closure in closures:
        results.extend(
            _validate_closure(
                closure,
                manifest.expected_diagonal_instance_code_length,
                manifest.expected_diagonal_instance_code_prefix,
            )
        )
    if bridge_targets_path.name != "fixed_point_equation_bridge_targets.json":
        results.append(_rejected("bridge_path", "unexpected bridge target file"))
    return results, tuple(closures)


def _build_closure(
    target: FixedPointTarget,
    construction: DiagonalConstructionTarget,
    bridge: FixedPointEquationBridgeTarget,
    bridge_observation: FixedPointEquationBridgeObservation,
    codebook: FormalCodebook,
    prefix_width: tuple[int, ...],
    diagonal_targets_path: Path,
    fixed_point_targets_path: Path,
) -> FixedPointDiagonalInstanceClosure:
    seed_node = build_diagonal_seed_node(target)
    seed_code = encode_node(seed_node, codebook)
    seed_quote = quote_tokens_as_term(seed_code)
    diagonal_instance_node = substitute_node(
        seed_node,
        target.template_variable,
        seed_quote,
    )
    diagonal_instance_code = build_diagonal_instance_code(
        construction_id=construction.construction_id,
        targets_path=diagonal_targets_path,
        fixed_point_targets_path=fixed_point_targets_path,
        codebook_path=codebook.path,
    )
    decoded_instance = decode_code(diagonal_instance_code, codebook)
    diagonal_slot = _target_slot(diagonal_instance_node)
    expected_diagonal_slot = {
        "kind": "substitution_code",
        "left": seed_quote,
        "right": seed_quote,
    }
    return FixedPointDiagonalInstanceClosure(
        closure_id="AS-FIXED-POINT-DIAGONAL-INSTANCE-CLOSURE",
        source_kind="diagonal-instance",
        target_id=target.target_id,
        construction_id=construction.construction_id,
        bridge_id=bridge.bridge_id,
        template_variable=target.template_variable,
        seed_code_length=len(seed_code),
        diagonal_instance_code_length=len(diagonal_instance_code),
        diagonal_instance_code_prefix=diagonal_instance_code[: len(prefix_width)],
        diagonal_instance_free_variables=tuple(sorted(free_variables(diagonal_instance_node))),
        diagonal_instance_closed=not free_variables(diagonal_instance_node),
        codebook_roundtrip=(
            decoded_instance == diagonal_instance_node
            and encode_node(decoded_instance, codebook) == diagonal_instance_code
        ),
        target_skeleton_preserved=_target_skeleton_preserved(
            target.template_node,
            diagonal_instance_node,
        ),
        diagonal_slot_is_quoted_seed_substitution=(diagonal_slot == expected_diagonal_slot),
        bridge_matches_diagonal_instance=(
            bridge_observation.diagonal_instance_code_length
            == len(diagonal_instance_code)
            and bridge_observation.diagonal_instance_code_prefix
            == diagonal_instance_code[: len(bridge_observation.diagonal_instance_code_prefix)]
        ),
        bridge_target_closed=(
            bridge_observation.diagonal_instance_closed
            and bridge_observation.direct_target_closed
            and bridge_observation.bridge_equation_closed
        ),
    )


def _validate_closure(
    closure: FixedPointDiagonalInstanceClosure,
    expected_length: int,
    expected_prefix: tuple[int, ...],
) -> list[FixedPointDiagonalInstanceClosureValidation]:
    subject = closure.closure_id
    results: list[FixedPointDiagonalInstanceClosureValidation] = []
    if closure.diagonal_instance_code_length != expected_length:
        results.append(
            _rejected(
                f"{subject}.length",
                "diagonal instance length mismatch: expected "
                + str(expected_length)
                + " got "
                + str(closure.diagonal_instance_code_length),
            )
        )
    elif closure.diagonal_instance_code_prefix != expected_prefix:
        results.append(_rejected(f"{subject}.length", "diagonal instance prefix mismatch"))
    else:
        results.append(_accepted(f"{subject}.length", "diagonal instance length is current"))

    if closure.diagonal_instance_closed:
        results.append(_accepted(f"{subject}.closure", "diagonal instance is closed"))
    else:
        results.append(
            _rejected(
                f"{subject}.closure",
                "free variables: " + ", ".join(closure.diagonal_instance_free_variables),
            )
        )

    if closure.codebook_roundtrip:
        results.append(_accepted(f"{subject}.roundtrip", "codebook roundtrip accepted"))
    else:
        results.append(_rejected(f"{subject}.roundtrip", "codebook roundtrip mismatch"))

    if closure.target_skeleton_preserved:
        results.append(_accepted(f"{subject}.skeleton", "target skeleton preserved"))
    else:
        results.append(_rejected(f"{subject}.skeleton", "target skeleton mismatch"))

    if closure.diagonal_slot_is_quoted_seed_substitution:
        results.append(_accepted(f"{subject}.slot", "diagonal slot accepted"))
    else:
        results.append(_rejected(f"{subject}.slot", "diagonal slot mismatch"))

    if closure.bridge_matches_diagonal_instance and closure.bridge_target_closed:
        results.append(_accepted(f"{subject}.bridge", "bridge observation matches closure"))
    else:
        results.append(_rejected(f"{subject}.bridge", "bridge observation mismatch"))
    return results


def _closure_payload(closure: FixedPointDiagonalInstanceClosure) -> dict[str, Any]:
    return {
        "closure_id": closure.closure_id,
        "source_kind": closure.source_kind,
        "target_id": closure.target_id,
        "construction_id": closure.construction_id,
        "bridge_id": closure.bridge_id,
        "template_variable": closure.template_variable,
        "seed_code_length": closure.seed_code_length,
        "observed_diagonal_instance_code_length": closure.diagonal_instance_code_length,
        "observed_diagonal_instance_code_prefix": list(closure.diagonal_instance_code_prefix),
        "observed_diagonal_instance_free_variables": list(
            closure.diagonal_instance_free_variables
        ),
        "observed_diagonal_instance_closed": closure.diagonal_instance_closed,
        "observed_codebook_roundtrip": closure.codebook_roundtrip,
        "observed_target_skeleton_preserved": closure.target_skeleton_preserved,
        "observed_diagonal_slot_is_quoted_seed_substitution": (
            closure.diagonal_slot_is_quoted_seed_substitution
        ),
        "observed_bridge_matches_diagonal_instance": (
            closure.bridge_matches_diagonal_instance
        ),
        "observed_bridge_target_closed": closure.bridge_target_closed,
    }


def _target_slot(node: dict[str, Any]) -> dict[str, Any]:
    body = node.get("body")
    if not isinstance(body, dict) or body.get("kind") != "less_than":
        raise ValueError("target body must be less_than")
    right = body.get("right")
    if not isinstance(right, dict):
        raise ValueError("target slot is not a term")
    return right


def _target_skeleton_preserved(
    template_node: dict[str, Any],
    diagonal_instance_node: dict[str, Any],
) -> bool:
    try:
        if template_node.get("kind") != diagonal_instance_node.get("kind"):
            return False
        if template_node.get("variable") != diagonal_instance_node.get("variable"):
            return False
        template_body = template_node.get("body")
        diagonal_body = diagonal_instance_node.get("body")
        if not isinstance(template_body, dict) or not isinstance(diagonal_body, dict):
            return False
        if template_body.get("kind") != diagonal_body.get("kind"):
            return False
        if template_body.get("left") != diagonal_body.get("left"):
            return False
        _target_slot(template_node)
        _target_slot(diagonal_instance_node)
    except ValueError:
        return False
    return True


def _find_by_id(items: tuple[Any, ...], id_attr: str, expected_id: str) -> Any:
    for item in items:
        if getattr(item, id_attr) == expected_id:
            return item
    raise ValueError(f"missing {id_attr}: {expected_id}")


def _failed_subject_for_result(subject: str) -> str:
    if subject == "closure_count":
        return "fixed-point-diagonal-instance-closure-count"
    if subject.endswith(".length"):
        return "fixed-point-diagonal-instance-closure-length"
    if subject.endswith(".closure"):
        return "fixed-point-diagonal-instance-closure"
    if subject.endswith(".roundtrip"):
        return "fixed-point-diagonal-instance-closure-roundtrip"
    if subject.endswith(".skeleton"):
        return "fixed-point-diagonal-instance-closure-skeleton"
    if subject.endswith(".slot"):
        return "fixed-point-diagonal-instance-closure-slot"
    if subject.endswith(".bridge"):
        return "fixed-point-diagonal-instance-closure-bridge"
    if subject in {"codebook", "fixed_point", "diagonal_construction", "fixed_point_equation_bridge"}:
        return "fixed-point-diagonal-instance-closure-dependency"
    if subject.endswith("_path"):
        return "fixed-point-diagonal-instance-closure-reference"
    if subject == "required_source_kinds":
        return "fixed-point-diagonal-instance-closure-source-kind"
    if subject == "required_future_work":
        return "fixed-point-diagonal-instance-closure-future-work"
    if subject == "non_claims":
        return "fixed-point-diagonal-instance-closure-non-claim"
    if subject == "next_as_action":
        return "fixed-point-diagonal-instance-closure-next-action"
    return "fixed-point-diagonal-instance-closure"


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = _required_list(item, key)
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        result.append(value)
    return result


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    values = _required_list(item, key)
    result: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} contains non-natural item")
        result.append(value)
    return result


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureValidation:
    return FixedPointDiagonalInstanceClosureValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureValidation:
    return FixedPointDiagonalInstanceClosureValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_diagonal_instance_closure_cli())
