from typing import Dict, Any, List

class DirectionModel:
    def __init__(self, index_symbol: str):
        self.index_symbol = index_symbol

    def predict(
        self,
        cpm: Dict[str, Any],
        battle: Dict[str, Any],
        anomaly: Dict[str, Any],
        heavyweight_contribs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Combines explainable signals into NIFTY / SENSEX 3:22 Closing Direction prediction.
        """
        cpm_score = cpm.get("score", 0.0)
        battle_score = battle.get("score", 0.0)

        # Total heavyweights net contribution
        net_hw = sum(item.get("estimated_contribution", 0.0) for item in heavyweight_contribs)
        hw_score = net_hw * 500.0

        # Weighted composite score
        composite_score = (cpm_score * 0.40) + (battle_score * 0.40) + (hw_score * 0.20)

        if composite_score >= 15.0:
            direction = "UP"
            prob = float(min(98.0, 50.0 + (composite_score / 2.0)))
            expected_move = round(0.05 + (composite_score * 0.002), 2)
        elif composite_score <= -15.0:
            direction = "DOWN"
            prob = float(min(98.0, 50.0 + (abs(composite_score) / 2.0)))
            expected_move = round(-0.05 + (composite_score * 0.002), 2)
        else:
            direction = "FLAT"
            prob = float(50.0 + abs(composite_score))
            expected_move = round(composite_score * 0.001, 2)

        return {
            "symbol": self.index_symbol,
            "direction": direction,
            "probability": round(prob, 1),
            "expected_move_pct": expected_move,
            "composite_score": round(composite_score, 2),
            "drivers": {
                "cpm_score": cpm_score,
                "battle_score": battle_score,
                "anomaly_label": anomaly.get("label", "NORMAL"),
                "top5_net_contrib": round(net_hw, 4)
            }
        }
