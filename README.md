# Veritas India V-CIP Agent

India-centric AI agent for **Video KYC (V-CIP)** with adversarial deepfake checks, compliance guardrails, deterministic decisions, and audit-ready traces.

## Overview

Veritas evaluates a structured V-CIP session and returns one of:

- `APPROVE_VCIP`
- `RETRY_SESSION`
- `ESCALATE_COMPLIANCE_REVIEW`

The engine combines:

- **Adversarial challenge-response signals** (latency, occlusion, PRNU, rPPG, shadow consistency)
- **Identity and compliance controls** (PAN, Aadhaar offline QR, CKYCR, AML/PEP/sanctions, consent/recording/operator traceability)
- **Policy thresholds** in a centralized policy module
- **Hash-chained audit events** for every decision stage

## Repository Structure

```text
.
├─ app.py                         # Gradio UI (interactive demo and analyst workflow)
├─ demo.py                        # Scripted scenarios (approve / retry / escalate)
├─ requirements.txt
├─ src/
│  └─ compliance_agent/
│     ├─ __init__.py
│     ├─ engine.py                # Decision engine
│     ├─ models.py                # Typed request/result models + audit ledger
│     └─ policies.py              # India V-CIP policy thresholds and citations
└─ tests/
   └─ test_agent.py               # Unit tests for decision paths
```

## Architecture

```text
+------------------------------+
|        Gradio UI (app.py)    |
|  - Analyst inputs            |
|  - Sample scenarios          |
+--------------+---------------+
               |
               v
+------------------------------+
|  VideoKycRequest (models.py) |
|  - DocumentEvidence          |
|  - ChallengeEvidence         |
|  - RiskSignals               |
+--------------+---------------+
               |
               v
+------------------------------+
| IndiaKycAgent.evaluate()     |
| (engine.py)                  |
| 1) Intake + validation       |
| 2) Product scope             |
| 3) Operational guardrails    |
| 4) Document checks           |
| 5) Adversarial detection     |
| 6) AML/context checks        |
| 7) Final decision            |
+--------------+---------------+
               |
               v
+------------------------------+
| AgentResult                  |
| - decision                   |
| - rationale / anomalies      |
| - next actions               |
| - compliance_report          |
| - audit_trail (hash-chained) |
+------------------------------+
```

## Data Flow

1. UI captures session data (customer, product, docs, challenge signals, risk signals).
2. Data is normalized into `VideoKycRequest`.
3. `IndiaKycAgent` evaluates controls in deterministic stages.
4. On each stage, an `AuditEvent` is appended with:
   - timestamp
   - stage
   - outcome
   - explanation
   - evidence
   - citation
   - previous hash / current hash
5. Engine returns `AgentResult` for UI rendering and downstream integration.

## Decision Logic (Current Policy)

Implemented in `src/compliance_agent/policies.py` and applied in `engine.py`:

- Product must be in allowed set:
  - `savings_account`, `upi_limit_upgrade`, `wallet_upgrade`, `current_account`
- Hard operational prerequisites:
  - consent captured
  - video recording available
  - operator employee id present
- Document consistency checks:
  - PAN verified
  - CKYCR match
  - name / DOB / address match
- Adversarial/deepfake thresholds:
  - face match `>= 0.82`
  - liveness `>= 0.75`
  - deepfake risk `<= 0.35`
  - occlusion integrity `>= 0.70`
  - challenge latency `<= 1800 ms`
  - PRNU consistency `>= 0.68`
  - rPPG present
  - shadow consistency passed
- AML/context escalation checks:
  - AML clear
  - no PEP/sanctions flag
  - geography in `{India, IN}`
  - supported language
  - device risk not `high`/`very_high`

## Real vs Simulated Components

| Component | Status |
|---|---|
| Deterministic decision engine (`engine.py`) | **Real (implemented)** |
| Typed models + audit chaining (`models.py`) | **Real (implemented)** |
| Policy thresholding (`policies.py`) | **Real (implemented)** |
| Interactive analyst UI (`app.py`) | **Real (implemented)** |
| PAN / Aadhaar / CKYCR live verification APIs | **Simulated input signals** |
| AML / PEP / sanctions live screening integrations | **Simulated input signals** |
| Deepfake model inference (video processing pipeline) | **Simulated input signals** |
| Production persistence / queueing / auth / RBAC | **Not implemented in this repo** |

## Example Input JSON

```json
{
  "session_id": "VKYC-001",
  "institution": "BharatFin Bank",
  "product_type": "savings_account",
  "customer_name": "Aarav Sharma",
  "language": "Hindi",
  "geography": "India",
  "consent_captured": true,
  "video_recording_available": true,
  "operator_employee_id": "EMP1024",
  "document_evidence": {
    "pan_number_masked": "ABCDE1234F",
    "pan_verified": true,
    "aadhaar_offline_qr_verified": true,
    "ckycr_match": true,
    "name_match": true,
    "dob_match": true,
    "address_match": true
  },
  "challenge_evidence": {
    "detected_object": "steel bottle",
    "challenge_prompt": "Please lift the steel bottle and move it across your chin from left to right.",
    "challenge_completed": true,
    "challenge_latency_ms": 890,
    "occlusion_integrity_score": 0.88,
    "prnu_consistency_score": 0.81,
    "rppg_signal_present": true,
    "shadow_consistency_passed": true
  },
  "risk_signals": {
    "face_match_score": 0.93,
    "liveness_score": 0.90,
    "deepfake_risk_score": 0.12,
    "aml_screen_clear": true,
    "pep_flag": false,
    "sanctions_flag": false,
    "device_risk": "low"
  },
  "notes": "Clean Hindi V-CIP session for savings onboarding."
}
```

## Example Output JSON (Truncated)

```json
{
  "session_id": "VKYC-001",
  "decision": "APPROVE_VCIP",
  "summary": "Session is approved for India-focused V-CIP onboarding.",
  "rationale": [
    "PAN, CKYCR, and identity attributes are aligned.",
    "Adversarial challenge, liveness, and deepfake checks passed.",
    "AML and context checks are clear for India V-CIP onboarding."
  ],
  "citations": [
    "RBI_KYC_2016_VCIP_2025",
    "PMLA_2002",
    "CKYCR_KYC_RECORDS_FLOW",
    "UIDAI_OFFLINE_AADHAAR_SECURE_QR"
  ],
  "anomalies": [],
  "next_actions": [
    "Approve the onboarding and push KYC status to downstream account-opening systems.",
    "Archive the video session, challenge trace, and audit log for regulatory review."
  ],
  "compliance_report": {
    "status": "approved",
    "framework": "RBI Master Direction - Know Your Customer (KYC) Direction, 2016 (updated June 12, 2025)",
    "product_type": "savings_account",
    "language": "Hindi",
    "deepfake_risk_score": 0.12
  }
}
```

## Local Development

### Prerequisites

- Python 3.10+ (recommended)

### Setup

```bash
python -m pip install -r requirements.txt
```

### Run Gradio UI

```bash
python app.py
```

Open the URL shown in terminal (default: `http://127.0.0.1:7860`).

### Run Demo Scenarios

```bash
python demo.py
```

### Run Tests

```bash
python -m unittest discover -s tests -v
```

## Developer Notes

- Core integration point: `IndiaKycAgent.evaluate(request)`
- To add policies/thresholds, update `INDIA_VCIP_POLICY` in `policies.py`
- Keep new checks stage-based and auditable (append `AuditEvent` at each stage)
- Prefer deterministic, explainable conditions for compliance workflows

## Disclaimer

This repository is a **prototype decision-support workflow** for experimentation and hackathon use.  
It is **not legal advice** and **not production-ready compliance software** without institutional validation, policy/legal review, and secure systems integration.
