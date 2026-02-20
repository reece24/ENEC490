# ENEC490 — Exposome CV Modifier Dashboard

Streamlit dashboard that maps ZIP-code environmental exposures to **guideline-informed cardiovascular counseling modifiers**.

## Features
- ZIP geocoding via Zippopotam.us (no key)
- Weather + humidity + trend lines via Open-Meteo (no key)
- Air quality via AirNow when `AIRNOW_API_KEY` is configured (graceful stub if missing)
- Pollen provider stub with explicit “not configured” messaging
- Soil nitrate **beta educational proxy** tile (no fabricated nitrate values)
- Rule-based counseling overlay backed by citations in `guidelines/rules.yaml`
- Markdown export + copy-ready summary
- Unit tests for thresholds and rule selection

## Project structure

```
/app.py
/run_dashboard.py
/providers/
  air_quality.py
  pollen.py
  weather.py
  soil.py
  geocode.py
/guidelines/
  rules.yaml
/utils/
  cache.py
  thresholds.py
  citations.py
/tests/
  test_thresholds.py
  test_guidelines.py
```

## Setup

1. Use Python 3.11+
2. Install dependencies:

```bash
pip install streamlit requests pydantic tenacity pandas pytest
```

3. Configure environment variables:

```bash
cp .env.example .env
# Add AIRNOW_API_KEY to .env if available
```

4. Run app (direct Streamlit):

```bash
streamlit run app.py
```

5. Or use the launcher interface:

```bash
python run_dashboard.py
# optional: python run_dashboard.py --host 0.0.0.0 --port 8501 --no-browser
```

## Clinical safety notes
- Counseling support only; **not** diagnosis, medication dosing, or emergency triage automation.
- If symptoms are reported (dyspnea/chest pain/wheeze), app displays safety-first language and avoids intensifying recommendations.
- No PHI storage is implemented; avoid combining ZIP inputs with patient identity in external logs.
