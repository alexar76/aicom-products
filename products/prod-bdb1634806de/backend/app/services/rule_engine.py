# aicom-factory-atlas-rule-engine — vendored only (data/code untouched).
"""Map ATLAS ai-market/v2 capability payloads into Sentinel hazard levels."""

from __future__ import annotations

from typing import Any


def _score_level(score: int | float | None) -> str:
    if score is None:
        return "UNKNOWN"
    s = float(score)
    if s >= 80:
        return "EMERGENCY"
    if s >= 60:
        return "WARNING"
    if s >= 40:
        return "WATCH"
    return "CALM"


def _layer_live(coverage: dict[str, Any] | None, *names: str) -> int:
    if not isinstance(coverage, dict):
        return 0
    total = 0
    for name in names:
        block = coverage.get(name)
        if isinstance(block, dict):
            total += int(block.get("live") or block.get("with_reading") or block.get("pins") or 0)
    return total


class RuleEngine:
    """Deterministic rule engine for ATLAS situation / fire.weather / nearest payloads."""

    def evaluate(
        self,
        situation: dict[str, Any],
        fire_weather: dict[str, Any],
        nearest: dict[str, Any],
    ) -> dict[str, Any]:
        hazards: list[dict[str, Any]] = []
        thresholds: list[dict[str, Any]] = []

        weather_level, weather_measurement, weather_thresholds = self._evaluate_weather(
            fire_weather, situation
        )
        hazards.append(
            {
                "type": "WEATHER",
                "level": weather_level,
                "measurement": weather_measurement or "",
                "distance_km": 0.0,
                "receipt": (fire_weather or {}).get("receipt_digest")
                or ((fire_weather or {}).get("receipt") or {}).get("digest"),
                "timestamp": "",
                "is_cached": False,
                "sim": bool((fire_weather or {}).get("sim")),
            }
        )
        thresholds.extend(weather_thresholds)

        fire_level, fire_measurement, fire_thresholds = self._evaluate_fire(
            situation, fire_weather, nearest
        )
        hazards.append(
            {
                "type": "WILDFIRE",
                "level": fire_level,
                "measurement": fire_measurement or "",
                "distance_km": 0.0,
                "receipt": (fire_weather or {}).get("receipt_digest")
                or ((situation or {}).get("receipt") or {}).get("digest"),
                "timestamp": "",
                "is_cached": False,
                "sim": bool((fire_weather or {}).get("sim") or (situation or {}).get("sim")),
            }
        )
        thresholds.extend(fire_thresholds)

        flood_level, flood_measurement, flood_thresholds = self._evaluate_flood(situation, nearest)
        hazards.append(
            {
                "type": "FLOOD",
                "level": flood_level,
                "measurement": flood_measurement or "",
                "distance_km": 0.0,
                "receipt": ((situation or {}).get("receipt") or {}).get("digest"),
                "timestamp": "",
                "is_cached": False,
                "sim": bool((situation or {}).get("sim")),
            }
        )
        thresholds.extend(flood_thresholds)

        overall_level, overall_reason = self._overall(hazards, situation, fire_weather)
        return {
            "overall": {
                "level": overall_level,
                "reason": overall_reason,
                "receipt": ((situation or {}).get("receipt") or {}).get("digest"),
            },
            "hazards": hazards,
            "thresholds": thresholds,
        }

    def _refuse_reason(self, *payloads: dict[str, Any] | None) -> str:
        for p in payloads:
            if isinstance(p, dict) and p.get("refuse_reason"):
                return str(p.get("refuse_reason"))
        return "mesh response unavailable"

    def _evaluate_weather(
        self, fire_weather: dict[str, Any] | None, situation: dict[str, Any] | None
    ) -> tuple:
        data = fire_weather if isinstance(fire_weather, dict) else {}
        if data.get("ok") is True:
            wind = data.get("wind_speed_kmh")
            if wind is None and isinstance(data.get("weather"), dict):
                wind = data["weather"].get("wind_speed_kmh")
            if wind is not None:
                w = float(wind)
                if w > 80:
                    return ("EMERGENCY", f"Wind {w} km/h", [{"name": "Wind speed", "condition": ">80 km/h", "fired": True}])
                if w > 50:
                    return ("WARNING", f"Wind {w} km/h", [{"name": "Wind speed", "condition": ">50 km/h", "fired": True}])
                if w > 30:
                    return ("WATCH", f"Wind {w} km/h", [{"name": "Wind speed", "condition": ">30 km/h", "fired": True}])
                return ("CALM", f"Wind {w} km/h", [{"name": "Wind speed", "condition": "<=30 km/h", "fired": False}])
            score = data.get("score")
            if score is not None:
                return (
                    _score_level(score),
                    str(data.get("summary") or f"score {score}"),
                    [{"name": "ATLAS fire.weather score", "condition": "score bands", "fired": True}],
                )
        sit = situation if isinstance(situation, dict) else {}
        if sit.get("ok") is True and sit.get("score") is not None:
            return (
                _score_level(sit.get("score")),
                str(sit.get("summary") or f"score {sit.get('score')}"),
                [{"name": "ATLAS situation score", "condition": "score bands", "fired": True}],
            )
        reason = self._refuse_reason(data, sit)
        return ("UNKNOWN", reason, [{"name": "Weather data", "condition": reason, "fired": False}])

    def _evaluate_fire(
        self,
        situation: dict[str, Any] | None,
        fire_weather: dict[str, Any] | None,
        nearest: dict[str, Any] | None,
    ) -> tuple:
        for data in (fire_weather, situation, nearest):
            if not isinstance(data, dict) or data.get("ok") is not True:
                continue
            active = data.get("active_fires")
            nearest_km = data.get("nearest_fire_km")
            if active is None:
                active = _layer_live(data.get("coverage"), "effis", "fire", "wildfire")
            if nearest_km is None and isinstance(data.get("nearest"), dict):
                nearest_km = data["nearest"].get("km")
            if nearest_km is not None and float(nearest_km) < 10:
                return (
                    "EMERGENCY",
                    f"Fire within {nearest_km} km",
                    [{"name": "Active fire distance", "condition": "<10 km", "fired": True}],
                )
            if active and int(active) > 3:
                return (
                    "WARNING",
                    f"{active} active fires",
                    [{"name": "Active fires", "condition": ">3", "fired": True}],
                )
            if active and int(active) > 0:
                return (
                    "WATCH",
                    f"{active} active fires",
                    [{"name": "Active fires", "condition": ">0", "fired": True}],
                )
            if data.get("score") is not None and "effis" in str(data.get("layers") or []):
                return (
                    _score_level(data.get("score")),
                    str(data.get("summary") or "ATLAS wildfire coverage"),
                    [{"name": "ATLAS wildfire score", "condition": "score bands", "fired": True}],
                )
            return ("CALM", "No active fires", [{"name": "Active fires", "condition": "=0", "fired": False}])
        reason = self._refuse_reason(fire_weather, situation, nearest)
        return ("UNKNOWN", reason, [{"name": "Fire data", "condition": reason, "fired": False}])

    def _evaluate_flood(
        self, situation: dict[str, Any] | None, nearest: dict[str, Any] | None
    ) -> tuple:
        for data in (situation, nearest):
            if not isinstance(data, dict) or data.get("ok") is not True:
                continue
            alerts = data.get("flood_alerts")
            if alerts is None:
                alerts = _layer_live(data.get("coverage"), "flood", "alerts")
            if alerts and int(alerts) > 5:
                return ("EMERGENCY", f"{alerts} flood alerts", [{"name": "Flood alerts", "condition": ">5", "fired": True}])
            if alerts and int(alerts) > 2:
                return ("WARNING", f"{alerts} flood alerts", [{"name": "Flood alerts", "condition": ">2", "fired": True}])
            if alerts and int(alerts) > 0:
                return ("WATCH", f"{alerts} flood alerts", [{"name": "Flood alerts", "condition": ">0", "fired": True}])
            return ("CALM", "No flood alerts", [{"name": "Flood alerts", "condition": "=0", "fired": False}])
        reason = self._refuse_reason(situation, nearest)
        return ("UNKNOWN", reason, [{"name": "Flood data", "condition": reason, "fired": False}])

    def _overall(
        self,
        hazards: list[dict[str, Any]],
        situation: dict[str, Any] | None,
        fire_weather: dict[str, Any] | None,
    ) -> tuple:
        levels = {"CALM": 0, "WATCH": 1, "WARNING": 2, "EMERGENCY": 3, "UNKNOWN": -1}
        max_level = "CALM"
        max_val = -1
        has_unknown = False
        for h in hazards:
            lvl = h["level"]
            if lvl == "UNKNOWN":
                has_unknown = True
                continue
            val = levels.get(lvl, -1)
            if val > max_val:
                max_val = val
                max_level = lvl
        if has_unknown and max_val == -1:
            reason = self._refuse_reason(situation, fire_weather)
            if situation and situation.get("ok") is True and situation.get("summary"):
                return (_score_level(situation.get("score")), str(situation.get("summary")))
            return ("UNKNOWN", reason)
        if has_unknown:
            return (max_level, "Highest hazard level is " + max_level + " (some unknowns)")
        if situation and situation.get("ok") is True and situation.get("summary"):
            return (max_level, str(situation.get("summary")))
        return (max_level, "Highest hazard level determined")
