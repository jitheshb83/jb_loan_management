"""Loan management module for CRUD operations."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QDateEdit, QTableWidget, QTableWidgetItem, QDialog,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QFont
from src.calculations import EMICalculator
from src.utils.helpers import to_datetime, format_currency
from src.utils.validators import validate_loan_input, ValidationError


class LoanForm(QDialog):
    """Dialog for adding/editing a loan."""

    loan_saved = Signal(dict)

    def __init__(self, parent=None, loan_data=None):
        super().__init__(parent)
        self.loan_data = loan_data
        self.setWindowTitle("Add Loan" if not loan_data else "Edit Loan")
        self.setMinimumWidth(500)
        self._init_ui()
        if loan_data:
            self._populate_form(loan_data)

    def _init_ui(self):
        """Initialize form UI."""
        layout = QGridLayout(self)
        layout.setSpacing(12)

        # Loan Name
        layout.addWidget(QLabel("Loan Name:"), 0, 0)
        self.loan_name_input = QLineEdit()
        self.loan_name_input.setPlaceholderText("e.g., Home Loan - XYZ Bank")
        layout.addWidget(self.loan_name_input, 0, 1)

        # Bank Name
        layout.addWidget(QLabel("Bank Name:"), 1, 0)
        self.bank_name_input = QLineEdit()
        self.bank_name_input.setPlaceholderText("e.g., HDFC Bank")
        layout.addWidget(self.bank_name_input, 1, 1)

        # Principal Amount
        layout.addWidget(QLabel("Principal Amount (₹):"), 2, 0)
        self.principal_input = QDoubleSpinBox()
        self.principal_input.setRange(0, 100000000)
        self.principal_input.setDecimals(2)
        self.principal_input.setSingleStep(100000)
        self.principal_input.setSuffix(" ₹")
        layout.addWidget(self.principal_input, 2, 1)

        # Annual Rate
        layout.addWidget(QLabel("Annual Interest Rate (%):"), 3, 0)
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0, 100)
        self.rate_input.setDecimals(2)
        self.rate_input.setSingleStep(0.1)
        self.rate_input.setSuffix(" %")
        layout.addWidget(self.rate_input, 3, 1)

        # Tenure
        layout.addWidget(QLabel("Tenure (Months):"), 4, 0)
        self.tenure_input = QSpinBox()
        self.tenure_input.setRange(1, 480)
        self.tenure_input.setSingleStep(12)
        layout.addWidget(self.tenure_input, 4, 1)

        # Start Date
        layout.addWidget(QLabel("Start Date:"), 5, 0)
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.start_date_input.setCalendarPopup(True)
        layout.addWidget(self.start_date_input, 5, 1)

        # EMI Display (read-only)
        layout.addWidget(QLabel("Calculated EMI (₹):"), 6, 0)
        self.emi_display = QLineEdit()
        self.emi_display.setReadOnly(True)
        self.emi_display.setStyleSheet("background-color: #f0f0f0;")
        layout.addWidget(self.emi_display, 6, 1)

        # Total Interest Display (read-only)
        layout.addWidget(QLabel("Total Interest (₹):"), 7, 0)
        self.total_interest_display = QLineEdit()
        self.total_interest_display.setReadOnly(True)
        self.total_interest_display.setStyleSheet("background-color: #f0f0f0;")
        layout.addWidget(self.total_interest_display, 7, 1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save Loan")
        save_btn.setMinimumWidth(120)
        save_btn.clicked.connect(self._save_loan)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout, 8, 0, 1, 2)

        # Connect inputs to update EMI
        self.principal_input.valueChanged.connect(self._update_emi)
        self.rate_input.valueChanged.connect(self._update_emi)
        self.tenure_input.valueChanged.connect(self._update_emi)

    def _update_emi(self):
        """Calculate and display EMI."""
        try:
            principal = self.principal_input.value()
            rate = self.rate_input.value()
            tenure = self.tenure_input.value()

            if principal > 0 and tenure > 0:
                emi = EMICalculator.calculate_emi(principal, rate, tenure)
                # Derivable from the EMI just computed — no second calculation
                total_interest = round(emi * tenure - principal, 2)

                self.emi_display.setText(format_currency(emi))
                self.total_interest_display.setText(format_currency(total_interest))
            else:
                self.emi_display.setText("--")
                self.total_interest_display.setText("--")
        except Exception:
            self.emi_display.setText("--")
            self.total_interest_display.setText("--")

    def _save_loan(self):
        """Validate and save loan data."""
        if not self.loan_name_input.text():
            QMessageBox.warning(self, "Validation Error", "Please enter loan name")
            return

        principal = self.principal_input.value()
        rate = self.rate_input.value()
        tenure = self.tenure_input.value()
        start_date = to_datetime(self.start_date_input.date().toPython())

        try:
            validate_loan_input(principal, rate, tenure, start_date)
        except ValidationError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
            return

        loan_data = {
            "name": self.loan_name_input.text(),
            "bank_name": self.bank_name_input.text(),
            "principal_amount": principal,
            "annual_rate": rate,
            "tenure_months": tenure,
            "start_date": start_date,
            # Recompute from the inputs — the display string is cosmetic, not
            # a data source (it can hold "--" and its format may change)
            "emi": EMICalculator.calculate_emi(principal, rate, tenure),
        }

        self.loan_saved.emit(loan_data)
        self.accept()

    def _populate_form(self, loan_data):
        """Populate form with existing loan data."""
        self.loan_name_input.setText(loan_data.get("name", ""))
        self.bank_name_input.setText(loan_data.get("bank_name", ""))
        self.principal_input.setValue(loan_data.get("principal_amount", 0))
        self.rate_input.setValue(loan_data.get("annual_rate", 0))
        self.tenure_input.setValue(loan_data.get("tenure_months", 0))

        start_date = to_datetime(loan_data.get("start_date"), default=None)
        if start_date:
            self.start_date_input.setDate(QDate(start_date.year, start_date.month, start_date.day))
        self._update_emi()


class LoanManagement(QWidget):
    """Loan management module for viewing and managing loans."""

    loan_selected = Signal(dict)

    def __init__(self):
        super().__init__()
        self.loans = []
        self._init_ui()

    def _init_ui(self):
        """Initialize UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Table for loans
        self.loans_table = QTableWidget()
        self.loans_table.setColumnCount(7)
        self.loans_table.setHorizontalHeaderLabels(
            ["Loan Name", "Bank", "Principal", "Rate (%)", "Tenure (M)", "EMI", "Status"]
        )
        self.loans_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.loans_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.loans_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.loans_table.itemSelectionChanged.connect(self._on_loan_selected)
        main_layout.addWidget(self.loans_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        add_btn = QPushButton("+ Add Loan")
        add_btn.setMinimumWidth(120)
        add_btn.clicked.connect(self._add_loan)
        button_layout.addWidget(add_btn)

        edit_btn = QPushButton("Edit Loan")
        edit_btn.setMinimumWidth(120)
        edit_btn.clicked.connect(self._edit_loan)
        button_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Delete Loan")
        delete_btn.setMinimumWidth(120)
        delete_btn.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        delete_btn.clicked.connect(self._delete_loan)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def _create_header(self) -> QWidget:
        """Create header section."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Loan Management")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("View and manage your loans")
        subtitle.setStyleSheet("color: #666;")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.setContentsMargins(0, 0, 0, 16)

        return widget

    def _add_loan(self):
        """Open dialog to add new loan."""
        dialog = LoanForm(self)
        dialog.loan_saved.connect(self._on_loan_saved)
        dialog.exec()

    def _edit_loan(self):
        """Edit selected loan in place."""
        selected_rows = self.loans_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a loan to edit")
            return

        row = selected_rows[0].row()
        loan_data = self.loans[row]
        dialog = LoanForm(self, loan_data)
        # Replace the edited row rather than appending a duplicate
        dialog.loan_saved.connect(lambda data, r=row: self._on_loan_edited(r, data))
        dialog.exec()

    def _delete_loan(self):
        """Delete selected loan."""
        selected_rows = self.loans_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a loan to delete")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this loan? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            self.loans.pop(row)
            self.loans_table.removeRow(row)

    def _on_loan_saved(self, loan_data):
        """Handle a newly added loan."""
        self.loans.append(loan_data)
        self._refresh_table()

    def _on_loan_edited(self, row: int, loan_data):
        """Replace an existing loan after editing."""
        if 0 <= row < len(self.loans):
            self.loans[row] = loan_data
        else:
            self.loans.append(loan_data)
        self._refresh_table()
        # Re-emit so dashboard and other tabs refresh with the edited values
        self.loan_selected.emit(loan_data)

    def _on_loan_selected(self):
        """Handle loan selection."""
        selected_rows = self.loans_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            if row < len(self.loans):
                self.loan_selected.emit(self.loans[row])

    def _refresh_table(self):
        """Refresh loans table."""
        self.loans_table.setRowCount(0)

        for loan in self.loans:
            row_pos = self.loans_table.rowCount()
            self.loans_table.insertRow(row_pos)

            # Loan Name
            self.loans_table.setItem(row_pos, 0, QTableWidgetItem(loan.get("name", "")))

            # Bank Name
            self.loans_table.setItem(row_pos, 1, QTableWidgetItem(loan.get("bank_name", "")))

            # Principal
            principal = loan.get("principal_amount", 0)
            self.loans_table.setItem(row_pos, 2, QTableWidgetItem(format_currency(principal)))

            # Rate
            rate = loan.get("annual_rate", 0)
            self.loans_table.setItem(row_pos, 3, QTableWidgetItem(f"{rate:.2f}%"))

            # Tenure
            tenure = loan.get("tenure_months", 0)
            self.loans_table.setItem(row_pos, 4, QTableWidgetItem(str(tenure)))

            # EMI
            emi = loan.get("emi", 0)
            self.loans_table.setItem(row_pos, 5, QTableWidgetItem(format_currency(emi)))

            # Status
            self.loans_table.setItem(row_pos, 6, QTableWidgetItem("Active"))

    def add_loan(self, loan_data: dict):
        """Programmatically add a loan."""
        self.loans.append(loan_data)
        self._refresh_table()

    def get_loans(self) -> list:
        """Get all loans."""
        return self.loans
