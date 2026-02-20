from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class PollenResult(BaseModel):
    configured: bool
    index_value: float | None = None
    band: str | None = None
    source: str = "Pollen provider (not configured)"
    source_url: str = "https://developers.google.com/maps/documentation/pollen"
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = "Pollen API is not configured. Add provider credentials to enable this tile."


def get_pollen(lat: float, lon: float) -> PollenResult:  # noqa: ARG001
    return PollenResult(configured=False)
