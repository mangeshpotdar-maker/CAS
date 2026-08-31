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

    def _ensure_sample_data(self, force_recreate: bool = False):
        """Generates realistic verified sample dataset for trading days starting 2026-08-03."""
        sample_file = os.path.join(self.data_dir, "sample_market_data.json")
        if os.path.exists(sample_file) and not force_recreate:
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
                    "RELIANCE": self._generate_stock_day("RELIANCE", 3000.0, dt_str),
                    "HDFCBANK": self._generate_stock_day("HDFCBANK", 1650.0, dt_str),
                    "ICICIBANK": self._generate_stock_day("ICICIBANK", 1200.0, dt_str),
                    "INFY": self._generate_stock_day("INFY", 1800.0, dt_str),
                    "TCS": self._generate_stock_day("TCS", 4200.0, dt_str)
                },
                "OPTIONS": {
                    "NIFTY": self._generate_options_day("NIFTY", 24500.0, dt_str),
                    "SENSEX": self._generate_options_day("SENSEX", 80500.0, dt_str)
                }
            }
            data[dt_str] = dt_data

        with open(sample_file, "w") as f:
            json.dump(data, f, indent=2)

    def _generate_index_day(self, symbol: str, base_price: float, date_str: str) -> Dict[str, Any]:
        timestamps = [f"15:{m:02d}" for m in range(0, 31)]
        np.random.seed(abs(hash(symbol + date_str)) % 100000)

        drift = 0.0003 if symbol == "NIFTY" else -0.0002
        moves = np.random.normal(drift, 0.0009, len(timestamps))
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
            "official_close": round(float(prices[-1] * (1 + np.random.normal(0.0003, 0.0004))), 2)
        }

    def _generate_stock_day(self, symbol: str, base_price: float, date_str: str) -> Dict[str, Any]:
        timestamps = [f"15:{m:02d}" for m in range(0, 31)]
        np.random.seed(abs(hash(symbol + date_str)) % 100000)
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

    def _generate_options_day(self, index_symbol: str, spot: float, date_str: str) -> List[Dict[str, Any]]:
        step = 50.0 if index_symbol == "NIFTY" else 100.0
        strikes = [spot - step*2, spot - step, spot, spot + step, spot + step*2]
        expiry = "2026-08-27"

        contracts = []
        for strike in strikes:
            for opt_type in ["CE", "PE"]:
                seed_val = abs(hash(f"{index_symbol}_{date_str}_{strike}_{opt_type}")) % 100000
                np.random.seed(seed_val)

                symbol = f"{index_symbol}_{expiry}_{int(strike)}_{opt_type}"
                base_prem = max(15.0, 180.0 - abs(spot - strike) * (0.4 if index_symbol == "NIFTY" else 0.15))

                # minute prices from 15:22 to 15:30 with unique realistic random walks
                replay = {}
                cur_prem = base_prem
                volatility = 0.012 if index_symbol == "NIFTY" else 0.018
                drift = np.random.normal(0.001, 0.005)

                for m in range(22, 31):
                    ts = f"15:{m:02d}"
                    if m == 22:
                        replay[ts] = round(base_prem, 2)
                    else:
                        step_chg = np.random.normal(drift, volatility)
                        cur_prem = max(5.0, cur_prem * (1 + step_chg))
                        replay[ts] = round(cur_prem, 2)

                spread_mult = 0.01 if index_symbol == "NIFTY" else 0.015
                oi_val = int(np.random.randint(40000, 150000))
                vol_val = int(np.random.randint(5000, 35000))

                contracts.append({
                    "symbol": symbol,
                    "expiry": expiry,
                    "strike": strike,
                    "option_type": opt_type,
                    "ltp_322": round(base_prem, 2),
                    "bid_322": round(base_prem * (1 - spread_mult), 2),
                    "ask_322": round(base_prem * (1 + spread_mult), 2),
                    "delta": round(0.55 if opt_type == "CE" else -0.45, 2),
                    "iv": round(13.5 + np.random.uniform(0, 4), 1),
                    "oi": oi_val,
                    "volume": vol_val,
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
