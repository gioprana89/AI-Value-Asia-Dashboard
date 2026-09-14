
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"

@pd.api.extensions.register_dataframe_accessor("dashboard")
class DashboardAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def nonempty(self):
        return not self._obj.empty

def _read_csv(name, parse_dates=None):
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path.name} tidak ditemukan. Jalankan prepare_data.py terlebih dahulu."
        )
    return pd.read_csv(path, parse_dates=parse_dates or [])

def load_company_master():
    return _read_csv("company_master.csv", parse_dates=["ipo_date"])

def load_ai_company():
    return _read_csv("ai_company.csv", parse_dates=["ipo_date"])

def load_financial_panel():
    return _read_csv("financial_panel.csv")

def load_quality_summary():
    return _read_csv("quality_summary.csv")

def load_all():
    return (
        load_company_master(),
        load_ai_company(),
        load_financial_panel(),
        load_quality_summary(),
    )
