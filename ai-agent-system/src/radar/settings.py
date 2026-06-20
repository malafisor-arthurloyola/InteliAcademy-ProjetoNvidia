from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ProviderMode = Literal["fixture", "external"]
SearchProviderName = Literal["fixture", "serpapi"]
PageProviderName = Literal["fixture", "firecrawl"]


class RadarSettings(BaseSettings):
    """Runtime settings with external providers disabled by default."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RADAR_",
        extra="ignore",
    )

    enable_external_providers: bool = False
    search_provider: SearchProviderName = "fixture"
    page_provider: PageProviderName = "fixture"
    provider_timeout_seconds: int = Field(default=10, ge=1, le=120)

    serpapi_api_key: str | None = Field(default=None, validation_alias="SERPAPI_API_KEY")
    firecrawl_api_key: str | None = Field(default=None, validation_alias="FIRECRAWL_API_KEY")

    @property
    def provider_mode(self) -> ProviderMode:
        if self.enable_external_providers:
            return "external"
        return "fixture"


@lru_cache
def get_settings() -> RadarSettings:
    return RadarSettings()