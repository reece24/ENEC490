from __future__ import annotations

def aqi_to_band(aqi: int | None) -> str:
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "USG"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


def pollen_to_band(value: float | None) -> str:
    if value is None:
        return "Unknown"
    if value < 2.5:
        return "Low"
    if value < 5:
        return "Moderate"
    if value < 7.5:
        return "High"
    return "Very High"


def c_to_f(temp_c: float) -> float:
    return temp_c * 9 / 5 + 32


def compute_heat_index_f(temp_f: float, rh: float) -> float:
    if temp_f < 80:
        return temp_f
    hi = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * rh
        - 0.22475541 * temp_f * rh
        - 0.00683783 * temp_f**2
        - 0.05481717 * rh**2
        + 0.00122874 * temp_f**2 * rh
        + 0.00085282 * temp_f * rh**2
        - 0.00000199 * temp_f**2 * rh**2
    )
    return round(hi, 1)


def heat_index_band(temp_c: float, rh: float) -> tuple[float, str]:
    temp_f = c_to_f(temp_c)
    hi = compute_heat_index_f(temp_f, rh)
    if hi < 80:
        return hi, "Low"
    if hi < 90:
        return hi, "Moderate"
    if hi < 103:
        return hi, "High"
    if hi < 125:
        return hi, "Very High"
    return hi, "Extreme"


def risk_score(bands: list[str]) -> str:
    order = ["Unknown", "Low", "Good", "Moderate", "USG", "High", "Unhealthy", "Very High", "Very Unhealthy", "Hazardous", "Extreme"]
    idx = max((order.index(b) for b in bands if b in order), default=0)
    if idx >= order.index("Unhealthy"):
        return "High"
    if idx >= order.index("Moderate"):
        return "Moderate"
    return "Low"
