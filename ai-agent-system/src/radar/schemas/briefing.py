from __future__ import annotations

from radar.schemas.base import RadarModel
from radar.schemas.recommendation import NvidiaRecommendation


class ExecutiveBriefing(RadarModel):
    title: str
    summary: str
    classification: str
    evidence_ids: list[str]
    recommendations: list[NvidiaRecommendation]
    caveats: list[str]
    suggested_approach: str
