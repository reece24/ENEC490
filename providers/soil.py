from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SoilProxyResult(BaseModel):
    label: str
    risk_band: str
    source: str
    source_url: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str


def get_soil_nitrate_proxy(lat: float, lon: float) -> SoilProxyResult:  # noqa: ARG001
    return SoilProxyResult(
        label="Agricultural runoff risk index (educational proxy)",
        risk_band="Beta",
        source="USDA/NRCS concept placeholder",
        source_url="https://www.nrcs.usda.gov/",
        notes=(
            "Real-time public soil nitrate APIs are not widely available by ZIP. "
            "This tile is educational and should not be used as a measured nitrate value."
        ),
    )
