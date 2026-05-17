"""Object-language validation for transition-chain claims."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, get_args

from autarkic_systems import transition_chain_predicates
from autarkic_systems.chain_claims import ChainClaim
from autarkic_systems.proof_certificates import (
    ClaimCertificate,
    MANIFEST_EXAMPLE_RULE,
)
from autarkic_systems.transition_chains import (
    ChainStatus,
    execute_neighbor_delivery_recipient_chain,
)
from autarkic_systems.universal_cell import (
    Cell,
    Signal,
    Status,
    VALID_AUTOMAIL,
    VALID_MEMORY,
    VALID_ROLES,
    VALID_SELF_MAILBOX,
)


REQUIRED_CHAIN_SYNTAX_CLASSES = (
    "terms",
    "chain_formulae",
    "chain_sentences",
    "proof_objects",
    "substrate_chain_claims",
)

REQUIRED_TERM_KEYS = (
    "roles",
    "memory",
    "signals",
    "automail",
    "command_messages",
    "transition_statuses",
    "chain_statuses",
    "cell_fields",
)

REQUIRED_CELL_FIELDS = (
    "role",
    "memory",
    "upstream",
    "input",
    "output",
    "automail",
    "self_mailbox",
    "control",
    "buffer",
)


@dataclass(frozen=True)
class TransitionChainClaimLanguage:
    """Loaded manifest for the transition-chain claim object language."""

    language_id: str
    syntax_classes: dict[str, Any]

    def without_syntax_class(self, class_name: str) -> "TransitionChainClaimLanguage":
        """Return a copy with one class removed for negative validation tests."""

        classes = dict(self.syntax_classes)
        classes.pop(class_name, None)
        return replace(self, syntax_classes=classes)

    def with_syntax_class(
        self,
        class_name: str,
        value: Any,
    ) -> "TransitionChainClaimLanguage":
        """Return a copy with one class replaced for focused tests."""

        classes = dict(self.syntax_classes)
        classes[class_name] = value
        return replace(self, syntax_classes=classes)


@dataclass(frozen=True)
class ChainLanguageValidation:
    """One transition-chain language validation result."""

    subject: str
    accepted: bool
    detail: str


def load_transition_chain_claim_language(
    path: Path | str,
) -> TransitionChainClaimLanguage:
    """Load the transition-chain claim language manifest."""

    language_path = Path(path)
    data = json.loads(language_path.read_text(encoding="utf-8"))
    return TransitionChainClaimLanguage(
        language_id=_required_text(data, "language_id"),
        syntax_classes=_required_mapping(data, "syntax_classes"),
    )


def validate_chain_language_manifest(
    language: TransitionChainClaimLanguage,
) -> list[ChainLanguageValidation]:
    """Validate the chain language manifest itself."""

    results: list[ChainLanguageValidation] = []
    for class_name in REQUIRED_CHAIN_SYNTAX_CLASSES:
        if class_name not in language.syntax_classes:
            results.append(
                _rejected(class_name, f"missing syntax class: {class_name}")
            )
        else:
            results.append(_accepted(class_name, "syntax class present"))

    terms = language.syntax_classes.get("terms")
    if isinstance(terms, dict):
        results.extend(_validate_term_class(terms))
    formulae = language.syntax_classes.get("chain_formulae")
    if isinstance(formulae, dict):
        results.extend(_validate_formula_class(formulae))
    sentences = language.syntax_classes.get("chain_sentences")
    if isinstance(sentences, dict):
        results.extend(_validate_sentence_class(sentences))
    proof_objects = language.syntax_classes.get("proof_objects")
    if isinstance(proof_objects, dict):
        results.extend(_validate_proof_object_class(proof_objects))
    substrate_claims = language.syntax_classes.get("substrate_chain_claims")
    if isinstance(substrate_claims, dict):
        results.extend(_validate_substrate_claim_class(substrate_claims))

    return results


def validate_chain_claim_surface(
    language: TransitionChainClaimLanguage,
    claims: Iterable[ChainClaim],
    certificates: Iterable[ClaimCertificate],
) -> list[ChainLanguageValidation]:
    """Validate chain claims and certificates against the chain language."""

    results: list[ChainLanguageValidation] = []
    allowed_predicates = _allowed_set(language, "chain_formulae", "predicate_symbols")
    claim_prefixes = tuple(
        _allowed_list(language, "chain_sentences", "claim_id_prefixes")
    )
    allowed_rules = _allowed_set(language, "proof_objects", "rules")
    claim_by_id = {claim.claim_id: claim for claim in claims}

    for claim in claim_by_id.values():
        if claim_prefixes and not claim.claim_id.startswith(claim_prefixes):
            results.append(
                _rejected(claim.claim_id, "claim id does not match sentence prefix")
            )
            continue
        if claim.predicate not in allowed_predicates:
            results.append(
                _rejected(claim.claim_id, f"unknown chain predicate: {claim.predicate}")
            )
            continue

        chain_issue = _first_chain_claim_issue(language, claim)
        if chain_issue is not None:
            results.append(_rejected(claim.claim_id, chain_issue))
            continue
        results.append(_accepted(claim.claim_id, "chain claim sentence is in language"))

    for certificate in certificates:
        if certificate.claim_id not in claim_by_id:
            results.append(
                _rejected(certificate.claim_id, "proof object cites unknown chain claim")
            )
            continue
        for step in certificate.steps:
            if step.rule not in allowed_rules:
                results.append(
                    _rejected(
                        certificate.claim_id,
                        f"unknown proof object rule: {step.rule}",
                    )
                )
                break
        else:
            results.append(
                _accepted(certificate.claim_id, "proof object is in language")
            )

    return results


def _validate_term_class(terms: dict[str, Any]) -> list[ChainLanguageValidation]:
    results: list[ChainLanguageValidation] = []
    for key in REQUIRED_TERM_KEYS:
        if key not in terms:
            results.append(_rejected(f"terms.{key}", f"missing term key: {key}"))
        else:
            results.append(_accepted(f"terms.{key}", "term key present"))

    results.append(_same_set("terms.roles", terms.get("roles"), VALID_ROLES))
    results.append(_same_set("terms.memory", terms.get("memory"), VALID_MEMORY))
    results.append(_same_set("terms.signals", terms.get("signals"), get_args(Signal)))
    results.append(_same_set("terms.automail", terms.get("automail"), VALID_AUTOMAIL))
    results.append(
        _same_set(
            "terms.command_messages",
            terms.get("command_messages"),
            VALID_SELF_MAILBOX,
        )
    )
    results.append(
        _same_set(
            "terms.transition_statuses",
            terms.get("transition_statuses"),
            get_args(Status),
        )
    )
    results.append(
        _same_set(
            "terms.chain_statuses",
            terms.get("chain_statuses"),
            get_args(ChainStatus),
        )
    )
    results.append(
        _same_set("terms.cell_fields", terms.get("cell_fields"), REQUIRED_CELL_FIELDS)
    )
    return results


def _validate_formula_class(formulae: dict[str, Any]) -> list[ChainLanguageValidation]:
    predicates = formulae.get("predicate_symbols")
    if not isinstance(predicates, list) or not predicates:
        return [_rejected("chain_formulae.predicate_symbols", "missing predicates")]

    results: list[ChainLanguageValidation] = []
    for predicate in predicates:
        if not isinstance(predicate, str):
            results.append(
                _rejected("chain_formulae.predicate_symbols", "predicate is not text")
            )
        elif getattr(transition_chain_predicates, predicate, None) is None:
            results.append(
                _rejected(
                    "chain_formulae.predicate_symbols",
                    f"unknown predicate implementation: {predicate}",
                )
            )
        else:
            results.append(
                _accepted(
                    "chain_formulae.predicate_symbols",
                    f"predicate implementation found: {predicate}",
                )
            )
    return results


def _validate_sentence_class(sentences: dict[str, Any]) -> list[ChainLanguageValidation]:
    kinds = sentences.get("kinds")
    prefixes = sentences.get("claim_id_prefixes")
    results: list[ChainLanguageValidation] = []
    if not isinstance(kinds, list) or "transition-chain-claim" not in kinds:
        results.append(
            _rejected("chain_sentences.kinds", "missing transition-chain-claim kind")
        )
    else:
        results.append(
            _accepted("chain_sentences.kinds", "transition-chain-claim kind present")
        )
    if not isinstance(prefixes, list) or not prefixes:
        results.append(
            _rejected("chain_sentences.claim_id_prefixes", "missing claim prefixes")
        )
    else:
        results.append(
            _accepted("chain_sentences.claim_id_prefixes", "claim prefixes present")
        )
    return results


def _validate_proof_object_class(
    proof_objects: dict[str, Any],
) -> list[ChainLanguageValidation]:
    rules = proof_objects.get("rules")
    if not isinstance(rules, list) or MANIFEST_EXAMPLE_RULE not in rules:
        return [_rejected("proof_objects.rules", "missing manifest-example rule")]
    return [_accepted("proof_objects.rules", "manifest-example rule present")]


def _validate_substrate_claim_class(
    substrate_claims: dict[str, Any],
) -> list[ChainLanguageValidation]:
    results: list[ChainLanguageValidation] = []
    for key in ("claim_manifest", "certificate_manifest"):
        if not isinstance(substrate_claims.get(key), str) or not substrate_claims[key]:
            results.append(_rejected(f"substrate_chain_claims.{key}", f"missing {key}"))
        else:
            results.append(
                _accepted(f"substrate_chain_claims.{key}", f"{key} present")
            )
    return results


def _first_chain_claim_issue(
    language: TransitionChainClaimLanguage,
    claim: ChainClaim,
) -> str | None:
    chain_statuses = _allowed_set(language, "terms", "chain_statuses")
    transition_statuses = _allowed_set(language, "terms", "transition_statuses")
    for example in claim.examples:
        sender_issue = _cell_issue(language, example.sender)
        if sender_issue is not None:
            return f"{example.name} sender has {sender_issue}"
        recipient_issue = _cell_issue(language, example.recipient)
        if recipient_issue is not None:
            return f"{example.name} recipient has {recipient_issue}"

        chain = execute_neighbor_delivery_recipient_chain(
            example.sender,
            example.recipient,
        )
        if chain.status not in chain_statuses:
            return f"{example.name} has unknown chain status: {chain.status}"
        if chain.sender_result.status not in transition_statuses:
            return (
                f"{example.name} sender result has unknown transition status: "
                f"{chain.sender_result.status}"
            )
        sender_result_issue = _cell_issue(language, chain.sender_result.cell)
        if sender_result_issue is not None:
            return f"{example.name} sender result has {sender_result_issue}"
        if chain.recipient_before is not None:
            before_issue = _cell_issue(language, chain.recipient_before)
            if before_issue is not None:
                return f"{example.name} recipient before has {before_issue}"
        if chain.recipient_result is not None:
            if chain.recipient_result.status not in transition_statuses:
                return (
                    f"{example.name} recipient result has unknown transition status: "
                    f"{chain.recipient_result.status}"
                )
            result_issue = _cell_issue(language, chain.recipient_result.cell)
            if result_issue is not None:
                return f"{example.name} recipient result has {result_issue}"
    return None


def _cell_issue(language: TransitionChainClaimLanguage, cell: Cell) -> str | None:
    roles = _allowed_set(language, "terms", "roles")
    memory = _allowed_set(language, "terms", "memory")
    automail = _allowed_set(language, "terms", "automail")
    command_messages = _allowed_set(language, "terms", "command_messages")
    signals = _allowed_set(language, "terms", "signals")
    if cell.role not in roles:
        return f"unknown role: {cell.role}"
    if cell.memory not in memory:
        return f"unknown memory: {cell.memory}"
    if cell.automail not in automail:
        return f"unknown automail: {cell.automail}"
    if cell.self_mailbox not in command_messages:
        return f"unknown self mailbox: {cell.self_mailbox}"
    channels = (*cell.upstream, *cell.input, *cell.output, *cell.control, *cell.buffer)
    for channel in channels:
        if channel not in signals:
            return f"unknown signal: {channel}"
    return None


def _allowed_set(
    language: TransitionChainClaimLanguage,
    class_name: str,
    key: str,
) -> set[Any]:
    values = _allowed_list(language, class_name, key)
    return set(values)


def _allowed_list(
    language: TransitionChainClaimLanguage,
    class_name: str,
    key: str,
) -> list[Any]:
    class_value = language.syntax_classes.get(class_name)
    if not isinstance(class_value, dict):
        return []
    values = class_value.get(key)
    if not isinstance(values, list):
        return []
    return values


def _same_set(
    subject: str,
    observed: Any,
    expected: Iterable[Any],
) -> ChainLanguageValidation:
    if not isinstance(observed, list):
        return _rejected(subject, "value must be a list")
    observed_set = set(observed)
    expected_set = set(expected)
    if observed_set != expected_set:
        return _rejected(
            subject,
            "set mismatch: "
            f"expected {_sorted_repr(expected_set)}, got {_sorted_repr(observed_set)}",
        )
    return _accepted(subject, "symbol set matches implementation")


def _sorted_repr(values: Iterable[Any]) -> str:
    return ", ".join(repr(value) for value in sorted(values, key=repr))


def _accepted(subject: str, detail: str) -> ChainLanguageValidation:
    return ChainLanguageValidation(subject=subject, accepted=True, detail=detail)


def _rejected(subject: str, detail: str) -> ChainLanguageValidation:
    return ChainLanguageValidation(subject=subject, accepted=False, detail=detail)


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_mapping(item: dict[str, Any], key: str) -> dict[str, Any]:
    value = item.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"required object field missing: {key}")
    return value
