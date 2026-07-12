"""Loan simulator for what-if scenarios."""

from datetime import datetime
from typing import Dict, Any
from .emi_calculator import EMICalculator
from .extra_payment_engine import ExtraPaymentEngine


class LoanSimulator:
    """Simulate various what-if scenarios for loans."""

    @staticmethod
    def simulate_rate_change(
        principal: float,
        current_rate: float,
        tenure_months: int,
        start_date: datetime,
        new_rate: float,
        rate_change_date: datetime
    ) -> Dict[str, Any]:
        """Simulate impact of interest rate change.

        Raises ValueError if `rate_change_date` falls before the loan start
        or on/after the final EMI — a rate change outside the tenure has no
        scenario to simulate.
        """
        # Calculate payments until rate change
        months_until_change = (rate_change_date.year - start_date.year) * 12 + \
                             (rate_change_date.month - start_date.month)
        if months_until_change < 0:
            raise ValueError(
                f"Rate change date ({rate_change_date:%d-%m-%Y}) is before the "
                f"loan start ({start_date:%d-%m-%Y})"
            )
        if months_until_change >= tenure_months:
            raise ValueError(
                f"Rate change date ({rate_change_date:%d-%m-%Y}) is after the "
                f"loan's final EMI — nothing left to simulate"
            )
        months_until_change = max(1, months_until_change)

        # Original scenario
        original_emi = EMICalculator.calculate_emi(principal, current_rate, tenure_months)
        original_interest = EMICalculator.calculate_total_interest(principal, current_rate, tenure_months)

        # After rate change
        remaining_balance = EMICalculator.calculate_remaining_balance(
            principal, current_rate, tenure_months, months_until_change - 1
        )
        remaining_tenure = tenure_months - months_until_change + 1

        new_emi = EMICalculator.calculate_emi(remaining_balance, new_rate, remaining_tenure)
        new_total_interest = EMICalculator.calculate_total_interest(
            remaining_balance, new_rate, remaining_tenure
        )

        # Interest paid before the change, in closed form: over k payments the
        # borrower pays k*EMI, of which (principal - remaining_balance) was
        # principal — the rest is interest.
        payments_before = months_until_change - 1
        emi_exact = EMICalculator.calculate_emi_exact(principal, current_rate, tenure_months)
        interest_before = emi_exact * payments_before - (principal - remaining_balance)
        total_new_interest = interest_before + new_total_interest

        return {
            "scenario_type": "rate_change",
            "original_rate": current_rate,
            "new_rate": new_rate,
            "rate_change_date": rate_change_date,
            "original_emi": round(original_emi, 2),
            "new_emi": round(new_emi, 2),
            "emi_change": round(new_emi - original_emi, 2),
            "original_total_interest": round(original_interest, 2),
            "new_total_interest": round(total_new_interest, 2),
            "interest_impact": round(total_new_interest - original_interest, 2),
        }

    @staticmethod
    def simulate_extra_payment(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: datetime,
        extra_payment: float,
        extra_payment_date: datetime
    ) -> Dict[str, Any]:
        """Simulate impact of extra/prepayment."""
        analysis = ExtraPaymentEngine.calculate_with_single_extra_payment(
            principal, annual_rate, tenure_months, start_date,
            extra_payment, extra_payment_date
        )

        return {
            "scenario_type": "extra_payment",
            "extra_payment": round(extra_payment, 2),
            "extra_payment_date": extra_payment_date,
            "original_tenure_months": analysis.original_tenure_months,
            "new_tenure_months": analysis.new_tenure_months,
            "tenure_reduction": analysis.months_saved,
            "original_total_interest": round(analysis.original_total_interest, 2),
            "new_total_interest": round(analysis.new_total_interest, 2),
            "interest_saved": round(analysis.interest_saved, 2),
            "new_closure_date": analysis.new_closure_date,
        }

    @staticmethod
    def simulate_tenure_change(
        principal: float,
        annual_rate: float,
        original_tenure_months: int,
        new_tenure_months: int
    ) -> Dict[str, Any]:
        """Simulate impact of tenure change (refinance scenario)."""
        original_emi = EMICalculator.calculate_emi(principal, annual_rate, original_tenure_months)
        original_interest = EMICalculator.calculate_total_interest(principal, annual_rate, original_tenure_months)

        new_emi = EMICalculator.calculate_emi(principal, annual_rate, new_tenure_months)
        new_interest = EMICalculator.calculate_total_interest(principal, annual_rate, new_tenure_months)

        return {
            "scenario_type": "tenure_change",
            "original_tenure_months": original_tenure_months,
            "new_tenure_months": new_tenure_months,
            "tenure_change": new_tenure_months - original_tenure_months,
            "original_emi": round(original_emi, 2),
            "new_emi": round(new_emi, 2),
            "emi_change": round(new_emi - original_emi, 2),
            "original_total_interest": round(original_interest, 2),
            "new_total_interest": round(new_interest, 2),
            "interest_impact": round(new_interest - original_interest, 2),
        }

