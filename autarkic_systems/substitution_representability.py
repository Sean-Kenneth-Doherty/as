"""Checked substitution-representability witness surface for AS.

This module validates one concrete meta-level graph point for the
``substitution_code`` diagonal route: the current diagonal seed applied to its
own code. The witness is intentionally weaker than a representability proof.
It records the formula code, argument code, output code length/prefix, and
closed free-variable boundary needed before a later delta0 graph formula can
be attempted.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.diagonal_construction import (
    DiagonalConstructionManifest,
    build_diagonal_seed_node,
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import (
    FixedPointTarget,
    load_fixed_point_targets,
    validate_fixed_point_targets,
)
from autarkic_systems.formal_code import (
    FormalCodebook,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)
from autarkic_systems.formal_quotation_term import quote_tokens_as_term
from autarkic_systems.formal_substitution import free_variables, substitute_node
from autarkic_systems.willard_map import load_willard_definition_map


DEFAULT_TARGETS = Path("claims/substitution_representability_targets.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_WILLARD_ANCHORS = (
    "W2011-D3.4-GENERIC-CONFIGURATION",
    "W2011-D5.7-SELFCONSK",
    "W2020-D3.2-SELF-JUSTIFYING-GENAC",
)
REQUIRED_FUTURE_WORK = (
    "delta0-graph-formula",
    "substitution-representability-proof",
    "diagonal-lemma-proof",
    "fixed-point-equation-proof",
    "self-consistency-theorem",
)
VALID_WITNESS_STATUSES = {
    "representability-witness-not-proof",
}


@dataclass(frozen=True)
class SubstitutionRepresentabilityWitness:
    """One checked meta-level substitution graph witness, not a proof."""

    witness_id: str
    construction_id: str
    target_id: str
    variable: str
    status: str
    expected_formula_code: tuple[int, ...]
    expected_argument_code: tuple[int, ...]
    expected_output_code_length: int
    expected_output_code_prefix: tuple[int, ...]
    expected_output_free_variables: tuple[str, ...]
    required_future_work: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class SubstitutionRepresentabilityManifest:
    """Loaded manifest for substitution-representability witnesses."""

    path: Path
    schema_version: int
    witness_set_id: str
    reviewed_at: str
    purpose: str
    diagonal_construction_targets_path: str
    fixed_point_targets_path: str
    codebook_path: str
    willard_anchor_ids: tuple[str, ...]
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...]


@dataclass(frozen=True)
class SubstitutionRepresentabilityValidation:
    """One validation result for substitution-representability witnesses."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class SubstitutionRepresentabilityObservation:
    """Observed substitution graph facts for one witness."""

    witness_id: str
    construction_id: str
    target_id: str
    status: str
    formula_code: tuple[int, ...]
    argument_code: tuple[int, ...]
    output_code_length: int
    output_code_prefix: tuple[int, ...]
    output_free_variables: tuple[str, ...]


@dataclass(frozen=True)
class SubstitutionRepresentabilityReport:
    """Validation report over substitution-representability witnesses."""

    manifest: SubstitutionRepresentabilityManifest
    diagonal_construction_targets_path: Path
    fixed_point_targets_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    results: tuple[SubstitutionRepresentabilityValidation, ...]
    observations: tuple[SubstitutionRepresentabilityObservation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every witness validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def witness_count(self) -> int:
        """Return the number of checked substitution witnesses."""

        return len(self.manifest.witnesses)

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


def build_substitution_witness_output_code(
    *,
    witness_id: str,
    targets_path: Path | str = DEFAULT_TARGETS,
    diagonal_targets_path: Path | str | None = None,
    fixed_point_targets_path: Path | str | None = None,
    codebook_path: Path | str | None = None,
) -> tuple[int, ...]:
    """Build and encode the output side of one substitution witness."""

    manifest = load_substitution_representability_targets(targets_path)
    witness = _find_witness(manifest.witnesses, witness_id)
    checked_diagonal_path = Path(
        diagonal_targets_path or manifest.diagonal_construction_targets_path
    )
    checked_fixed_point_path = Path(
        fixed_point_targets_path or manifest.fixed_point_targets_path
    )
    checked_codebook_path = Path(codebook_path or manifest.codebook_path)
    diagonal_targets = load_diagonal_construction_targets(checked_diagonal_path)
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    codebook = load_formal_codebook(checked_codebook_path)
    return _witness_graph(
        witness,
        diagonal_targets,
        fixed_point_targets.targets,
        codebook,
    )[3]


def load_substitution_representability_targets(
    path: Path | str = DEFAULT_TARGETS,
) -> SubstitutionRepresentabilityManifest:
    """Load substitution-representability witness targets from JSON."""

    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return SubstitutionRepresentabilityManifest(
        path=manifest_path,
        schema_version=_required_int(data, "schema_version"),
        witness_set_id=_required_text(data, "witness_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        diagonal_construction_targets_path=_required_text(
            data,
            "diagonal_construction_targets_path",
        ),
        fixed_point_targets_path=_required_text(data, "fixed_point_targets_path"),
        codebook_path=_required_text(data, "codebook_path"),
        willard_anchor_ids=tuple(_required_text_list(data, "willard_anchor_ids")),
        witnesses=tuple(
            _parse_witness(item) for item in _required_list(data, "witnesses")
        ),
    )


def validate_substitution_representability_targets(
    manifest: SubstitutionRepresentabilityManifest,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> SubstitutionRepresentabilityReport:
    """Validate substitution-representability witnesses and dependencies."""

    checked_language_path = Path(formal_language_path)
    checked_willard_map_path = Path(willard_map_path)
    checked_diagonal_path = Path(manifest.diagonal_construction_targets_path)
    checked_fixed_point_path = Path(manifest.fixed_point_targets_path)
    checked_codebook_path = Path(manifest.codebook_path)

    willard_map = load_willard_definition_map(checked_willard_map_path)
    known_anchor_ids = {anchor.anchor_id for anchor in willard_map.anchors}
    diagonal_targets = load_diagonal_construction_targets(checked_diagonal_path)
    diagonal_report = validate_diagonal_construction_targets(
        diagonal_targets,
        checked_language_path,
        checked_willard_map_path,
    )
    fixed_point_targets = load_fixed_point_targets(checked_fixed_point_path)
    fixed_point_report = validate_fixed_point_targets(
        fixed_point_targets,
        checked_willard_map_path,
        checked_language_path,
    )
    codebook = load_formal_codebook(checked_codebook_path)
    codebook_report = validate_formal_codebook(
        codebook,
        checked_language_path,
        checked_willard_map_path,
    )

    results: list[SubstitutionRepresentabilityValidation] = [
        _accepted("manifest", f"loaded {len(manifest.witnesses)} witness(es)")
    ]
    observations: list[SubstitutionRepresentabilityObservation] = []
    results.extend(_validate_references(manifest))
    results.extend(
        _validate_dependency_reports(
            diagonal_report,
            fixed_point_report,
            codebook_report,
        )
    )
    results.extend(_validate_willard_anchors(manifest, known_anchor_ids))
    witness_results, observations = _validate_witnesses(
        manifest.witnesses,
        diagonal_targets,
        fixed_point_targets.targets,
        codebook,
    )
    results.extend(witness_results)

    return SubstitutionRepresentabilityReport(
        manifest=manifest,
        diagonal_construction_targets_path=checked_diagonal_path,
        fixed_point_targets_path=checked_fixed_point_path,
        codebook_path=checked_codebook_path,
        formal_language_path=checked_language_path,
        willard_map_path=checked_willard_map_path,
        results=tuple(results),
        observations=tuple(observations),
    )


def substitution_representability_report_payload(
    report: SubstitutionRepresentabilityReport,
) -> dict[str, Any]:
    """Return a JSON-ready substitution-representability payload."""

    observations = {
        observation.witness_id: observation
        for observation in report.observations
    }
    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "witness_manifest": str(report.manifest.path),
        "witness_set_id": report.manifest.witness_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "diagonal_construction_targets_path": str(
            report.diagonal_construction_targets_path
        ),
        "fixed_point_targets_path": str(report.fixed_point_targets_path),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "willard_anchor_ids": list(report.manifest.willard_anchor_ids),
        "witness_count": report.witness_count,
        "failed_subjects": list(report.failed_subjects),
        "witnesses": [
            _witness_payload(witness, observations.get(witness.witness_id))
            for witness in report.manifest.witnesses
        ],
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


def format_substitution_representability_report(
    report: SubstitutionRepresentabilityReport,
) -> str:
    """Format a concise human-readable substitution witness report."""

    observations = {
        observation.witness_id: observation
        for observation in report.observations
    }
    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Substitution representability witnesses: {status}",
        f"Witness set: {report.manifest.witness_set_id}",
        f"Witnesses: {report.witness_count}",
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for witness in report.manifest.witnesses:
        observation = observations.get(witness.witness_id)
        output_length = "unknown"
        if observation is not None:
            output_length = str(observation.output_code_length)
        lines.extend([
            f"- {witness.witness_id}",
            f"  Construction: {witness.construction_id}",
            f"  Target: {witness.target_id}",
            f"  Status: {witness.status}",
            f"  Output code length: {output_length}",
            "  Future work: " + _joined_or_none(witness.required_future_work),
        ])
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_substitution_representability_cli(argv: list[str] | None = None) -> int:
    """Run the substitution-representability witness validation command."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.substitution_representability",
        description="Validate AS substitution-representability witnesses.",
    )
    parser.add_argument(
        "--targets",
        default=str(DEFAULT_TARGETS),
        help="Path to the substitution-representability witness manifest.",
    )
    parser.add_argument(
        "--language",
        default=str(DEFAULT_FORMAL_LANGUAGE),
        help="Path to the formal arithmetic language manifest.",
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

    manifest = load_substitution_representability_targets(args.targets)
    report = validate_substitution_representability_targets(
        manifest,
        args.language,
        args.willard_map,
    )
    if args.format == "json":
        print(json.dumps(substitution_representability_report_payload(report), sort_keys=True))
    else:
        print(format_substitution_representability_report(report))
    return 0 if report.accepted else 1


def _witness_payload(
    witness: SubstitutionRepresentabilityWitness,
    observation: SubstitutionRepresentabilityObservation | None,
) -> dict[str, Any]:
    payload = {
        "witness_id": witness.witness_id,
        "construction_id": witness.construction_id,
        "target_id": witness.target_id,
        "substitution_variable": witness.variable,
        "status": witness.status,
        "expected_formula_code": list(witness.expected_formula_code),
        "expected_argument_code": list(witness.expected_argument_code),
        "expected_output_code_length": witness.expected_output_code_length,
        "expected_output_code_prefix": list(witness.expected_output_code_prefix),
        "expected_output_free_variables": list(
            witness.expected_output_free_variables
        ),
        "required_future_work": list(witness.required_future_work),
        "non_claims": list(witness.non_claims),
        "next_as_action": witness.next_as_action,
    }
    if observation is None:
        payload.update({
            "observed_formula_code_length": None,
            "observed_formula_code": None,
            "observed_argument_code_length": None,
            "observed_argument_code": None,
            "observed_output_code_length": None,
            "observed_output_code_prefix": None,
            "observed_output_free_variables": None,
        })
    else:
        payload.update({
            "observed_formula_code_length": len(observation.formula_code),
            "observed_formula_code": list(observation.formula_code),
            "observed_argument_code_length": len(observation.argument_code),
            "observed_argument_code": list(observation.argument_code),
            "observed_output_code_length": observation.output_code_length,
            "observed_output_code_prefix": list(observation.output_code_prefix),
            "observed_output_free_variables": list(observation.output_free_variables),
        })
    return payload


def _validate_references(
    manifest: SubstitutionRepresentabilityManifest,
) -> list[SubstitutionRepresentabilityValidation]:
    expected = (
        (
            "diagonal_construction_targets_path",
            manifest.diagonal_construction_targets_path,
            "claims/diagonal_construction_targets.json",
        ),
        (
            "fixed_point_targets_path",
            manifest.fixed_point_targets_path,
            "claims/fixed_point_targets.json",
        ),
        ("codebook_path", manifest.codebook_path, "language/formal_codebook.json"),
    )
    results: list[SubstitutionRepresentabilityValidation] = []
    for subject, actual, expected_value in expected:
        if actual != expected_value:
            results.append(
                _rejected(subject, f"expected {expected_value} but found {actual}")
            )
        else:
            results.append(_accepted(subject, f"{expected_value} referenced"))
    return results


def _validate_dependency_reports(
    diagonal_report: Any,
    fixed_point_report: Any,
    codebook_report: Any,
) -> list[SubstitutionRepresentabilityValidation]:
    checks = (
        ("diagonal_construction", diagonal_report, "diagonal construction"),
        ("fixed_point", fixed_point_report, "fixed-point target"),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[SubstitutionRepresentabilityValidation] = []
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


def _validate_willard_anchors(
    manifest: SubstitutionRepresentabilityManifest,
    known_anchor_ids: set[str],
) -> list[SubstitutionRepresentabilityValidation]:
    unknown_anchor_ids = sorted(set(manifest.willard_anchor_ids) - known_anchor_ids)
    missing_required = sorted(
        set(REQUIRED_WILLARD_ANCHORS) - set(manifest.willard_anchor_ids)
    )
    if unknown_anchor_ids:
        return [
            _rejected(
                "willard_anchors",
                "unknown Willard anchor IDs: " + ", ".join(unknown_anchor_ids),
            )
        ]
    if missing_required:
        return [
            _rejected(
                "willard_anchors",
                "missing required Willard anchors: " + ", ".join(missing_required),
            )
        ]
    return [_accepted("willard_anchors", "required anchors are present and known")]


def _validate_witnesses(
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    diagonal_targets: DiagonalConstructionManifest,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    codebook: FormalCodebook,
) -> tuple[
    list[SubstitutionRepresentabilityValidation],
    list[SubstitutionRepresentabilityObservation],
]:
    if not witnesses:
        return [_rejected("witnesses", "no substitution witnesses")], []

    results: list[SubstitutionRepresentabilityValidation] = []
    observations: list[SubstitutionRepresentabilityObservation] = []
    witness_ids = [witness.witness_id for witness in witnesses]
    duplicate_ids = _duplicates(witness_ids)
    if duplicate_ids:
        results.append(
            _rejected(
                "witnesses.witness_id",
                "duplicate witness ids: " + ", ".join(duplicate_ids),
            )
        )
    else:
        results.append(_accepted("witnesses.witness_id", "witness ids are unique"))

    for witness in witnesses:
        witness_results, observation = _validate_witness(
            witness,
            diagonal_targets,
            fixed_point_targets,
            codebook,
        )
        results.extend(witness_results)
        if observation is not None:
            observations.append(observation)
    results.append(_accepted("witnesses", f"checked {len(witnesses)} witness(es)"))
    return results, observations


def _validate_witness(
    witness: SubstitutionRepresentabilityWitness,
    diagonal_targets: DiagonalConstructionManifest,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    codebook: FormalCodebook,
) -> tuple[
    list[SubstitutionRepresentabilityValidation],
    SubstitutionRepresentabilityObservation | None,
]:
    subject = witness.witness_id
    results: list[SubstitutionRepresentabilityValidation] = []

    if witness.status in {
        "representability-proved",
        "substitution-representability-proved",
    }:
        results.append(
            _rejected(
                f"{subject}.status",
                "proved substitution representability is not supported",
            )
        )
    elif witness.status not in VALID_WITNESS_STATUSES:
        results.append(_rejected(f"{subject}.status", f"unknown status: {witness.status}"))
    else:
        results.append(_accepted(f"{subject}.status", "status preserves non-claim"))

    missing_future_work = [
        item for item in REQUIRED_FUTURE_WORK if item not in witness.required_future_work
    ]
    if missing_future_work:
        results.append(
            _rejected(
                f"{subject}.required_future_work",
                "missing future work: " + ", ".join(missing_future_work),
            )
        )
    else:
        results.append(_accepted(f"{subject}.required_future_work", "future work is explicit"))

    if not witness.non_claims:
        results.append(_rejected(f"{subject}.non_claims", "non-claims must be explicit"))
    else:
        results.append(_accepted(f"{subject}.non_claims", "non-claims are explicit"))

    try:
        observation = _observe_witness(
            witness,
            diagonal_targets,
            fixed_point_targets,
            codebook,
        )
    except ValueError as exc:
        results.append(_rejected(f"{subject}.witness", str(exc)))
        return results, None

    if observation.formula_code != witness.expected_formula_code:
        results.append(
            _rejected(
                f"{subject}.witness",
                "formula code mismatch: expected "
                + _format_code(witness.expected_formula_code)
                + " got "
                + _format_code(observation.formula_code),
            )
        )
    elif observation.argument_code != witness.expected_argument_code:
        results.append(
            _rejected(
                f"{subject}.witness",
                "argument code mismatch: expected "
                + _format_code(witness.expected_argument_code)
                + " got "
                + _format_code(observation.argument_code),
            )
        )
    else:
        results.append(_accepted(f"{subject}.witness", "formula and argument codes accepted"))

    if observation.output_code_length != witness.expected_output_code_length:
        results.append(
            _rejected(
                f"{subject}.output",
                "output code length mismatch: expected "
                + str(witness.expected_output_code_length)
                + " got "
                + str(observation.output_code_length),
            )
        )
    elif observation.output_code_prefix != witness.expected_output_code_prefix:
        results.append(
            _rejected(
                f"{subject}.output",
                "output code prefix mismatch: expected "
                + _format_code(witness.expected_output_code_prefix)
                + " got "
                + _format_code(observation.output_code_prefix),
            )
        )
    elif observation.output_free_variables != witness.expected_output_free_variables:
        results.append(
            _rejected(
                f"{subject}.output",
                "output free variables mismatch: expected "
                + _joined_or_none(witness.expected_output_free_variables)
                + " got "
                + _joined_or_none(observation.output_free_variables),
            )
        )
    else:
        results.append(_accepted(f"{subject}.output", "output graph point accepted"))

    return results, observation


def _observe_witness(
    witness: SubstitutionRepresentabilityWitness,
    diagonal_targets: DiagonalConstructionManifest,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    codebook: FormalCodebook,
) -> SubstitutionRepresentabilityObservation:
    formula_code, argument_code, output_node, output_code = _witness_graph(
        witness,
        diagonal_targets,
        fixed_point_targets,
        codebook,
    )
    return SubstitutionRepresentabilityObservation(
        witness_id=witness.witness_id,
        construction_id=witness.construction_id,
        target_id=witness.target_id,
        status=witness.status,
        formula_code=formula_code,
        argument_code=argument_code,
        output_code_length=len(output_code),
        output_code_prefix=output_code[: len(witness.expected_output_code_prefix)],
        output_free_variables=tuple(sorted(free_variables(output_node))),
    )


def _witness_graph(
    witness: SubstitutionRepresentabilityWitness,
    diagonal_targets: DiagonalConstructionManifest,
    fixed_point_targets: tuple[FixedPointTarget, ...],
    codebook: FormalCodebook,
) -> tuple[tuple[int, ...], tuple[int, ...], dict[str, Any], tuple[int, ...]]:
    construction = _find_construction(diagonal_targets, witness.construction_id)
    if construction.target_id != witness.target_id:
        raise ValueError(
            "witness target mismatch: construction "
            + construction.target_id
            + " but witness names "
            + witness.target_id
        )
    fixed_point_target = _find_fixed_point_target(fixed_point_targets, witness.target_id)
    if witness.variable != fixed_point_target.template_variable:
        raise ValueError(
            "substitution variable mismatch: expected "
            + fixed_point_target.template_variable
            + " but found "
            + witness.variable
        )
    seed_node = build_diagonal_seed_node(fixed_point_target)
    formula_code = encode_node(seed_node, codebook)
    argument_code = formula_code
    output_node = _output_node_from_seed(seed_node, witness.variable, argument_code)
    output_code = encode_node(output_node, codebook)
    return formula_code, argument_code, output_node, output_code


def _output_node_from_seed(
    seed_node: dict[str, Any],
    variable: str,
    argument_code: tuple[int, ...],
) -> dict[str, Any]:
    argument_term = quote_tokens_as_term(argument_code)
    return substitute_node(seed_node, variable, argument_term)


def _find_witness(
    witnesses: tuple[SubstitutionRepresentabilityWitness, ...],
    witness_id: str,
) -> SubstitutionRepresentabilityWitness:
    for witness in witnesses:
        if witness.witness_id == witness_id:
            return witness
    raise ValueError(f"unknown substitution witness: {witness_id}")


def _find_construction(
    manifest: DiagonalConstructionManifest,
    construction_id: str,
) -> Any:
    for construction in manifest.constructions:
        if construction.construction_id == construction_id:
            return construction
    raise ValueError(f"unknown diagonal construction: {construction_id}")


def _find_fixed_point_target(
    targets: tuple[FixedPointTarget, ...],
    target_id: str,
) -> FixedPointTarget:
    for target in targets:
        if target.target_id == target_id:
            return target
    raise ValueError(f"unknown fixed-point target: {target_id}")


def _parse_witness(item: dict[str, Any]) -> SubstitutionRepresentabilityWitness:
    return SubstitutionRepresentabilityWitness(
        witness_id=_required_text(item, "witness_id"),
        construction_id=_required_text(item, "construction_id"),
        target_id=_required_text(item, "target_id"),
        variable=_required_text(item, "substitution_variable"),
        status=_required_text(item, "status"),
        expected_formula_code=tuple(_required_int_list(item, "expected_formula_code")),
        expected_argument_code=tuple(_required_int_list(item, "expected_argument_code")),
        expected_output_code_length=_required_int(
            item,
            "expected_output_code_length",
        ),
        expected_output_code_prefix=tuple(
            _required_int_list(item, "expected_output_code_prefix")
        ),
        expected_output_free_variables=tuple(
            _required_text_list(
                item,
                "expected_output_free_variables",
                allow_empty=True,
            )
        ),
        required_future_work=tuple(_required_text_list(item, "required_future_work")),
        non_claims=tuple(_required_text_list(item, "non_claims")),
        next_as_action=_required_text(item, "next_as_action"),
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject == "willard_anchors":
        return "substitution-representability-willard-anchor"
    if subject.endswith(".status"):
        return "substitution-representability-status"
    if subject.endswith(".witness"):
        return "substitution-representability-witness"
    if subject.endswith(".output"):
        return "substitution-representability-output"
    if subject.endswith(".required_future_work"):
        return "substitution-representability-future-work"
    if subject.endswith(".non_claims"):
        return "substitution-representability-non-claim"
    if subject in {"diagonal_construction", "fixed_point", "codebook"}:
        return "substitution-representability-dependency"
    if subject.endswith("_path"):
        return "substitution-representability-reference"
    if subject.startswith("witnesses"):
        return "substitution-representability-witness"
    return "substitution-representability"


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


def _required_text_list(
    item: dict[str, Any],
    key: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    values = item.get(key)
    if not isinstance(values, list) or (not values and not allow_empty):
        raise ValueError(f"required list field missing: {key}")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        result.append(value)
    return result


def _required_int_list(item: dict[str, Any], key: str) -> list[int]:
    values = item.get(key)
    if not isinstance(values, list) or not values:
        raise ValueError(f"required integer list missing: {key}")
    result: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"{key} contains non-natural item")
        result.append(value)
    return result


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def _accepted(
    subject: str,
    detail: str,
) -> SubstitutionRepresentabilityValidation:
    return SubstitutionRepresentabilityValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> SubstitutionRepresentabilityValidation:
    return SubstitutionRepresentabilityValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _format_code(values: tuple[int, ...]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def _joined_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


if __name__ == "__main__":
    raise SystemExit(run_substitution_representability_cli())
