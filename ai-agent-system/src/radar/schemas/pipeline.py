from __future__ import annotations

from radar.schemas.base import IdentifiedModel


class PipelineError(IdentifiedModel):
    step: str
    message: str
    recoverable: bool = True
