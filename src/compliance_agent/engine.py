from __future__ import annotations

from dataclasses import asdict

from .models import AgentResult, AuditLedger, KycDecision, VideoKycRequest
from .policies import INDIA_VCIP_POLICY


class IndiaKycAgent:
    def evaluate(self, request: VideoKycRequest) -> AgentResult:
        ledger = AuditLedger()
        rationale: list[str] = []
        citations: list[str] = [INDIA_VCIP_POLICY["policy_id"], *INDIA_VCIP_POLICY["secondary_citations"]]
        anomalies: list[str] = []
        next_actions: list[str] = []

        ledger.add(
            stage="intake",
            outcome="received",
            explanation="Structured India V-CIP session accepted for evaluation.",
            evidence={"request": request.to_safe_dict()},
        )

        missing_fields = self._detect_missing_fields(request)
        if missing_fields:
            explanation = f"Required V-CIP fields missing: {', '.join(missing_fields)}."
            ledger.add(
                stage="validation",
                outcome="missing_required_fields",
                explanation=explanation,
                evidence={"missing_fields": missing_fields},
                citation=INDIA_VCIP_POLICY["policy_id"],
            )
            next_actions.append("Collect the missing KYC session inputs and restart the assisted video-KYC flow.")
            return self._finalize(
                request=request,
                decision=KycDecision.RETRY_SESSION,
                summary="Session is incomplete and cannot be approved.",
                rationale=[explanation],
                citations=citations,
                anomalies=["incomplete_vcip_package"],
                next_actions=next_actions,
                compliance_report={"status": "incomplete_session"},
                ledger=ledger,
            )

        if request.product_type not in INDIA_VCIP_POLICY["allowed_products"]:
            ledger.add(
                stage="product_check",
                outcome="product_not_supported",
                explanation="The requested product is outside the approved automated V-CIP scope.",
                evidence={"product_type": request.product_type},
                citation=INDIA_VCIP_POLICY["policy_id"],
            )
            next_actions.append("Route onboarding to manual compliance operations.")
            return self._finalize(
                request=request,
                decision=KycDecision.ESCALATE_COMPLIANCE_REVIEW,
                summary="Session escalated because the product type is outside the automated policy scope.",
                rationale=["Unsupported onboarding product for this automated V-CIP flow."],
                citations=citations,
                anomalies=["unsupported_product_type"],
                next_actions=next_actions,
                compliance_report={"status": "unsupported_product"},
                ledger=ledger,
            )

        operational_failures = []
        if not request.consent_captured:
            operational_failures.append("missing_customer_consent")
        if not request.video_recording_available:
            operational_failures.append("missing_video_recording")
        if not request.operator_employee_id.strip():
            operational_failures.append("missing_operator_identity")

        if operational_failures:
            anomalies.extend(operational_failures)
            ledger.add(
                stage="operational_guardrails",
                outcome="mandatory_operational_control_failed",
                explanation="Mandatory V-CIP operational guardrails were not satisfied.",
                evidence={"failures": operational_failures},
                citation=INDIA_VCIP_POLICY["policy_id"],
            )
            next_actions.append("Restart V-CIP with consent capture, operator traceability, and recorded session enabled.")
            return self._finalize(
                request=request,
                decision=KycDecision.RETRY_SESSION,
                summary="Session failed mandatory operational controls and must be redone.",
                rationale=["Consent, operator traceability, and recording are hard prerequisites for this flow."],
                citations=citations,
                anomalies=sorted(set(anomalies)),
                next_actions=next_actions,
                compliance_report={"status": "operational_control_failure"},
                ledger=ledger,
            )

        doc = request.document_evidence
        doc_failures = []
        if not doc.pan_verified:
            doc_failures.append("pan_not_verified")
        if not doc.ckycr_match:
            doc_failures.append("ckyc_mismatch")
        if not doc.name_match:
            doc_failures.append("name_mismatch")
        if not doc.dob_match:
            doc_failures.append("dob_mismatch")
        if not doc.address_match:
            doc_failures.append("address_mismatch")

        ledger.add(
            stage="document_check",
            outcome="documents_evaluated",
            explanation="PAN, CKYCR, and identity attribute matching were evaluated.",
            evidence={"document_failures": doc_failures, "document_evidence": asdict(doc)},
            citation="CKYCR_KYC_RECORDS_FLOW",
        )

        if doc_failures:
            anomalies.extend(doc_failures)
            next_actions.append("Queue session for document remediation or manual compliance review.")
            return self._finalize(
                request=request,
                decision=KycDecision.ESCALATE_COMPLIANCE_REVIEW,
                summary="Session escalated because identity records are inconsistent across PAN/CKYCR/document checks.",
                rationale=["Identity document mismatches exceed the safe approval boundary."],
                citations=citations,
                anomalies=sorted(set(anomalies)),
                next_actions=next_actions,
                compliance_report={"status": "document_mismatch", "document_failures": doc_failures},
                ledger=ledger,
            )

        challenge = request.challenge_evidence
        risk = request.risk_signals

        fraud_failures = []
        if not challenge.challenge_completed:
            fraud_failures.append("challenge_not_completed")
        if challenge.challenge_latency_ms > INDIA_VCIP_POLICY["max_challenge_latency_ms"]:
            fraud_failures.append("challenge_latency_anomaly")
        if challenge.occlusion_integrity_score < INDIA_VCIP_POLICY["min_occlusion_integrity_score"]:
            fraud_failures.append("occlusion_failure")
        if challenge.prnu_consistency_score < INDIA_VCIP_POLICY["min_prnu_consistency_score"]:
            fraud_failures.append("sensor_noise_inconsistency")
        if not challenge.rppg_signal_present:
            fraud_failures.append("rppg_absent")
        if not challenge.shadow_consistency_passed:
            fraud_failures.append("shadow_geometry_failure")
        if risk.face_match_score < INDIA_VCIP_POLICY["min_face_match_score"]:
            fraud_failures.append("face_match_below_threshold")
        if risk.liveness_score < INDIA_VCIP_POLICY["min_liveness_score"]:
            fraud_failures.append("liveness_below_threshold")
        if risk.deepfake_risk_score > INDIA_VCIP_POLICY["max_deepfake_risk_score"]:
            fraud_failures.append("deepfake_risk_high")

        ledger.add(
            stage="adversarial_detection",
            outcome="challenge_and_risk_scored",
            explanation="Dynamic challenge, liveness, deepfake, PRNU, rPPG, and shadow checks were evaluated.",
            evidence={
                "challenge_evidence": asdict(challenge),
                "risk_signals": asdict(risk),
                "fraud_failures": fraud_failures,
            },
            citation=INDIA_VCIP_POLICY["policy_id"],
        )

        if fraud_failures:
            anomalies.extend(fraud_failures)
            next_actions.append("Block straight-through onboarding and transfer the session to fraud ops.")
            next_actions.append("Ask customer to retry V-CIP with a fresh challenge on a clean device/network.")
            return self._finalize(
                request=request,
                decision=KycDecision.RETRY_SESSION,
                summary="Session shows deepfake or liveness anomalies and cannot be approved automatically.",
                rationale=["The adversarial video-KYC challenge produced signals inconsistent with a genuine live user."],
                citations=citations,
                anomalies=sorted(set(anomalies)),
                next_actions=next_actions,
                compliance_report={"status": "fraud_or_liveness_risk", "fraud_failures": fraud_failures},
                ledger=ledger,
            )

        aml_failures = []
        if not risk.aml_screen_clear:
            aml_failures.append("aml_screen_not_clear")
        if risk.pep_flag:
            aml_failures.append("pep_flag")
        if risk.sanctions_flag:
            aml_failures.append("sanctions_flag")
        if request.geography not in INDIA_VCIP_POLICY["india_geo_values"]:
            aml_failures.append("non_india_geography")
        if request.language not in INDIA_VCIP_POLICY["supported_languages"]:
            aml_failures.append("unsupported_language_path")
        if risk.device_risk in {"high", "very_high"}:
            aml_failures.append("high_device_risk")

        ledger.add(
            stage="aml_and_context_check",
            outcome="aml_context_evaluated",
            explanation="AML, PEP, sanctions, geography, language, and device-risk checks were evaluated.",
            evidence={"aml_failures": aml_failures, "risk_signals": asdict(risk)},
            citation="PMLA_2002",
        )

        if aml_failures:
            anomalies.extend(aml_failures)
            next_actions.append("Send the case to compliance review with full session evidence and AML context.")
            return self._finalize(
                request=request,
                decision=KycDecision.ESCALATE_COMPLIANCE_REVIEW,
                summary="Session requires compliance review because AML, geography, or risk-context exceptions were detected.",
                rationale=["The user appears genuine, but regulatory or contextual exceptions prevent straight-through approval."],
                citations=citations,
                anomalies=sorted(set(anomalies)),
                next_actions=next_actions,
                compliance_report={"status": "aml_or_context_exception", "aml_failures": aml_failures},
                ledger=ledger,
            )

        rationale.append("PAN, CKYCR, and identity attributes are aligned.")
        rationale.append("Adversarial challenge, liveness, and deepfake checks passed.")
        rationale.append("AML and context checks are clear for India V-CIP onboarding.")
        next_actions.append("Approve the onboarding and push KYC status to downstream account-opening systems.")
        next_actions.append("Archive the video session, challenge trace, and audit log for regulatory review.")
        return self._finalize(
            request=request,
            decision=KycDecision.APPROVE_VCIP,
            summary="Session is approved for India-focused V-CIP onboarding.",
            rationale=rationale,
            citations=citations,
            anomalies=sorted(set(anomalies)),
            next_actions=next_actions,
            compliance_report={
                "status": "approved",
                "framework": INDIA_VCIP_POLICY["framework"],
                "product_type": request.product_type,
                "language": request.language,
                "deepfake_risk_score": risk.deepfake_risk_score,
            },
            ledger=ledger,
        )

    def _detect_missing_fields(self, request: VideoKycRequest) -> list[str]:
        missing = []
        for field_name, value in asdict(request).items():
            if field_name in {"notes", "tags"}:
                continue
            if value is None or value == "" or value == []:
                missing.append(field_name)
        return missing

    def _finalize(
        self,
        *,
        request: VideoKycRequest,
        decision: KycDecision,
        summary: str,
        rationale: list[str],
        citations: list[str],
        anomalies: list[str],
        next_actions: list[str],
        compliance_report: dict[str, object],
        ledger: AuditLedger,
    ) -> AgentResult:
        ledger.add(
            stage="final_decision",
            outcome=decision.value,
            explanation=summary,
            evidence={
                "rationale": rationale,
                "citations": citations,
                "anomalies": anomalies,
                "next_actions": next_actions,
                "compliance_report": compliance_report,
            },
            citation=", ".join(citations),
        )
        return AgentResult(
            session_id=request.session_id,
            decision=decision,
            summary=summary,
            rationale=rationale,
            citations=citations,
            anomalies=anomalies,
            next_actions=next_actions,
            compliance_report=compliance_report,
            audit_trail=ledger.events,
        )
