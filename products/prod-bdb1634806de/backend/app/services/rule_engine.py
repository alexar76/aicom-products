from typing import Dict, Any, List, Optional

class RuleEngine:
    """Deterministic rule engine mapping ATLAS evidence to hazard levels."""

    def evaluate(self, situation: Dict[str, Any], fire_weather: Dict[str, Any], nearest: Dict[str, Any]) -> Dict[str, Any]:
        hazards = []
        thresholds = []

        # Weather from fire_weather or situation
        weather_level, weather_measurement, weather_thresholds = self._evaluate_weather(fire_weather)
        hazards.append({
            "type": "WEATHER",
            "level": weather_level,
            "measurement": weather_measurement,
            "distance_km": None,
            "receipt": fire_weather.get("receipt_digest") if fire_weather else None,
            "timestamp": None,
            "is_cached": False,
            "sim": fire_weather.get("sim", False) if fire_weather else False
        })
        thresholds.extend(weather_thresholds)

        # Fire from situation or fire_weather
        fire_level, fire_measurement, fire_thresholds = self._evaluate_fire(situation, fire_weather)
        hazards.append({
            "type": "WILDFIRE",
            "level": fire_level,
            "measurement": fire_measurement,
            "distance_km": None,
            "receipt": fire_weather.get("receipt_digest") if fire_weather else None,
            "timestamp": None,
            "is_cached": False,
            "sim": fire_weather.get("sim", False) if fire_weather else False
        })
        thresholds.extend(fire_thresholds)

        # Flood from situation
        flood_level, flood_measurement, flood_thresholds = self._evaluate_flood(situation)
        hazards.append({
            "type": "FLOOD",
            "level": flood_level,
            "measurement": flood_measurement,
            "distance_km": None,
            "receipt": situation.get("receipt_digest") if situation else None,
            "timestamp": None,
            "is_cached": False,
            "sim": situation.get("sim", False) if situation else False
        })
        thresholds.extend(flood_thresholds)

        overall_level, overall_reason = self._overall(hazards)
        return {
            "overall": {"level": overall_level, "reason": overall_reason},
            "hazards": hazards,
            "thresholds": thresholds
        }

    def _evaluate_weather(self, data: Dict[str, Any]) -> tuple:
        if not data or data.get("ok") is False:
            return ("UNKNOWN", None, [{"name": "Weather data", "condition": "mesh response unavailable", "fired": False}])
        # Assume data has wind_speed_kmh, temperature_c, etc.
        wind = data.get("wind_speed_kmh", 0)
        if wind > 80:
            return ("EMERGENCY", f"Wind {wind} km/h", [{"name": "Wind speed", "condition": ">80 km/h", "fired": True}])
        elif wind > 50:
            return ("WARNING", f"Wind {wind} km/h", [{"name": "Wind speed", "condition": ">50 km/h", "fired": True}])
        elif wind > 30:
            return ("WATCH", f"Wind {wind} km/h", [{"name": "Wind speed", "condition": ">30 km/h", "fired": True}])
        else:
            return ("CALM", f"Wind {wind} km/h", [{"name": "Wind speed", "condition": "<=30 km/h", "fired": False}])

    def _evaluate_fire(self, situation: Dict[str, Any], fire_weather: Dict[str, Any]) -> tuple:
        # Use fire_weather if available, else situation
        data = fire_weather if fire_weather else situation
        if not data or data.get("ok") is False:
            return ("UNKNOWN", None, [{"name": "Fire data", "condition": "mesh response unavailable", "fired": False}])
        # Assume fire_weather has active_fires count or nearest distance
        active_fires = data.get("active_fires", 0)
        nearest_fire_km = data.get("nearest_fire_km", None)
        if nearest_fire_km is not None and nearest_fire_km < 10:
            return ("EMERGENCY", f"Fire within {nearest_fire_km} km", [{"name": "Active fire distance", "condition": "<10 km", "fired": True}])
        elif active_fires > 3:
            return ("WARNING", f"{active_fires} active fires", [{"name": "Active fires", "condition": ">3", "fired": True}])
        elif active_fires > 0:
            return ("WATCH", f"{active_fires} active fires", [{"name": "Active fires", "condition": ">0", "fired": True}])
        else:
            return ("CALM", "No active fires", [{"name": "Active fires", "condition": "=0", "fired": False}])

    def _evaluate_flood(self, situation: Dict[str, Any]) -> tuple:
        if not situation or situation.get("ok") is False:
            return ("UNKNOWN", None, [{"name": "Flood data", "condition": "mesh response unavailable", "fired": False}])
        flood_alerts = situation.get("flood_alerts", 0)
        if flood_alerts > 5:
            return ("EMERGENCY", f"{flood_alerts} flood alerts", [{"name": "Flood alerts", "condition": ">5", "fired": True}])
        elif flood_alerts > 2:
            return ("WARNING", f"{flood_alerts} flood alerts", [{"name": "Flood alerts", "condition": ">2", "fired": True}])
        elif flood_alerts > 0:
            return ("WATCH", f"{flood_alerts} flood alerts", [{"name": "Flood alerts", "condition": ">0", "fired": True}])
        else:
            return ("CALM", "No flood alerts", [{"name": "Flood alerts", "condition": "=0", "fired": False}])

    def _overall(self, hazards: List[Dict[str, Any]]) -> tuple:
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
            return ("UNKNOWN", "All hazards unknown")
        if has_unknown:
            return (max_level, "Highest hazard level is " + max_level + " (some unknowns)")
        return (max_level, "Highest hazard level determined")
