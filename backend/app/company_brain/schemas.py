from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class IntakeRequest(BaseModel):
    text: str = Field(min_length=3, max_length=2000)

    @field_validator("text")
    @classmethod
    def reject_control_heavy_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("text must not be blank")
        control_count = sum(1 for char in cleaned if ord(char) < 32 and char not in "\n\t\r")
        if control_count:
            raise ValueError("text contains unsupported control characters")
        return cleaned


class ResolveApprovalRequest(BaseModel):
    decision: Literal["Sales", "Engineering"]
    rationale: str = Field(min_length=3, max_length=500)


class CaseFacts(BaseModel):
    name: str
    role: str
    location: str
    source_text: str


class Decision(BaseModel):
    department: str
    it_access: list[str]
    finance_tier: str


class BrainRule(BaseModel):
    id: str
    pattern: dict[str, str]
    decision: Decision
    source_case: str
    created_by: str = "human"
    created_at: str = Field(default_factory=now_iso)
    times_applied: int = 0
    last_applied_at: str | None = None


class ApprovalOption(BaseModel):
    label: Literal["Sales", "Engineering"]
    impact: list[str]


class Approval(BaseModel):
    id: str
    case_id: str
    question: str
    facts: CaseFacts
    options: list[ApprovalOption]
    status: Literal["pending", "resolved"] = "pending"
    created_at: str = Field(default_factory=now_iso)
    resolved_at: str | None = None
    resolution: str | None = None
    rationale: str | None = None


class AuditEvent(BaseModel):
    id: str
    case_id: str
    event_type: str
    summary: str
    timestamp: str = Field(default_factory=now_iso)
    metadata: dict = Field(default_factory=dict)


class StoreState(BaseModel):
    rules: list[BrainRule] = Field(default_factory=list)
    approvals: list[Approval] = Field(default_factory=list)
    audit: list[AuditEvent] = Field(default_factory=list)
