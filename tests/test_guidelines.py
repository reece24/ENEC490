from utils.citations import select_actions


def test_select_actions_matches_band_and_caution():
    ruleset = {
        "rules": [
            {"id": "r1", "exposure": "aqi", "bands": ["Unhealthy"], "caution": "standard", "action": "a"},
            {"id": "r2", "exposure": "aqi", "bands": ["Unhealthy"], "caution": "elevated_only", "action": "b"},
        ]
    }
    exposure_bands = {"aqi": "Unhealthy"}

    normal = select_actions(exposure_bands, {"high_risk": False}, ruleset)
    assert {r["id"] for r in normal} == {"r1"}

    elevated = select_actions(exposure_bands, {"high_risk": True}, ruleset)
    assert {r["id"] for r in elevated} == {"r1", "r2"}
