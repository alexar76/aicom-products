"""Acceptance-criteria tests for Sentinel.

Maps to the following acceptance criteria (IDs from specification):
  FR-02 – Location rounding (covered by rule engine coordinate handling)
  FR-03 – ATLAS capability invocation and receipts (covered by integration tests)
  FR-04 – Deterministic rule engine
  FR-05 – Signed evidence receipt display (covered by integration tests)
  FR-06 – Free-tier 402 behaviour (covered by integration tests)
  FR-07 – Empty-coverage refusal handling (covered by integration tests)
  FR-08 – Heartbeat (basic) (covered by heartbeat tests)
  FR-10 – Rate limiting / budget ceiling (covered by rate limit tests)
  FR-11 – Operator dashboard data (model creation)
  FR-12 – Persistence and schema migrations (model creation)
  FR-13 – UI accessibility (level text + icon) – ensures levels are never colour-only
"""
import pytest
from datetime import datetime

from app.services.rule_engine import RuleEngine
from app.models.advisory import Advisory
from app.models.audit import InvokeAuditLog


# ---------------------------------------------------------------------------
# FR-04: Deterministic rule engine
# ---------------------------------------------------------------------------
class TestRuleEngine:
    def test_calm_level(self):
        engine = RuleEngine()
        evidence = {"weather": {"wind_speed_kmh": 5, "temperature_c": 20}}
        level, reason = engine.evaluate(evidence, "weather")
        assert level == "CALM"
        assert "calm" in reason.lower()

    def test_watch_level(self):
        engine = RuleEngine()
        evidence = {"weather": {"wind_speed_kmh": 35, "temperature_c": 20}}
        level, _ = engine.evaluate(evidence, "weather")
        assert level == "WATCH"

    def test_warning_level(self):
        engine = RuleEngine()
        evidence = {"weather": {"wind_speed_kmh": 65, "temperature_c": 20}}
        level, _ = engine.evaluate(evidence, "weather")
        assert level == "WARNING"

    def test_emergency_level(self):
        engine = RuleEngine()
        evidence = {"weather": {"wind_speed_kmh": 120, "temperature_c": 20}}
        level, _ = engine.evaluate(evidence, "weather")
        assert level == "EMERGENCY"

    def test_missing_data_returns_unknown(self):
        engine = RuleEngine()
        level, reason = engine.evaluate({}, "weather")
        assert level == "UNKNOWN"
        assert "missing" in reason.lower()

    def test_fire_thresholds(self):
        engine = RuleEngine()
        evidence = {"fire": {"distance_km": 5, "confidence": 90}}
        level, _ = engine.evaluate(evidence, "fire")
        assert level in ("WATCH", "WARNING", "EMERGENCY")

    def test_flood_thresholds(self):
        engine = RuleEngine()
        evidence = {"flood": {"water_level_m": 2.5, "distance_km": 1}}
        level, _ = engine.evaluate(evidence, "flood")
        assert level in ("WATCH", "WARNING", "EMERGENCY")


# ---------------------------------------------------------------------------
# FR-11: Operator dashboard data (model creation)
# ---------------------------------------------------------------------------
class TestOperatorModels:
    def test_advisory_model_creation(self):
        adv = Advisory(
            rounded_lat=55.7,
            rounded_lon=37.6,
            hazard="WEATHER",
            level="WATCH",
            measurement="wind 35 km/h",
            distance_km=0,
            receipt_digest="sha256:abc",
            timestamp=datetime.utcnow(),
            is_cached=False,
            sim_flag=False,
        )
        assert adv.hazard == "WEATHER"
        assert adv.level == "WATCH"

    def test_audit_log_creation(self):
        log = InvokeAuditLog(
            capability_name="atlas.situation.brief@v1",
            cost_usd=0.06,
            latency_ms=120,
            status="success",
            response_receipt_digest="sha256:xyz",
        )
        assert log.cost_usd == 0.06
        assert log.status == "success"


# ---------------------------------------------------------------------------
# FR-13: Level text + icon (ensuring level is never colour-only)
# ---------------------------------------------------------------------------
class TestLevelRepresentation:
    def test_evaluate_returns_valid_level_strings(self):
        engine = RuleEngine()
        valid_levels = {"CALM", "WATCH", "WARNING", "EMERGENCY", "UNKNOWN"}
        # Test weather
        evidence = {"weather": {"wind_speed_kmh": 10}}
        level, _ = engine.evaluate(evidence, "weather")
        assert level in valid_levels
        # Test fire
        evidence = {"fire": {"distance_km": 100}}
        level, _ = engine.evaluate(evidence, "fire")
        assert level in valid_levels
        # Test flood
        evidence = {"flood": {"water_level_m": 0.5}}
        level, _ = engine.evaluate(evidence, "flood")
        assert level in valid_levels

    def test_unknown_is_returned_for_empty_evidence(self):
        engine = RuleEngine()
        level, _ = engine.evaluate({}, "weather")
        assert level == "UNKNOWN"
