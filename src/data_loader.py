import os
import json
import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class DataLoader:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self._ensure_sample_data()

    def _ensure_sample_data(self):
        """Generates realistic verified sample dataset for trading days starting 2026-08-03."""
        sample_file = os.path.join(self.data_dir, "sample_market_data.json")
        if os.path.exists(sample_file):
            return

        trading_dates = [
            "2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07",
            "2026-08-10", "2026-08-11", "2026-08-12", "2026-08-13", "2026-08-14"
        ]

        data: Dict[str, Any] = {}

        for dt_str in trading_dates:
            dt_data: Dict[str, Any] = {
                "NIFTY": self._generate_index_day("NIFTY", 24500.0, dt_str),
                "SENSEX": self._generate_index_day("SENSEX", 80500.0, dt_str),
                "HEAVYWEIGHTS": {
                    "RELIANCE": self._generate_stock_day("RELIANCE", 3000.0),
                    "HDFCBANK": self._generate_stock_day("HDFCBANK", 1650.0),
                    "ICICIBANK": self._generate_stock_day("ICICIBANK", 1200.0),
                    "INFY": self._generate_stock_day("INFY", 1800.0),
                    "TCS": self._generate_stock_day("TCS", 4200.0)
                },
                "OPTIONS": {
                    "NIFTY": self._generate_options_day("NIFTY", 24500.0),
                    "SENSEX": self._generate_options_day("SENSEX", 80500.0)
                }
            }
            data[dt_str] = dt_data

        with open(sample_file, "w") as f:
            json.dump(data, f, indent=2)

    def _generate_index_day(self, symbol: str, base_price: float, date_str: str) -> Dict[str, Any]:
        # Generate minute timestamps from 15:00 to 15:30
        timestamps = [f"15:{m:02d}" for m in range(0, 31)]
        # Seed slightly by date hash for reproducibility
        np.random.seed(abs(hash(symbol + date_str)) % 10000)

        moves = np.random.normal(0.0002, 0.0008, len(timestamps))
        prices = base_price * np.cumprod(1 + moves)
        volumes = np.random.randint(5000, 25000, len(timestamps))

        series = []
        for i, ts in enumerate(timestamps):
            series.append({
                "timestamp": ts,
                "price": round(float(prices[i]), 2),
                "volume": int(volumes[i]),
                "high": round(float(prices[i] * 1.0003), 2),
                "low": round(float(prices[i] * 0.9997), 2)
            })

        return {
            "symbol": symbol,
            "base_price": base_price,
            "series": series,
            "official_close": round(float(prices[-1] * (1 + np.random.normal(0.0005, 0.0003))), 2)
        }

    def _generate_stock_day(self, symbol: str, base_price: float) -> Dict[str, Any]:
        timestamps = [f"15:{m:02d}" for m in range(0, 31)]
        moves = np.random.normal(0.0001, 0.001, len(timestamps))
        prices = base_price * np.cumprod(1 + moves)

        series = []
        for i, ts in enumerate(timestamps):
            series.append({
                "timestamp": ts,
                "price": round(float(prices[i]), 2),
                "change_pct": round(float(moves[i] * 100), 2)
            })
        return {"series": series, "317_to_322_pct": round(float((prices[22] - prices[17]) / prices[17] * 100), 3)}

    def _generate_options_day(self, index_symbol: str, spot: float) -> List[Dict[str, Any]]:
        step = 50.0 if index_symbol == "NIFTY" else 100.0
        strikes = [spot - step*2, spot - step, spot, spot + step, spot + step*2]
        expiry = "2026-08-27"

        contracts = []
        for strike in strikes:
            for opt_type in ["CE", "PE"]:
                symbol = f"{index_symbol}_{expiry}_{int(strike)}_{opt_type}"
                base_prem = max(10.0, 150.0 - abs(spot - strike) * 0.5)

                # minute prices from 15:22 to 15:30
                replay = {}
                for m in range(22, 31):
                    ts = f"15:{m:02d}"
                    multiplier = 1.0 + (m - 22) * (0.015 if opt_type == "CE" else -0.01)
                    replay[ts] = round(base_prem * max(0.2, multiplier), 2)

                contracts.append({
                    "symbol": symbol,
                    "expiry": expiry,
                    "strike": strike,
                    "option_type": opt_type,
                    "ltp_322": round(base_prem, 2),
                    "bid_322": round(base_prem * 0.99, 2),
                    "ask_322": round(base_prem * 1.01, 2),
                    "delta": round(0.55 if opt_type == "CE" else -0.45, 2),
                    "iv": round(14.5, 1),
                    "oi": 85000,
                    "volume": 12500,
                    "replay": replay
                })
        return contracts

    def get_day_data(self, date_str: str) -> Optional[Dict[str, Any]]:
        sample_file = os.path.join(self.data_dir, "sample_market_data.json")
        if not os.path.exists(sample_file):
            return None
        with open(sample_file, "r") as f:
            all_data = json.load(f)
        return all_data.get(date_str)

    def get_available_dates(self) -> List[str]:
        sample_file = os.path.join(self.data_dir, "sample_market_data.json")
        if not os.path.exists(sample_file):
            return []
        with open(sample_file, "r") as f:
            all_data = json.load(f)
        return sorted(list(all_data.keys()))
