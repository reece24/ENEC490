from __future__ import annotations

from datetime import datetime, timezone

import requests
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential


class WeatherResult(BaseModel):
    temperature_c: float
    relative_humidity: float
    apparent_temperature_c: float | None = None
    wind_speed_kmh: float | None = None
    source: str = "Open-Meteo"
    source_url: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_iso: str | None = None


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4), reraise=True)
def get_current_weather(lat: float, lon: float, timeout_s: int = 12) -> WeatherResult:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m"
        "&hourly=temperature_2m,relative_humidity_2m&past_days=1&forecast_days=7"
        "&timezone=auto"
    )

    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    payload = response.json()
    current = payload.get("current", {})

    return WeatherResult(
        temperature_c=float(current.get("temperature_2m")),
        relative_humidity=float(current.get("relative_humidity_2m")),
        apparent_temperature_c=current.get("apparent_temperature"),
        wind_speed_kmh=current.get("wind_speed_10m"),
        source_url=url,
        last_updated_iso=current.get("time"),
    )


def get_weather_timeseries(lat: float, lon: float, timeout_s: int = 12) -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,relative_humidity_2m&past_days=1&forecast_days=7"
        "&timezone=auto"
    )
    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    payload = response.json()
    return {
        "time": payload.get("hourly", {}).get("time", []),
        "temperature_2m": payload.get("hourly", {}).get("temperature_2m", []),
        "relative_humidity_2m": payload.get("hourly", {}).get("relative_humidity_2m", []),
        "source": "Open-Meteo",
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
