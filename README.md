# CAS 3:22 NIFTY + SENSEX AI Closing Direction & Option Backtesting System

Production-quality, self-contained trading research and backtesting application for the Closing Auction Session (CAS).

## Canonical Production Directory
`C:\Mangesh\Jules\CAS`

## Features
- Manual 3:22 PM IST analysis trigger
- NIFTY and SENSEX direction prediction models (UP/DOWN/FLAT)
- 4 AI Feature Calculators: Closing Pressure Momentum, 5-Minute Battle, AI Anomaly Detection, Top-5 Heavyweight Contribution
- Option Trade Engine for NIFTY & SENSEX options with realistic liquidity filtering
- Exact Option Performance Replay: 3:22 -> 3:25, 3:22 -> CAS Close, 3:22 -> Official Close
- Single-day and Date-range backtesting screens with interactive Plotly charts & equity curves
- Audit logging & reproducible version tracking stored in local SQLite database

## Setup & Running
See `INSTALL.md` and `RUN.md`. Quick start:
```cmd
INSTALL.bat
RUN.bat
```
