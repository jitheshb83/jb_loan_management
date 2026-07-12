"""Extra payments module for configuring and analyzing prepayments."""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QDoubleSpinBox, QComboBox,
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from src.calculations.extra_payment_engine import ExtraPaymentEngine
from src.utils.helpers import to_datetime

FREQUENCY_INTERVALS = {
    "One-Time": None,
    "Monthly": 1,
    "Quarterly": 3,
    "Yearly": 12,
}


class ImpactCard(QFrame):
    """Small stat card for displaying prepayment impact metrics."""

    def __init__(self, title: str, color: str = "#366092"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666;")
        title_font = QFont()
        title_font.setPointSize(9)
        title_label.setFont(title_font)

        self.value_label = QLabel("--")
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)


class ExtraPaymentsView(QWidget):
    """View for configuring extra payments and analyzing their impact."""

    impact_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.loan_data = None
        self.extra_payments = []
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header
        title = QLabel("Extra Payments")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        self.loan_name_label = QLabel("No Loan Selected")
        self.loan_name_label.setStyleSheet("color: #666;")

        main_layout.addWidget(title)
        main_layout.addWidget(self.loan_name_label)

        # Configuration form
        form_layout = QGridLayout()
        form_layout.setSpacing(12)

        form_layout.addWidget(QLabel("Extra Payment Amount (₹):"), 0, 0)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 100000000)
        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(10000)
        form_layout.addWidget(self.amount_input, 0, 1)

        form_layout.addWidget(QLabel("Frequency:"), 0, 2)
        self.frequency_input = QComboBox()
        self.frequency_input.addItems(list(FREQUENCY_INTERVALS.keys()))
        form_layout.addWidget(self.frequency_input, 0, 3)

        form_layout.addWidget(QLabel("Start Date:"), 1, 0)
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        form_layout.addWidget(self.start_date_input, 1, 1)

        add_btn = QPushButton("+ Add Extra Payment")
        add_btn.clicked.connect(self._add_extra_payment)
        form_layout.addWidget(add_btn, 1, 3)

        main_layout.addLayout(form_layout)

        # Configured extra payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(4)
        self.payments_table.setHorizontalHeaderLabels(["Amount", "Frequency", "Start Date", ""])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.payments_table.setMaximumHeight(160)
        main_layout.addWidget(self.payments_table)

        # Impact summary
        impact_label = QLabel("Prepayment Impact")
        impact_font = QFont()
        impact_font.setPointSize(14)
        impact_font.setBold(True)
        impact_label.setFont(impact_font)
        main_layout.addWidget(impact_label)

        impact_layout = QGridLayout()
        impact_layout.setSpacing(16)
        self.new_tenure_card = ImpactCard("New Tenure", color="#366092")
        self.tenure_reduction_card = ImpactCard("Tenure Reduction", color="#4CAF50")
        self.interest_saved_card = ImpactCard("Interest Saved", color="#FF9800")
        self.new_closure_date_card = ImpactCard("New Closure Date", color="#45B7D1")

        impact_layout.addWidget(self.new_tenure_card, 0, 0)
        impact_layout.addWidget(self.tenure_reduction_card, 0, 1)
        impact_layout.addWidget(self.interest_saved_card, 0, 2)
        impact_layout.addWidget(self.new_closure_date_card, 0, 3)
        main_layout.addLayout(impact_layout)

        main_layout.addStretch()

        note = QLabel(
            "Note: Impact reflects all configured extra payments combined — add as many "
            "one-time, monthly, quarterly, or yearly plans as you like across the tenure."
        )
        note.setStyleSheet("color: #999; font-size: 11px;")
        main_layout.addWidget(note)

    def set_loan_data(self, loan: dict):
        """Set the active loan and reset configured extra payments."""
        self.loan_data = loan
        self.extra_payments = []
        self._refresh_table()
        self._clear_impact()

        if loan:
            self.loan_name_label.setText(f"{loan.get('name', 'Unnamed Loan')} - {loan.get('bank_name', '')}")
        else:
            self.loan_name_label.setText("No Loan Selected")

    def _add_extra_payment(self):
        """Add a new extra payment configuration and recalculate impact."""
        if not self.loan_data:
            QMessageBox.warning(self, "No Loan Selected", "Please select a loan first")
            return

        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Extra payment amount must be greater than 0")
            return

        frequency = self.frequency_input.currentText()
        start_date = self.start_date_input.date().toPython()
        start_date = datetime(start_date.year, start_date.month, start_date.day)

        payment = {"amount": amount, "frequency": frequency, "start_date": start_date}
        self.extra_payments.append(payment)
        self._refresh_table()
        self._calculate_impact()

    def _refresh_table(self):
        """Refresh the configured extra payments table."""
        self.payments_table.setRowCount(0)
        for row, payment in enumerate(self.extra_payments):
            self.payments_table.insertRow(row)
            self.payments_table.setItem(row, 0, QTableWidgetItem(f"₹{payment['amount']:,.2f}"))
            self.payments_table.setItem(row, 1, QTableWidgetItem(payment["frequency"]))
            self.payments_table.setItem(row, 2, QTableWidgetItem(payment["start_date"].strftime("%d-%m-%Y")))

            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked=False, r=row: self._remove_extra_payment(r))
            self.payments_table.setCellWidget(row, 3, remove_btn)

    def _remove_extra_payment(self, row: int):
        """Remove a configured extra payment."""
        if 0 <= row < len(self.extra_payments):
            self.extra_payments.pop(row)
        self._refresh_table()

        if self.extra_payments:
            self._calculate_impact()
        else:
            self._clear_impact()

    def _calculate_impact(self):
        """Calculate and display the combined impact of every configured extra payment."""
        if not self.loan_data or not self.extra_payments:
            return

        principal = self.loan_data.get("principal_amount", 0)
        rate = self.loan_data.get("annual_rate", 0)
        tenure = self.loan_data.get("tenure_months", 0)
        loan_start = to_datetime(self.loan_data.get("start_date"))

        try:
            plans = [
                {
                    "amount": payment["amount"],
                    "interval_months": FREQUENCY_INTERVALS[payment["frequency"]],
                    "start_date": payment["start_date"],
                }
                for payment in self.extra_payments
            ]

            analysis = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
                principal, rate, tenure, loan_start, plans
            )

            self.new_tenure_card.set_value(f"{analysis.new_tenure_months} months")
            self.tenure_reduction_card.set_value(f"{analysis.months_saved} months")
            self.interest_saved_card.set_value(f"₹{analysis.interest_saved:,.2f}")
            self.new_closure_date_card.set_value(analysis.new_closure_date.strftime("%d-%m-%Y"))

            self.impact_changed.emit(analysis.to_dict())
        except Exception as e:
            QMessageBox.warning(self, "Calculation Error", f"Could not calculate impact: {str(e)}")

    def _clear_impact(self):
        """Reset impact cards to empty state."""
        for card in [
            self.new_tenure_card, self.tenure_reduction_card,
            self.interest_saved_card, self.new_closure_date_card
        ]:
            card.set_value("--")
        self.impact_changed.emit({})
