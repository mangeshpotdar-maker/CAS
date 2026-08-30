import os
import sqlite3
import json
from typing import Dict, Any

def get_db_path() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_dir = os.path.join(base_dir, "db")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "cas_system.db")

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        nifty_signal TEXT,
        nifty_prob REAL,
        sensex_signal TEXT,
        sensex_prob REAL,
        nifty_option TEXT,
        sensex_option TEXT,
        application_version TEXT,
        model_version TEXT,
        feature_version TEXT,
        data_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS market_snapshot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        price_322 REAL NOT NULL,
        series_json TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS index_snapshot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        official_close REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS option_snapshot (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        ltp_322 REAL NOT NULL,
        bid_322 REAL,
        ask_322 REAL
    );

    CREATE TABLE IF NOT EXISTS features (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        index_symbol TEXT NOT NULL,
        cpm_score REAL NOT NULL,
        cpm_label TEXT NOT NULL,
        battle_score REAL NOT NULL,
        battle_label TEXT NOT NULL,
        anomaly_score REAL NOT NULL,
        anomaly_label TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        symbol TEXT NOT NULL,
        direction TEXT NOT NULL,
        probability REAL NOT NULL,
        expected_move REAL NOT NULL,
        features_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS option_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        index_symbol TEXT NOT NULL,
        option_symbol TEXT NOT NULL,
        expiry TEXT NOT NULL,
        strike REAL NOT NULL,
        option_type TEXT NOT NULL,
        entry_price REAL NOT NULL,
        entry_method TEXT NOT NULL,
        bid REAL,
        ask REAL,
        ltp REAL,
        delta REAL,
        iv REAL,
        oi INTEGER,
        volume INTEGER,
        spread_pct REAL,
        option_score REAL,
        recommendation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS option_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        date TEXT NOT NULL,
        index_symbol TEXT NOT NULL,
        option_symbol TEXT NOT NULL,
        entry_price REAL NOT NULL,
        price_325 REAL,
        price_close REAL,
        return_325_pct REAL,
        return_close_pct REAL,
        mfe_pct REAL,
        mae_pct REAL,
        result TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS backtest_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT UNIQUE NOT NULL,
        mode TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        total_trades INTEGER,
        win_rate REAL,
        total_pnl_pct REAL,
        application_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS model_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", get_db_path())
