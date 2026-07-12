"""Application configuration."""

from pathlib import Path

# Application
APP_NAME = "Housing Loan Manager"
APP_VERSION = "0.1.0"

# Paths
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = Path.home() / ".loan_manager"
DATABASE_PATH = DATA_DIR / "loans.db"
LOGS_DIR = DATA_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# UI
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_CURRENCY = "₹"

# Calculations
DEFAULT_DECIMAL_PLACES = 2
