"""Tests for EMI calculator."""

import pytest
from src.calculations import EMICalculator


class TestEMICalculator:
    """Test cases for EMICalculator."""

    def test_calculate_emi_basic(self):
        """Test basic EMI calculation."""
        # Principal: 25,00,000, Rate: 7%, Tenure: 240 months (20 years)
        emi = EMICalculator.calculate_emi(2500000, 7, 240)
        assert emi > 0
        assert isinstance(emi, float)

    def test_calculate_emi_zero_rate(self):
        """Test EMI calculation with zero interest rate."""
        principal = 1000000
        emi = EMICalculator.calculate_emi(principal, 0, 120)
        expected = principal / 120
        assert abs(emi - expected) < 0.01

    def test_calculate_total_interest(self):
        """Test total interest calculation."""
        principal = 1000000
        annual_rate = 7
        tenure = 120
        total_interest = EMICalculator.calculate_total_interest(principal, annual_rate, tenure)
        assert total_interest > 0
        assert total_interest < principal * annual_rate

    def test_principal_interest_split(self):
        """Test principal and interest split for a payment."""
        principal = 1000000
        annual_rate = 7
        tenure = 120
        principal_part, interest_part = EMICalculator.calculate_principal_interest_split(
            principal, annual_rate, tenure, 1
        )
        assert principal_part > 0
        assert interest_part > 0
        emi = EMICalculator.calculate_emi(principal, annual_rate, tenure)
        assert abs((principal_part + interest_part) - emi) < 0.01

    def test_remaining_balance(self):
        """Test remaining balance calculation."""
        principal = 1000000
        annual_rate = 7
        tenure = 120
        remaining = EMICalculator.calculate_remaining_balance(principal, annual_rate, tenure, 60)
        assert 0 < remaining < principal

    def test_invalid_tenure(self):
        """Test that invalid tenure raises error."""
        with pytest.raises(ValueError):
            EMICalculator.calculate_emi(1000000, 7, 0)

    def test_negative_rate(self):
        """Test that negative rate raises error."""
        with pytest.raises(ValueError):
            EMICalculator.calculate_emi(1000000, -5, 120)
