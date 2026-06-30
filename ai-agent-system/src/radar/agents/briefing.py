from __future__ import annotations

from radar.graph.retry_policy import MAX_COLLECTION_ATTEMPTS, has_collection_retry_limit_reached
from radar.graph.state import RadarState
from radar.schemas import ExecutiveBriefing


def generate_briefing(state: RadarState) -> ExecutiveBriefing:
    classification = state.get("classification")
    validation = state.get("validation")
    recommendations = state.get("recommendations", [])

    query = state.get("query", "analise de startup")
    title = f"Briefing: {query}"
    classification_label = classification.label if classification else "Inconclusivo"
    caveats = []
    if validation and not validation.has_minimum_evidence:
        caveats.append("Evidencias publicas validadas insuficientes para recomendacoes.")
    if has_collection_retry_limit_reached(state):
        caveats.append(
            f"Limite de tentativas de coleta atingido apos {MAX_COLLECTION_ATTEMPTS} tentativas."
        )
    caveats.extend(_collection_error_caveats(state))

    return ExecutiveBriefing(
        title=title,
        summary="Briefing automatizado gerado a partir do estado atual da pipeline.",
        classification=classification_label,
        evidence_ids=[claim.id for claim in state.get("claims", [])],
        recommendations=recommendations,
        caveats=caveats,
        suggested_approach="Revisar cobertura de evidencias antes de contato comercial ou tecnico.",
    )


def _collection_error_caveats(state: RadarState) -> list[str]:
    caveats: list[str] = []
    for error in state.get("errors", []):
        if not error.step.startswith("scraper."):
            continue
        location = f" em {error.source_url}" if error.source_url else ""
        provider = f" via {error.provider}" if error.provider else ""
        caveats.append(
            f"Aviso de coleta em {error.step}{location}{provider}: {error.message}"
        )
    return caveats
