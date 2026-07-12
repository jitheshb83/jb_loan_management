"""Tests for extra payment engine."""

from datetime import datetime
from src.calculations.extra_payment_engine import ExtraPaymentEngine
from src.calculations import EMICalculator


class TestExtraPaymentEngine:
    """Test cases for ExtraPaymentEngine."""

    PRINCIPAL = 2500000
    RATE = 7.5
    TENURE = 240
    START = datetime(2024, 1, 1)

    def test_single_extra_payment_reduces_interest_plausibly(self):
        """A modest extra payment late in the tenure should trim interest
        by roughly the extra amount, not by an order of magnitude more."""
        result = ExtraPaymentEngine.calculate_with_single_extra_payment(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, 100000, datetime(2031, 7, 1)
        )
        # A single 100k prepayment can't plausibly save 10x+ its own value
        assert result.interest_saved < 500000
        assert result.interest_saved > 0
        assert result.new_tenure_months < self.TENURE

    def test_full_payoff_via_single_extra_payment(self):
        """An extra payment large enough to clear the balance should close
        the loan almost immediately with a small residual interest, not
        report zero interest paid."""
        result = ExtraPaymentEngine.calculate_with_single_extra_payment(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, 5000000, datetime(2025, 1, 1)
        )
        assert result.new_tenure_months <= 13
        assert result.new_total_interest > 0

    def test_multiple_one_time_payments_combine(self):
        """Two one-time prepayments at different points in the tenure should
        save more than either payment alone."""
        both = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START,
            [
                {"amount": 100000, "interval_months": None, "start_date": datetime(2027, 1, 1)},
                {"amount": 150000, "interval_months": None, "start_date": datetime(2031, 1, 1)},
            ],
        )
        first_only = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START,
            [{"amount": 100000, "interval_months": None, "start_date": datetime(2027, 1, 1)}],
        )
        second_only = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START,
            [{"amount": 150000, "interval_months": None, "start_date": datetime(2031, 1, 1)}],
        )
        assert both.interest_saved > first_only.interest_saved
        assert both.interest_saved > second_only.interest_saved

    def test_periodic_intervals_more_frequent_saves_more(self):
        """For the same extra amount, monthly should save more than
        quarterly, which should save more than yearly."""
        monthly = ExtraPaymentEngine.calculate_with_periodic_extra_payment(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, 5000, interval_months=1
        )
        quarterly = ExtraPaymentEngine.calculate_with_periodic_extra_payment(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, 5000, interval_months=3
        )
        yearly = ExtraPaymentEngine.calculate_with_periodic_extra_payment(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, 5000, interval_months=12
        )
        assert monthly.interest_saved > quarterly.interest_saved > yearly.interest_saved

    def test_no_extra_payment_matches_baseline(self):
        """An empty extra payment list should leave the schedule unchanged."""
        result = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, []
        )
        baseline_interest = EMICalculator.calculate_total_interest(self.PRINCIPAL, self.RATE, self.TENURE)
        assert abs(result.new_total_interest - baseline_interest) < 1
        assert result.new_tenure_months == self.TENURE

    def test_baseline_never_negative_across_rates(self):
        """Regression: with the rounded EMI the baseline simulation could run
        one month past tenure (months_saved = -1) at rates like 9.37%. The
        simulation must use the exact EMI so the baseline closes on time."""
        for rate in (6.9, 7.1, 8.13, 9.37, 11.01, 12.5):
            result = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
                self.PRINCIPAL, rate, self.TENURE, self.START, []
            )
            assert result.months_saved == 0, f"rate {rate}: months_saved {result.months_saved}"
            assert abs(result.interest_saved) < 1, f"rate {rate}: interest_saved {result.interest_saved}"

    def test_payment_before_loan_start_rejected(self):
        """Regression: a plan dated before the loan start used to be silently
        clamped to month 1, overstating savings. It must raise instead."""
        import pytest
        with pytest.raises(ValueError):
            ExtraPaymentEngine.calculate_with_multiple_extra_payments(
                self.PRINCIPAL, self.RATE, self.TENURE, self.START,
                [{"amount": 100000, "interval_months": None,
                  "start_date": datetime(2020, 1, 1)}],
            )

    def test_closure_date_uses_calendar_months(self):
        """Regression: closure dates used +30*n days, drifting ~5 days/year
        from the schedule's real due dates."""
        result = ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            self.PRINCIPAL, self.RATE, self.TENURE, self.START, []
        )
        assert result.new_closure_date == datetime(2044, 1, 1)
