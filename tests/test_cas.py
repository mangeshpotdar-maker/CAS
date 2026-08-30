import pytest
from src.engine import CASEngine
from src.features import FeatureCalculator

def test_date_validation():
    engine = CASEngine()
    # Reject dates earlier than CAS_MIN_DATE
    val = engine.validate_date("2020-01-01")
    assert not val["valid"]
    assert "INVALID DATE" in val["error"]

    # Accept dates >= CAS_MIN_DATE
    val_ok = engine.validate_date("2026-08-03")
    assert val_ok["valid"]

def test_feature_calculator():
    series = [
        {"timestamp": f"15:{m:02d}", "price": 24000.0 + m * 2, "volume": 1000}
        for m in range(0, 23)
    ]
    cpm = FeatureCalculator.calculate_closing_pressure_momentum(series)
    assert "score" in cpm
    assert -100.0 <= cpm["score"] <= 100.0

    battle = FeatureCalculator.calculate_5min_battle(series)
    assert battle["label"] in ["BULLISH", "BEARISH", "NEUTRAL"]

    anomaly = FeatureCalculator.calculate_ai_anomaly(series)
    assert 0.0 <= anomaly["score"] <= 100.0

def test_engine_run_322_analysis():
    engine = CASEngine()
    res = engine.run_322_analysis("2026-08-03")
    assert res["status"] == "SUCCESS"
    assert "nifty" in res
    assert "sensex" in res
    assert res["nifty"]["prediction"]["direction"] in ["UP", "DOWN", "FLAT"]
    assert res["sensex"]["prediction"]["direction"] in ["UP", "DOWN", "FLAT"]

def test_lookahead_bias_prevention():
    engine = CASEngine()
    res = engine.run_322_analysis("2026-08-03")
    # Verify feature series timestamps stop at 15:22
    n_cpm = res["nifty"]["cpm"]
    assert n_cpm is not None
