import numpy as np
from typing import Dict, Any, List

class FeatureCalculator:
    """Calculates strict 3:22 features using data up to 15:22 IST without look-ahead bias."""

    @staticmethod
    def calculate_closing_pressure_momentum(series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Measures buying/selling pressure approaching CAS from 15:00 to 15:22.
        Returns label (STRONG BUY, BUY, NEUTRAL, SELL, STRONG SELL) and score (-100 to +100).
        """
        # Slice up to 15:22
        valid = [s for s in series if s["timestamp"] <= "15:22"]
        if not valid or len(valid) < 5:
            return {"label": "NEUTRAL", "score": 0.0}

        prices = np.array([s["price"] for s in valid])
        volumes = np.array([s["volume"] for s in valid])

        price_change_pct = (prices[-1] - prices[0]) / prices[0] * 100.0
        vwap = np.sum(prices * volumes) / np.sum(volumes)
        vwap_diff_pct = (prices[-1] - vwap) / vwap * 100.0

        # Raw score from trend and vwap position
        raw_score = (price_change_pct * 300.0) + (vwap_diff_pct * 500.0)
        score = float(np.clip(raw_score, -100.0, 100.0))

        if score >= 60:
            label = "STRONG BUY"
        elif score >= 20:
            label = "BUY"
        elif score <= -60:
            label = "STRONG SELL"
        elif score <= -20:
            label = "SELL"
        else:
            label = "NEUTRAL"

        return {
            "label": label,
            "score": round(score, 2),
            "price_change_pct": round(float(price_change_pct), 4),
            "vwap_diff_pct": round(float(vwap_diff_pct), 4)
        }

    @staticmethod
    def calculate_5min_battle(series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes 15:17 to 15:22 5-minute battle.
        Returns label (BULLISH, BEARISH, NEUTRAL) and score (-100 to +100).
        """
        battle_series = [s for s in series if "15:17" <= s["timestamp"] <= "15:22"]
        if len(battle_series) < 2:
            return {"label": "NEUTRAL", "score": 0.0, "time_interval": "15:17 to 15:22 IST"}

        p_start = battle_series[0]["price"]
        p_end = battle_series[-1]["price"]
        change_pct = (p_end - p_start) / p_start * 100.0

        # Score conversion
        raw_score = change_pct * 1000.0
        score = float(np.clip(raw_score, -100.0, 100.0))

        if score >= 25:
            label = "BULLISH"
        elif score <= -25:
            label = "BEARISH"
        else:
            label = "NEUTRAL"

        return {
            "label": label,
            "score": round(score, 2),
            "time_interval": "15:17 to 15:22 IST",
            "battle_change_pct": round(float(change_pct), 4)
        }

    @staticmethod
    def calculate_ai_anomaly(series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detects unusual volume/price acceleration leading to 15:22.
        Returns label (NORMAL, WATCH, ANOMALY, HIGH ANOMALY) and score (0-100).
        """
        valid = [s for s in series if s["timestamp"] <= "15:22"]
        if len(valid) < 10:
            return {"label": "NORMAL", "score": 10.0, "explanation": "Normal volume and price distribution."}

        volumes = np.array([s["volume"] for s in valid])
        recent_vol = np.mean(volumes[-5:])
        hist_vol = np.mean(volumes[:-5])
        vol_ratio = recent_vol / (hist_vol + 1e-5)

        prices = np.array([s["price"] for s in valid])
        returns = np.abs(np.diff(prices) / prices[:-1])
        recent_volatility = np.mean(returns[-5:])
        hist_volatility = np.mean(returns[:-5])
        volatility_ratio = recent_volatility / (hist_volatility + 1e-5)

        anomaly_score = float(np.clip((vol_ratio * 25.0 + volatility_ratio * 25.0) - 25.0, 0.0, 100.0))

        if anomaly_score >= 75:
            label = "HIGH ANOMALY"
            explanation = "Extreme volume spike and abnormal volatility divergence detected in final 5 minutes."
        elif anomaly_score >= 50:
            label = "ANOMALY"
            explanation = "Elevated volume acceleration relative to historical session baseline."
        elif anomaly_score >= 25:
            label = "WATCH"
            explanation = "Moderate volume variance observed."
        else:
            label = "NORMAL"
            explanation = "Normal statistical behavior; no volume or volatility anomaly detected."

        return {
            "label": label,
            "score": round(anomaly_score, 2),
            "explanation": explanation
        }

    @staticmethod
    def calculate_heavyweight_contribution(index_constituents: List[Dict[str, Any]], stock_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculates Top-5 index heavyweight contribution dynamically.
        """
        contributions = []
        for rank, item in enumerate(index_constituents, 1):
            sym = item["symbol"]
            weight = item["weight"]
            s_info = stock_data.get(sym, {})
            chg = s_info.get("317_to_322_pct", 0.0)
            contrib = (chg * weight) / 100.0

            contributions.append({
                "rank": rank,
                "stock": sym,
                "weight": f"{weight}%",
                "price_change": f"{chg:+.2f}%",
                "estimated_contribution": round(contrib, 4),
                "direction": "UP" if contrib > 0 else ("DOWN" if contrib < 0 else "FLAT")
            })
        return contributions
