from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd
import streamlit as st

from providers.air_quality import get_air_quality
from providers.geocode import geocode_zip
from providers.pollen import get_pollen
from providers.soil import get_soil_nitrate_proxy
from providers.weather import get_current_weather, get_weather_timeseries
from utils.citations import load_rules, select_actions
from utils.thresholds import aqi_to_band, heat_index_band, pollen_to_band

st.set_page_config(page_title="Exposome CV Modifier Dashboard", layout="wide")


@st.cache_data(ttl=900, show_spinner=False)
def cached_geocode(zip_code: str):
    return geocode_zip(zip_code)


@st.cache_data(ttl=900, show_spinner=False)
def cached_weather(lat: float, lon: float):
    return get_current_weather(lat, lon)


@st.cache_data(ttl=900, show_spinner=False)
def cached_weather_ts(lat: float, lon: float):
    return get_weather_timeseries(lat, lon)


@st.cache_data(ttl=900, show_spinner=False)
def cached_air(zip_code: str):
    return get_air_quality(zip_code)


@st.cache_data(ttl=900, show_spinner=False)
def cached_pollen(lat: float, lon: float):
    return get_pollen(lat, lon)


@st.cache_data(ttl=900, show_spinner=False)
def cached_soil(lat: float, lon: float):
    return get_soil_nitrate_proxy(lat, lon)


st.title("Exposome CV Modifier Dashboard")
st.warning(
    "Clinical decision support disclaimer: This dashboard provides environmental counseling modifiers only. "
    "It does not diagnose disease, dose medications, or replace clinical judgment. No PHI is stored."
)

with st.sidebar:
    st.header("Inputs")
    zip_code = st.text_input("US ZIP code", max_chars=5, placeholder="e.g., 02139")

    st.subheader("Patient context (optional)")
    asthma_copd = st.toggle("Asthma/COPD", value=False)
    ascvd = st.toggle("Known ASCVD", value=False)
    pregnancy = st.toggle("Pregnancy", value=False)
    outdoor_worker = st.toggle("Outdoor worker", value=False)
    statin_on = st.toggle("On statin", value=False)
    high_risk = st.toggle("High-risk (diabetes/CKD)", value=False)

    activity_level = st.selectbox("Activity level today", ["low", "moderate", "vigorous"])
    has_symptoms = st.radio("Has symptoms today? (dyspnea/chest pain/wheeze)", ["no", "yes"], horizontal=True)

    run = st.button("Generate dashboard", type="primary")

if not run:
    st.info("Enter a ZIP code and click **Generate dashboard**.")
    st.stop()

if not zip_code or len(zip_code) != 5 or not zip_code.isdigit():
    st.error("Please enter a valid 5-digit US ZIP code.")
    st.stop()

if has_symptoms == "yes":
    st.error(
        "Symptoms reported today. Prioritize clinical evaluation and follow emergency guidance for severe symptoms "
        "(e.g., chest pain, severe shortness of breath). Recommendations below will remain safety-focused."
    )

try:
    geo = cached_geocode(zip_code)
except Exception as exc:  # noqa: BLE001
    st.error(f"Failed to geocode ZIP code: {exc}")
    st.stop()

try:
    weather = cached_weather(geo.latitude, geo.longitude)
    weather_ts = cached_weather_ts(geo.latitude, geo.longitude)
except Exception as exc:  # noqa: BLE001
    st.error(f"Failed to fetch weather data: {exc}")
    st.stop()

try:
    air = cached_air(zip_code)
except Exception as exc:  # noqa: BLE001
    st.warning(f"Air quality lookup failed: {exc}")
    air = None

pollen = cached_pollen(geo.latitude, geo.longitude)
soil = cached_soil(geo.latitude, geo.longitude)

heat_index_f, heat_band = heat_index_band(weather.temperature_c, weather.relative_humidity)
aqi_band = aqi_to_band(air.aqi if air else None)
pollen_band = pollen_to_band(pollen.index_value)

exposure_bands = {
    "aqi": aqi_band,
    "pollen": pollen_band,
    "heat": heat_band,
}

patient_flags = {
    "asthma_copd": asthma_copd,
    "ascvd": ascvd,
    "pregnancy": pregnancy,
    "outdoor_worker": outdoor_worker,
    "statin_on": statin_on,
    "high_risk": high_risk,
}

ruleset = load_rules()
actions = select_actions(exposure_bands, patient_flags, ruleset)

st.subheader("Environmental Snapshot")
col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("AQI category", aqi_band)
col2.metric("PM2.5 AQI", air.pm25_aqi if air and air.pm25_aqi is not None else "n/a")
col3.metric("Ozone AQI", air.ozone_aqi if air and air.ozone_aqi is not None else "n/a")
col4.metric("Pollen index", pollen.band or "Not configured")
col5.metric("Temp / RH", f"{weather.temperature_c:.1f}°C / {weather.relative_humidity:.0f}%")
col6.metric("Soil nitrate proxy", soil.risk_band)

st.caption(
    f"Location: {geo.city or ''}, {geo.state or ''} ({geo.latitude:.3f}, {geo.longitude:.3f}) | "
    f"Last updated (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
)

st.subheader("Trend view (weather 24h + 7d)")
weather_df = pd.DataFrame(
    {
        "time": weather_ts["time"],
        "temperature_c": weather_ts["temperature_2m"],
        "humidity": weather_ts["relative_humidity_2m"],
    }
)
if not weather_df.empty:
    weather_df["time"] = pd.to_datetime(weather_df["time"])
    st.line_chart(weather_df.set_index("time")[["temperature_c", "humidity"]])
else:
    st.info("Weather time series unavailable; showing current values only.")

st.subheader("Guideline overlay: counseling modifiers")
if not actions:
    st.info("No triggered guideline modifiers for current bands. Continue routine prevention counseling.")

for action in actions:
    st.markdown(f"- **{action['action']}**")
    for cite in action.get("citations", []):
        st.markdown(f"  - Citation: [{cite['org']} {cite['year']} — {cite['title']}]({cite['url']})")

if has_symptoms == "yes":
    st.warning("Symptom flag is ON: recommendations are intentionally not intensified beyond immediate safety language.")

st.subheader("Environmental Modifiers Summary")
summary_lines = [
    f"- Today in ZIP {zip_code}, AQI band is **{aqi_band}**, pollen is **{pollen_band}**, and heat risk is **{heat_band}** (heat index ~{heat_index_f}°F).",
    f"- Activity guidance for {activity_level} activity: prioritize lower exposure windows and indoor alternatives when outdoor air/heat risk is elevated.",
]
if actions:
    summary_lines.extend([f"- {a['action']}" for a in actions])

summary_lines.append(
    "\n**Why this matters:** Air pollution and heat stress are associated with higher short-term cardiovascular strain and event risk; "
    "counseling on exposure reduction aligns with AHA/ACC prevention principles and AHA scientific statements."
)

summary_lines.append("\n**Data provenance:**")
summary_lines.append(f"- Geocoding: {geo.source} ({geo.source_url}) at {geo.fetched_at.isoformat()}")
summary_lines.append(f"- Weather: {weather.source} ({weather.source_url}) at {weather.fetched_at.isoformat()}")
if air:
    summary_lines.append(f"- Air quality: {air.source} ({air.source_url}) at {air.fetched_at.isoformat()}")
summary_lines.append(f"- Pollen: {pollen.source} ({pollen.source_url}) at {pollen.fetched_at.isoformat()}")
summary_lines.append(f"- Soil proxy: {soil.source} ({soil.source_url}) at {soil.fetched_at.isoformat()}")

summary_md = "\n".join(summary_lines)
st.markdown(summary_md)

st.download_button(
    label="Download summary (Markdown)",
    data=summary_md,
    file_name=f"exposome_cv_modifier_{zip_code}.md",
    mime="text/markdown",
)
st.text_area("Copy-to-clipboard summary", value=summary_md, height=220)

with st.expander("Raw exposure data + sources"):
    st.json(
        {
            "geocode": geo.model_dump(mode="json"),
            "weather": weather.model_dump(mode="json"),
            "air_quality": air.model_dump(mode="json") if air else None,
            "pollen": pollen.model_dump(mode="json"),
            "soil_proxy": soil.model_dump(mode="json"),
        }
    )

map_df = pd.DataFrame({"lat": [geo.latitude], "lon": [geo.longitude]})
st.map(map_df, zoom=9)
