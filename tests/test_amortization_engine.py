"""Tests for amortization engine."""

from datetime import datetime
from src.calculations import AmortizationEngine


class TestAmortizationEngine:
    """Test cases for AmortizationEngine."""

    def test_generate_schedule(self):
        """Test amortization schedule generation."""
        principal = 1000000
        annual_rate = 7
        tenure = 12
        start_date = datetime(2024, 1, 1)

        schedule = AmortizationEngine.generate_schedule(principal, annual_rate, tenure, start_date)

        assert len(schedule) == tenure
        assert schedule[0].beginning_balance == principal
        assert schedule[-1].ending_balance == 0 or schedule[-1].ending_balance < 1

    def test_schedule_principal_interest_sum(self):
        """Test that principal + interest equals EMI."""
        principal = 1000000
        annual_rate = 7
        tenure = 12
        start_date = datetime(2024, 1, 1)

        schedule = AmortizationEngine.generate_schedule(principal, annual_rate, tenure, start_date)

        for entry in schedule:
            total = entry.principal + entry.interest
            assert abs(total - entry.emi) < 0.01

    def test_get_summary(self):
        """Test summary statistics."""
        principal = 1000000
        annual_rate = 7
        tenure = 12
        start_date = datetime(2024, 1, 1)

        schedule = AmortizationEngine.generate_schedule(principal, annual_rate, tenure, start_date)
        summary = AmortizationEngine.get_summary(schedule)

        assert summary["total_payments"] == tenure
        assert summary["total_principal"] > 0
        assert summary["total_interest"] > 0
        assert summary["total_amount"] > principal

    def test_empty_schedule_summary(self):
        """Test summary of empty schedule."""
        summary = AmortizationEngine.get_summary([])
        assert summary == {}
