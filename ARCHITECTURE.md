# System Architecture

## Overview
The CAS 3:22 NIFTY + SENSEX AI System is designed with modularity, auditability, and Phase 2 automation preparedness.

```text
[ USER UI / AUTOMATED TRIGGER ]
             │
             ▼
     run_322_analysis()
             │
 ┌───────────┴───────────┐
 │                       │
 ▼                       ▼
DataLoader (3:22 Cutoff) DB Engine (SQLite)
 │
 ▼
Feature Extractors
 - Closing Pressure Momentum
 - 5-Min Battle
 - AI Anomaly Detection
 - Top-5 Heavyweights
 │
 ▼
Direction Models (NIFTY & SENSEX)
 │
 ▼
Option Trade Engine (Liquidity Filters & Scoring)
 │
 ▼
Performance Replayer (Post-3:22 Data Evaluation)
 - 3:22 -> 3:25 Return
 - 3:22 -> CAS Match Return
 - 3:22 -> Official Close Return
 - MFE & MAE Calculation
 │
 ▼
Audit Trail & UI Visualization
```
