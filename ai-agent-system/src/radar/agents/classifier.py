from __future__ import annotations

from radar.schemas import StartupClassification
from radar.graph.state import RadarState


def classify_startup(state: RadarState) -> StartupClassification:
    claims = state.get("claims", [])
    ai_claims = [
        claim
        for claim in claims
        if any(marker in claim.text.lower() for marker in ("ai", "ia", "llm", "machine learning"))
    ]

    if ai_claims:
        return StartupClassification(
            label="AI-Enabled",
            confidence=0.55,
            rationale="Public evidence mentions AI usage, but the MVP classifier cannot yet verify deep AI-native dependency.",
            supporting_evidence_ids=[claim.id for claim in ai_claims],
            caveats=["Replace this deterministic placeholder with a structured classifier before production use."],
        )

    return StartupClassification(
        label="Non-AI",
        confidence=0.4,
        rationale="No explicit public AI evidence was extracted by the MVP pipeline.",
        supporting_evidence_ids=[],
        caveats=["Absence of extracted evidence is not proof that the startup does not use AI."],
    )
