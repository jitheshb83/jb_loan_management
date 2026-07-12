"""Amortization schedule engine."""

from datetime import datetime
from typing import List, Dict
from dateutil.relativedelta import relativedelta
from .emi_calculator import EMICalculator


class AmortizationEntry:
    """Single entry in amortization schedule."""

    def __init__(
        self,
        payment_number: int,
        due_date: datetime,
        beginning_balance: float,
        emi: float,
        principal: float,
        interest: float,
        ending_balance: float
    ):
        self.payment_number = payment_number
        self.due_date = due_date
        self.beginning_balance = beginning_balance
        self.emi = emi
        self.principal = principal
        self.interest = interest
        self.ending_balance = ending_balance

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "payment_number": self.payment_number,
            "due_date": self.due_date,
            "beginning_balance": round(self.beginning_balance, 2),
            "emi": round(self.emi, 2),
            "principal": round(self.principal, 2),
            "interest": round(self.interest, 2),
            "ending_balance": round(self.ending_balance, 2),
        }


class AmortizationEngine:
    """Generate amortization schedules."""

    @staticmethod
    def generate_schedule(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: datetime
    ) -> List[AmortizationEntry]:
        """Generate full amortization schedule."""
        if tenure_months <= 0:
            raise ValueError("Tenure must be greater than 0")

        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        monthly_rate = annual_rate / 100 / 12

        schedule = []
        remaining_balance = principal

        for payment_num in range(1, tenure_months + 1):
            # Calculate interest for this month
            interest = remaining_balance * monthly_rate if monthly_rate > 0 else 0
            interest = round(interest, 2)

            # Principal component
            principal_payment = emi - interest
            principal_payment = round(principal_payment, 2)

            # Ensure last payment balances out exactly (rounding may leave a residual)
            if payment_num == tenure_months:
                principal_payment = remaining_balance

            # New balance
            new_balance = remaining_balance - principal_payment
            new_balance = max(0, round(new_balance, 2))

            # Actual payment amount this month (differs from nominal EMI only on the
            # final installment, where principal is adjusted to clear the balance)
            payment_amount = round(principal_payment + interest, 2)

            # Due date: same day-of-month as the loan start, one month per EMI
            # (relativedelta clamps 31st -> 30th/28th where needed)
            due_date = start_date + relativedelta(months=payment_num)

            entry = AmortizationEntry(
                payment_number=payment_num,
                due_date=due_date,
                beginning_balance=remaining_balance,
                emi=payment_amount,
                principal=principal_payment,
                interest=interest,
                ending_balance=new_balance
            )

            schedule.append(entry)
            remaining_balance = new_balance

        return schedule

    @staticmethod
    def get_summary(schedule: List[AmortizationEntry]) -> Dict:
        """Get summary statistics from amortization schedule."""
        if not schedule:
            return {}

        total_interest = sum(entry.interest for entry in schedule)
        total_principal = sum(entry.principal for entry in schedule)
        total_emi = sum(entry.emi for entry in schedule)

        return {
            "total_payments": len(schedule),
            "total_principal": round(total_principal, 2),
            "total_interest": round(total_interest, 2),
            "total_amount": round(total_emi, 2),
            "first_payment_date": schedule[0].due_date,
            "last_payment_date": schedule[-1].due_date,
            "average_monthly_emi": round(total_emi / len(schedule), 2),
        }
