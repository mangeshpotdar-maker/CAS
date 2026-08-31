# System Configuration Guide

System configurations are stored in `config/config.json`.

## Key Parameters
- `CAS_MIN_DATE`: Officially verified CAS inception date (e.g., `2026-08-03`). Dates prior to this will be rejected by date validation.
- `DEFAULT_DATE`: Default selection date (`2026-08-03` or earliest permitted valid date).
- `VERSION_INFO`:
  - `application_version`: "1.0.0"
  - `model_version`: "1.0.0"
  - `feature_version`: "1.0.0"
  - `data_version`: "1.0.0"
  - `backtest_version`: "1.0.0"
- `LIQUIDITY_FILTERS`:
  - `min_open_interest`: 10000
  - `min_volume`: 500
  - `max_spread_pct`: 5.0
