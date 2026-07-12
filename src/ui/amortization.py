"""Amortization module for viewing and exporting payment schedules."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.reporting import ExcelExporter
from src.ui.widgets import StatCard
from src.utils.helpers import format_currency, format_date


class AmortizationView(QWidget):
    """View for browsing and exporting the full amortization schedule."""

    def __init__(self):
        super().__init__()
        self.loan_data = None
        self.amortization_data = None
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header
        header_layout = QVBoxLayout()
        title = QLabel("Amortization Schedule")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        self.loan_name_label = QLabel("No Loan Selected")
        self.loan_name_label.setStyleSheet("color: #666;")
        header_layout.addWidget(title)
        header_layout.addWidget(self.loan_name_label)
        main_layout.addLayout(header_layout)

        # Summary cards
        summary_layout = QGridLayout()
        summary_layout.setSpacing(16)
        self.total_payments_card = StatCard("Total Payments", color="#366092")
        self.total_principal_card = StatCard("Total Principal", color="#4CAF50")
        self.total_interest_card = StatCard("Total Interest", color="#FF9800")
        self.total_amount_card = StatCard("Total Amount Payable", color="#FF6B6B")

        summary_layout.addWidget(self.total_payments_card, 0, 0)
        summary_layout.addWidget(self.total_principal_card, 0, 1)
        summary_layout.addWidget(self.total_interest_card, 0, 2)
        summary_layout.addWidget(self.total_amount_card, 0, 3)
        main_layout.addLayout(summary_layout)

        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(7)
        self.schedule_table.setHorizontalHeaderLabels([
            "#", "Due Date", "Beginning Balance", "EMI", "Principal", "Interest", "Ending Balance"
        ])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.schedule_table)

        # Export button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        export_btn = QPushButton("Export to Excel")
        export_btn.setMinimumWidth(150)
        export_btn.clicked.connect(self._export_to_excel)
        button_layout.addWidget(export_btn)
        main_layout.addLayout(button_layout)

    def set_loan_data(self, loan: dict, amortization: list):
        """Set loan data and populate the schedule."""
        self.loan_data = loan
        self.amortization_data = amortization

        if not loan or not amortization:
            self._clear_view()
            return

        self.loan_name_label.setText(f"{loan.get('name', 'Unnamed Loan')} - {loan.get('bank_name', '')}")

        total_principal = sum(entry.get("principal", 0) for entry in amortization)
        total_interest = sum(entry.get("interest", 0) for entry in amortization)

        self.total_payments_card.set_value(str(len(amortization)))
        self.total_principal_card.set_value(format_currency(total_principal))
        self.total_interest_card.set_value(format_currency(total_interest))
        self.total_amount_card.set_value(format_currency(total_principal + total_interest))

        self._populate_table(amortization)

    def _populate_table(self, amortization: list):
        """Populate the schedule table."""
        self.schedule_table.setRowCount(0)
        self.schedule_table.setRowCount(len(amortization))

        for row, entry in enumerate(amortization):
            values = [
                str(entry.get("payment_number", "")),
                format_date(entry.get("due_date")),
                format_currency(entry.get("beginning_balance", 0)),
                format_currency(entry.get("emi", 0)),
                format_currency(entry.get("principal", 0)),
                format_currency(entry.get("interest", 0)),
                format_currency(entry.get("ending_balance", 0)),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col > 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.schedule_table.setItem(row, col, item)

    def _export_to_excel(self):
        """Export the current schedule to Excel."""
        if not self.amortization_data or not self.loan_data:
            QMessageBox.warning(self, "No Data", "Please select a loan first")
            return

        default_name = f"{self.loan_data.get('name', 'loan')}_amortization.xlsx"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Amortization Schedule", default_name, "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        try:
            loan_details = {
                "Loan Name": self.loan_data.get("name"),
                "Bank": self.loan_data.get("bank_name"),
                "Principal": self.loan_data.get("principal_amount"),
                "Annual Rate (%)": self.loan_data.get("annual_rate"),
                "Tenure (Months)": self.loan_data.get("tenure_months"),
                "EMI": self.loan_data.get("emi"),
            }
            ExcelExporter.export_amortization_schedule(self.amortization_data, loan_details, file_path)
            QMessageBox.information(self, "Export Complete", f"Schedule exported to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export: {str(e)}")

    def _clear_view(self):
        """Clear the view when no loan is selected."""
        self.loan_name_label.setText("No Loan Selected")
        for card in [
            self.total_payments_card, self.total_principal_card,
            self.total_interest_card, self.total_amount_card
        ]:
            card.set_value("--")
        self.schedule_table.setRowCount(0)
