"""User interface components built with PySide6."""

from .main_window import MainWindow
from .dashboard import Dashboard
from .loan_management import LoanManagement
from .amortization import AmortizationView
from .extra_payments import ExtraPaymentsView
from .simulator import WhatIfSimulator

__all__ = [
    "MainWindow",
    "Dashboard",
    "LoanManagement",
    "AmortizationView",
    "ExtraPaymentsView",
    "WhatIfSimulator",
]
