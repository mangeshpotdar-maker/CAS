import os
import json
import uuid
import datetime
import sqlite3
from typing import Dict, Any, List, Optional

from src.data_loader import DataLoader
from src.features import FeatureCalculator
from src.models import DirectionModel
from src.options import OptionSelector
from src.backtest import PerformanceReplayer
from src.db import get_db_path, init_db
from src.logger import setup_logger

class CASEngine:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            config_path = os.path.join(base_dir, "config", "config.json")

        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.cas_min_date = self.config.get("CAS_MIN_DATE", "2026-08-03")
        self.loader = DataLoader()
        self.nifty_model = DirectionModel("NIFTY")
        self.sensex_model = DirectionModel("SENSEX")
        self.option_selector = OptionSelector(self.config.get("LIQUIDITY_FILTERS", {}))

        # Ensure database is initialized
        init_db()

    def validate_date(self, date_str: str) -> Dict[str, Any]:
        """Strictly validates date against CAS_MIN_DATE."""
        if date_str < self.cas_min_date:
            return {
                "valid": False,
                "error": f"INVALID DATE: CAS analysis is not available before the officially verified CAS inception date ({self.cas_min_date})."
            }
        return {"valid": True, "error": None}

    def run_322_analysis(self, date_str: str, timestamp_str: str = "15:22:00 IST") -> Dict[str, Any]:
        """
        Main execution interface designed for Phase 1 (manual trigger)
        and seamlessly compatible with Phase 2 automated triggers.
        """
        val = self.validate_date(date_str)
        if not val["valid"]:
            return {
                "status": "INVALID_DATE",
                "error": val["error"],
                "cas_min_date": self.cas_min_date
            }

        day_data = self.loader.get_day_data(date_str)
        if not day_data:
            return {
                "status": "DATA_UNAVAILABLE",
                "error": f"DATA UNAVAILABLE: No market data found for date {date_str}.",
                "cas_min_date": self.cas_min_date
            }

        # Initialize daily logging directory
        setup_logger(date_str)

        run_id = f"RUN_{date_str.replace('-', '')}_{uuid.uuid4().hex[:6].upper()}"

        # 1. Calculate NIFTY Features & Prediction
        nifty_raw = day_data["NIFTY"]
        n_cpm = FeatureCalculator.calculate_closing_pressure_momentum(nifty_raw["series"])
        n_battle = FeatureCalculator.calculate_5min_battle(nifty_raw["series"])
        n_anomaly = FeatureCalculator.calculate_ai_anomaly(nifty_raw["series"])
        n_hw = FeatureCalculator.calculate_heavyweight_contribution(
            self.config["INDEX_CONSTITUENTS"]["NIFTY"],
            day_data["HEAVYWEIGHTS"]
        )
        nifty_pred = self.nifty_model.predict(n_cpm, n_battle, n_anomaly, n_hw)

        # 2. Calculate SENSEX Features & Prediction
        sensex_raw = day_data["SENSEX"]
        s_cpm = FeatureCalculator.calculate_closing_pressure_momentum(sensex_raw["series"])
        s_battle = FeatureCalculator.calculate_5min_battle(sensex_raw["series"])
        s_anomaly = FeatureCalculator.calculate_ai_anomaly(sensex_raw["series"])
        s_hw = FeatureCalculator.calculate_heavyweight_contribution(
            self.config["INDEX_CONSTITUENTS"]["SENSEX"],
            day_data["HEAVYWEIGHTS"]
        )
        sensex_pred = self.sensex_model.predict(s_cpm, s_battle, s_anomaly, s_hw)

        # 3. Select Options
        nifty_opt_rec = self.option_selector.select_best_option(
            "NIFTY", nifty_pred["direction"], nifty_pred["probability"], day_data["OPTIONS"]["NIFTY"]
        )
        sensex_opt_rec = self.option_selector.select_best_option(
            "SENSEX", sensex_pred["direction"], sensex_pred["probability"], day_data["OPTIONS"]["SENSEX"]
        )

        # 4. Replay Performance
        nifty_perf = PerformanceReplayer.replay_option_performance(nifty_opt_rec, nifty_opt_rec.get("raw_contract"))
        sensex_perf = PerformanceReplayer.replay_option_performance(sensex_opt_rec, sensex_opt_rec.get("raw_contract"))

        # Write to audit database & predictions tables
        self._write_records(run_id, date_str, timestamp_str, nifty_pred, sensex_pred, nifty_opt_rec, sensex_opt_rec, nifty_perf, sensex_perf, n_cpm, n_battle, n_anomaly, s_cpm, s_battle, s_anomaly)

        return {
            "status": "SUCCESS",
            "run_id": run_id,
            "date": date_str,
            "timestamp": timestamp_str,
            "versions": self.config["VERSION_INFO"],
            "nifty": {
                "prediction": nifty_pred,
                "cpm": n_cpm,
                "battle": n_battle,
                "anomaly": n_anomaly,
                "heavyweights": n_hw,
                "option_recommendation": nifty_opt_rec,
                "performance": nifty_perf
            },
            "sensex": {
                "prediction": sensex_pred,
                "cpm": s_cpm,
                "battle": s_battle,
                "anomaly": s_anomaly,
                "heavyweights": s_hw,
                "option_recommendation": sensex_opt_rec,
                "performance": sensex_perf
            }
        }

    def _write_records(self, run_id, date_str, ts_str, n_pred, s_pred, n_opt, s_opt, n_perf, s_perf, n_cpm, n_battle, n_anomaly, s_cpm, s_battle, s_anomaly):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            v_info = self.config["VERSION_INFO"]
            cursor.execute("""
                INSERT INTO audit_log (
                    run_id, date, timestamp, nifty_signal, nifty_prob, sensex_signal, sensex_prob,
                    nifty_option, sensex_option, application_version, model_version, feature_version, data_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, date_str, ts_str,
                n_pred["direction"], n_pred["probability"],
                s_pred["direction"], s_pred["probability"],
                n_opt.get("option", {}).get("symbol") if n_opt.get("option") else "NONE",
                s_opt.get("option", {}).get("symbol") if s_opt.get("option") else "NONE",
                v_info["application_version"], v_info["model_version"],
                v_info["feature_version"], v_info["data_version"]
            ))

            # Store predictions
            cursor.execute("""
                INSERT INTO predictions (run_id, date, symbol, direction, probability, expected_move, features_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (run_id, date_str, "NIFTY", n_pred["direction"], n_pred["probability"], n_pred["expected_move_pct"], json.dumps(n_pred["drivers"])))

            cursor.execute("""
                INSERT INTO predictions (run_id, date, symbol, direction, probability, expected_move, features_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (run_id, date_str, "SENSEX", s_pred["direction"], s_pred["probability"], s_pred["expected_move_pct"], json.dumps(s_pred["drivers"])))

            # Store feature values
            cursor.execute("""
                INSERT INTO features (run_id, date, index_symbol, cpm_score, cpm_label, battle_score, battle_label, anomaly_score, anomaly_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (run_id, date_str, "NIFTY", n_cpm["score"], n_cpm["label"], n_battle["score"], n_battle["label"], n_anomaly["score"], n_anomaly["label"]))

            cursor.execute("""
                INSERT INTO features (run_id, date, index_symbol, cpm_score, cpm_label, battle_score, battle_label, anomaly_score, anomaly_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (run_id, date_str, "SENSEX", s_cpm["score"], s_cpm["label"], s_battle["score"], s_battle["label"], s_anomaly["score"], s_anomaly["label"]))

            # Store option recommendations & performance if available
            if n_opt.get("option"):
                opt = n_opt["option"]
                cursor.execute("""
                    INSERT INTO option_recommendations (run_id, date, index_symbol, option_symbol, expiry, strike, option_type, entry_price, entry_method, bid, ask, ltp, delta, iv, oi, volume, spread_pct, option_score, recommendation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (run_id, date_str, "NIFTY", opt["symbol"], opt["expiry"], opt["strike"], opt["option_type"], opt["entry_price"], opt["entry_method"], opt["bid"], opt["ask"], opt["ltp"], opt["delta"], opt["iv"], opt["oi"], opt["volume"], opt["spread_pct"], opt["option_score"], n_opt["recommendation"]))

                if n_perf.get("status") == "COMPLETED":
                    cursor.execute("""
                        INSERT INTO option_performance (run_id, date, index_symbol, option_symbol, entry_price, price_325, price_close, return_325_pct, return_close_pct, mfe_pct, mae_pct, result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (run_id, date_str, "NIFTY", opt["symbol"], n_perf["entry_price"], n_perf["price_325"], n_perf["price_close"], n_perf["return_325_pct"], n_perf["return_close_pct"], n_perf["mfe_pct"], n_perf["mae_pct"], n_perf["result"]))

            if s_opt.get("option"):
                opt = s_opt["option"]
                cursor.execute("""
                    INSERT INTO option_recommendations (run_id, date, index_symbol, option_symbol, expiry, strike, option_type, entry_price, entry_method, bid, ask, ltp, delta, iv, oi, volume, spread_pct, option_score, recommendation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (run_id, date_str, "SENSEX", opt["symbol"], opt["expiry"], opt["strike"], opt["option_type"], opt["entry_price"], opt["entry_method"], opt["bid"], opt["ask"], opt["ltp"], opt["delta"], opt["iv"], opt["oi"], opt["volume"], opt["spread_pct"], opt["option_score"], s_opt["recommendation"]))

                if s_perf.get("status") == "COMPLETED":
                    cursor.execute("""
                        INSERT INTO option_performance (run_id, date, index_symbol, option_symbol, entry_price, price_325, price_close, return_325_pct, return_close_pct, mfe_pct, mae_pct, result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (run_id, date_str, "SENSEX", opt["symbol"], s_perf["entry_price"], s_perf["price_325"], s_perf["price_close"], s_perf["return_325_pct"], s_perf["return_close_pct"], s_perf["mfe_pct"], s_perf["mae_pct"], s_perf["result"]))

            conn.commit()
            conn.close()
        except Exception as e:
            pass
