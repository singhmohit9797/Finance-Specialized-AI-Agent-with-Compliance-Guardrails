from __future__ import annotations

import os
import sys
from dataclasses import asdict
import json
from typing import Any

import gradio as gr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from compliance_agent import IndiaKycAgent
from compliance_agent.models import ChallengeEvidence, DocumentEvidence, RiskSignals, VideoKycRequest
from compliance_agent.policies import INDIA_VCIP_POLICY


AGENT = IndiaKycAgent()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, set):
        return sorted(_json_safe(v) for v in value)
    if hasattr(value, "value"):
        return str(value.value)
    return value


def _sample_payload(kind: str) -> dict[str, Any]:
    payloads = {
        "clean": {
            "session_id": "VKYC-DEMO-001",
            "institution": "BharatFin Bank",
            "product_type": "savings_account",
            "customer_name": "Aarav Sharma",
            "language": "Hindi",
            "geography": "India",
            "consent_captured": True,
            "video_recording_available": True,
            "operator_employee_id": "EMP1024",
            "pan_number_masked": "ABCDE1234F",
            "pan_verified": True,
            "aadhaar_offline_qr_verified": True,
            "ckycr_match": True,
            "name_match": True,
            "dob_match": True,
            "address_match": True,
            "detected_object": "steel bottle",
            "challenge_prompt": "Please lift the steel bottle and move it across your chin from left to right.",
            "challenge_completed": True,
            "challenge_latency_ms": 890,
            "occlusion_integrity_score": 0.88,
            "prnu_consistency_score": 0.81,
            "rppg_signal_present": True,
            "shadow_consistency_passed": True,
            "face_match_score": 0.93,
            "liveness_score": 0.90,
            "deepfake_risk_score": 0.12,
            "aml_screen_clear": True,
            "pep_flag": False,
            "sanctions_flag": False,
            "device_risk": "low",
            "notes": "Clean V-CIP onboarding session.",
        },
        "deepfake": {
            "session_id": "VKYC-DEMO-002",
            "institution": "BharatFin Bank",
            "product_type": "upi_limit_upgrade",
            "customer_name": "Neha Verma",
            "language": "English",
            "geography": "India",
            "consent_captured": True,
            "video_recording_available": True,
            "operator_employee_id": "EMP2240",
            "pan_number_masked": "PQRSX5678K",
            "pan_verified": True,
            "aadhaar_offline_qr_verified": True,
            "ckycr_match": True,
            "name_match": True,
            "dob_match": True,
            "address_match": True,
            "detected_object": "coffee mug",
            "challenge_prompt": "Move the mug in front of your face and look left.",
            "challenge_completed": True,
            "challenge_latency_ms": 2480,
            "occlusion_integrity_score": 0.42,
            "prnu_consistency_score": 0.44,
            "rppg_signal_present": False,
            "shadow_consistency_passed": False,
            "face_match_score": 0.77,
            "liveness_score": 0.59,
            "deepfake_risk_score": 0.81,
            "aml_screen_clear": True,
            "pep_flag": False,
            "sanctions_flag": False,
            "device_risk": "medium",
            "notes": "Likely deepfake attack signature.",
        },
        "pep": {
            "session_id": "VKYC-DEMO-003",
            "institution": "BharatFin Bank",
            "product_type": "wallet_upgrade",
            "customer_name": "Mohammed Ali",
            "language": "English",
            "geography": "India",
            "consent_captured": True,
            "video_recording_available": True,
            "operator_employee_id": "EMP3090",
            "pan_number_masked": "LMNOP4567Q",
            "pan_verified": True,
            "aadhaar_offline_qr_verified": True,
            "ckycr_match": True,
            "name_match": True,
            "dob_match": True,
            "address_match": True,
            "detected_object": "pen",
            "challenge_prompt": "Hold the pen near your cheek and rotate it slowly.",
            "challenge_completed": True,
            "challenge_latency_ms": 980,
            "occlusion_integrity_score": 0.82,
            "prnu_consistency_score": 0.78,
            "rppg_signal_present": True,
            "shadow_consistency_passed": True,
            "face_match_score": 0.91,
            "liveness_score": 0.88,
            "deepfake_risk_score": 0.18,
            "aml_screen_clear": True,
            "pep_flag": True,
            "sanctions_flag": False,
            "device_risk": "low",
            "notes": "Customer appears genuine but PEP workflow applies.",
        },
    }
    return payloads[kind]


def _build_request(
    session_id: str,
    institution: str,
    product_type: str,
    customer_name: str,
    language: str,
    geography: str,
    consent_captured: bool,
    video_recording_available: bool,
    operator_employee_id: str,
    pan_number_masked: str,
    pan_verified: bool,
    aadhaar_offline_qr_verified: bool,
    ckycr_match: bool,
    name_match: bool,
    dob_match: bool,
    address_match: bool,
    detected_object: str,
    challenge_prompt: str,
    challenge_completed: bool,
    challenge_latency_ms: int,
    occlusion_integrity_score: float,
    prnu_consistency_score: float,
    rppg_signal_present: bool,
    shadow_consistency_passed: bool,
    face_match_score: float,
    liveness_score: float,
    deepfake_risk_score: float,
    aml_screen_clear: bool,
    pep_flag: bool,
    sanctions_flag: bool,
    device_risk: str,
    notes: str,
) -> VideoKycRequest:
    return VideoKycRequest(
        session_id=session_id.strip(),
        institution=institution.strip(),
        product_type=product_type,
        customer_name=customer_name.strip(),
        language=language,
        geography=geography,
        consent_captured=consent_captured,
        video_recording_available=video_recording_available,
        operator_employee_id=operator_employee_id.strip(),
        document_evidence=DocumentEvidence(
            pan_number_masked=pan_number_masked.strip(),
            pan_verified=pan_verified,
            aadhaar_offline_qr_verified=aadhaar_offline_qr_verified,
            ckycr_match=ckycr_match,
            name_match=name_match,
            dob_match=dob_match,
            address_match=address_match,
        ),
        challenge_evidence=ChallengeEvidence(
            detected_object=detected_object.strip(),
            challenge_prompt=challenge_prompt.strip(),
            challenge_completed=challenge_completed,
            challenge_latency_ms=int(challenge_latency_ms),
            occlusion_integrity_score=float(occlusion_integrity_score),
            prnu_consistency_score=float(prnu_consistency_score),
            rppg_signal_present=rppg_signal_present,
            shadow_consistency_passed=shadow_consistency_passed,
        ),
        risk_signals=RiskSignals(
            face_match_score=float(face_match_score),
            liveness_score=float(liveness_score),
            deepfake_risk_score=float(deepfake_risk_score),
            aml_screen_clear=aml_screen_clear,
            pep_flag=pep_flag,
            sanctions_flag=sanctions_flag,
            device_risk=device_risk,
        ),
        notes=notes.strip(),
    )


def _evaluate(*args: Any) -> tuple[str, str, str, str, dict[str, Any], list[list[str]], dict[str, Any]]:
    request = _build_request(*args)
    result = AGENT.evaluate(request)
    result_dict = _json_safe(asdict(result))
    decision = result.decision.value
    decision_color = {
        "APPROVE_VCIP": "#1d8348",
        "RETRY_SESSION": "#b9770e",
        "ESCALATE_COMPLIANCE_REVIEW": "#b03a2e",
    }.get(decision, "#1f4e79")

    decision_html = (
        f"<div style='padding:12px;border-radius:10px;background:{decision_color};color:white;'>"
        f"<b>Decision:</b> {decision}</div>"
    )
    rationale_md = "\n".join(f"- {item}" for item in result.rationale) or "- None"
    anomalies_md = "\n".join(f"- {item}" for item in result.anomalies) or "- None"
    next_steps_md = "\n".join(f"- {item}" for item in result.next_actions) or "- None"

    audit_rows = []
    for event in result.audit_trail:
        audit_rows.append(
            [
                event.timestamp_utc,
                event.stage,
                event.outcome,
                event.citation or "",
                event.explanation,
            ]
        )

    return (
        decision_html,
        f"### Summary\n{result.summary}\n\n### Rationale\n{rationale_md}",
        f"### Anomalies\n{anomalies_md}",
        f"### Next Actions\n{next_steps_md}",
        _json_safe(result.compliance_report),
        audit_rows,
        result_dict,
    )


def _load_example(kind: str) -> list[Any]:
    p = _sample_payload(kind)
    return [
        p["session_id"],
        p["institution"],
        p["product_type"],
        p["customer_name"],
        p["language"],
        p["geography"],
        p["consent_captured"],
        p["video_recording_available"],
        p["operator_employee_id"],
        p["pan_number_masked"],
        p["pan_verified"],
        p["aadhaar_offline_qr_verified"],
        p["ckycr_match"],
        p["name_match"],
        p["dob_match"],
        p["address_match"],
        p["detected_object"],
        p["challenge_prompt"],
        p["challenge_completed"],
        p["challenge_latency_ms"],
        p["occlusion_integrity_score"],
        p["prnu_consistency_score"],
        p["rppg_signal_present"],
        p["shadow_consistency_passed"],
        p["face_match_score"],
        p["liveness_score"],
        p["deepfake_risk_score"],
        p["aml_screen_clear"],
        p["pep_flag"],
        p["sanctions_flag"],
        p["device_risk"],
        p["notes"],
    ]


def build_ui() -> gr.Blocks:
    clean = _sample_payload("clean")
    with gr.Blocks(
        title="Veritas India V-CIP",
        theme=gr.themes.Soft(primary_hue="emerald", secondary_hue="amber"),
        css="""
        .app-title {font-size: 34px; font-weight: 800; margin-bottom: 4px;}
        .app-sub {font-size: 16px; opacity: 0.9; margin-bottom: 12px;}
        """,
    ) as demo:
        gr.HTML("<div class='app-title'>Veritas India V-CIP</div><div class='app-sub'>Interactive adversarial video-KYC assistant for India-focused onboarding</div>")
        gr.Markdown(
            "**How to use:** Pick a sample case, review/edit fields, then click `Evaluate Session`."
        )

        with gr.Row():
            load_clean = gr.Button("Load Clean Case", variant="secondary")
            load_deepfake = gr.Button("Load Deepfake Attack", variant="secondary")
            load_pep = gr.Button("Load PEP Review Case", variant="secondary")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Core Session")
                session_id = gr.Textbox(label="Session ID", value=clean["session_id"])
                institution = gr.Textbox(label="Institution", value=clean["institution"])
                product_type = gr.Dropdown(
                    label="Product Type",
                    choices=sorted(INDIA_VCIP_POLICY["allowed_products"]),
                    value=clean["product_type"],
                )
                customer_name = gr.Textbox(label="Customer Name", value=clean["customer_name"])
                language = gr.Dropdown(
                    label="Language",
                    choices=sorted(INDIA_VCIP_POLICY["supported_languages"]),
                    value=clean["language"],
                )
                geography = gr.Dropdown(label="Geography", choices=["India", "IN", "Outside India"], value=clean["geography"])
                notes = gr.Textbox(label="Analyst Notes", value=clean["notes"], lines=2)

                with gr.Accordion("Operational Controls", open=False):
                    consent_captured = gr.Checkbox(label="Consent Captured", value=clean["consent_captured"])
                    video_recording_available = gr.Checkbox(label="Video Recording Available", value=clean["video_recording_available"])
                    operator_employee_id = gr.Textbox(label="Operator Employee ID", value=clean["operator_employee_id"])

                with gr.Accordion("Document Evidence", open=False):
                    pan_number_masked = gr.Textbox(label="PAN (masked)", value=clean["pan_number_masked"])
                    pan_verified = gr.Checkbox(label="PAN Verified", value=clean["pan_verified"])
                    aadhaar_offline_qr_verified = gr.Checkbox(label="Aadhaar Offline QR Verified", value=clean["aadhaar_offline_qr_verified"])
                    ckycr_match = gr.Checkbox(label="CKYCR Match", value=clean["ckycr_match"])
                    name_match = gr.Checkbox(label="Name Match", value=clean["name_match"])
                    dob_match = gr.Checkbox(label="DOB Match", value=clean["dob_match"])
                    address_match = gr.Checkbox(label="Address Match", value=clean["address_match"])

            with gr.Column(scale=1):
                gr.Markdown("### Adversarial Challenge & Risk")
                detected_object = gr.Textbox(label="Detected Object", value=clean["detected_object"])
                challenge_prompt = gr.Textbox(label="Challenge Prompt", value=clean["challenge_prompt"], lines=3)
                challenge_completed = gr.Checkbox(label="Challenge Completed", value=clean["challenge_completed"])
                challenge_latency_ms = gr.Slider(label="Challenge Latency (ms)", minimum=0, maximum=5000, step=10, value=clean["challenge_latency_ms"])
                occlusion_integrity_score = gr.Slider(label="Occlusion Integrity Score", minimum=0, maximum=1, step=0.01, value=clean["occlusion_integrity_score"])
                prnu_consistency_score = gr.Slider(label="PRNU Consistency Score", minimum=0, maximum=1, step=0.01, value=clean["prnu_consistency_score"])
                rppg_signal_present = gr.Checkbox(label="rPPG Signal Present", value=clean["rppg_signal_present"])
                shadow_consistency_passed = gr.Checkbox(label="Shadow Consistency Passed", value=clean["shadow_consistency_passed"])
                face_match_score = gr.Slider(label="Face Match Score", minimum=0, maximum=1, step=0.01, value=clean["face_match_score"])
                liveness_score = gr.Slider(label="Liveness Score", minimum=0, maximum=1, step=0.01, value=clean["liveness_score"])
                deepfake_risk_score = gr.Slider(label="Deepfake Risk Score", minimum=0, maximum=1, step=0.01, value=clean["deepfake_risk_score"])
                aml_screen_clear = gr.Checkbox(label="AML Screen Clear", value=clean["aml_screen_clear"])
                pep_flag = gr.Checkbox(label="PEP Flag", value=clean["pep_flag"])
                sanctions_flag = gr.Checkbox(label="Sanctions Flag", value=clean["sanctions_flag"])
                device_risk = gr.Dropdown(label="Device Risk", choices=["low", "medium", "high", "very_high"], value=clean["device_risk"])

        input_components = [
            session_id, institution, product_type, customer_name, language, geography,
            consent_captured, video_recording_available, operator_employee_id,
            pan_number_masked, pan_verified, aadhaar_offline_qr_verified, ckycr_match, name_match, dob_match, address_match,
            detected_object, challenge_prompt, challenge_completed, challenge_latency_ms, occlusion_integrity_score,
            prnu_consistency_score, rppg_signal_present, shadow_consistency_passed, face_match_score, liveness_score,
            deepfake_risk_score, aml_screen_clear, pep_flag, sanctions_flag, device_risk, notes
        ]

        with gr.Row():
            evaluate_btn = gr.Button("Evaluate Session", variant="primary")
            reset_btn = gr.Button("Reset to Clean Case")

        decision_html = gr.HTML(label="Decision")
        summary_md = gr.Markdown()
        anomalies_md = gr.Markdown()
        next_actions_md = gr.Markdown()
        compliance_json = gr.JSON(label="Compliance Report")
        audit_table = gr.Dataframe(
            label="Audit Trail",
            headers=["Timestamp", "Stage", "Outcome", "Citation", "Explanation"],
            datatype=["str", "str", "str", "str", "str"],
            wrap=True,
        )
        raw_json = gr.JSON(label="Raw Result JSON")

        evaluate_btn.click(
            fn=_evaluate,
            inputs=input_components,
            outputs=[decision_html, summary_md, anomalies_md, next_actions_md, compliance_json, audit_table, raw_json],
        )

        load_clean.click(fn=lambda: _load_example("clean"), outputs=input_components)
        load_deepfake.click(fn=lambda: _load_example("deepfake"), outputs=input_components)
        load_pep.click(fn=lambda: _load_example("pep"), outputs=input_components)
        reset_btn.click(fn=lambda: _load_example("clean"), outputs=input_components)

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="127.0.0.1", server_port=7860, inbrowser=False)
