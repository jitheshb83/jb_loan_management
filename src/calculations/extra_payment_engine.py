"""Extra payment (prepayment) calculation engine."""

from datetime import datetime
from typing import List, Dict
from dateutil.relativedelta import relativedelta
from .emi_calculator import EMICalculator


class ExtraPaymentAnalysis:
    """Analysis results of extra payments."""

    def __init__(
        self,
        original_tenure_months: int,
        new_tenure_months: int,
        original_total_interest: float,
        new_total_interest: float,
        interest_saved: float,
        months_saved: int,
        new_closure_date: datetime
    ):
        self.original_tenure_months = original_tenure_months
        self.new_tenure_months = new_tenure_months
        self.original_total_interest = original_total_interest
        self.new_total_interest = new_total_interest
        self.interest_saved = interest_saved
        self.months_saved = months_saved
        self.new_closure_date = new_closure_date

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "original_tenure_months": self.original_tenure_months,
            "new_tenure_months": self.new_tenure_months,
            "original_total_interest": round(self.original_total_interest, 2),
            "new_total_interest": round(self.new_total_interest, 2),
            "interest_saved": round(self.interest_saved, 2),
            "months_saved": self.months_saved,
            "new_closure_date": self.new_closure_date,
        }


class ExtraPaymentEngine:
    """Calculate impact of extra/prepayments on loan."""

    @staticmethod
    def calculate_with_single_extra_payment(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: datetime,
        extra_payment: float,
        extra_payment_date: datetime
    ) -> ExtraPaymentAnalysis:
        """Calculate loan impact with a single one-time extra payment."""
        return ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            principal, annual_rate, tenure_months, start_date,
            [{"amount": extra_payment, "interval_months": None, "start_date": extra_payment_date}]
        )

    @staticmethod
    def calculate_with_periodic_extra_payment(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: datetime,
        extra_payment: float,
        interval_months: int = 1
    ) -> ExtraPaymentAnalysis:
        """
        Calculate loan impact with a recurring extra payment applied every
        `interval_months` (1 = monthly, 3 = quarterly, 12 = yearly), on top
        of the regular EMI. First extra payment lands with EMI number
        `interval_months` (e.g. yearly = month 12), matching the original
        periodic semantics.
        """
        if interval_months <= 0:
            raise ValueError("interval_months must be greater than 0")

        return ExtraPaymentEngine.calculate_with_multiple_extra_payments(
            principal, annual_rate, tenure_months, start_date,
            [{
                "amount": extra_payment,
                "interval_months": interval_months,
                "start_date": start_date + relativedelta(months=interval_months),
            }]
        )

    @staticmethod
    def calculate_with_multiple_extra_payments(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: datetime,
        extra_payments: List[Dict]
    ) -> ExtraPaymentAnalysis:
        """
        Calculate combined loan impact of any number of extra payment plans,
        applied together across the full tenure. Each plan in `extra_payments`
        is a dict with:
          - "amount": float
          - "interval_months": Optional[int] — None for a one-time payment,
            or 1/3/12 (etc.) for a recurring payment every N months
          - "start_date": datetime — when the plan begins

        Multiple one-time payments at different points in the tenure, and/or
        overlapping recurring plans, are all applied cumulatively in the same
        month-by-month simulation.

        A plan dated before the loan start raises ValueError — silently
        applying it in month 1 would overstate the savings.
        """
        # The exact EMI is required here: with the 2-decimal rounded EMI the
        # per-month shortfall compounds and a no-extras baseline can need a
        # 241st month on a 240-month loan, yielding negative months_saved.
        original_emi = EMICalculator.calculate_emi_exact(principal, annual_rate, tenure_months)
        original_interest = EMICalculator.calculate_total_interest(principal, annual_rate, tenure_months)

        monthly_rate = annual_rate / 100 / 12
        remaining_balance = principal
        months_elapsed = 0
        total_interest_paid = 0.0

        plans = []
        for ep in extra_payments:
            offset = (ep["start_date"].year - start_date.year) * 12 + \
                     (ep["start_date"].month - start_date.month)
            if offset < 0:
                raise ValueError(
                    f"Extra payment dated {ep['start_date']:%d-%m-%Y} is before "
                    f"the loan start ({start_date:%d-%m-%Y})"
                )
            # A payment in the loan's first month lands with EMI #1
            offset = max(1, offset)
            plans.append({
                "amount": ep["amount"],
                "interval_months": ep.get("interval_months"),
                "offset": offset,
                "applied": False,
            })

        while remaining_balance > 0.01 and months_elapsed < (tenure_months * 2):  # Safety limit
            interest = remaining_balance * monthly_rate
            months_elapsed += 1

            extra_total = 0.0
            for plan in plans:
                if plan["interval_months"] is None:
                    if months_elapsed == plan["offset"] and not plan["applied"]:
                        extra_total += plan["amount"]
                        plan["applied"] = True
                elif months_elapsed >= plan["offset"] and \
                        (months_elapsed - plan["offset"]) % plan["interval_months"] == 0:
                    extra_total += plan["amount"]

            principal_payment = min(original_emi - interest + extra_total, remaining_balance)

            total_interest_paid += interest
            remaining_balance -= principal_payment

        new_interest = round(total_interest_paid, 2)
        interest_saved = original_interest - new_interest
        months_saved = tenure_months - months_elapsed
        new_closure_date = start_date + relativedelta(months=months_elapsed)

        return ExtraPaymentAnalysis(
            tenure_months, months_elapsed, original_interest, new_interest,
            interest_saved, months_saved, new_closure_date
        )

    @staticmethod
    def calculate_with_monthly_extra_payment(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: datetime,
        monthly_extra: float
    ) -> ExtraPaymentAnalysis:
        """Calculate loan impact with monthly extra payment."""
        return ExtraPaymentEngine.calculate_with_periodic_extra_payment(
            principal, annual_rate, tenure_months, start_date, monthly_extra, interval_months=1
        )
