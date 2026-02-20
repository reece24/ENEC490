from utils.thresholds import aqi_to_band, heat_index_band, pollen_to_band


def test_aqi_to_band():
    assert aqi_to_band(40) == "Good"
    assert aqi_to_band(75) == "Moderate"
    assert aqi_to_band(120) == "USG"
    assert aqi_to_band(175) == "Unhealthy"


def test_pollen_to_band():
    assert pollen_to_band(1.0) == "Low"
    assert pollen_to_band(3.2) == "Moderate"
    assert pollen_to_band(6.8) == "High"


def test_heat_index_band():
    hi, band = heat_index_band(33.0, 65.0)
    assert hi >= 90
    assert band in {"High", "Very High", "Extreme"}
