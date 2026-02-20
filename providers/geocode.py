from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class GeocodeResult(BaseModel):
    zip_code: str
    latitude: float
    longitude: float
    city: Optional[str] = None
    state: Optional[str] = None
    source: str = "Zippopotam.us"
    source_url: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
def geocode_zip(zip_code: str, timeout_s: int = 10) -> GeocodeResult:
    url = f"https://api.zippopotam.us/us/{zip_code}"
    response = requests.get(url, timeout=timeout_s)
    if response.status_code == 404:
        raise ValueError(f"ZIP code {zip_code} was not found.")
    response.raise_for_status()

    payload = response.json()
    place = payload.get("places", [{}])[0]

    return GeocodeResult(
        zip_code=payload.get("post code", zip_code),
        latitude=float(place.get("latitude")),
        longitude=float(place.get("longitude")),
        city=place.get("place name"),
        state=place.get("state abbreviation"),
        source_url=url,
    )
