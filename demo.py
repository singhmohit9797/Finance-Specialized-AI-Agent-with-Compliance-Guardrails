from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from compliance_agent import IndiaKycAgent, VideoKycRequest
from compliance_agent.models import ChallengeEvidence, DocumentEvidence, RiskSignals


def main() -> None:
    agent = IndiaKycAgent()
    scenarios = [
        VideoKycRequest(
            session_id="VKYC-001",
            institution="BharatFin Bank",
            product_type="savings_account",
            customer_name="Aarav Sharma",
            language="Hindi",
            geography="India",
            consent_captured=True,
            video_recording_available=True,
            operator_employee_id="EMP1024",
            document_evidence=DocumentEvidence("ABCDE1234F", True, True, True, True, True, True),
            challenge_evidence=ChallengeEvidence(
                detected_object="steel bottle",
                challenge_prompt="Please lift the steel bottle and move it across your chin from left to right.",
                challenge_completed=True,
                challenge_latency_ms=890,
                occlusion_integrity_score=0.88,
                prnu_consistency_score=0.81,
                rppg_signal_present=True,
                shadow_consistency_passed=True,
            ),
            risk_signals=RiskSignals(0.93, 0.90, 0.12, True, False, False, "low"),
            notes="Clean Hindi V-CIP session for savings onboarding.",
        ),
        VideoKycRequest(
            session_id="VKYC-002",
            institution="BharatFin Bank",
            product_type="upi_limit_upgrade",
            customer_name="Neha Verma",
            language="English",
            geography="India",
            consent_captured=True,
            video_recording_available=True,
            operator_employee_id="EMP2240",
            document_evidence=DocumentEvidence("PQRSX5678K", True, True, True, True, True, True),
            challenge_evidence=ChallengeEvidence(
                detected_object="coffee mug",
                challenge_prompt="Please move the mug slowly in front of your face and look left.",
                challenge_completed=True,
                challenge_latency_ms=2480,
                occlusion_integrity_score=0.42,
                prnu_consistency_score=0.44,
                rppg_signal_present=False,
                shadow_consistency_passed=False,
            ),
            risk_signals=RiskSignals(0.77, 0.59, 0.81, True, False, False, "medium"),
            notes="Adversarial challenge indicates likely deepfake injection.",
        ),
        VideoKycRequest(
            session_id="VKYC-003",
            institution="BharatFin Bank",
            product_type="wallet_upgrade",
            customer_name="Mohammed Ali",
            language="English",
            geography="India",
            consent_captured=True,
            video_recording_available=True,
            operator_employee_id="EMP3090",
            document_evidence=DocumentEvidence("LMNOP4567Q", True, True, True, True, True, True),
            challenge_evidence=ChallengeEvidence(
                detected_object="pen",
                challenge_prompt="Please hold the pen near your cheek and rotate it slowly.",
                challenge_completed=True,
                challenge_latency_ms=980,
                occlusion_integrity_score=0.82,
                prnu_consistency_score=0.78,
                rppg_signal_present=True,
                shadow_consistency_passed=True,
            ),
            risk_signals=RiskSignals(0.91, 0.88, 0.18, True, True, False, "low"),
            notes="Session looks genuine but requires manual review due to PEP hit.",
        ),
    ]

    results = [json.loads(agent.evaluate(scenario).to_json()) for scenario in scenarios]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
