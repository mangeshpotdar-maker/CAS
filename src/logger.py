import os
import logging
import datetime
from typing import Optional

def setup_logger(run_date_str: Optional[str] = None):
    """
    Creates daily log directory logs/YYYY-MM-DD/ and configures application loggers.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if not run_date_str:
        run_date_str = datetime.date.today().strftime("%Y-%m-%d")

    log_dir = os.path.join(base_dir, "logs", run_date_str)
    os.makedirs(log_dir, exist_ok=True)

    log_files = [
        "application.log", "data.log", "feature.log",
        "model.log", "option.log", "backtest.log", "error.log", "audit.log"
    ]

    for log_file in log_files:
        path = os.path.join(log_dir, log_file)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(f"=== Log Initialized {datetime.datetime.now().isoformat()} ===\n")

    return log_dir
