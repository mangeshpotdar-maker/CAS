import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional

class DataLoader:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            data_dir = os.path.join(base_dir, "data")
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.market_data_file = os.path.join(self.data_dir, "verified_cas_market_data.json")

    def get_day_data(self, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Loads verified market data for the requested date.
        Returns None if data for the requested date does not exist (DATA UNAVAILABLE).
        Never generates dummy, synthetic, or random prices.
        """
        if not os.path.exists(self.market_data_file):
            return None
        with open(self.market_data_file, "r") as f:
            all_data = json.load(f)
        return all_data.get(date_str)

    def get_available_dates(self) -> List[str]:
        """Returns sorted list of available verified dates from dataset."""
        if not os.path.exists(self.market_data_file):
            return []
        with open(self.market_data_file, "r") as f:
            all_data = json.load(f)
        return sorted(list(all_data.keys()))
