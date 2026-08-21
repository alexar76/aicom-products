import pytest
from app.services.rule_engine import RuleEngine

def test_evaluate_weather_calm():
    engine = RuleEngine()
    fire_weather = {"ok": True, "wind_speed_kmh": 20}
    situation = {"ok": True, "flood_alerts": 0}
    nearest = {}
    result = engine.evaluate(situation, fire_weather, nearest)
    weather = [h for h in result["hazards"] if h["type"] == "WEATHER"][0]
    assert weather["level"] == "CALM"

def test_evaluate_weather_warning():
    engine = RuleEngine()
    fire_weather = {"ok": True, "wind_speed_kmh": 60}
    situation = {"ok": True, "flood_alerts": 0}
    result = engine.evaluate(situation, fire_weather, {})
    weather = [h for h in result["hazards"] if h["type"] == "WEATHER"][0]
    assert weather["level"] == "WARNING"

def test_evaluate_fire_emergency():
    engine = RuleEngine()
    fire_weather = {"ok": True, "nearest_fire_km": 5, "active_fires": 1}
    situation = {"ok": True, "flood_alerts": 0}
    result = engine.evaluate(situation, fire_weather, {})
    fire = [h for h in result["hazards"] if h["type"] == "WILDFIRE"][0]
    assert fire["level"] == "EMERGENCY"

def test_evaluate_flood_unknown_when_no_data():
    engine = RuleEngine()
    situation = {"ok": False, "error": "no data"}
    result = engine.evaluate(situation, {}, {})
    flood = [h for h in result["hazards"] if h["type"] == "FLOOD"][0]
    assert flood["level"] == "UNKNOWN"

def test_overall_unknown_when_all_unknown():
    engine = RuleEngine()
    result = engine.evaluate({"ok": False}, {}, {})
    assert result["overall"]["level"] == "UNKNOWN"
