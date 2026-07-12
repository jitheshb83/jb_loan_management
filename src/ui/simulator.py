"""What-If Simulator module for comparing loan scenarios."""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QDoubleSpinBox, QSpinBox,
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from src.calculations import LoanSimulator
from src.utils.helpers import to_datetime


class RateChangeForm(QWidget):
    """Form for simulating an interest rate change."""

    def __init__(self, run_callback):
        super().__init__()
        self.run_callback = run_callback
        layout = QGridLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("New Annual Rate (%):"), 0, 0)
        self.new_rate_input = QDoubleSpinBox()
        self.new_rate_input.setRange(0, 100)
        self.new_rate_input.setDecimals(2)
        self.new_rate_input.setSingleStep(0.1)
        layout.addWidget(self.new_rate_input, 0, 1)

        layout.addWidget(QLabel("Effective Date:"), 1, 0)
        self.effective_date_input = QDateEdit()
        self.effective_date_input.setDate(QDate.currentDate())
        self.effective_date_input.setCalendarPopup(True)
        layout.addWidget(self.effective_date_input, 1, 1)

        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self._run)
        layout.addWidget(run_btn, 2, 1)
        layout.setRowStretch(3, 1)

    def _run(self):
        date = self.effective_date_input.date().toPython()
        self.run_callback("rate_change", {
            "new_rate": self.new_rate_input.value(),
            "rate_change_date": datetime(date.year, date.month, date.day),
        })


class TenureChangeForm(QWidget):
    """Form for simulating a tenure change."""

    def __init__(self, run_callback):
        super().__init__()
        self.run_callback = run_callback
        layout = QGridLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("New Tenure (Months):"), 0, 0)
        self.new_tenure_input = QSpinBox()
        self.new_tenure_input.setRange(1, 480)
        self.new_tenure_input.setSingleStep(12)
        layout.addWidget(self.new_tenure_input, 0, 1)

        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self._run)
        layout.addWidget(run_btn, 1, 1)
        layout.setRowStretch(2, 1)

    def _run(self):
        self.run_callback("tenure_change", {
            "new_tenure_months": self.new_tenure_input.value(),
        })


class ExtraPaymentForm(QWidget):
    """Form for simulating a one-time extra payment."""

    def __init__(self, run_callback):
        super().__init__()
        self.run_callback = run_callback
        layout = QGridLayout(self)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Extra Payment Amount (₹):"), 0, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 100000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(10000)
        layout.addWidget(self.amount_input, 0, 1)

        layout.addWidget(QLabel("Payment Date:"), 1, 0)
        self.payment_date_input = QDateEdit()
        self.payment_date_input.setDate(QDate.currentDate())
        self.payment_date_input.setCalendarPopup(True)
        layout.addWidget(self.payment_date_input, 1, 1)

        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self._run)
        layout.addWidget(run_btn, 2, 1)
        layout.setRowStretch(3, 1)

    def _run(self):
        date = self.payment_date_input.date().toPython()
        self.run_callback("extra_payment", {
            "extra_payment": self.amount_input.value(),
            "extra_payment_date": datetime(date.year, date.month, date.day),
        })


class WhatIfSimulator(QWidget):
    """Simulator for comparing multiple what-if loan scenarios side by side."""

    def __init__(self):
        super().__init__()
        self.loan_data = None
        self.results = []
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header
        title = QLabel("What-If Simulator")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        self.loan_name_label = QLabel("No Loan Selected")
        self.loan_name_label.setStyleSheet("color: #666;")

        main_layout.addWidget(title)
        main_layout.addWidget(self.loan_name_label)

        # Scenario tabs
        self.scenario_tabs = QTabWidget()
        self.scenario_tabs.addTab(RateChangeForm(self._run_scenario), "Rate Change")
        self.scenario_tabs.addTab(TenureChangeForm(self._run_scenario), "Tenure Change")
        self.scenario_tabs.addTab(ExtraPaymentForm(self._run_scenario), "Extra Payment")
        self.scenario_tabs.setMaximumHeight(180)
        main_layout.addWidget(self.scenario_tabs)

        # Comparison table
        comparison_label = QLabel("Scenario Comparison")
        comparison_font = QFont()
        comparison_font.setPointSize(14)
        comparison_font.setBold(True)
        comparison_label.setFont(comparison_font)
        main_layout.addWidget(comparison_label)

        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(6)
        self.comparison_table.setHorizontalHeaderLabels([
            "Scenario", "Details", "New EMI", "New Total Interest", "Interest Impact", "Tenure Impact"
        ])
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.comparison_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.comparison_table)

        clear_btn = QPushButton("Clear Comparisons")
        clear_btn.clicked.connect(self._clear_results)
        main_layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def set_loan_data(self, loan: dict):
        """Set the active loan and reset comparisons."""
        self.loan_data = loan
        self.results = []
        self._refresh_table()

        if loan:
            self.loan_name_label.setText(f"{loan.get('name', 'Unnamed Loan')} - {loan.get('bank_name', '')}")
        else:
            self.loan_name_label.setText("No Loan Selected")

    def _run_scenario(self, scenario_type: str, params: dict):
        """Run a simulation scenario and add it to the comparison table."""
        if not self.loan_data:
            QMessageBox.warning(self, "No Loan Selected", "Please select a loan first")
            return

        principal = self.loan_data.get("principal_amount", 0)
        rate = self.loan_data.get("annual_rate", 0)
        tenure = self.loan_data.get("tenure_months", 0)
        start_date = to_datetime(self.loan_data.get("start_date"))

        try:
            if scenario_type == "rate_change":
                result = LoanSimulator.simulate_rate_change(
                    principal, rate, tenure, start_date,
                    params["new_rate"], params["rate_change_date"]
                )
                details = f"Rate → {params['new_rate']}% from {params['rate_change_date'].strftime('%d-%m-%Y')}"
                row = {
                    "scenario": "Rate Change",
                    "details": details,
                    "new_emi": result["new_emi"],
                    "new_total_interest": result["new_total_interest"],
                    "interest_impact": result["interest_impact"],
                    "tenure_impact": "—",
                }

            elif scenario_type == "tenure_change":
                result = LoanSimulator.simulate_tenure_change(
                    principal, rate, tenure, params["new_tenure_months"]
                )
                details = f"Tenure → {params['new_tenure_months']} months"
                row = {
                    "scenario": "Tenure Change",
                    "details": details,
                    "new_emi": result["new_emi"],
                    "new_total_interest": result["new_total_interest"],
                    "interest_impact": result["interest_impact"],
                    "tenure_impact": f"{result['tenure_change']:+d} months",
                }

            elif scenario_type == "extra_payment":
                result = LoanSimulator.simulate_extra_payment(
                    principal, rate, tenure, start_date,
                    params["extra_payment"], params["extra_payment_date"]
                )
                details = f"₹{params['extra_payment']:,.0f} on {params['extra_payment_date'].strftime('%d-%m-%Y')}"
                row = {
                    "scenario": "Extra Payment",
                    "details": details,
                    "new_emi": None,
                    "new_total_interest": result["new_total_interest"],
                    "interest_impact": -result["interest_saved"],
                    "tenure_impact": f"-{result['tenure_reduction']} months",
                }
            else:
                return

            self.results.append(row)
            self._refresh_table()

        except Exception as e:
            QMessageBox.warning(self, "Simulation Error", f"Could not run simulation: {str(e)}")

    def _refresh_table(self):
        """Refresh the comparison table."""
        self.comparison_table.setRowCount(0)
        for row_idx, row in enumerate(self.results):
            self.comparison_table.insertRow(row_idx)

            emi_str = f"₹{row['new_emi']:,.2f}" if row["new_emi"] is not None else "—"
            interest_str = f"₹{row['new_total_interest']:,.2f}"

            impact = row["interest_impact"]
            impact_str = f"{'+' if impact >= 0 else ''}₹{impact:,.2f}"

            values = [row["scenario"], row["details"], emi_str, interest_str, impact_str, row["tenure_impact"]]
            for col, value in enumerate(values):
                self.comparison_table.setItem(row_idx, col, QTableWidgetItem(value))

    def _clear_results(self):
        """Clear all scenario comparisons."""
        self.results = []
        self._refresh_table()
