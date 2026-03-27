# Veritas India V-CIP Agent

An India-centric, domain-specialized AI agent for adversarial video KYC (V-CIP) with compliance guardrails, deepfake-risk scoring, and auditable decisions.

This project converts the Veritas / G-AKYC idea into a practical onboarding workflow agent for banks and fintech teams.

## Why this project

Modern KYC attacks increasingly use real-time deepfakes and avatar overlays. Static liveness checks are often predictable. This agent uses dynamic challenge-response signals and policy guardrails to make onboarding decisions safer and more auditable.

## What it does

The agent processes a structured V-CIP session and returns:

- `APPROVE_VCIP`
- `RETRY_SESSION`
- `ESCALATE_COMPLIANCE_REVIEW`

Each output includes:

- rationale
- anomaly list
- next actions
- compliance report
- immutable audit trail (hash-chained events)

## India-centric controls

The workflow is modeled around India onboarding contexts and control expectations:

- PAN verification
- Aadhaar offline QR verification
- CKYCR consistency checks
- consent + session recording + operator traceability
- AML / PEP / sanctions checks
- India geography and language path checks

## Adversarial deepfake signals

The engine supports challenge-response style risk features inspired by your Veritas concept:

- dynamic object-based challenge prompt
- challenge latency
- occlusion integrity score
- PRNU consistency score
- rPPG presence
- shadow consistency
- face match, liveness, and deepfake risk score

## Interactive GUI (Gradio)

The app uses Gradio for a more interactive and judge-friendly experience:

- one-click sample cases (`Clean`, `Deepfake Attack`, `PEP Review`)
- guided form sections
- simple decision cards
- audit table and full raw JSON output

## Quick start

```bash
python -m pip install -r requirements.txt
python app.py
```

Open the local URL shown in terminal (typically `http://127.0.0.1:7860`).

## Demo + tests

Run sample sessions:

```bash
python demo.py
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
app.py
demo.py
requirements.txt
src/compliance_agent/
  __init__.py
  engine.py
  models.py
  policies.py
tests/test_agent.py
```

## Example outcomes

- Clean session -> `APPROVE_VCIP`
- Deepfake-like session -> `RETRY_SESSION`
- Genuine but PEP/AML exception -> `ESCALATE_COMPLIANCE_REVIEW`

## Notes

- This is a competition prototype focused on workflow, controls, and auditability.
- It is not legal advice and not production compliance software.
- Policy thresholds are intentionally conservative and route uncertain cases to manual review.
