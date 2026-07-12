"""Tests for the loan what-if simulator."""

import pytest
from datetime import datetime
from src.calculations import LoanSimulator, EMICalculator


class TestLoanSimulator:
    """Test cases for LoanSimulator."""

    PRINCIPAL = 2500000
    RATE = 7.5
    TENURE = 240
    START = datetime(2024, 1, 1)

    def test_rate_change_within_tenure(self):
        """A mid-tenure rate drop should lower the EMI and total interest."""
        result = LoanSimulator.simulate_rate_change(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START,
            6.5, datetime(2030, 1, 1)
        )
        assert result["new_emi"] < result["original_emi"]
        assert result["interest_impact"] < 0

    def test_rate_change_closed_form_interest_before(self):
        """Regression: interest paid before the change must equal the sum of
        the per-payment interest components (closed form vs loop)."""
        k = 71  # payments before the change
        result = LoanSimulator.simulate_rate_change(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START,
            6.5, datetime(2030, 1, 1)
        )
        loop_interest = sum(
            EMICalculator.calculate_principal_interest_split(
                self.PRINCIPAL, self.RATE, self.TENURE, i
            )[1] for i in range(1, k + 1)
        )
        remaining = EMICalculator.calculate_remaining_balance(
            self.PRINCIPAL, self.RATE, self.TENURE, k
        )
        expected_after = EMICalculator.calculate_total_interest(
            remaining, 6.5, self.TENURE - k
        )
        assert abs(result["new_total_interest"] - (loop_interest + expected_after)) < 5

    def test_rate_change_before_start_rejected(self):
        """Regression: dates outside the tenure raised cryptic internal
        errors; they must raise a clear ValueError."""
        with pytest.raises(ValueError):
            LoanSimulator.simulate_rate_change(
                self.PRINCIPAL, self.RATE, self.TENURE, self.START,
                6.5, datetime(2020, 1, 1)
            )

    def test_rate_change_after_end_rejected(self):
        with pytest.raises(ValueError):
            LoanSimulator.simulate_rate_change(
                self.PRINCIPAL, self.RATE, 12, self.START,
                6.5, datetime(2030, 1, 1)
            )

    def test_tenure_change(self):
        """Shortening tenure raises the EMI but cuts total interest."""
        result = LoanSimulator.simulate_tenure_change(
            self.PRINCIPAL, self.RATE, self.TENURE, 180
        )
        assert result["new_emi"] > result["original_emi"]
        assert result["interest_impact"] < 0
        assert result["tenure_change"] == -60
