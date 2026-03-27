from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any


class KycDecision(str, Enum):
    APPROVE_VCIP = "APPROVE_VCIP"
    RETRY_SESSION = "RETRY_SESSION"
    ESCALATE_COMPLIANCE_REVIEW = "ESCALATE_COMPLIANCE_REVIEW"


@dataclass(slots=True)
class DocumentEvidence:
    pan_number_masked: str
    pan_verified: bool
    aadhaar_offline_qr_verified: bool
    ckycr_match: bool
    name_match: bool
    dob_match: bool
    address_match: bool


@dataclass(slots=True)
class ChallengeEvidence:
    detected_object: str
    challenge_prompt: str
    challenge_completed: bool
    challenge_latency_ms: int
    occlusion_integrity_score: float
    prnu_consistency_score: float
    rppg_signal_present: bool
    shadow_consistency_passed: bool


@dataclass(slots=True)
class RiskSignals:
    face_match_score: float
    liveness_score: float
    deepfake_risk_score: float
    aml_screen_clear: bool
    pep_flag: bool
    sanctions_flag: bool
    device_risk: str


@dataclass(slots=True)
class VideoKycRequest:
    session_id: str
    institution: str
    product_type: str
    customer_name: str
    language: str
    geography: str
    consent_captured: bool
    video_recording_available: bool
    operator_employee_id: str
    document_evidence: DocumentEvidence
    challenge_evidence: ChallengeEvidence
    risk_signals: RiskSignals
    notes: str = ""
    tags: list[str] = field(default_factory=list)

    def to_safe_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuditEvent:
    timestamp_utc: str
    stage: str
    outcome: str
    explanation: str
    evidence: dict[str, Any]
    citation: str | None
    previous_hash: str
    current_hash: str


@dataclass(slots=True)
class AgentResult:
    session_id: str
    decision: KycDecision
    summary: str
    rationale: list[str]
    citations: list[str]
    anomalies: list[str]
    next_actions: list[str]
    compliance_report: dict[str, Any]
    audit_trail: list[AuditEvent]

    def to_json(self) -> str:
        def _default(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if hasattr(value, "__dict__"):
                return value.__dict__
            return str(value)

        return json.dumps(asdict(self), indent=2, default=_default)


class AuditLedger:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> list[AuditEvent]:
        return list(self._events)

    def add(
        self,
        *,
        stage: str,
        outcome: str,
        explanation: str,
        evidence: dict[str, Any],
        citation: str | None = None,
    ) -> None:
        previous_hash = self._events[-1].current_hash if self._events else "GENESIS"
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        normalized_evidence = self._normalize(evidence)
        payload = {
            "timestamp_utc": timestamp_utc,
            "stage": stage,
            "outcome": outcome,
            "explanation": explanation,
            "evidence": normalized_evidence,
            "citation": citation,
            "previous_hash": previous_hash,
        }
        current_hash = sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        self._events.append(
            AuditEvent(
                timestamp_utc=timestamp_utc,
                stage=stage,
                outcome=outcome,
                explanation=explanation,
                evidence=normalized_evidence,
                citation=citation,
                previous_hash=previous_hash,
                current_hash=current_hash,
            )
        )

    def _normalize(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._normalize(inner) for key, inner in value.items()}
        if isinstance(value, list):
            return [self._normalize(item) for item in value]
        if isinstance(value, tuple):
            return [self._normalize(item) for item in value]
        if isinstance(value, set):
            return sorted(self._normalize(item) for item in value)
        return value
