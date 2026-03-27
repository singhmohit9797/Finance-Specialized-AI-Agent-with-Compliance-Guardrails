from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from compliance_agent import IndiaKycAgent, KycDecision, VideoKycRequest
from compliance_agent.models import ChallengeEvidence, DocumentEvidence, RiskSignals


class IndiaKycAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = IndiaKycAgent()

    def test_approves_clean_india_vcip_session(self) -> None:
        request = VideoKycRequest(
            session_id="VKYC-APPROVE",
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
                "steel bottle",
                "Move the steel bottle across your chin.",
                True,
                890,
                0.88,
                0.81,
                True,
                True,
            ),
            risk_signals=RiskSignals(0.93, 0.90, 0.12, True, False, False, "low"),
        )

        result = self.agent.evaluate(request)

        self.assertEqual(result.decision, KycDecision.APPROVE_VCIP)
        self.assertIn("RBI_KYC_2016_VCIP_2025", result.citations)

    def test_retries_when_deepfake_risk_is_high(self) -> None:
        request = VideoKycRequest(
            session_id="VKYC-RETRY",
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
                "coffee mug",
                "Move the mug in front of your face.",
                True,
                2480,
                0.42,
                0.44,
                False,
                False,
            ),
            risk_signals=RiskSignals(0.77, 0.59, 0.81, True, False, False, "medium"),
        )

        result = self.agent.evaluate(request)

        self.assertEqual(result.decision, KycDecision.RETRY_SESSION)
        self.assertIn("deepfake_risk_high", result.anomalies)

    def test_escalates_when_aml_context_has_exceptions(self) -> None:
        request = VideoKycRequest(
            session_id="VKYC-ESCALATE",
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
                "pen",
                "Hold the pen near your cheek.",
                True,
                980,
                0.82,
                0.78,
                True,
                True,
            ),
            risk_signals=RiskSignals(0.91, 0.88, 0.18, True, True, False, "low"),
        )

        result = self.agent.evaluate(request)

        self.assertEqual(result.decision, KycDecision.ESCALATE_COMPLIANCE_REVIEW)
        self.assertIn("pep_flag", result.anomalies)

    def test_escalates_when_document_records_do_not_match(self) -> None:
        request = VideoKycRequest(
            session_id="VKYC-DOC",
            institution="BharatFin Bank",
            product_type="savings_account",
            customer_name="Riya Gupta",
            language="Hindi",
            geography="India",
            consent_captured=True,
            video_recording_available=True,
            operator_employee_id="EMP4081",
            document_evidence=DocumentEvidence("AAAAA1111A", True, False, False, False, True, False),
            challenge_evidence=ChallengeEvidence(
                "ID card",
                "Hold the card near your face.",
                True,
                900,
                0.85,
                0.76,
                True,
                True,
            ),
            risk_signals=RiskSignals(0.89, 0.86, 0.15, True, False, False, "low"),
        )

        result = self.agent.evaluate(request)

        self.assertEqual(result.decision, KycDecision.ESCALATE_COMPLIANCE_REVIEW)
        self.assertIn("ckyc_mismatch", result.anomalies)


if __name__ == "__main__":
    unittest.main()
