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

        categories = ['Principal', 'Interest']
        values = [principal_total, interest_total]
        colors = [pg.mkColor('#4CAF50'), pg.mkColor('#FF9800')]

        x = np.arange(len(categories))
        bar_graph = pg.BarGraphItem(x=x, height=values, width=0.6, brushes=colors)
        self.plot_widget.addItem(bar_graph)

        # Set x-axis labels
        ax = self.plot_widget.getAxis('bottom')
        ax.setTicks([[(0, 'Principal'), (1, 'Interest')]])


class Dashboard(QWidget):
    """Main dashboard widget displaying loan overview and KPIs."""

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
        self.outstanding_balance_card = KPICard("Outstanding Balance", "₹0.00", color="#FF6B6B")
        self.total_interest_paid_card = KPICard("Total Interest Paid", "₹0.00", color="#4ECDC4")
        self.interest_saved_card = KPICard("Interest Saved", "₹0.00", color="#45B7D1")
        self.closure_date_card = KPICard("Projected Closure", "--/--/----", color="#96CEB4")

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
        self.loan_data = loan
        self.amortization_data = amortization

        if not loan or not amortization:
            self._clear_dashboard()
            return

        # Update header
        self.loan_name_label.setText(f"{loan.get('name', 'Unnamed Loan')} - {loan.get('bank_name', '')}")

        # Full-tenure totals (used for the principal/interest distribution chart)
        principal_total = loan.get('principal_amount', 0)
        total_interest = sum(entry.get('interest', 0) for entry in amortization)

        # Figure out how many EMIs have actually elapsed since the loan
        # started, so "outstanding" and "interest paid" reflect today, not
        # the schedule's final (near-zero) balance.
        elapsed = self._elapsed_payments(loan, len(amortization))

        if elapsed > 0:
            outstanding = amortization[elapsed - 1].get('ending_balance', 0)
            total_interest_paid = sum(entry.get('interest', 0) for entry in amortization[:elapsed])
        else:
            outstanding = principal_total
            total_interest_paid = 0

        # Projected final closure date (end of the full schedule)
        closure_date = amortization[-1].get('due_date')

        # Interest saved (from extra payments)
        interest_saved = 0
        if extra_payments_impact:
            interest_saved = extra_payments_impact.get('interest_saved', 0)

        # Update KPI cards
        self.outstanding_balance_card.set_value(f"₹{outstanding:,.2f}")
        self.total_interest_paid_card.set_value(f"₹{total_interest_paid:,.2f}")
        self.interest_saved_card.set_value(f"₹{interest_saved:,.2f}")

        # Format closure date
        if closure_date:
            if isinstance(closure_date, str):
                closure_date_str = closure_date
            else:
                closure_date_str = closure_date.strftime("%d-%m-%Y")
        else:
            closure_date_str = "--/--/----"
        self.closure_date_card.set_value(closure_date_str)

        # Update charts
        self.balance_chart.update_chart(amortization)
        self.interest_chart.update_chart(principal_total, total_interest)

    @staticmethod
    def _elapsed_payments(loan: dict, tenure_months: int) -> int:
        """Number of EMIs due between the loan's start date and today, clamped
        to the schedule length."""
        start_date = to_datetime(loan.get('start_date'))

        today = datetime.now()
        elapsed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
        if today.day < start_date.day:
            elapsed -= 1

        return max(0, min(elapsed, tenure_months))

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
