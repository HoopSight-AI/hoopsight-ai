from pathlib import Path

# Core seasonal configuration
CURRENT_SEASON = "2025-26"
CURRENT_SEASON_START_YEAR = 2025
CURRENT_SEASON_END_YEAR = 2026
MODEL_VERSION = "rf-1.1.0"

# Derived paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_EXPORT_DIR = PROJECT_ROOT / "Front" / "CSVFiles"
DATA_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

PREDICTION_RESULTS_CSV = DATA_EXPORT_DIR / "prediction_results.csv"
WIN_LOSS_RECORD_CSV = DATA_EXPORT_DIR / "win_loss_records.csv"
PREDICTION_HISTORY_JSON = DATA_EXPORT_DIR / "prediction_history.json"

# Schedule configuration
SCHEDULE_ROOT = PROJECT_ROOT / "Schedule"
HISTORICAL_DATA_ROOT = PROJECT_ROOT / "Cleaned_Data"
CURRENT_DATA_ROOT = PROJECT_ROOT / "Current_Data"
