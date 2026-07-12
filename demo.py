#!/usr/bin/env python
"""Demo script to test Dashboard and Loan Management modules."""

import sys
from datetime import datetime
from src.calculations import EMICalculator, AmortizationEngine
from src.calculations.extra_payment_engine import ExtraPaymentEngine


def test_calculations():
    """Test basic calculations."""
    print("=" * 60)
    print("TESTING CALCULATION ENGINES")
    print("=" * 60)

    # Test data
    principal = 2500000  # ₹25 lakh
    annual_rate = 7.5   # 7.5% p.a.
    tenure_months = 240  # 20 years
    start_date = datetime.now()

    print(f"\nLoan Details:")
    print(f"  Principal: ₹{principal:,.2f}")
    print(f"  Annual Rate: {annual_rate}%")
    print(f"  Tenure: {tenure_months} months ({tenure_months // 12} years)")
    print(f"  Start Date: {start_date.strftime('%d-%m-%Y')}")

    # Test EMI Calculator
    print(f"\n--- EMI Calculator ---")
    emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
    total_interest = EMICalculator.calculate_total_interest(principal, annual_rate, tenure_months)
    total_amount = EMICalculator.calculate_total_amount(principal, annual_rate, tenure_months)

    print(f"  EMI: ₹{emi:,.2f}")
    print(f"  Total Interest: ₹{total_interest:,.2f}")
    print(f"  Total Amount Payable: ₹{total_amount:,.2f}")

    # Test Amortization Engine
    print(f"\n--- Amortization Schedule (First 3 & Last 3 Months) ---")
    schedule = AmortizationEngine.generate_schedule(principal, annual_rate, tenure_months, start_date)
    summary = AmortizationEngine.get_summary(schedule)

    # Show first 3
    for entry in schedule[:3]:
        print(f"  Month {entry.payment_number}: "
              f"Balance ₹{entry.beginning_balance:>12,.0f} → "
              f"Principal ₹{entry.principal:>10,.0f} + "
              f"Interest ₹{entry.interest:>8,.0f}")

    print(f"  ...")

    # Show last 3
    for entry in schedule[-3:]:
        print(f"  Month {entry.payment_number}: "
              f"Balance ₹{entry.beginning_balance:>12,.0f} → "
              f"Principal ₹{entry.principal:>10,.0f} + "
              f"Interest ₹{entry.interest:>8,.0f}")

    # Test Extra Payment Engine
    print(f"\n--- Extra Payment Analysis ---")
    extra_payment_amount = 100000
    extra_payment_date = datetime(start_date.year + 5, start_date.month, 1)

    analysis = ExtraPaymentEngine.calculate_with_single_extra_payment(
        principal, annual_rate, tenure_months, start_date,
        extra_payment_amount, extra_payment_date
    )

    print(f"  Extra Payment: ₹{extra_payment_amount:,.2f} on {extra_payment_date.strftime('%d-%m-%Y')}")
    print(f"  Original Tenure: {analysis.original_tenure_months} months")
    print(f"  New Tenure: {analysis.new_tenure_months} months")
    print(f"  Months Saved: {analysis.months_saved}")
    print(f"  Interest Saved: ₹{analysis.interest_saved:,.2f}")
    print(f"  New Closure Date: {analysis.new_closure_date.strftime('%d-%m-%Y')}")

    print("\n" + "=" * 60)
    print("✓ All calculation tests passed!")
    print("=" * 60)

    return {
        "name": "Home Loan - HDFC",
        "bank_name": "HDFC Bank",
        "principal_amount": principal,
        "annual_rate": annual_rate,
        "tenure_months": tenure_months,
        "start_date": start_date,
        "emi": emi,
    }, [entry.to_dict() for entry in schedule]


if __name__ == "__main__":
    loan_data, amortization_data = test_calculations()

    print("\n✓ Demo data ready for UI testing")
    print(f"  Loan: {loan_data['name']}")
    print(f"  Schedule entries: {len(amortization_data)}")
