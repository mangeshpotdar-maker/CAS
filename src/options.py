from typing import Dict, Any, List, Optional

class OptionSelector:
    def __init__(self, liquidity_filters: Dict[str, Any]):
        self.min_oi = liquidity_filters.get("min_open_interest", 1000)
        self.min_vol = liquidity_filters.get("min_volume", 100)
        self.max_spread_pct = liquidity_filters.get("max_spread_pct", 5.0)

    def select_best_option(
        self,
        index_symbol: str,
        predicted_direction: str,
        confidence: float,
        options_chain: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Selects one best option based on direction (CE for UP, PE for DOWN, NO TRADE for FLAT)
        and scores candidates using Greeks, liquidity, and spread.
        """
        if predicted_direction == "FLAT":
            return {
                "recommendation": "NO TRADE",
                "reason": "Predicted direction is FLAT. Strategy calls for NO TRADE.",
                "option": None
            }

        target_type = "CE" if predicted_direction == "UP" else "PE"
        eligible = [opt for opt in options_chain if opt.get("option_type") == target_type]

        if not eligible:
            return {
                "recommendation": "NO TRADE",
                "reason": f"No {target_type} contracts found in option chain.",
                "option": None
            }

        candidates = []
        for opt in eligible:
            oi = opt.get("oi", 0)
            vol = opt.get("volume", 0)
            bid = opt.get("bid_322", 0.0)
            ask = opt.get("ask_322", 0.0)

            if bid > 0:
                spread_pct = ((ask - bid) / bid) * 100.0
            else:
                spread_pct = 999.0

            # Liquidity Filtering
            rejections = []
            if oi < self.min_oi:
                rejections.append(f"Insufficient OI ({oi} < {self.min_oi})")
            if vol < self.min_vol:
                rejections.append(f"Insufficient Volume ({vol} < {self.min_vol})")
            if spread_pct > self.max_spread_pct:
                rejections.append(f"Excessive Spread ({spread_pct:.2f}% > {self.max_spread_pct}%)")

            if rejections:
                continue

            # Calculate Option Score (0-100)
            delta = abs(opt.get("delta", 0.5))
            score = (confidence * 0.4) + (delta * 40.0) + (min(vol, 20000) / 20000.0 * 20.0)
            score = min(100.0, score)

            candidates.append({
                "contract": opt,
                "score": round(score, 1),
                "spread_pct": round(spread_pct, 2)
            })

        if not candidates:
            return {
                "recommendation": "NO TRADE",
                "reason": "All matching contracts rejected by liquidity/spread filters.",
                "option": None
            }

        # Select highest-scoring eligible contract
        candidates.sort(key=lambda x: x["score"], reverse=True)
        best = candidates[0]
        best_contract = best["contract"]

        # Freeze 3:22 recommendation fields strictly
        entry_price = best_contract.get("ask_322") if best_contract.get("ask_322") else best_contract.get("ltp_322")
        entry_method = "ASK" if best_contract.get("ask_322") else "LTP"

        frozen_card = {
            "symbol": best_contract.get("symbol"),
            "index_symbol": index_symbol,
            "expiry": best_contract.get("expiry"),
            "strike": best_contract.get("strike"),
            "option_type": best_contract.get("option_type"),
            "entry_price": entry_price,
            "entry_method": entry_method,
            "bid": best_contract.get("bid_322"),
            "ask": best_contract.get("ask_322"),
            "ltp": best_contract.get("ltp_322"),
            "delta": best_contract.get("delta"),
            "iv": best_contract.get("iv"),
            "oi": best_contract.get("oi"),
            "volume": best_contract.get("volume"),
            "spread_pct": best["spread_pct"],
            "option_score": best["score"],
            "confidence": confidence,
            "expected_option_move_pct": round(best["score"] * 0.2, 1),
            "recommendation": "BUY"
        }

        return {
            "recommendation": "BUY",
            "reason": f"Selected highest scoring eligible {target_type} contract.",
            "option": frozen_card,
            "raw_contract": best_contract
        }
