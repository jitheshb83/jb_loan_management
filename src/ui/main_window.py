"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
)
from PySide6.QtCore import Qt
from src.ui.dashboard import Dashboard
from src.ui.loan_management import LoanManagement
from src.ui.amortization import AmortizationView
from src.ui.extra_payments import ExtraPaymentsView
from src.ui.simulator import WhatIfSimulator
from src.calculations import AmortizationEngine
from src.database import get_session
from src.utils.helpers import to_datetime
import traceback


class MainWindow(QMainWindow):
    """Main application window with tabs for different modules."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Housing Loan Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Tab widget for different modules
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # One database session shared by all persistent views
        self.db_session = get_session()

        # Initialize modules
        self.dashboard = Dashboard()
        self.loan_management = LoanManagement(session=self.db_session)
        self.amortization_view = AmortizationView()
        self.extra_payments_view = ExtraPaymentsView(session=self.db_session)
        self.simulator_view = WhatIfSimulator()

        # Track the most recent amortization schedule and extra-payment
        # impact for the currently selected loan, so the dashboard can
        # combine both when re-rendering.
        self._current_amortization_data = None
        self._current_extra_payment_impact = None

        # Create tabs
        self._create_tabs()

        # Wire up signals
        self._connect_signals()

        # Status bar
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

        # If loans were loaded from the database, show the first one
        if self.loan_management.loans:
            self.loan_management.loans_table.selectRow(0)

    def _create_tabs(self):
        """Create tabs for each module."""
        # Dashboard
        self.tabs.addTab(self.dashboard, "Dashboard")

        # Loan Management
        self.tabs.addTab(self.loan_management, "Loan Management")

        # Amortization
        self.tabs.addTab(self.amortization_view, "Amortization")

        # Extra Payments
        self.tabs.addTab(self.extra_payments_view, "Extra Payments")

        # What-If Simulator
        self.tabs.addTab(self.simulator_view, "What-If Simulator")

        # Reporting (placeholder)
        reporting_widget = QWidget()
        layout = QVBoxLayout(reporting_widget)
        label = QLabel("Reporting Module - Coming Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.tabs.addTab(reporting_widget, "Reporting")

    def _connect_signals(self):
        """Connect signals between modules."""
        # When a loan is selected in loan management, update all modules
        self.loan_management.loan_selected.connect(self._on_loan_selected)

        # When extra payment impact changes, refresh the dashboard's KPIs
        self.extra_payments_view.impact_changed.connect(self._on_extra_payment_impact_changed)

    def _on_loan_selected(self, loan_data):
        """Handle loan selection from loan management."""
        if not loan_data:
            return

        # Generate amortization schedule
        try:
            principal = loan_data.get("principal_amount", 0)
            rate = loan_data.get("annual_rate", 0)
            tenure = loan_data.get("tenure_months", 0)
            start_date = to_datetime(loan_data.get("start_date"))

            schedule = AmortizationEngine.generate_schedule(principal, rate, tenure, start_date)
            amortization_data = [entry.to_dict() for entry in schedule]
            self._current_amortization_data = amortization_data
            self._current_extra_payment_impact = None

            # Update every module with the newly selected loan
            self.dashboard.set_loan_data(loan_data, amortization_data)
            self.amortization_view.set_loan_data(loan_data, amortization_data)
            self.extra_payments_view.set_loan_data(loan_data)
            self.simulator_view.set_loan_data(loan_data)

            # Switch to dashboard tab
            self.tabs.setCurrentIndex(0)

            self.statusbar.showMessage(f"Loan selected: {loan_data.get('name', 'Unknown')}")
        except Exception as e:
            # Surface the full traceback for debugging — a status-bar string
            # alone has already hidden a real rendering bug once.
            traceback.print_exc()
            self.statusbar.showMessage(f"Error loading loan: {str(e)}")

    def _on_extra_payment_impact_changed(self, impact: dict):
        """Refresh the dashboard's Interest Saved KPI when prepayment impact changes."""
        loan_data = self.extra_payments_view.loan_data
        if not loan_data or not self._current_amortization_data:
            return

        self._current_extra_payment_impact = impact or None
        self.dashboard.set_loan_data(
            loan_data, self._current_amortization_data, self._current_extra_payment_impact
        )
