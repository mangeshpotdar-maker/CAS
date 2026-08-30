from typing import Dict, Any, Optional

class PerformanceReplayer:
    @staticmethod
    def replay_option_performance(recommendation: Dict[str, Any], raw_contract: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Replays exact contract performance from 15:22 to 15:30 using minute series data.
        Calculates 3:22 -> 3:25 return, 3:22 -> close return, MFE, and MAE.
        """
        if recommendation.get("recommendation") != "BUY" or not recommendation.get("option") or not raw_contract:
            return {
                "status": "NO_TRADE",
                "entry_price": 0.0,
                "price_325": 0.0,
                "price_close": 0.0,
                "return_325_pct": 0.0,
                "return_close_pct": 0.0,
                "mfe_pct": 0.0,
                "mae_pct": 0.0,
                "result": "N/A",
                "replay_timeline": {}
            }

        opt = recommendation["option"]
        entry_price = float(opt["entry_price"])
        replay_series = raw_contract.get("replay", {})

        if not replay_series or entry_price <= 0:
            return {
                "status": "DATA_UNAVAILABLE",
                "entry_price": entry_price,
                "price_325": 0.0,
                "price_close": 0.0,
                "return_325_pct": 0.0,
                "return_close_pct": 0.0,
                "mfe_pct": 0.0,
                "mae_pct": 0.0,
                "result": "DATA_UNAVAILABLE",
                "replay_timeline": {}
            }

        price_325 = float(replay_series.get("15:25", entry_price))
        prices = [float(v) for v in replay_series.values()]
        price_close = prices[-1] if prices else entry_price

        return_325_pct = round(((price_325 - entry_price) / entry_price) * 100.0, 2)
        return_close_pct = round(((price_close - entry_price) / entry_price) * 100.0, 2)

        max_price = max(prices)
        min_price = min(prices)

        mfe_pct = round(((max_price - entry_price) / entry_price) * 100.0, 2)
        mae_pct = round(((min_price - entry_price) / entry_price) * 100.0, 2)

        result = "WIN" if return_close_pct > 0 else ("LOSS" if return_close_pct < 0 else "FLAT")

        return {
            "status": "COMPLETED",
            "symbol": opt["symbol"],
            "entry_price": entry_price,
            "price_325": price_325,
            "price_close": price_close,
            "return_325_pct": return_325_pct,
            "return_close_pct": return_close_pct,
            "mfe_pct": mfe_pct,
            "mae_pct": mae_pct,
            "result": result,
            "replay_timeline": replay_series
        }
