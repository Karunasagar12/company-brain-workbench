from __future__ import annotations

import re
from hashlib import sha256

from .schemas import Approval, ApprovalOption, AuditEvent, BrainRule, CaseFacts, Decision, StoreState, now_iso


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("|".join(parts).encode("utf-8")).hexdigest()[:8]
    human = "-".join(slug(part) for part in parts if part)[:48].strip("-")
    return f"{prefix}_{human}_{digest}" if human else f"{prefix}_{digest}"


def audit(case_id: str, event_type: str, summary: str, **metadata: object) -> AuditEvent:
    return AuditEvent(
        id=stable_id("audit", case_id, event_type, str(len(summary)), now_iso()),
        case_id=case_id,
        event_type=event_type,
        summary=summary,
        metadata=metadata,
    )


def extract_facts(text: str) -> CaseFacts:
    lower = text.lower()
    if "priya" in lower:
        name = "Priya Sharma"
    elif "omar" in lower:
        name = "Omar Reyes"
    else:
        match = re.search(r"([A-Z][a-z]+\s+[A-Z][a-z]+)", text)
        name = match.group(1) if match else "Unknown Person"

    role = "Sales Engineer" if "sales engineer" in lower else "Unknown Role"
    location = "Dubai" if "dubai" in lower else "Unknown Location"
    return CaseFacts(name=name, role=role, location=location, source_text=text)


def find_matching_rule(state: StoreState, facts: CaseFacts) -> BrainRule | None:
    role = facts.role.lower()
    location = facts.location.lower()
    for rule in state.rules:
        if rule.pattern.get("role", "").lower() == role and rule.pattern.get("location", "").lower() == location:
            return rule
    return None


def create_approval(facts: CaseFacts) -> Approval:
    case_id = stable_id("case", facts.name, facts.role, facts.location)
    return Approval(
        id=stable_id("approval", facts.name, facts.role, facts.location),
        case_id=case_id,
        question="Should Sales Engineer map to Sales or Engineering for this company?",
        facts=facts,
        options=[
            ApprovalOption(
                label="Sales",
                impact=["CRM access", "sales-core group", "sales-field finance tier"],
            ),
            ApprovalOption(
                label="Engineering",
                impact=["GitHub access", "engineering-core group", "engineering-tools finance tier"],
            ),
        ],
    )


def create_rule_from_resolution(approval: Approval, decision_label: str) -> BrainRule:
    if decision_label == "Sales":
        decision = Decision(
            department="Sales",
            it_access=["sales-core", "crm-users"],
            finance_tier="sales-field",
        )
    else:
        decision = Decision(
            department="Engineering",
            it_access=["engineering-core", "github-users"],
            finance_tier="engineering-tools",
        )
    return BrainRule(
        id=stable_id("rule", approval.facts.role, approval.facts.location, decision.department),
        pattern={"role": approval.facts.role, "location": approval.facts.location},
        decision=decision,
        source_case=approval.facts.name,
    )


def process_intake(state: StoreState, text: str) -> tuple[StoreState, dict]:
    facts = extract_facts(text)
    case_id = stable_id("case", facts.name, facts.role, facts.location)
    state.audit.append(audit(case_id, "CASE_RECEIVED", f"Received workflow case for {facts.name}.", text=text))
    state.audit.append(audit(case_id, "FACTS_EXTRACTED", f"Extracted {facts.name}, {facts.role}, {facts.location}.", facts=facts.model_dump()))

    matched = find_matching_rule(state, facts)
    if matched:
        matched.times_applied += 1
        matched.last_applied_at = now_iso()
        state.audit.append(
            audit(
                case_id,
                "BRAIN_RULE_MATCHED",
                f"Matched Company Brain rule {matched.id}; auto-resolved as {matched.decision.department}.",
                rule_id=matched.id,
            )
        )
        state.audit.append(audit(case_id, "CASE_AUTO_RESOLVED", f"Auto-resolved {facts.name} without human escalation."))
        return state, {
            "status": "auto_resolved",
            "facts": facts.model_dump(),
            "matched_rule": matched.model_dump(),
            "summary": f"{facts.name} was auto-resolved to {matched.decision.department} from the Company Brain.",
        }

    if facts.role == "Sales Engineer" and facts.location == "Dubai":
        approval = create_approval(facts)
        existing = next((item for item in state.approvals if item.id == approval.id), None)
        if not existing:
            state.approvals.append(approval)
        else:
            approval = existing
        state.audit.append(
            audit(
                case_id,
                "AMBIGUITY_DETECTED",
                "Sales Engineer in Dubai can map to Sales or Engineering.",
                options=[option.model_dump() for option in approval.options],
            )
        )
        state.audit.append(audit(case_id, "APPROVAL_CREATED", f"Created approval {approval.id} for human resolution."))
        return state, {
            "status": "needs_human",
            "facts": facts.model_dump(),
            "approval": approval.model_dump(),
            "summary": "Ambiguity detected. Human resolution is required before this case can continue.",
        }

    state.audit.append(audit(case_id, "CASE_REVIEW_REQUIRED", "No confident automation rule exists for this case."))
    return state, {"status": "review_required", "facts": facts.model_dump(), "summary": "No confident automation rule exists yet."}


def resolve_approval(state: StoreState, approval_id: str, decision: str, rationale: str) -> tuple[StoreState, dict] | None:
    approval = next((item for item in state.approvals if item.id == approval_id), None)
    if approval is None:
        return None

    approval.status = "resolved"
    approval.resolution = decision
    approval.rationale = rationale
    approval.resolved_at = now_iso()

    rule = create_rule_from_resolution(approval, decision)
    existing = next((item for item in state.rules if item.id == rule.id), None)
    if existing is None:
        state.rules.append(rule)
    else:
        rule = existing

    state.audit.append(audit(approval.case_id, "HUMAN_RESOLUTION_RECORDED", f"Human resolved {approval.facts.role} as {decision}.", rationale=rationale))
    state.audit.append(audit(approval.case_id, "BRAIN_RULE_CREATED", f"Created Company Brain rule {rule.id}.", rule_id=rule.id))

    return state, {"rule_created": True, "approval": approval.model_dump(), "rule": rule.model_dump()}
