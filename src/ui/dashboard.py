"""Dashboard module for loan overview and KPIs."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
)
from PySide6.QtGui import QFont
from datetime import datetime
from src.utils.helpers import to_datetime, format_currency, format_date
from src.ui.widgets import StatCard
import pyqtgraph as pg


class BalanceChartWidget(QWidget):
    """Chart showing balance reduction over time."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Outstanding Balance Over Time")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Create PyQtGraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Balance', units='₹')
        self.plot_widget.setLabel('bottom', 'Month')
        self.plot_widget.setTitle('Loan Balance Reduction')
        self.plot_widget.setMinimumHeight(300)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        layout.addWidget(self.plot_widget)

    def update_chart(self, amortization_data):
        """Update chart with amortization data."""
        if not amortization_data:
            return

        months = list(range(1, len(amortization_data) + 1))
        balances = [entry.get('ending_balance', 0) for entry in amortization_data]

        self.plot_widget.clear()
        self.plot_widget.plot(months, balances, pen='#366092', symbol='o', symbolSize=3)


class InterestChartWidget(QWidget):
    """Bar chart showing principal vs interest split."""

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Principal vs Interest Distribution")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Create PyQtGraph plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Amount', units='₹')
        self.plot_widget.setTitle('Payment Distribution')
        self.plot_widget.setMinimumHeight(300)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        layout.addWidget(self.plot_widget)

    def update_chart(self, principal_total: float, interest_total: float):
        """Update bar chart with principal and interest totals."""
        self.plot_widget.clear()

        values = [principal_total, interest_total]
        colors = [pg.mkColor('#4CAF50'), pg.mkColor('#FF9800')]

        bar_graph = pg.BarGraphItem(x=[0, 1], height=values, width=0.6, brushes=colors)
        self.plot_widget.addItem(bar_graph)

        # Set x-axis labels
        ax = self.plot_widget.getAxis('bottom')
        ax.setTicks([[(0, 'Principal'), (1, 'Interest')]])


class Dashboard(QWidget):
    """Main dashboard widget displaying loan overview and KPIs."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # KPI Cards
        kpi_section = self._create_kpi_section()
        main_layout.addWidget(kpi_section)

        # Charts section
        charts_section = self._create_charts_section()
        main_layout.addWidget(charts_section)

        main_layout.addStretch()

    def _create_header(self) -> QWidget:
        """Create dashboard header with loan name and status."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("Dashboard")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        self.loan_name_label = QLabel("No Loan Selected")
        loan_font = QFont()
        loan_font.setPointSize(12)
        self.loan_name_label.setFont(loan_font)
        self.loan_name_label.setStyleSheet("color: #666;")

        layout.addWidget(title)
        layout.addWidget(self.loan_name_label)
        layout.setContentsMargins(0, 0, 0, 16)

        return widget

    def _create_kpi_section(self) -> QWidget:
        """Create KPI cards section."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(16)

        # KPI Cards
        self.outstanding_balance_card = StatCard("Outstanding Balance", color="#FF6B6B", value_point_size=24)
        self.total_interest_paid_card = StatCard("Total Interest Paid", color="#4ECDC4", value_point_size=24)
        self.interest_saved_card = StatCard("Interest Saved", color="#45B7D1", value_point_size=24)
        self.closure_date_card = StatCard("Projected Closure", color="#96CEB4", value_point_size=24)

        layout.addWidget(self.outstanding_balance_card, 0, 0)
        layout.addWidget(self.total_interest_paid_card, 0, 1)
        layout.addWidget(self.interest_saved_card, 0, 2)
        layout.addWidget(self.closure_date_card, 0, 3)

        return widget

    def _create_charts_section(self) -> QWidget:
        """Create charts section."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(16)

        # Balance chart
        self.balance_chart = BalanceChartWidget()
        layout.addWidget(self.balance_chart)

        # Interest chart
        self.interest_chart = InterestChartWidget()
        layout.addWidget(self.interest_chart)

        return widget

    def set_loan_data(self, loan: dict, amortization: list, extra_payments_impact: dict = None):
        """Set loan data and update dashboard display."""
        if not loan or not amortization:
            self._clear_dashboard()
            return

        # Update header
        self.loan_name_label.setText(f"{loan.get('name', 'Unnamed Loan')} - {loan.get('bank_name', '')}")

        # Full-tenure totals (used for the principal/interest distribution chart)
        principal_total = loan.get('principal_amount', 0)
        total_interest = sum(entry.get('interest', 0) for entry in amortization)

        # EMIs elapsed = schedule entries whose due date has passed. Counting
        # from the schedule itself (rather than re-deriving month arithmetic)
        # keeps this KPI consistent with the dates the Amortization tab shows.
        today = datetime.now()
        elapsed = sum(1 for entry in amortization
                      if to_datetime(entry.get('due_date'), default=today) <= today)

        if elapsed > 0:
            outstanding = amortization[elapsed - 1].get('ending_balance', 0)
            total_interest_paid = sum(entry.get('interest', 0) for entry in amortization[:elapsed])
        else:
            outstanding = principal_total
            total_interest_paid = 0

        # Projected closure: with prepayments configured, use the recalculated
        # closure date so this KPI agrees with the Interest Saved card;
        # otherwise the full schedule's final due date.
        interest_saved = 0
        closure_date = amortization[-1].get('due_date')
        if extra_payments_impact:
            interest_saved = extra_payments_impact.get('interest_saved', 0)
            closure_date = extra_payments_impact.get('new_closure_date', closure_date)

        # Update KPI cards
        self.outstanding_balance_card.set_value(format_currency(outstanding))
        self.total_interest_paid_card.set_value(format_currency(total_interest_paid))
        self.interest_saved_card.set_value(format_currency(interest_saved))
        self.closure_date_card.set_value(format_date(closure_date) if closure_date else "--/--/----")

        # Update charts
        self.balance_chart.update_chart(amortization)
        self.interest_chart.update_chart(principal_total, total_interest)

    def _clear_dashboard(self):
        """Clear dashboard when no loan is selected."""
        self.loan_name_label.setText("No Loan Selected")
        # Reset KPI cards
        for card in [
            self.outstanding_balance_card,
            self.total_interest_paid_card,
            self.interest_saved_card,
            self.closure_date_card
        ]:
            card.set_value("--")
