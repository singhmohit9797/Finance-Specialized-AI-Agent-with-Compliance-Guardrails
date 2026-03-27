from __future__ import annotations

INDIA_VCIP_POLICY = {
    "policy_id": "RBI_KYC_2016_VCIP_2025",
    "framework": "RBI Master Direction - Know Your Customer (KYC) Direction, 2016 (updated June 12, 2025)",
    "secondary_citations": [
        "PMLA_2002",
        "CKYCR_KYC_RECORDS_FLOW",
        "UIDAI_OFFLINE_AADHAAR_SECURE_QR",
    ],
    "allowed_products": {"savings_account", "upi_limit_upgrade", "wallet_upgrade", "current_account"},
    "min_face_match_score": 0.82,
    "min_liveness_score": 0.75,
    "max_deepfake_risk_score": 0.35,
    "min_occlusion_integrity_score": 0.70,
    "max_challenge_latency_ms": 1800,
    "min_prnu_consistency_score": 0.68,
    "supported_languages": {"English", "Hindi", "Tamil", "Telugu", "Bengali", "Marathi"},
    "india_geo_values": {"India", "IN"},
}
