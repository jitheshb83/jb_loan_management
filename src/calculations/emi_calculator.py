"""EMI (Equated Monthly Installment) calculator."""

from typing import Tuple


class EMICalculator:
    """Calculate EMI and related loan metrics."""

    @staticmethod
    def calculate_emi_exact(principal: float, annual_rate: float, tenure_months: int) -> float:
        """
        Calculate the exact (unrounded) EMI:
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        where P = principal, r = monthly rate, n = tenure in months.

        Simulations must use this value — with the 2-decimal rounded EMI, a
        baseline (no-prepayment) simulation can need one extra month to clear
        the rounding shortfall, producing nonsense like negative months saved.
        """
        if tenure_months <= 0:
            raise ValueError("Tenure must be greater than 0")
        if annual_rate < 0:
            raise ValueError("Annual rate cannot be negative")

        monthly_rate = annual_rate / 100 / 12

        if monthly_rate == 0:
            return principal / tenure_months

        numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
        denominator = ((1 + monthly_rate) ** tenure_months) - 1

        return numerator / denominator

    @staticmethod
    def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
        """Calculate the EMI rounded to 2 decimals (display/payment value)."""
        return round(EMICalculator.calculate_emi_exact(principal, annual_rate, tenure_months), 2)

    @staticmethod
    def calculate_total_interest(principal: float, annual_rate: float, tenure_months: int) -> float:
        """Calculate total interest payable over the loan tenure."""
        emi = EMICalculator.calculate_emi_exact(principal, annual_rate, tenure_months)
        total_paid = emi * tenure_months
        total_interest = total_paid - principal
        return round(total_interest, 2)

    @staticmethod
    def calculate_total_amount(principal: float, annual_rate: float, tenure_months: int) -> float:
        """Calculate total amount to be paid (principal + interest)."""
        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
        return round(emi * tenure_months, 2)

    @staticmethod
    def calculate_principal_interest_split(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        payment_number: int
    ) -> Tuple[float, float]:
        """
        Calculate principal and interest components for a specific payment.
        Returns (principal_amount, interest_amount)
        """
        if payment_number <= 0 or payment_number > tenure_months:
            raise ValueError(f"Payment number must be between 1 and {tenure_months}")

        monthly_rate = annual_rate / 100 / 12
        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)

        # Calculate remaining balance before this payment
        if monthly_rate == 0:
            remaining_balance = principal - (emi * (payment_number - 1))
            interest = 0
        else:
            remaining_balance = principal * (
                ((1 + monthly_rate) ** tenure_months - (1 + monthly_rate) ** (payment_number - 1)) /
                ((1 + monthly_rate) ** tenure_months - 1)
            )
            interest = remaining_balance * monthly_rate

        principal_amount = emi - interest
        return round(principal_amount, 2), round(interest, 2)

    @staticmethod
    def calculate_remaining_balance(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        payments_made: int
    ) -> float:
        """Calculate remaining balance after a certain number of payments."""
        if payments_made < 0 or payments_made > tenure_months:
            raise ValueError(f"Payments made must be between 0 and {tenure_months}")

        monthly_rate = annual_rate / 100 / 12
        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)

        if monthly_rate == 0:
            return principal - (emi * payments_made)

        remaining_balance = principal * (
            ((1 + monthly_rate) ** tenure_months - (1 + monthly_rate) ** payments_made) /
            ((1 + monthly_rate) ** tenure_months - 1)
        )

        return round(max(0, remaining_balance), 2)
