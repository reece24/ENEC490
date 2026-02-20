from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_rules(path: str = "guidelines/rules.yaml") -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def select_actions(exposure_bands: dict[str, str], patient_flags: dict[str, bool], ruleset: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for rule in ruleset.get("rules", []):
        exposure = rule.get("exposure")
        if exposure_bands.get(exposure) not in rule.get("bands", []):
            continue
        caution = rule.get("caution", "standard")
        if caution == "elevated_only" and not any(patient_flags.values()):
            continue
        actions.append(rule)

    dedup: dict[str, dict[str, Any]] = {}
    for action in actions:
        dedup[action["id"]] = action
    return list(dedup.values())
