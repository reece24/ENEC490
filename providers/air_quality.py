from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class AirQualityResult(BaseModel):
    configured: bool
    aqi: int | None = None
    aqi_category: str | None = None
    primary_pollutant: str | None = None
    pm25_aqi: int | None = None
    ozone_aqi: int | None = None
    observations: list[dict[str, Any]] = Field(default_factory=list)
    source: str
    source_url: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: str | None = None


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
def get_air_quality(zip_code: str, timeout_s: int = 12) -> AirQualityResult:
    api_key = os.getenv("AIRNOW_API_KEY")
    if not api_key:
        return AirQualityResult(
            configured=False,
            source="AirNow",
            source_url="https://docs.airnowapi.org/",
            message="AIRNOW_API_KEY not set. Air quality provider not configured.",
        )

    url = (
        "https://www.airnowapi.org/aq/observation/zipCode/current/"
        f"?format=application/json&zipCode={zip_code}&distance=25&API_KEY={api_key}"
    )
    response = requests.get(url, timeout=timeout_s)
    if response.status_code == 429:
        return AirQualityResult(
            configured=True,
            source="AirNow",
            source_url="https://docs.airnowapi.org/",
            message="AirNow rate limited this request. Please retry shortly.",
        )
    response.raise_for_status()

    observations: list[dict[str, Any]] = response.json()
    if not observations:
        return AirQualityResult(
            configured=True,
            source="AirNow",
            source_url=url,
            message="No air quality observations returned for this ZIP.",
        )

    sorted_obs = sorted(observations, key=lambda o: o.get("AQI", -1), reverse=True)
    top = sorted_obs[0]

    pm25_aqi = None
    ozone_aqi = None
    for obs in observations:
        param = (obs.get("ParameterName") or "").lower()
        if "pm2.5" in param:
            pm25_aqi = obs.get("AQI")
        if param in {"o3", "ozone"}:
            ozone_aqi = obs.get("AQI")

    return AirQualityResult(
        configured=True,
        aqi=top.get("AQI"),
        aqi_category=top.get("Category", {}).get("Name"),
        primary_pollutant=top.get("ParameterName"),
        pm25_aqi=pm25_aqi,
        ozone_aqi=ozone_aqi,
        observations=observations,
        source="AirNow",
        source_url=url,
    )
