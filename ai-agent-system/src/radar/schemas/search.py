from __future__ import annotations

from radar.schemas.base import RadarModel


class SearchPlan(RadarModel):
    query: str
    keywords: list[str]
    source_types: list[str]
    collection_plan: list[str]
